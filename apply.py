#!/usr/bin/env python3
import re
import sys
import os
import textwrap

def extract_and_write_code_blocks(full_text):
    """
    Extracts code blocks and writes them to files.
    Supports two formats:
    1. Traditional format:
        ```
        // path/to/file.ext
        content
        ```
    2. Inline format:
        ```lang:path/to/file.ext
        content
        ```
    """
    # Unified regex pattern to handle both formats
    pattern = re.compile(
        r"^\s*```(\w*)(?::\s*([^\n]+?))?\s*\n"  # Optional language and inline path
        r"(\s*(?:#|//|--)\s*(.*?)\s*\n)?"       # Traditional path line (comment style) - made optional
        r"(.*?)"                                 # Content block
        r"\n^\s*```\s*$",
        re.DOTALL | re.MULTILINE
    )

    matches = pattern.findall(full_text)

    if not matches:
        print("No valid code blocks found.")
        return

    print(f"Found {len(matches)} code block(s). Processing...")

    for match in matches:
        lang = match[0]
        inline_path = match[1] if match[1] else None
        traditional_path_line = match[2] if match[2] else None
        traditional_path = match[3] if match[3] else None
        content = match[4]

        # Determine which path format we're using
        if inline_path:
            filepath = inline_path
        elif traditional_path:
            filepath = traditional_path
        else:
            print("Warning: Found a code block with an empty filepath. Skipping.")
            continue

        filepath = filepath.replace("\\", "/")  # Normalize path separators
        print(f"  Processing: {filepath}")

        try:
            # Ensure the directory exists
            dir_name = os.path.dirname(filepath)
            if dir_name:
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

    try:
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
