import re
import subprocess
import argparse
import shlex
import sys

def extract_tasks(text):
    pattern = r'<Task>(.*?)</Task>'
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Remove duplicates while preserving order
    unique_tasks = []
    for match in matches:
        if match not in unique_tasks:
            unique_tasks.append(match)
    
    return unique_tasks

def parse_arguments():
    parser = argparse.ArgumentParser(description="Execute tasks using aider with custom arguments.")
    parser.add_argument('aider_args', nargs=argparse.REMAINDER, help="Arguments to pass to aider command")
    return parser.parse_args()

def get_input():
    print("Please paste your text below. When finished, press Ctrl+D (Unix) or Ctrl+Z (Windows) followed by Enter:")
    return sys.stdin.read().strip()

def main():
    args = parse_arguments()
    aider_args = ' '.join(args.aider_args)
    text = get_input()
    
    tasks = extract_tasks(text)
    if not tasks:
        print("No tasks found in the input.")
        return
    
    for i, task in enumerate(tasks, 1):
        print("#"*20)
        print("#"*20)
        print(f"Executing task {i}/{len(tasks)}...")
        # Use shlex.quote to properly escape the task content
        escaped_task = shlex.quote(task)
        command = (
                f'python -m aider '
                f'--yes '
                f'--deepseek '
                f'--no-suggest-shell-commands '
                f'--no-auto-commits'
                f'{aider_args} '
                f'--message {escaped_task}'
            )
        #  command = f'python -m aider --yes --deepseek  --no-suggest-shell-commands {aider_args} --message {escaped_task}'

        print(f"Running command: {command}")
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Task {i} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing task {i}: {e}")

if __name__ == "__main__":
    main()
