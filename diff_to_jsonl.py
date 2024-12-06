import os
import json
import subprocess
import argparse

def get_git_diff(path):
    """Get git diff for the specified path."""
    try:
        # Change to the directory containing the path
        working_dir = os.path.dirname(path) if os.path.isfile(path) else path
        result = subprocess.run(
            ['git', 'diff', '--no-color', 'HEAD'],
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        return None

def get_instance_id(path):
    """Extract instance_id (parent folder name) from the path."""
    # Get the absolute path
    abs_path = os.path.abspath(path)

    # If the path is a file, get its directory first
    if os.path.isfile(abs_path):
        directory = os.path.dirname(abs_path)
    else:
        directory = abs_path

    # Get the parent directory name
    parent_dir = os.path.basename(directory)
    return parent_dir

def create_jsonl_output(diff_data, instance_id, output_file="output.jsonl", model_name="default-model"):
    """Create JSONL output with the specified format."""
    output_data = {
        "instance_id": instance_id,
        "model_patch": diff_data,
        "model_name_or_path": model_name
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f)
        f.write('\n')

def main():
    parser = argparse.ArgumentParser(description='Process git diff and create JSONL output')
    parser.add_argument('path', help='Path to the file or directory to process')
    parser.add_argument('--output', default='output.jsonl', help='Output JSONL file path')
    parser.add_argument('--model-name', default='default-model', help='Model name or path')

    args = parser.parse_args()

    # Get git diff
    diff_data = get_git_diff(args.path)
    if diff_data is None:
        return

    # Get instance ID from parent folder
    instance_id = get_instance_id(args.path)

    # Create JSONL output
    create_jsonl_output(diff_data, instance_id, args.output, args.model_name)
    print(f"Output written to {args.output}")

if __name__ == "__main__":
    main()
