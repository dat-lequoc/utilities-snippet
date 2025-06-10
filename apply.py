#!/usr/bin/env python3
import re
import sys
import os
import textwrap
import argparse

def get_clipboard_content():
    """Get content from system clipboard."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        clipboard_content = root.clipboard_get()
        root.destroy()
        return clipboard_content
    except ImportError:
        print("Error: tkinter not available. Cannot access clipboard.")
        sys.exit(1)
    except tk.TclError:
        print("Error: No content in clipboard or unable to access clipboard.")
        sys.exit(1)
    except Exception as e:
        print(f"Error accessing clipboard: {e}")
        sys.exit(1)

def save_full_content_to_candidate_file(content, candidate_number):
    """Save full content to a numbered candidate file."""
    candidates_dir = "candidates"

    # Ensure the candidates directory exists
    os.makedirs(candidates_dir, exist_ok=True)

    filename = f"implementation_{candidate_number}.txt"
    filepath = os.path.join(candidates_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully saved full content to {filepath}")
        return True
    except OSError as e:
        print(f"Error writing to {filepath}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred writing to {filepath}: {e}")
        return False

def extract_and_write_code_blocks(full_text):
    """
    Extracts code blocks and writes them to files.
    Supports three formats:
    1. Traditional format (WRITE):
        ```
        // path/to/file.ext
        content
        ```
    2. Inline format (WRITE):
        ```lang:path/to/file.ext
        content
        ```
    3. SEARCH/REPLACE format (can have multiple S/R blocks):
        ```lang:path/to/file.ext
        <<<<<<< SEARCH
        search content 1
        =======
        replace content 1
        >>>>>>> REPLACE
        ... any other text here is ignored if S/R blocks are present ...
        <<<<<<< SEARCH
        search content 2
        =======
        replace content 2
        >>>>>>> REPLACE
        ```
    """
    # Unified regex pattern to handle both formats for extracting the main block
    pattern = re.compile(
        r"^\s*```(\w*)(?::\s*([^\n]+?))?\s*\n"  # Optional language and inline path
        r"(\s*(?:#|//|--)\s*(.*?)\s*\n)?"       # Traditional path line (comment style) - made optional
        r"(.*?)"                                 # Content block
        r"\n^\s*```\s*$",
        re.DOTALL | re.MULTILINE
    )

    # Pattern for individual SEARCH/REPLACE blocks (finds all occurrences)
    sr_pattern = re.compile(
        r'<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE',
        re.DOTALL
    )

    matches = pattern.findall(full_text)

    if not matches:
        print("No valid code blocks found.")
        return

    print(f"Found {len(matches)} code block(s). Processing...")

    for match_idx, match_tuple in enumerate(matches):
        lang = match_tuple[0]
        inline_path = match_tuple[1] if match_tuple[1] else None
        # traditional_path_line = match_tuple[2] # Not directly used, but part of capture
        traditional_path = match_tuple[3] if match_tuple[3] else None
        content = match_tuple[4]

        # Determine which path format we're using
        if inline_path:
            filepath = inline_path.strip()
        elif traditional_path:
            filepath = traditional_path.strip()
        else:
            print(f"Warning: Found a code block (match #{match_idx+1}) with an empty filepath. Skipping.")
            continue

        filepath = filepath.replace("\\", "/")  # Normalize path separators
        print(f"\n  Processing: {filepath}")

        # Check for SEARCH/REPLACE segments within the content
        sr_segments = sr_pattern.findall(content)

        if sr_segments:
            print(f"    [SEARCH/REPLACE mode with {len(sr_segments)} operation(s)]")

            # Warn if there's other content mixed with S/R blocks, as it will be ignored.
            content_remainder = sr_pattern.sub('', content).strip()
            if content_remainder:
                print(f"    Warning: Code block for {filepath} contains SEARCH/REPLACE blocks mixed with other literal content.")
                print(f"    This other literal content will be IGNORED. Only SEARCH/REPLACE operations will be applied.")
                # print(f"    Ignored content: \n{textwrap.indent(content_remainder, '      ')}")


            try:
                if not os.path.exists(filepath):
                    print(f"    Error: File not found for SEARCH/REPLACE operations: {filepath}")
                    continue

                with open(filepath, 'r', encoding='utf-8') as f:
                    current_file_content = f.read()

                modified_content = current_file_content
                replacements_performed_count = 0
                successful_operations = 0

                for i, (search_text, replace_text) in enumerate(sr_segments):
                    op_num = i + 1
                    print(f"      Applying S/R operation #{op_num}...")

                    if not search_text:
                        print(f"        Warning: Search text for operation #{op_num} is empty. Skipping this operation.")
                        continue

                    if search_text in modified_content:
                        # Count occurrences before replacement for more accurate feedback if needed
                        # num_occurrences = modified_content.count(search_text)
                        modified_content = modified_content.replace(search_text, replace_text)
                        replacements_performed_count += 1 # Counts segments that led to a change
                        successful_operations +=1
                        print(f"        Successfully applied replacement for operation #{op_num}.")
                    else:
                        print(f"        Warning: Search text for operation #{op_num} not found in the current state of {filepath}.")
                        print(f"          Search text (first 80 chars): {search_text[:80].replace(chr(10), '↵')}...")
                        # print(f"          Full Search text: \n{textwrap.indent(search_text, '            ')}")


                if replacements_performed_count > 0: # if any search_text was found and replaced
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    print(f"    Successfully updated {filepath} with {successful_operations} SEARCH/REPLACE operation(s).")
                elif successful_operations == 0 and len(sr_segments) > 0 :
                     print(f"    No search texts were found in {filepath} for any of the {len(sr_segments)} S/R operations. No changes made.")
                else: # Should not happen if sr_segments is not empty and replacements_performed_count is 0
                     print(f"    No changes made to {filepath} via S/R (no replacements performed).")


            except OSError as e:
                print(f"    Error during SEARCH/REPLACE for {filepath}: {e}")
            except Exception as e:
                print(f"    An unexpected error occurred with {filepath} during S/R: {e}")

        else:
            # Normal code block (WRITE mode)
            print("    [WRITE mode]")
            try:
                # Ensure the directory exists
                dir_name = os.path.dirname(filepath)
                if dir_name: # Only create if not writing to root
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
    parser = argparse.ArgumentParser(
        description="Extract code blocks from text and write them to files. Supports WRITE and SEARCH/REPLACE modes."
    )
    parser.add_argument(
        "-c", "--clipboard",
        action="store_true",
        help="Read input from clipboard instead of stdin"
    )

    # Add mutually exclusive group for candidate options
    candidate_group = parser.add_mutually_exclusive_group()
    candidate_group.add_argument(
        "-1", "--candidate1",
        action="store_true",
        help="Save full content to candidates/implementation_1.txt"
    )
    candidate_group.add_argument(
        "-2", "--candidate2",
        action="store_true",
        help="Save full content to candidates/implementation_2.txt"
    )
    candidate_group.add_argument(
        "-3", "--candidate3",
        action="store_true",
        help="Save full content to candidates/implementation_3.txt"
    )
    candidate_group.add_argument(
        "-4", "--candidate4",
        action="store_true",
        help="Save full content to candidates/implementation_4.txt"
    )
    candidate_group.add_argument(
        "-5", "--candidate5",
        action="store_true",
        help="Save full content to candidates/implementation_5.txt"
    )

    args = parser.parse_args()

    # Determine which candidate number was selected
    candidate_number = None
    if args.candidate1:
        candidate_number = 1
    elif args.candidate2:
        candidate_number = 2
    elif args.candidate3:
        candidate_number = 3
    elif args.candidate4:
        candidate_number = 4
    elif args.candidate5:
        candidate_number = 5

    if args.clipboard:
        print("Reading from clipboard...")
        try:
            full_input_text = get_clipboard_content()
            if full_input_text is not None: # Ensure content was actually retrieved
                 print("Clipboard content retrieved successfully.")
            else: # Should be caught by exceptions in get_clipboard_content, but as a safeguard
                 print("Failed to retrieve clipboard content or clipboard was empty.")
                 return
        except SystemExit: # Raised by get_clipboard_content on error
            return
    else:
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

    # If a candidate number is specified, save the full content to the candidate file
    if candidate_number:
        print(f"Saving full content to candidate file #{candidate_number}...")
        success = save_full_content_to_candidate_file(full_input_text, candidate_number)
        if success:
            print("-------------------------------------------------------------------------")
            print("Candidate file saved successfully.")
        else:
            print("-------------------------------------------------------------------------")
            print("Failed to save candidate file.")
        return

    # Otherwise, proceed with normal code block extraction
    extract_and_write_code_blocks(full_input_text)
    print("-------------------------------------------------------------------------")
    print("Processing complete.")

if __name__ == "__main__":
    main()
