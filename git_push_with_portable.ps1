# NeuroPrime Git Push Script using Portable Git

$ErrorActionPreference = "Stop"

# Set Git path
$gitPath = "C:\Users\Administrator\Desktop\new hope\code\NeuroPrime\mingit\cmd\git.exe"

Write-Host "=========================================="
Write-Host "NeuroPrime Git Push Script"
Write-Host "=========================================="

# Verify Git exists
if (-not (Test-Path $gitPath)) {
    Write-Host "ERROR: Git not found at $gitPath"
    exit 1
}

Write-Host "`n[1/8] Verifying Git installation..."
& $gitPath --version

# Set Git config
Write-Host "`n[2/8] Configuring Git user..."
& $gitPath config --global user.name "AlvyYim"
& $gitPath config --global user.email "github@example.com"

# Initialize Git repo (if not exists)
Write-Host "`n[3/8] Initializing Git repository..."
if (-not (Test-Path ".git")) {
    & $gitPath init
    Write-Host "Git repository initialized"
} else {
    Write-Host "Git repository already exists"
}

# Create .gitignore
Write-Host "`n[4/8] Creating .gitignore..."
$gitignoreContent = @"
# Virtual environments
venv/
env/

# Python cache
__pycache__/
*.py[cod]
*`$py.class

# Data files
test2/
data/
*.h5
*.nev
*.ncs

# Log files
*.log

# Temporary files
*.tmp
*.temp
*.swp

# IDE configuration
.vscode/
.idea/
*.sublime-*

# Operating system
Thumbs.db
Desktop.ini
.DS_Store

# Compiled files
*.pyc
*.pyo

# Jupyter Notebook
.ipynb_checkpoints/

# Project specific
psth_data.csv
*.png
*.jpg
*.zip
GitInstaller.exe
mingit.zip
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host ".gitignore created"

# Add remote
Write-Host "`n[5/8] Adding remote repository..."
$remoteUrl = "https://github.com/AlvyYim/NeuroPrime.git"
& $gitPath remote remove origin 2>$null | Out-Null
& $gitPath remote add origin $remoteUrl
Write-Host "Remote added: $remoteUrl"

# Add all files
Write-Host "`n[6/8] Adding files to staging area..."
& $gitPath add .

# Check status
Write-Host "`n[7/8] Committing changes..."
$commitMessage = "NeuroPrime project - Macaque electrophysiology data analysis software"
& $gitPath commit -m $commitMessage

# Push to GitHub
Write-Host "`n[8/8] Pushing to GitHub..."
Write-Host "This may take a moment..."
try {
    & $gitPath push -u origin master --force
    Write-Host "`n=========================================="
    Write-Host "SUCCESS! Project pushed to GitHub!"
    Write-Host "Repository URL: https://github.com/AlvyYim/NeuroPrime"
    Write-Host "=========================================="
} catch {
    Write-Host "`nPush failed: $_"
    Write-Host "`nPossible reasons:"
    Write-Host "1. Remote repository has commits that conflict with local"
    Write-Host "2. Authentication required"
    Write-Host "3. Network connection issue"
}

Write-Host "`nScript completed!"
