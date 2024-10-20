import subprocess
import re
import pyperclip
import argparse
import os
import requests
from bs4 import BeautifulSoup

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process XML files and execute code blocks.")
    parser.add_argument('-i', '--input', default='.run.xml', help='Input filename (default: .run.xml)')
    parser.add_argument('-o', '--output', default='.out.xml', help='Output filename (default: .out.xml)')
    parser.add_argument('-c', '--crawl', action='store_true', help='Enable URL crawling')
    parser.add_argument('--init', nargs='?', const='.', help='Initialize or replace .run.xml with template. Optionally specify a directory path.')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively list files when initializing')
    parser.add_argument('--exclude', nargs='+', default=[
        '.log', '.xml', '.gitignore', '.env', '.json', 'archives', 'data', '.DS_Store',
        '*aider', '*git*', '.ipynb', '__pycache__', '*cache', '.db', '.swp', '.zip', 'repo',
        '.jsonl', '.parquet', '.safetensors', '.csv'
        ], help='List of files or extensions to exclude')
    parser.add_argument('--exclude-folders', nargs='+', default=[], help='List of folders to exclude when using recursive option')
    parser.add_argument('-s', '--structure', type=int, nargs='?', const=2, metavar='DEPTH', default=2, help='Include project structure with specified depth (default: 2)')
    return parser.parse_args()

args = parse_arguments()

# Handle the init option
if args.init is not None:
    # Backup existing .run.xml if it exists
    if os.path.exists('.run.xml'):
        import shutil
        shutil.copy2('.run.xml', '.old.run.xml')
        print("Backed up existing .run.xml to .old.run.xml")

    def should_exclude(item, is_dir=False):
        if is_dir:
            return any(folder == item for folder in args.exclude_folders)
        return any(
            (exclude.startswith('.') and item.endswith(exclude)) or
            (exclude.startswith('*') and exclude.endswith('*') and exclude[1:-1] in item) or
            (exclude.startswith('*') and exclude[1:] in item) or
            (not exclude.startswith('*') and not exclude.startswith('.') and exclude == item)
            for exclude in args.exclude
        )

    def get_files(directory, recursive=False):
        if recursive:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if not should_exclude(d, is_dir=True)]
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, directory)
                    if not should_exclude(relative_path):
                        yield relative_path
        else:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                is_dir = os.path.isdir(full_path)
                if not should_exclude(item, is_dir):
                    if os.path.isfile(full_path):
                        yield item
                    elif is_dir:
                        yield f"{item}/"

    template = """<purpose>

</purpose>

{structure_placeholder}

<code-files>
  files-to-prompt --cxml
{placeholder}

</code-files>


<!--
<code-old-reference>
    files-to-prompt --cxml 
</code-old-reference>
-->

<!--
<documentation>

</documentation>
-->

<!--
<instructions>
  <instruction>
    Provide code for each new or updated file in a single block. Only include the updated parts
    of the code in your response.
  </instruction>
  <instruction>
    Maintain the existing file names unless a change is necessary for better clarity or
    structure. Respect the currently used libraries to avoid introducing unnecessary
    dependencies.
  </instruction>
</instructions>

<output_format>
  <files_content>
    <file>
      <path>path/to/file</path>
      <action>create | update | delete</action>
      <description>Description of changes and purpose.</description>
      <code>Updated parts of the code</code>
    </file>
  </files_content>
</output_format> 
-->
"""
    # Get all files and folders in the specified directory
    directory = args.init
    
    items = list(get_files(directory, recursive=args.recursive))
    
    # Create a string with each item on a new line, wrapped in XML comments
    placeholder = "\n".join(f"  <!-- {item} -->" for item in items)
    
    # Generate project structure if --structure option is used
    structure_placeholder = ""

    if args.structure:
        structure_file = '.structure.xml'
        if os.path.exists(structure_file):
            with open(structure_file, 'r') as f:
                structure_content = f.read().strip()
                # Remove the outer <project_structure> tags if present
                structure_placeholder = re.sub(r'^\s*<project_structure>\s*(.*)\s*</project_structure>\s*$', r'\1', structure_content, flags=re.DOTALL)
        else:
            try:
                structure = subprocess.check_output(['tree', '--gitignore', '-L', str(args.structure)], text=True)
                structure_placeholder = structure.strip()
                with open(structure_file, 'w') as f:
                    f.write(f"<project_structure>\n{structure_placeholder}\n</project_structure>")
            except subprocess.CalledProcessError:
                print("Warning: 'tree' command failed. Make sure it's installed and in your PATH.")
                structure_placeholder = "Project structure unavailable"
        
        structure_placeholder = f"<project_structure>\n{structure_placeholder}\n</project_structure>"

    # Replace the placeholders in the template
    template = template.format(placeholder=placeholder, structure_placeholder=structure_placeholder.strip())
    
    with open('.run.xml', 'w') as file:
        file.write(template)
    print("Created or replaced .run.xml with default template and directory contents.")
    exit(0)

# Define input and output filenames
if os.path.isabs(args.input):
    input_filename = args.input
else:
    input_filename = os.path.join(os.getcwd(), args.input)

if os.path.isabs(args.output):
    output_filename = args.output
else:
    output_filename = os.path.join(os.getcwd(), args.output)

