import asyncio
import subprocess
import shlex
import sys
import os
import argparse
from typing import List, Dict
from datetime import datetime

# Predefined prompts for different improvement aspects
PROMPTS = {
    "enhance": """
Explore the codebase and identify opportunities to add value through new features or improvements to existing functionality.  
Think creatively about how to make the code more useful, intuitive, or powerful.  
Implement small, incremental changes that align with the code's purpose and enhance its overall quality.  
Focus on user experience, functionality, and efficiency, but prioritize changes that are easy to integrate and maintain.  
""",
    
    "bug_fix": """
Analyze the codebase for potential issues, bugs, or areas of improvement.  
Propose and implement fixes that are minimal yet effective, ensuring the code remains robust and reliable.  
Focus on stability and correctness while maintaining the existing functionality.  
""",
}

COMMON_SUFFIX = """
Approach guidelines:
- Make precise, self-contained improvements
- Preserve existing functionality while adding value
- Implement changes autonomously and confidently
- Keep code dense compact and focused, without comments.
- Work within the current file structure, do not create new files.
"""

async def run_aider_command(file_path: str, prompt: str, iteration: int, prompt_type: str) -> bool:
    """Run aider command with the given prompt and file."""
    log_folder = os.path.join('.prompts', 'log', f'iteration_{iteration}')
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, f'{prompt_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Combine prompt with common suffix
    full_prompt = f"{prompt}\n{COMMON_SUFFIX}"
    
    # Build base command with common options
    command = (
        f'python -m aider '
        f'--yes '
        f'--model deepseek/deepseek-chat '
        f'{"--auto-commits" if args.auto_commits else "--no-auto-commits"} '
        f'--no-suggest-shell-commands '
        f'--message {shlex.quote(full_prompt)} '
        f'{shlex.quote(file_path)}'
    )
    
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

async def improve_codebase(file_path: str, iterations: int, auto_mode: bool):
    """Iteratively improve the codebase using different prompts."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found!")
        return
    
    print(f"Starting iterative improvement of {file_path} for {iterations} iterations...")
    
    results: Dict[int, Dict[str, bool]] = {}
    prompt_types = list(PROMPTS.keys())
    
    for iteration in range(1, iterations + 1):
        print(f"\nIteration {iteration}/{iterations}")
                
        results[iteration] = {}
        
        # Get the prompt type for this iteration by cycling through them
        prompt_type = prompt_types[(iteration - 1) % len(prompt_types)]
        prompt = PROMPTS[prompt_type]
        
        success = await run_aider_command(file_path, prompt, iteration, prompt_type)
        results[iteration][prompt_type] = success
        
        # Delay between iterations
        await asyncio.sleep(2)
        
        if not auto_mode:
            response = input("Continue with this iteration? (y/n): ").lower()
            if response != 'y':
                print("Stopping iterations as requested.")
                break
    
    # Print summary
    print("\nExecution Summary:")
    for iteration, result in results.items():
        print(f"\nIteration {iteration}:")
        for prompt_type, success in result.items():
            status = "Success" if success else "Failed"
            print(f"  {prompt_type}: {status}")

def main():
    parser = argparse.ArgumentParser(description='Iteratively improve code using AI suggestions.')
    parser.add_argument('file_path', help='Path to the file to improve')
    parser.add_argument('iterations', type=int, help='Number of improvement iterations')
    parser.add_argument('--auto', '-a', action='store_true', default=False,
                      help='Run automatically without confirmation between iterations')
    parser.add_argument('--auto-commits', action='store_true', default=True,
                      help='Enable automatic commits (default: True)')
    
    # Make args globally accessible for run_aider_command
    global args
    args = parser.parse_args()
    
    asyncio.run(improve_codebase(args.file_path, args.iterations, args.auto))

if __name__ == "__main__":
    main() 