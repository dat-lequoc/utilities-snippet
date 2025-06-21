<#
.SYNOPSIS
    A full setup script that installs Chocolatey, then installs Firefox, Git, and VS Code,
    and finally downloads a specific ZIP file to the user's Downloads folder.

.DESCRIPTION
    This script performs the following actions in order:
    1. Checks if it is running with Administrator privileges, which is required.
    2. Installs the Chocolatey package manager if it's not already present.
    3. Uses Chocolatey to install Mozilla Firefox, Git, and Visual Studio Code.
    4. Reliably determines the path to the current user's Downloads folder.
    5. Downloads a specified file from a GitHub repository into that Downloads folder.

.NOTES
    Author: Gemini
    Date: June 21, 2025
    Requires: Windows PowerShell 5.1 or later. An active internet connection.
#>

# --- Main Script Body ---

# Step 1: Check for Administrator privileges
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "This script needs to be run with Administrator privileges." -ForegroundColor Red
    Write-Host "Please right-click on the script file and select 'Run as administrator'." -ForegroundColor Red
    Start-Sleep -Seconds 7
    Exit 1
}

Write-Host "Starting the full setup and download script..." -ForegroundColor Green
Write-Host "Administrator privileges confirmed." -ForegroundColor Green

# Step 2: Install Chocolatey and Core Software
Write-Host "--- Starting Software Installation Phase ---" -ForegroundColor Magenta

# Check if Chocolatey is already installed
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "Chocolatey is already installed. Skipping installation." -ForegroundColor Cyan
} else {
    Write-Host "Attempting to install Chocolatey..." -ForegroundColor Yellow
    
    # Set Execution Policy and TLS version for the installation process [1, 6, 10, 12]
    Set-ExecutionPolicy Bypass -Scope Process -Force | Out-Null
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    
    try {
        # Download and install Chocolatey [1, 6, 10, 12]
        iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "Chocolatey installed successfully!" -ForegroundColor Green
        
        # Refresh environment variables to make 'choco' command available immediately
        $env:Path += ";$($env:ALLUSERSPROFILE)\chocolatey\bin"
    }
    catch {
        Write-Host "FATAL ERROR: Could not install Chocolatey. $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please check your internet connection and try again. Aborting script." -ForegroundColor Red
        Start-Sleep -Seconds 7
        Exit 1
    }
}

# Verify Chocolatey is ready
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "FATAL ERROR: Chocolatey command not found after installation attempt." -ForegroundColor Red
    Write-Host "Please close and reopen this PowerShell window as Administrator and re-run." -ForegroundColor Red
    Start-Sleep -Seconds 7
    Exit 1
}

# Install packages using Chocolatey
$packages = @(
    @{Name="Mozilla Firefox"; Package="firefox"}, # [4, 12, 17]
    @{Name="Git"; Package="git.install"}, # [2, 5, 12, 14]
    @{Name="Visual Studio Code"; Package="vscode"} # [9, 12, 13, 19]
)

foreach ($item in $packages) {
    Write-Host "Checking for $($item.Name)..." -ForegroundColor Yellow
    # Use '-y' to automatically confirm prompts
    try {
        choco install $item.Package -y
        Write-Host "$($item.Name) installed successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "ERROR: Failed to install $($item.Name). $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "--- Software Installation Phase Complete ---" -ForegroundColor Magenta
Start-Sleep -Seconds 2

# Step 3: Download the specified file
Write-Host "--- Starting File Download Phase ---" -ForegroundColor Magenta

# --- Download Configuration ---
$fileUrl = "https://raw.githubusercontent.com/dat-lequoc/apps/refs/heads/main/extension-1.1.26-firefox.zip"
$fileName = "extension-1.1.26-firefox.zip"

# Find the user's Downloads folder path robustly
try {
    # This COM object method reliably finds the Downloads folder, even if relocated. [11, 15, 18]
    $downloadsPath = (New-Object -ComObject Shell.Application).Namespace('shell:Downloads').Self.Path
    if (-not $downloadsPath) {
        throw "Could not determine the Downloads folder path via COM object."
    }
}
catch {
    Write-Host "Warning: Could not determine the Downloads folder path automatically. $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Falling back to default user profile path for Downloads."
    $downloadsPath = "$env:USERPROFILE\Downloads"
}

# Create the Downloads directory if it doesn't exist
if (-not (Test-Path -Path $downloadsPath)) {
    Write-Host "Downloads folder not found at '$downloadsPath', creating it now." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $downloadsPath | Out-Null
}

$destinationPath = Join-Path -Path $downloadsPath -ChildPath $fileName

Write-Host "File will be saved to: $destinationPath" -ForegroundColor Cyan
Write-Host "Downloading from: $fileUrl" -ForegroundColor Cyan

# Download the file using Invoke-WebRequest
try {
    # Using Invoke-WebRequest is the modern standard for file downloads in PowerShell. [16, 20]
    Invoke-WebRequest -Uri $fileUrl -OutFile $destinationPath
    Write-Host "Download complete!" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: An error occurred during download. $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check your internet connection and the file URL." -ForegroundColor Red
}

Write-Host "--- Script Finished ---" -ForegroundColor Green
Write-Host "You may need to restart your terminal or computer for all changes to take full effect." -ForegroundColor Green
Start-Sleep -Seconds 10
