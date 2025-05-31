#!/usr/bin/env python3
"""
Utility script to read ALL variables from .env file and set them as secrets in Fly.io
Usage: python set_fly_secrets.py
"""

import os
import subprocess
from dotenv import dotenv_values

def set_fly_secrets():
    # Read .env file
    env_vars = dotenv_values(".env")
    
    if not env_vars:
        print("Error: No environment variables found in .env file")
        return
    
    # Build secrets string from all variables in .env
    secrets = [f"{key}={value}" for key, value in env_vars.items()]
    
    # Print summary of what will be set (without values)
    print(f"Setting {len(secrets)} secrets in Fly.io:")
    print("Keys:", ", ".join(env_vars.keys()))
    
    # Construct and run fly secrets set command
    cmd = ["fly", "secrets", "set"] + secrets
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("Successfully set secrets in Fly.io")
        else:
            print(f"Error setting secrets: {result.stderr}")
    except Exception as e:
        print(f"Failed to execute fly command: {str(e)}")

if __name__ == "__main__":
    set_fly_secrets() 
