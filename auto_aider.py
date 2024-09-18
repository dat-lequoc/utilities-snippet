import re
import subprocess
import argparse
import shlex
import sys
import json
import os
import xml.etree.ElementTree as ET

def extract_tasks(text):
    tasks = []
    
    # Try to parse as JSON
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "filesContent" in data:
            for file_info in data["filesContent"]:
                tasks.append(f"Update file: {file_info['file']}\n\nDescription: {file_info['description']}\n\nNew content:\n\n{file_info['fullCode']}")
            return tasks
    except json.JSONDecodeError:
        pass  # Not JSON, continue to XML parsing
    
    # Try to parse as XML
    try:
        root = ET.fromstring(text)
        for document in root.findall('.//document'):
            for file in document.findall('.//file'):
                file_name = file.find('name').text
                description = file.find('description').text
                full_code = file.find('fullCode').text
                tasks.append(f"Update file: {file_name}\n\nDescription: {description}\n\nNew content:\n\n{full_code}")
        if tasks:
            return tasks
    except ET.ParseError:
        pass  # Not XML, fall back to regex method
    
    # Fall back to regex method
    pattern = r'<Task>(.*?)</Task>'
    matches = re.findall(pattern, text, re.DOTALL)
    return list(dict.fromkeys(matches))  # Remove duplicates while preserving order

def trim_command(command, max_length=200):
    if len(command) <= max_length:
        return command
    head = command[:max_length//2 - 3]
    tail = command[-max_length//2 + 3:]
    return f"{head}...{tail}"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Execute tasks using aider with custom arguments.")
    parser.add_argument('--mini', action='store_true', help="Use --mini instead of --deepseek")
    parser.add_argument('aider_args', nargs=argparse.REMAINDER, help="Arguments to pass to aider command")
    return parser.parse_args()

def get_input():
    print("Please paste your text below. When finished, press Ctrl+D (Unix) or Ctrl+Z (Windows) followed by Enter:")
    return sys.stdin.read().strip()

def extract_file_path(task):
    match = re.search(r'Update file: (.*?)(?:\n|$)', task)
    return match.group(1) if match else None

def main():
    args = parse_arguments()
    aider_args = ' '.join(args.aider_args)
    text = get_input()
    tasks = extract_tasks(text)
    if not tasks:
        print("No tasks found in the input.")
        return
    
    model_flag = '--mini' if args.mini else '--deepseek'
    for i, task in enumerate(tasks, 1):
        print("#"*20)
        print("#"*20)
        print(f"Executing task {i}/{len(tasks)}...")
        
        file_path = extract_file_path(task)
        if file_path:
            # Extract action from the task
            action_match = re.search(r'action: (\w+)', task)
            action = action_match.group(1) if action_match else "update"
            
            dir_path = os.path.dirname(file_path)
            
            if action.lower() == "create" and dir_path:
                # Create directory only if action is create and dir_path is not empty
                mkdir_command = f'mkdir -p {shlex.quote(dir_path)}'
                print(f"Creating directory: {mkdir_command}")
                try:
                    subprocess.run(mkdir_command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Warning: Failed to create directory: {e}")
            
            # Touch file regardless of action
            touch_command = f'touch {shlex.quote(file_path)}'
            print(f"Creating/updating file: {touch_command}")
            try:
                subprocess.run(touch_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to create/update file: {e}")
        else:
            print("Warning: Could not extract file path from task.")
        
        # Use shlex.quote to properly escape the task content
        escaped_task = shlex.quote(task)
        command = (
            f'python -m aider '
            f'--yes '
            f'{model_flag} '
            f'--no-suggest-shell-commands '
            f'--no-auto-commits '
            f'{aider_args} '
            f'--message {escaped_task}'
        )
        if file_path:
            command += f' {shlex.quote(file_path)}'
        
        print(f"Running command: {trim_command(command)}")
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"Task {i} executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing task {i}: {e}")

if __name__ == "__main__":
    main()