# Check if input file exists, if not, try in the script's directory
if not os.path.exists(input_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    alternative_input = os.path.join(script_dir, args.input)
    if os.path.exists(alternative_input):
        input_filename = alternative_input
        print(f"Input file not found in current directory. Using {input_filename}")
    else:
        # If .run.xml doesn't exist anywhere, create it with the template
        if args.input == '.run.xml':
            template = """<purpose>

</purpose>


<instructions>
  <instruction>
    Provide code for each new or updated file in a single block. Only include the updated parts
    of the code in your response.
  </instruction>
  <instruction>
    Maintain the existing file names unless a change is necessary for better clarity or
    structure. Respect the currently used libraries to avoid introducing unnecessary
    dependencies.
  </instruction>
</instructions>


<code-files>
  files-to-prompt --cxml 

</code-files>

<code-old-reference>
    files-to-prompt --cxml 
</code-old-reference>
         


<output_format>
  <files_content>
    <file>
      <path>path/to/file</path>
      <action>create | update | delete</action>
      <description>Description of changes and purpose.</description>
      <code>Updated parts of the code</code>
    </file>
  </files_content>
</output_format> 
"""
            with open(input_filename, 'w') as file:
                file.write(template)
            print(f"Created {input_filename} with default template.")
        else:
            print(f"Error: The file '{input_filename}' does not exist.")
            exit(1)

# Read the file content
try:
    with open(input_filename, 'r') as file:
        content = file.read()
except Exception as e:
    print(f"Error reading '{input_filename}': {e}")
    exit(1)

# Remove XML comments (<!-- comment -->)
content_no_comments = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

def crawl_url(url):
    driver = None
    try:
        # First, try with requests
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('body')
        if main_content:
            main_content = main_content.get_text(strip=True)
        else:
            main_content = ""
        
        # Check if the content is asking for JavaScript or cookies
        if "Please turn JavaScript on" in main_content or "Please enable Cookies" in main_content:
            print(f"JavaScript or cookies required for {url}. Using Selenium...")
            
            # Set up Selenium with Chrome in headless mode
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=chrome_options)
            
            # Load the page
            driver.get(url)
            
            # Wait for the body to be present
            body = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check for captcha
            try:
                captcha_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#px-captcha'))
                )
                print("Captcha detected. Attempting to solve...")
                
                action = ActionChains(driver)
                action.click_and_hold(captcha_element)
                action.perform()
                time.sleep(10)
                action.release(captcha_element)
                action.perform()
                time.sleep(0.2)
                action.click(captcha_element)
                action.perform()
                
                # Wait for page to load after captcha
                body = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except Exception as captcha_error:
                print(f"No captcha found or error solving captcha: {captcha_error}")
            
            # Get the page source after JavaScript has run and potential captcha is solved
            main_content = body.text
        
        return main_content
    except requests.RequestException as e:
        return f"Error crawling {url}: {str(e)}"
    except Exception as e:
        return f"Unexpected error crawling {url}: {str(e)}"
    finally:
        if driver:
            driver.quit()

# Define a function to process each <code-*> tag and <documentation> tag
def process_tag(match):
    tag = match.group(1)  # e.g., code-files, code-example, documentation, etc.
    content = match.group(2)
    
    if tag.startswith('code-'):
        # Process code tags as before
        command_lines = content.strip().splitlines()
        command_cleaned = ' '.join(line.strip() for line in command_lines if line.strip())
        
        print(f"Processing <{tag}> with command: {command_cleaned}")
        
        try:
            result = subprocess.check_output(command_cleaned, shell=True, text=True)
            result = result.rstrip()
        except subprocess.CalledProcessError as e:
            print(f"Error running command in <{tag}>: {e}")
            result = f"Error executing command: {e}"
        except Exception as e:
            print(f"Unexpected error running command in <{tag}>: {e}")
            result = f"Unexpected error: {e}"
        
        return f"<{tag}>\n{result}\n</{tag}>"
    
    elif tag == 'documentation':
        if args.crawl:
            # Process documentation tags only if crawl flag is set
            urls = re.findall(r'https?://\S+', content)
            crawled_content = []
            for url in urls:
                print(f"Crawling URL: {url}")
                crawled_text = crawl_url(url)
                crawled_content.append(f"<url>{url}</url>\n<content>{crawled_text}</content>")
            
            return f"<{tag}>\n{''.join(crawled_content)}\n</{tag}>"
        else:
            # If crawl flag is not set, return the original content
            return match.group(0)
    
    else:
        # Return unmodified for unknown tags
        return match.group(0)

# Regular expression pattern to find all <code-*>...</code-*> tags and <documentation>...</documentation> tags
pattern = r'<(code-[^>]+|documentation)>(.*?)</\1>'

# Use re.sub with the processing function to replace each tag content
new_content = re.sub(pattern, process_tag, content_no_comments, flags=re.DOTALL)

# Save the modified content to the output file
try:
    with open(output_filename, 'w') as outfile:
        outfile.write(new_content)
    print(f"Modified content has been saved to '{output_filename}'.")
except Exception as e:
    print(f"Error writing to '{output_filename}': {e}")
    exit(1)

# Copy the modified content to the clipboard
try:
    pyperclip.copy(new_content)
    print("Modified content copied to clipboard.")
except pyperclip.PyperclipException as e:
    print(f"Error copying to clipboard: {e}")
