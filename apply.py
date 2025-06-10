#!/usr/bin/env python3
import re
import sys
import os
import argparse
import json

def get_clipboard_content():
    """Get content from system clipboard."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        clipboard_content = root.clipboard_get()
        root.destroy()
        return clipboard_content
    except ImportError:
        raise RuntimeError("tkinter not available. Cannot access clipboard.")
    except tk.TclError:
        raise RuntimeError("No content in clipboard or unable to access clipboard.")
    except Exception as e:
        raise RuntimeError(f"Error accessing clipboard: {e}")

def save_full_content_to_candidate_file(content, candidate_number):
    """Save full content to a numbered candidate file. Returns success status."""
    candidates_dir = "candidates"
    os.makedirs(candidates_dir, exist_ok=True)
    filepath = os.path.join(candidates_dir, f"implementation_{candidate_number}.txt")
    try:
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            f.write(content)
        return True, f"Successfully saved full content to {filepath}"
    except OSError as e:
        return False, f"Error writing to {filepath}: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred writing to {filepath}: {e}"

def parse_search_replace_blocks(content: str):
    """
    Parses a string containing one or more SEARCH/REPLACE blocks.
    Returns a tuple: (list of (search, replace) tuples, remaining content string).
    """
    sr_blocks = []
    remainder_parts = []
    parts = content.split('<<<<<<< SEARCH\n')

    if parts[0].strip():
        remainder_parts.append(parts[0])

    for part in parts[1:]:
        if '\n=======\n' not in part or '>>>>>>> REPLACE' not in part:
            remainder_parts.append('<<<<<<< SEARCH\n' + part)
            continue

        search_text, rest_of_block = part.split('\n=======\n', 1)
        end_marker = '>>>>>>> REPLACE'
        end_marker_pos = rest_of_block.find(end_marker)

        if end_marker_pos == -1:
            remainder_parts.append('<<<<<<< SEARCH\n' + part)
            continue

        replace_candidate = rest_of_block[:end_marker_pos]
        # Compatibility for Python < 3.9 which doesn't have removesuffix
        replace_text = replace_candidate[:-1] if replace_candidate.endswith('\n') else replace_candidate
        sr_blocks.append((search_text, replace_text))

        remainder = rest_of_block[end_marker_pos + len(end_marker):]
        if remainder.strip():
            remainder_parts.append(remainder)

    return sr_blocks, "".join(remainder_parts).strip()

def extract_and_apply_changes(full_text, project_root, readonly_files=None):
    """
    Extracts code blocks and writes them to files. Returns a list of operation logs.
    """
    pattern = re.compile(
        r"^\s*```(\w*):([^\n]+?)\s*\n"
        r"(.*?)"
        r"\n^\s*```end:\2\s*$",
        re.DOTALL | re.MULTILINE
    )

    project_root_abs = os.path.abspath(project_root)
    readonly_set = set(readonly_files or [])
    operation_logs = []

    matches = pattern.findall(full_text)

    if not matches:
        operation_logs.append({
            "filepath": None,
            "operation_type": "parse",
            "status": "error",
            "message": "No valid code blocks found. Expected format: ```language:path/to/file ... ```end:path/to/file",
        })
        return operation_logs

    for language, filepath, content in matches:
        filepath = filepath.strip().replace("\\", "/")
        target_path_abs = os.path.abspath(os.path.join(project_root_abs, filepath))

        if not target_path_abs.startswith(project_root_abs):
            operation_logs.append({
                "filepath": filepath, "operation_type": "security_check", "status": "error",
                "message": f"Path traversal attempt: '{filepath}' is outside of the project directory.",
            })
            continue

        if filepath in readonly_set:
            operation_logs.append({
                "filepath": filepath, "operation_type": "security_check", "status": "skipped",
                "message": f"Attempt to modify a read-only file: {filepath}.",
            })
            continue

        sr_segments, content_remainder = parse_search_replace_blocks(content)

        if sr_segments:
            op_log = {
                "filepath": filepath, "operation_type": "search_replace", "status": "pending",
                "message": f"Found {len(sr_segments)} S/R operation(s).", "sr_operations": []
            }
            if content_remainder:
                op_log["message"] += " Warning: Mixed content found and ignored."

            if not os.path.exists(target_path_abs):
                op_log.update({"status": "error", "message": f"File not found for SEARCH/REPLACE: {filepath}"})
                operation_logs.append(op_log)
                continue

            try:
                with open(target_path_abs, 'r', encoding='utf-8', errors='replace') as f:
                    current_file_content = f.read()

                modified_content = current_file_content
                successful_ops = 0

                for i, (search_text, replace_text) in enumerate(sr_segments):
                    sr_op_log = {"search_text_preview": search_text[:80].replace(chr(10), '↵') + '...'}
                    if not search_text:
                        sr_op_log.update({"status": "skipped", "message": "Search text was empty."})
                    elif search_text in modified_content:
                        modified_content = modified_content.replace(search_text, replace_text, 1)
                        successful_ops += 1
                        sr_op_log.update({"status": "success", "message": f"Replacement #{i+1} applied."})
                    else:
                        sr_op_log.update({"status": "not_found", "message": f"Search text for operation #{i+1} not found."})
                    op_log["sr_operations"].append(sr_op_log)

                if successful_ops > 0:
                    with open(target_path_abs, 'w', encoding='utf-8', errors='replace') as f:
                        f.write(modified_content)
                    op_log.update({
                        "status": "success",
                        "message": f"Successfully applied {successful_ops}/{len(sr_segments)} S/R operation(s)."
                    })
                else:
                    op_log.update({
                        "status": "skipped",
                        "message": "No search texts found; no changes made."
                    })
                operation_logs.append(op_log)
            except (OSError, Exception) as e:
                op_log.update({"status": "error", "message": f"Error during S/R: {e}"})
                operation_logs.append(op_log)
        else: # Normal write mode
            op_log = {"filepath": filepath, "operation_type": "write", "status": "pending"}
            try:
                dir_name = os.path.dirname(target_path_abs)
                if dir_name: os.makedirs(dir_name, exist_ok=True)
                with open(target_path_abs, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
                op_log.update({"status": "success", "message": f"Successfully wrote {len(content)} characters."})
                operation_logs.append(op_log)
            except (OSError, Exception) as e:
                op_log.update({"status": "error", "message": f"Error writing file: {e}"})
                operation_logs.append(op_log)
    return operation_logs

def main():
    parser = argparse.ArgumentParser(
        description="Extracts and applies code changes from text. Outputs a JSON result."
    )
    parser.add_argument(
        "--readonly-files", nargs='*', default=[],
        help="A list of file paths that should not be modified."
    )
    parser.add_argument("-c", "--clipboard", action="store_true", help="Read from clipboard")

    candidate_group = parser.add_mutually_exclusive_group()
    candidate_group.add_argument("-1", "--candidate1", action="store_true", help="Save to candidates/implementation_1.txt")
    candidate_group.add_argument("-2", "--candidate2", action="store_true", help="Save to candidates/implementation_2.txt")
    candidate_group.add_argument("-3", "--candidate3", action="store_true", help="Save to candidates/implementation_3.txt")
    candidate_group.add_argument("-4", "--candidate4", action="store_true", help="Save to candidates/implementation_4.txt")
    candidate_group.add_argument("-5", "--candidate5", action="store_true", help="Save to candidates/implementation_5.txt")

    args = parser.parse_args()

    final_result = {}

    try:
        candidate_number = next((i for i, c in enumerate([args.candidate1, args.candidate2, args.candidate3, args.candidate4, args.candidate5], 1) if c), None)

        if args.clipboard:
            full_input_text = get_clipboard_content()
        else:
            full_input_text = sys.stdin.read()

        if not full_input_text.strip():
            raise ValueError("No input received.")

        if candidate_number:
            success, message = save_full_content_to_candidate_file(full_input_text, candidate_number)
            final_result = {"status": "success" if success else "error", "summary": message, "operations": []}
        else:
            project_root = os.getcwd()
            operation_logs = extract_and_apply_changes(full_input_text, project_root, readonly_files=args.readonly_files)

            has_errors = any(op.get('status') == 'error' for op in operation_logs)

            final_result = {
                "status": "error" if has_errors else "success",
                "summary": f"Processed {len(operation_logs)} operation(s).",
                "operations": operation_logs
            }

        json.dump(final_result, sys.stdout, indent=2)
        if final_result.get("status") == "error":
            sys.exit(1)

    except (RuntimeError, ValueError) as e:
        json.dump({"status": "error", "summary": str(e), "operations": []}, sys.stdout, indent=2)
        sys.exit(1)
    except KeyboardInterrupt:
        json.dump({"status": "error", "summary": "Operation cancelled by user (Ctrl+C).", "operations": []}, sys.stdout, indent=2)
        sys.exit(1)
    except Exception as e:
        json.dump({"status": "error", "summary": f"An unexpected fatal error occurred: {e}", "operations": []}, sys.stdout, indent=2)
        sys.exit(1)

if __name__ == "__main__":
    main()
