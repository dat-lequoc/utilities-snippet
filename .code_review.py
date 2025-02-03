"""
Code Review XML Generator
------------------------

A tool to generate structured XML files for code review by comparing git branches/commits.

Usage:
    python code_review.py --base <base-branch> --head <target-branch> [--debug] [--dry-run]

Key Features:
- Generates .review.xml with diff and related files for review
- Creates .output.xml with full file contents for context
- Automatically identifies related files using LLM
- Filters out binary and data files
- Preserves file structure and formatting

Example:
    python code_review.py --base main --head feature/new-feature

Output Files:
    .review.xml  - Contains diff and file list for review
    .output.xml  - Contains full content of related files

Debug Options:
    --debug    - Show detailed processing information
    --dry-run  - Preview without writing files
"""

import argparse
import os
import subprocess
import re
from datetime import datetime
import logging  # Add logging import
from litellm import completion

"""
STAGE 1: Generate .review.xml

Input Processing:
- Accept two command line arguments: --base (base branch/commit) and --head (target branch/commit)
- Validate inputs are valid git references
- Exit with error if validation fails

File Selection Process:
- Get git diff between base and head branches
- Filter out binary files and files matching common data patterns (.json, .pyc, etc.)
- Send filtered diff to LLM using XML format
- Parse LLM response to get list of related files
- Get list of all files from base branch

XML Generation (.review.xml):
- Create .review.xml with following structure:
  - <purpose> tag contains system prompt for code review
  - <code-files> tag lists all files from base
    - Related files (from LLM) are uncommented
    - Other files are commented with <!-- -->
  - <diff> tag contains filtered git diff output

Error Handling:
- Validate XML structure before saving
- Create backup if .review.xml already exists
- Log all operations in debug mode

STAGE 2: Generate .output.xml

File Processing:
- Read .review.xml
- Process only uncommented files in <code-files>
- Read raw content of each file from base branch
- Preserve original file formatting

Output Generation:
- Create .output.xml with same structure as .review.xml
- Replace file names in <code-files> with actual file content
- Keep <purpose> and <diff> sections unchanged
- Validate XML before saving

Utility Features:
- Create .gitignore entries for .review.xml and .output.xml
- Add --dry-run option to preview without saving
- Add --debug option to show LLM interactions

Files to Exclude:
- Binary files
- Common data files (.json, .log, .pyc)
- Cache files and directories
- Large files (configurable threshold)
- Version control files (.git/)

"""

# Constants
EXCLUDED_PATTERNS = [
    '*.json', '*.pyc', '*.log', '*.cache', '*.git*', 
    '*__pycache__*', '*.zip', '*.tar.gz', '*.db',
    '*.csv', '*.parquet', '*.txt', '*.lock'
]

TREE_EXCLUDE_PATTERNS = [
    '*.json', '*.pyc', '__pycache__', '*.git*', '*.zip',
    '*.tar.gz', '*.db', '*.csv', '*.parquet', '*.cache',
    '*.log', 'node_modules', '*.lock'
]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate code review files")
    parser.add_argument('--base', required=True, help='Base branch or commit')
    parser.add_argument('--head', required=True, help='Target branch or commit')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    return parser.parse_args()

