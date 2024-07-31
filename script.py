import os
import shutil
import tkinter as tk
from tkinter import filedialog
import tiktoken

def get_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        # Ignore temporary files and directories
        exclude_dirs = {
            '__pycache__', 'venv', '.git', 'Flattened_Files', 'Flattened_Files--files', 'databases', 'database', 'chroma_persist', 'docker'}
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in exclude_dirs]
        for file in files:
            remove_pattern = ['__pycache__', 'venv', '.git', '.sqlite3', '.ipynb', '.log', '.png']
            if any(pattern in file for pattern in remove_pattern):
                continue
            if not file.startswith('.') and file != '.env' and file != '__init__.py':  # Skip __init__.py files
                file_list.append(os.path.join(root, file))
    return file_list

def rename_file(file_path, base_dir):
    relative_path = os.path.relpath(file_path, base_dir)
    new_name = relative_path.replace(os.path.sep, '--')
    # if True:
    #     new_name = "new_code--" + new_name
    return new_name

def count_tokens(file_path):
    encoding = tiktoken.get_encoding("cl100k_base")
    print(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return len(encoding.encode(content))

def create_combined_content(dest_folder, files_subfolder):
    content = "You are now reading a repository of code files. Each file's content is preceded by its path.\n\n"
    for root, _, files in os.walk(files_subfolder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, files_subfolder)
            relative_path = relative_path.replace('--', '/')
            content += f"File: {relative_path}\n"
            content += "```\n"
            with open(file_path, 'r', encoding='utf-8') as f:
                print(f"Reading {file_path}")
                content += f.read()
            content += "\n```\n\n"
    
    content += "Now, please do the following request using the data above. \n"
    
    with open(os.path.join(dest_folder, 'new_code.txt'), 'w', encoding='utf-8') as f:
        f.write(content)
    
    import pyperclip
    pyperclip.copy(content)

def handle_readme(source_folder, files_subfolder):
    parent_dir = os.path.dirname(source_folder)
    readme_path = os.path.join(parent_dir, "README.md")
    if os.path.exists(readme_path):
        dest_path = os.path.join(files_subfolder, "README.md")
        shutil.copy2(readme_path, dest_path)
        print(f"Added README.md to {files_subfolder}")
        return True
    return False

def process_additional_folders(additional_folders, files_subfolder):
    for folder in additional_folders:
        if os.path.exists(folder):
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    dest_path = os.path.join(files_subfolder, file)
                    shutil.copy2(file_path, dest_path)

def process_additional_files(additional_files, files_subfolder):
    for file_path in additional_files:
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(files_subfolder, file_name)
            shutil.copy2(file_path, dest_path)

def main():
    additional_folders = [
        # r"C:\Users\quocd\Coding\Upwork\webapp\docs"
        # r"C:\Users\quocd\Coding\Upwork\webapp\docker"
    ]
    additional_files = [
        r"C:\Users\quocd\Coding\Upwork\webapp\.env.example"
    ]
    root = tk.Tk()
    root.withdraw()

    source_folder = filedialog.askdirectory(title="Select the source folder")
    if not source_folder:
        print("No folder selected. Exiting.")
        return

    dest_folder = os.path.join(os.path.dirname(source_folder), "Flattened_Files")
    print(f"Destination folder: {dest_folder}")
    
    # Check if the Flattened_Files folder exists and remove it
    if os.path.exists(dest_folder):
        print(f"Removing existing {dest_folder}")
        shutil.rmtree(dest_folder)
    
    os.makedirs(dest_folder, exist_ok=True)

    files_subfolder = os.path.join(dest_folder, "files")
    os.makedirs(files_subfolder, exist_ok=True)

    # 1. Open the subfolder
    # os.startfile(files_subfolder)
    # 2. Process the files and paste into subfolder
    all_files = get_all_files(source_folder)
    total_tokens = 0

    # Handle README.md
    # readme_added = handle_readme(source_folder, files_subfolder)

    from tqdm import tqdm
    for file_path in tqdm(all_files):
        new_name = rename_file(file_path, source_folder)
        dest_path = os.path.join(files_subfolder, new_name)
        
        shutil.copy2(file_path, dest_path)
        print(f"Copied and renamed: {file_path} -> {dest_path}")

        file_tokens = count_tokens(dest_path)
        total_tokens += file_tokens
        print(f"Tokens in {new_name}: {file_tokens}")
    
    # Process additional folders
    process_additional_folders(additional_folders, files_subfolder)

    process_additional_files(additional_files, files_subfolder)

    # If README.md was added, count its tokens
    # if readme_added:
        # readme_tokens = count_tokens(os.path.join(files_subfolder, "README.md"))
        # total_tokens += readme_tokens
        # print(f"Tokens in README.md: {readme_tokens}")

    # 3. Show cost
    print(f"Total tokens in all output files: {total_tokens}")
    cost = (total_tokens / 1_000_000) * 3.00
    print(f"Estimated cost (Claude Sonnet rate): ${cost:.2f} USD")

    # 4. Create the combined content file
    create_combined_content(dest_folder, files_subfolder)
    print(f"Combined content file created: {os.path.join(dest_folder, 'new_code.txt')}")

    os.startfile(dest_folder)

if __name__ == "__main__":
    main()