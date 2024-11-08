import os
import sys
import asyncio
import re
import argparse
import logging
from dotenv import load_dotenv

# Attempt to import AsyncOpenAI
try:
    from openai import AsyncOpenAI
except ImportError:
    sys.exit("Error: AsyncOpenAI not found in the openai package. Please check the package version.")

def get_debug_flag():
    """
    Perform preliminary parsing to detect if --debug flag is set.
    This allows configuring logging before other arguments are processed.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
    args, _ = parser.parse_known_args()
    return args.debug

# Preliminary parsing to check for --debug flag
debug_mode = get_debug_flag()

# Configure logging based on the debug flag
if debug_mode:
    logging_level = logging.DEBUG
else:
    logging_level = logging.WARNING  # Suppress INFO and DEBUG logs by default

logging.basicConfig(
    level=logging_level,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Adjust logging level for external libraries if necessary
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Retrieve API key with validation
api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    logger.error("DEEPSEEK_API_KEY environment variable not set.")
    sys.exit(1)

# Initialize DeepSeek API client
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/beta",
)

def extract_sys_and_content(input_text):
    """
    Extracts system prompt and user content from the input text.
    If <sys> tags are present, extracts the system prompt; otherwise, uses a default prompt.
    """
    sys_match = re.search(r'<sys>(.*?)</sys>', input_text, re.DOTALL)
    if sys_match:
        sys_prompt = sys_match.group(1).strip()
        content = re.sub(r'<sys>.*?</sys>', '', input_text, flags=re.DOTALL).strip()
    else:
        sys_prompt = "You are a helpful assistant."
        content = input_text.strip()
    return sys_prompt, content

async def send_to_deepseek(system_prompt, user_prompt, model, temperature, max_tokens):
    """
    Sends the system and user prompts to the DeepSeek API and returns the response.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        logger.debug(f"Sending request to DeepSeek API with messages: {messages}")
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.debug(f"Received response: {response}")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error communicating with DeepSeek API: {e}")
        return f"Error: {str(e)}"

async def main():
    parser = argparse.ArgumentParser(
        description=(
            "Send prompts to the DeepSeek API. You can include <sys> tags to define system prompts.\n"
            "Example: cli_deepseek.py \"<sys>Your system prompt</sys> Your user prompt\""
        )
    )
    parser.add_argument("prompt", nargs='?', default=None,
                        help="The prompt to send to DeepSeek. Can include <sys> tags for system prompt.")
    parser.add_argument("--model", type=str, default="deepseek-chat", help="Model to use for the API.")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--max_tokens", type=int, default=8192, help="Maximum number of tokens to generate.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")

    args = parser.parse_args()

    # If debug flag was set after preliminary parsing, adjust logging level
    if args.debug and not debug_mode:
        logger.setLevel(logging.DEBUG)
        logging.getLogger("openai").setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled via command-line argument.")

    # Determine the input source for the prompt
    if args.prompt is None:
        logger.debug("No prompt provided as a command-line argument. Reading from standard input...")
        input_text = sys.stdin.read()
        if not input_text:
            logger.error("No input received from standard input.")
            sys.exit(1)
    else:
        input_text = args.prompt

    system_prompt, user_prompt = extract_sys_and_content(input_text)
    logger.debug(f"Extracted System Prompt: {system_prompt}")
    logger.debug(f"Extracted User Prompt: {user_prompt}")

    result = await send_to_deepseek(
        system_prompt,
        user_prompt,
        args.model,
        args.temperature,
        args.max_tokens
    )
    print(result)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
        sys.exit(0)

