import argparse
import time
import difflib
from openai import OpenAI

SYSTEM_PROMPT = """You are an coding assistant that helps merge code updates, ensuring every modification is fully integrated."""

USER_PROMPT = """Merge all changes from the <update> snippet into the <code> below.
- Preserve the code's structure, order, comments, and indentation exactly.
- Output only the raw updated code without any wrapping tags or markup
- Do not include any additional text, explanations, placeholders, ellipses, or code fences.
- Discard instruction comments from
 updated snippet, while keeping existing code comments

<code>{}</code>

<update>{}</update>

Provide the complete updated code without any wrapping tags."""

def parse_args():
    parser = argparse.ArgumentParser(description='Update code file using OpenAI API')
    parser.add_argument('file_path', help='Path to the file to be updated')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--gpt4o', action='store_true', help='Use GPT-4o model')
    group.add_argument('--mini', action='store_true', default=True, help='Use GPT-4o-mini model (default)')
    return parser.parse_args()

def get_update_snippet():
    print("Paste in the update snippet, then type Ctrl + D:")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        print("-" * 40)
        print("Processing...")
        return "\n".join(lines)

def count_line_changes(old_content, new_content):
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    
    diff = list(difflib.unified_diff(old_lines, new_lines, n=0))
    additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
    
    return additions, deletions

def update_file_content(file_path, debug=False, model_args=None):
    # Read the input file
    if debug:
        print(f"Reading file: {file_path}")
    try:
        with open(file_path, 'r') as file:
            code = file.read()
        if debug:
            print(f"Successfully read {len(code)} characters from file")
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Initialize OpenAI client
    client = OpenAI()

    try:
        # Get update instructions from user
        if debug:
            print("Waiting for update snippet input...")
        update_snippet = get_update_snippet()
        if debug:
            print(f"Received update snippet ({len(update_snippet)} characters)")
            print("Making API call to OpenAI...")
        
        start_time = time.time()
        
        completion = client.chat.completions.create(
            model="gpt-4o" if args.gpt4o else "gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": USER_PROMPT.format(code, update_snippet)
                }
            ],
            prediction={
                "type": "content",
                "content": code
            }
        )

        # Get the modified content
        new_content = completion.choices[0].message.content

        # Write the modified content back to the file
        if debug:
            print(f"Writing updated content ({len(new_content)} characters)")
        with open(file_path, 'w') as file:
            file.write(new_content)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        completion_tokens = completion.usage.completion_tokens
        throughput = completion_tokens / elapsed_time
        
        # Count line changes
        additions, deletions = count_line_changes(code, new_content)
        
        model_name = "GPT-4o" if args.gpt4o else "GPT-4o-mini"
        print(f"Successfully updated {file_path} using {model_name}")
        print(f"Lines changed: +{additions} -{deletions}")
        print(f"Throughput: {throughput:.2f} tokens/second ({completion_tokens} tokens in {elapsed_time:.2f}s)")

    except Exception as e:
        print(f"Error during API call or file writing: {e}")

if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        print("Debug mode enabled")
    update_file_content(args.file_path, args.debug, args)
