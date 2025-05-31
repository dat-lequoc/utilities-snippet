#!/usr/bin/env python3
import re
import sys
import os
import textwrap

def extract_and_write_code_blocks(full_text):
    """
    Extracts code blocks and writes them to files.
    A code block is expected in the format:
    ```
    // path/to/file.ext
    [[ content ]]
    ```
    """
    # Regex to find the file path and the content
    # - ```: Matches the opening backticks
    # - \s*\n: Matches optional whitespace and a newline
    # - //\s*(.*?)\s*\n: Captures the file path (non-greedy)
    #   - //: Matches the comment start
    #   - \s*: Matches optional leading whitespace for the path
    #   - (.*?): Captures the actual path (non-greedy)
    #   - \s*\n: Matches optional trailing whitespace and a newline before content
    # - (.*?): Captures the content (non-greedy, dot matches newline)
    # - \n```: Matches a newline and the closing backticks
    # re.DOTALL allows . to match newline characters for the content block
    # re.MULTILINE allows ^ to match at the beginning of each line
    # The first capturing group (\w*) is for the optional language specifier.
    # (?:#|//|--) matches #, //, or -- for the file path line.
    pattern = re.compile(r"^\s*```(\w*)\s*\n^\s*(?:#|//|--)\s*(.*?)\s*\n(.*?)\n^\s*```\s*$", re.DOTALL | re.MULTILINE)
    
    matches = pattern.findall(full_text)
    
    if not matches:
        print("No valid code blocks found.")
        return

    print(f"Found {len(matches)} code block(s). Processing...")
    
    # lang will store the language specifier (e.g., "python", "typescript") or an empty string if not provided.
    # It's not used in the current logic but is parsed correctly.
    for lang, filepath, content in matches:
        filepath = filepath.strip() # Remove any leading/trailing whitespace from path
        filepath = filepath.replace("\\", "/") # Normalize path separators
        # content = textwrap.dedent(content) # Dedent the content block <-- Removed this line
        # content = content.strip()   # Remove leading/trailing whitespace/newlines from content
        
        if not filepath:
            print("Warning: Found a code block with an empty filepath. Skipping.")
            continue
            
        print(f"  Processing: {filepath}")
        
        try:
            # Ensure the directory exists
            dir_name = os.path.dirname(filepath)
            if dir_name: # If dirname is not empty (i.e., not a top-level file)
                os.makedirs(dir_name, exist_ok=True)
            
            # Write/overwrite the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    Successfully wrote to {filepath}")
            
        except OSError as e:
            print(f"    Error writing to {filepath}: {e}")
        except Exception as e:
            print(f"    An unexpected error occurred with {filepath}: {e}")

def main():
    print("Paste your text containing code blocks.")
    print("Press Ctrl+D (Linux/macOS) or Ctrl+Z then Enter (Windows) to finish input.")
    print("-------------------------------------------------------------------------")
    
    input_lines = []
    try:
        # Read all lines from stdin until EOF
        full_input_text = sys.stdin.read()
    except KeyboardInterrupt:
        print("\nInput interrupted by user (Ctrl+C). Exiting.")
        sys.exit(1)

    if not full_input_text.strip():
        print("No input received. Exiting.")
        return
        
    extract_and_write_code_blocks(full_input_text)
    print("-------------------------------------------------------------------------")
    print("Processing complete.")

if __name__ == "__main__":
    main()
