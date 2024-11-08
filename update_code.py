import argparse
from openai import OpenAI

SYSTEM_PROMPT = """You are an coding assistant that helps merge code updates, ensuring every modification is fully integrated."""

USER_PROMPT = """Merge all changes from the <update> snippet into the <code> below.
- Preserve the code's structure, order, comments, and indentation exactly.
- Output only the raw updated code without any wrapping tags or markup
- Do not include any additional text, explanations, placeholders, ellipses, or code fences.

<code>{}</code>

<update>{}</update>

Provide the complete updated code without any wrapping tags."""

def parse_args():
    parser = argparse.ArgumentParser(description='Update code file using OpenAI API')
    parser.add_argument('file_path', help='Path to the file to be updated')
    return parser.parse_args()

def get_update_snippet():
    print("Paste in the update snippet, then type Ctrl + D:")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        return "\n".join(lines)

def update_file_content(file_path):
    # Read the input file
    try:
        with open(file_path, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Initialize OpenAI client
    client = OpenAI()

    try:
        # Make API call
        # Get update instructions from user
        update_snippet = get_update_snippet()
        
        completion = client.chat.completions.create(
            model="gpt-4o",
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
        with open(file_path, 'w') as file:
            file.write(new_content)
        
        print(f"Successfully updated {file_path}")

    except Exception as e:
        print(f"Error during API call or file writing: {e}")

if __name__ == "__main__":
    args = parse_args()
    update_file_content(args.file_path)
