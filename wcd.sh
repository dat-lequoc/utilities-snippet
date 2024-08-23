#!/bin/bash

convert_and_cd() {
    # Check if an argument was provided
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <Windows_path>"
        return 1
    fi

    # Get the Windows path from the argument
    windows_path="$1"

    # Remove the drive letter and colon
    path_without_drive="${windows_path#*:}"

    # Replace backslashes with forward slashes
    unix_path="${path_without_drive//\\//}"

    # Add /mnt/c at the beginning
    wsl_path="/mnt/c$unix_path"

    # Change to the directory
    cd "$wsl_path"

    # Print the new current directory
    echo "Changed directory to: $(pwd)"
}

# Call the function with all provided arguments
convert_and_cd "$@"
