import argparse
import os
import subprocess
import re
from datetime import datetime
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
    '*.csv', '*.parquet', '*.txt'
]

TREE_EXCLUDE_PATTERNS = [
    '*.json', '*.pyc', '__pycache__', '*.git*', '*.zip',
    '*.tar.gz', '*.db', '*.csv', '*.parquet', '*.cache',
    '*.log', 'node_modules'
]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate code review files")
    parser.add_argument('--base', required=True, help='Base branch or commit')
    parser.add_argument('--head', required=True, help='Target branch or commit')
    parser.add_argument('--debug', action='store_true', help='Show debug information')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    return parser.parse_args()

def get_git_diff(base, head):
    try:
        diff = subprocess.check_output(['git', 'diff', base, head], text=True)
        return diff
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get git diff: {e}")

def get_base_files(base):
    try:
        files = subprocess.check_output(['git', 'ls-tree', '-r', base, '--name-only'], text=True)
        return files.splitlines()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to get base files: {e}")

def is_excluded(filename):
    return any(re.match(pattern.replace('*', '.*'), filename) for pattern in EXCLUDED_PATTERNS)

def get_project_structure():
    """Get the project structure using tree command while excluding irrelevant files"""
    exclude_patterns = [f"-I '{pattern}'" for pattern in TREE_EXCLUDE_PATTERNS]
    exclude_str = ' '.join(exclude_patterns)
    
    try:
        cmd = f"tree -L 3 {exclude_str}"
        structure = subprocess.check_output(cmd, shell=True, text=True)
        return structure
    except subprocess.CalledProcessError:
        return "Failed to get project structure"

def get_related_files(diff):
    structure = get_project_structure()
    
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
    
    try:
        response = completion(model="gpt-4", prompt=prompt)
        matches = re.search(r'<files>(.*?)</files>', response, re.DOTALL)
        if matches:
            return matches.group(1).strip().splitlines()
        return []
    except Exception as e:
        print(f"LLM error: {e}")
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
            files_content.append(f"  {file}")
        else:
            files_content.append(f"  <!-- {file} -->")
    
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
    
    try:
        # Stage 1: Generate .review.xml
        diff = get_git_diff(args.base, args.head)
        base_files = get_base_files(args.base)
        related_files = get_related_files(diff)
        
        if args.debug:
            print(f"Found {len(related_files)} related files")
            print("Related files:", related_files)
        
        review_xml = generate_review_xml(args.base, args.head, diff, base_files, related_files)
        
        if not args.dry_run:
            with open('.review.xml', 'w') as f:
                f.write(review_xml)
            print("Generated .review.xml")
            
            # Stage 2: Generate .output.xml
            output_xml = generate_output_xml(review_xml)
            with open('.output.xml', 'w') as f:
                f.write(output_xml)
            print("Generated .output.xml")
        else:
            print("Dry run - no files written")
            if args.debug:
                print("\nReview XML preview:")
                print(review_xml)
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
