import argparse
from openai import OpenAI

SYSTEM_PROMPT = """You are an expert code editor. Your task is to merge all changes from the update snippet into the provided code, ensuring every modification is fully integrated.

Instructions:
- Preserve the code's structure, order, comments, and indentation exactly
- Only output the complete updated code
- Do not include any additional text, explanations, placeholders, or code fences
- Do not wrap the output in any tags

The update snippet describes the changes to make. The code that follows is the content to update."""

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
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user", 
                    "content": f"Update instructions:\n{update_snippet}\n\nCode to update:\n{code}"
                }
            ]
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
