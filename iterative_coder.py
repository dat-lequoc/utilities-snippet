import asyncio
import subprocess
import shlex
import sys
import os
import json
import argparse
from typing import List, Dict
from datetime import datetime

# Predefined prompt for requirements implementation
PROMPT = """
Review the REQUIREMENTS and implement the necessary changes while following the guidelines.
"""

async def run_aider_command(files_config: Dict[str, List[str]], prompt: str, iteration: int, prompt_type: str) -> bool:
    """Run aider command with the given prompt and files configuration."""
    log_folder = os.path.join('.prompts', 'log', f'iteration_{iteration}')
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, f'{prompt_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Build base command with common options
    command = [
        'python -m aider',
        '--yes',
        '--model deepseek/deepseek-chat',
        '--auto-commits' if args.auto_commits else '--no-auto-commits',
        '--no-suggest-shell-commands',
        f'--message {shlex.quote(prompt)}'
    ]
    
    # Add read-only files
    for read_only_file in files_config.get('read_only', []):
        command.append(f'--read {shlex.quote(read_only_file)}')
    
    # Add project files
    command.extend(shlex.quote(file) for file in files_config.get('project_files', []))
    
    # Join command parts
    command = ' '.join(command)
    
    try:
        with open(log_file, 'w') as log_fh:
            log_fh.write(f"Running command for {prompt_type} (Iteration {iteration}):\n{command}\n\n")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            log_fh.write("Standard Output:\n")
            log_fh.write(stdout.decode() + "\n")
            log_fh.write("Standard Error:\n")
            log_fh.write(stderr.decode() + "\n")
            
            success = process.returncode == 0
            status = "Success" if success else "Failed"
            print(f"Iteration {iteration} - {prompt_type}: {status}")
            
            return success
            
    except Exception as e:
        print(f"Error in iteration {iteration} - {prompt_type}: {e}")
        return False

async def improve_codebase(files_config: Dict[str, List[str]], iterations: int, auto_mode: bool):
    """Iteratively improve the codebase using requirements-focused prompt."""
    print(f"Starting iterative improvement for {iterations} iterations...")
    print(f"Read-only files: {', '.join(files_config.get('read_only', []))}")
    print(f"Project files: {', '.join(files_config.get('project_files', []))}")
    
    results: Dict[int, bool] = {}
    
    for iteration in range(1, iterations + 1):
        print(f"\nIteration {iteration}/{iterations}")
        
        success = await run_aider_command(files_config, PROMPT, iteration, "requirements")
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
    parser = argparse.ArgumentParser(description='Iteratively improve code using AI suggestions.')
    parser.add_argument('files_json', help='Path to JSON file containing file configurations')
    parser.add_argument('iterations', type=int, help='Number of improvement iterations')
    parser.add_argument('--auto', '-a', action='store_true', default=False,
                      help='Run automatically without confirmation between iterations')
    parser.add_argument('--auto-commits', action='store_true', default=True,
                      help='Enable automatic commits (default: True)')
    
    # Make args globally accessible for run_aider_command
    global args
    args = parser.parse_args()
    
    try:
        with open(args.files_json, 'r') as f:
            files_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading files configuration: {e}")
        sys.exit(1)
    
    asyncio.run(improve_codebase(files_config, args.iterations, args.auto))

if __name__ == "__main__":
    main() 