def git_checkout(ref):
    """Checkout a git reference (branch/commit)"""
    try:
        subprocess.check_output(['git', 'checkout', ref], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to checkout {ref}: {e.output}")

def get_git_diff(base, head):
    try:
        # First checkout base to ensure correct state
        git_checkout(base)
        # Build the git diff command with pathspec exclusions.
        # Git supports the ":(exclude)pattern" syntax after a "--" separator.
        cmd = ['git', 'diff', base, head, '--']
        for pattern in EXCLUDED_PATTERNS:
            cmd.append(f":(exclude){pattern}")
        # Run the command and return the diff text.
        diff = subprocess.check_output(cmd, text=True)
        return diff
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get git diff: {e}")

def get_base_files(base):
    try:
        # Make sure we're on the base branch/commit
        git_checkout(base)
        # Get list of files
        files = subprocess.check_output(['git', 'ls-tree', '-r', base, '--name-only'], text=True)
        return files.splitlines()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get base files: {e}")

def is_excluded(filename):
    return any(re.match(pattern.replace('*', '.*'), filename) for pattern in EXCLUDED_PATTERNS)

def get_project_structure(ref=None):
    """Get the project structure using tree command while excluding irrelevant files"""
    if ref:
        git_checkout(ref)
        
    exclude_patterns = [f"-I '{pattern}'" for pattern in TREE_EXCLUDE_PATTERNS]
    exclude_str = ' '.join(exclude_patterns)
    
    try:
        cmd = f"tree -L 3 {exclude_str}"
        structure = subprocess.check_output(cmd, shell=True, text=True)
        return structure
    except subprocess.CalledProcessError:
        return "Failed to get project structure"

def setup_logging(debug_mode):
    """Configure logging to both file and console"""
    os.makedirs('.prompts', exist_ok=True)
    
    # Clear existing log file
    log_file = '.prompts/.code_review.log'
    with open(log_file, 'w') as f:
        f.write(f"=== New logging session started at {datetime.now()} ===\n")
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Setup file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Set log level based on debug mode
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

def get_related_files(diff, base):
    structure = get_project_structure(base)
    
    prompt = f"""
    Analyze this git diff and project structure to list only the filenames that are directly related 
    or highly coupled with the changes. Consider:
    - Files being modified
    - Files that import/use modified code
    - Files that provide the context or importance of the project
    
    Project structure:
    <structure>
    {structure}
    </structure>
    
    Respond in this format:
    <files>
    filename1
    filename2
    </files>
    
    Git diff:
    {diff}
    """
    
    logging.info("LLM Prompt for related files:\n%s", prompt)
    
    try:
        response = completion(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="claude-3-5-sonnet-20241022",
        )
        logging.info("LLM Response:\n%s", response.choices[0].message.content)
        
        matches = re.search(r'<files>(.*?)</files>', response.choices[0].message.content, re.DOTALL)
        if matches:
            files = matches.group(1).strip().splitlines()
            logging.info("Found %d related files: %s", len(files), files)
            return files
        return []
    except Exception as e:
        logging.error("LLM error: %s", e)
        return []

def generate_review_xml(base, head, diff, base_files, related_files):
    purpose = """
    Review the code changes focusing on:
    - Code correctness and potential bugs
    - Architecture and design consistency with existing code
    Provide a code review, and refactored updated snippets if needed. 
    """
    
    files_content = []
    for file in base_files:
        if is_excluded(file):
            continue
        if file in related_files:
            files_content.append(f"  {file}\n")
        else:
            files_content.append(f"  <!-- {file} -->\n")
    
    return f"""<purpose>
{purpose}
</purpose>

<code-files>
{"".join(files_content)}
</code-files>

<diff>
{diff}
</diff>"""

def generate_output_xml(review_xml):
    # Parse the review XML to get uncommented files
    files_section = re.search(r'<code-files>(.*?)</code-files>', review_xml, re.DOTALL)
    if not files_section:
        raise Exception("No code-files section found in review XML")
    
    files = []
    for line in files_section.group(1).splitlines():
        line = line.strip()
        if line and not line.startswith('<!--'):
            files.append(line.strip())
    
    # Replace file names with content
    files_content = []
    for file in files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                files_content.append(f"<file path='{file}'>\n{content}\n</file>")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Preserve purpose and diff sections
    purpose = re.search(r'<purpose>(.*?)</purpose>', review_xml, re.DOTALL).group(1)
    diff = re.search(r'<diff>(.*?)</diff>', review_xml, re.DOTALL).group(1)
    
    return f"""<purpose>
{purpose}
</purpose>

<code-files>
{"".join(files_content)}
</code-files>

<diff>
{diff}
</diff>"""

def main():
    args = parse_arguments()
    
    # Setup logging first thing
    setup_logging(args.debug)
    logging.info("Starting code review generation")
    logging.info("Base: %s, Head: %s", args.base, args.head)
    
    try:
        # Stage 1: Generate .review.xml
        logging.info("Getting git diff...")
        diff = get_git_diff(args.base, args.head)
        
        logging.info("Getting base files...")
        base_files = get_base_files(args.base)
        
        logging.info("Finding related files...")
        related_files = get_related_files(diff, args.base)
        
        logging.info("Generating review XML...")
        review_xml = generate_review_xml(args.base, args.head, diff, base_files, related_files)
        
        # Create .prompts directory if it doesn't exist
        os.makedirs('.prompts', exist_ok=True)
        
        if not args.dry_run:
            logging.info("Writing .review.xml...")
            with open('.prompts/.review.xml', 'w') as f:
                f.write(review_xml)
            logging.info("Generated .prompts/.review.xml")
            
            logging.info("Generating output XML...")
            output_xml = generate_output_xml(review_xml)
            
            logging.info("Writing .output.xml...")
            with open('.prompts/.output.xml', 'w') as f:
                f.write(output_xml)
            logging.info("Generated .prompts/.output.xml")
        else:
            logging.info("Dry run - no files written")
            if args.debug:
                logging.debug("\nReview XML preview:\n%s", review_xml)
    
    except Exception as e:
        logging.error("Error: %s", e, exc_info=True)
        return 1
    
    logging.info("Code review generation completed successfully")
    return 0

if __name__ == "__main__":
    exit(main())

