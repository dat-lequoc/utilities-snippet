import asyncio
import subprocess
import shlex
import sys
import os
import json
import argparse
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Predefined prompt for requirements implementation
DEFAULT_PROMPT = """
Review the REQUIREMENTS and implement the necessary changes while following the guidelines.
"""

async def run_test_commands(test_commands: List[str]) -> Tuple[bool, Optional[str]]:
    """Run test commands and return success status and output if failed."""
    if not test_commands:
        return True, None
        
    for cmd in test_commands:
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                output = f"Test command failed: {cmd}\n"
                if stdout:
                    output += f"stdout:\n{stdout.decode()}\n"
                if stderr:
                    output += f"stderr:\n{stderr.decode()}\n"
                return False, output
                
        except Exception as e:
            return False, f"Error running test command '{cmd}': {str(e)}"
    
    return True, None

async def run_aider_command(files_config: Dict[str, List[str]], prompt: str, iteration: int) -> bool:
    """Run aider command with the given prompt and files configuration."""
    log_folder = os.path.join('.prompts', 'log')
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Run test commands if they exist
    test_success, test_output = await run_test_commands(files_config.get('test-cmd', []))
    print(test_output)
    if not test_success:
        # Prepend test failure output to the prompt
        prompt = f"""Test failures detected:

{test_output}

Please fix the above test failures.

{prompt}"""
    
    # Build base command with common options
    command = [
        'python -m aider',
        '--yes',
        # '--auto-test'
    ]
    
    # Add remaining options
    command.extend([
        f'--model {args.model}',
        '--auto-commits' if args.auto_commits else '--no-auto-commits',
        '--no-suggest-shell-commands',
        f'--message {shlex.quote(prompt)}'
    ])

    print(command)
    
    # Add read-only files
    for read_only_file in files_config.get('read_only', []):
        command.append(f'--read {shlex.quote(read_only_file)}')
    
    # Add project files
    command.extend(shlex.quote(file) for file in files_config.get('project_files', []))
    
    # Join command parts
    command = ' '.join(command)
    
    try:
        with open(log_file, 'w') as log_fh:
            log_fh.write(f"Running command (Iteration {iteration}):\n{command}\n\n")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            async def stream_output(stream, prefix=''):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded_line = line.decode().rstrip()
                    print(f"{prefix}{decoded_line}")
                    log_fh.write(f"{prefix}{decoded_line}\n")
                    log_fh.flush()

            # Stream both stdout and stderr concurrently
            await asyncio.gather(
                stream_output(process.stdout, ''),
                stream_output(process.stderr, '[ERROR] ')
            )
            
            # Wait for process to complete
            await process.wait()
            success = process.returncode == 0
            status = "Success" if success else "Failed"
            print(f"Iteration {iteration}: {status}")
            
            return success
            
    except Exception as e:
        print(f"Error in iteration {iteration}: {e}")
        return False

async def improve_codebase(files_config: Dict[str, List[str]], iterations: int, auto_mode: bool):
    """Iteratively improve the codebase using requirements-focused prompt."""
    print(f"Starting iterative improvement for {iterations} iterations...")
    print(f"Read-only files: {', '.join(files_config.get('read_only', []))}")
    print(f"Project files: {', '.join(files_config.get('project_files', []))}")
    
    results: Dict[int, bool] = {}
    
    for iteration in range(1, iterations + 1):
        print(f"\nIteration {iteration}/{iterations}")
        
        success = await run_aider_command(files_config, PROMPT, iteration)
        results[iteration] = success
        
        # Delay between iterations
        await asyncio.sleep(2)
        
        if not auto_mode:
            response = input("Continue with next iteration? (y/n): ").lower()
            if response != 'y':
                print("Stopping iterations as requested.")
                break
    
    # Print summary
    print("\nExecution Summary:")
    for iteration, success in results.items():
        status = "Success" if success else "Failed"
        print(f"Iteration {iteration}: {status}")

def main():
    # Define model mapping
    MODEL_MAPPING = {
        'deepseek': 'deepseek/deepseek-chat',
        'sonnet': 'anthropic/claude-3-5-sonnet-20241022',
        'deepseek/deepseek-chat': 'deepseek/deepseek-chat',
        'anthropic/claude-3-5-sonnet-20241022': 'anthropic/claude-3-5-sonnet-20241022'
    }

    parser = argparse.ArgumentParser(description='Iteratively improve code using AI suggestions.')
    parser.add_argument('--files-json', help='Path to JSON file containing file configurations')
    parser.add_argument('iterations', type=int, help='Number of improvement iterations')
    parser.add_argument('--auto', '-a', action='store_true', default=False,
                      help='Run automatically without confirmation between iterations')
    parser.add_argument('--auto-commits', action='store_true', default=True,
                      help='Enable automatic commits (default: True)')
    parser.add_argument('--prompt-file', '-p', help='Path to file containing custom prompt')
    parser.add_argument('--message', '-m', help='Direct message to use instead of prompt file or default prompt')
    parser.add_argument('--model', choices=list(MODEL_MAPPING.keys()),
                      default='deepseek',
                      help='Model to use: deepseek (default) or sonnet, or their full names')
    
    # Make args globally accessible for run_aider_command
    global args
    args = parser.parse_args()
    
    # Map model alias to full name
    args.model = MODEL_MAPPING[args.model]
    
    # Initialize default empty configuration
    files_config = {
        'read_only': [],
        'project_files': [],
        'test-cmd': []
    }
    
    # Load configuration from file if provided
    if args.files_json:
        try:
            with open(args.files_json, 'r') as f:
                files_config.update(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading files configuration: {e}")
            sys.exit(1)
    
    # Set PROMPT based on priority: message arg > prompt file > default prompt
    global PROMPT
    PROMPT = DEFAULT_PROMPT
    
    if args.message:
        PROMPT = args.message
    elif args.prompt_file:
        try:
            with open(args.prompt_file, 'r') as f:
                PROMPT = f.read()
        except FileNotFoundError:
            print(f"Error: Prompt file '{args.prompt_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading prompt file: {e}")
            sys.exit(1)
    
    asyncio.run(improve_codebase(files_config, args.iterations, args.auto))

if __name__ == "__main__":
    main() 