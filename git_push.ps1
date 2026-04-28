# NeuroPrime Git Initialization and Push Script

# Step 1: Set Git path
$env:PATH += ";C:\Program Files\Git\bin;C:\Program Files\Git\cmd"

# Verify Git is available
Write-Host "Checking Git installation..."
try {
    $gitVersion = & git --version 2>&1
    Write-Host "Git version: $gitVersion"
} catch {
    Write-Host "Error: Git is not properly installed"
    Write-Host "Please install Git manually: https://git-scm.com/download/win"
    exit 1
}

# Step 2: Initialize Git repository (if not already initialized)
Write-Host "`nChecking Git repository status..."
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..."
    & git init
} else {
    Write-Host "Git repository already exists"
}

# Step 3: Configure user information (if not already configured)
Write-Host "`nConfiguring Git user information..."
try {
    $userName = & git config user.name 2>&1
    if ([string]::IsNullOrEmpty($userName)) {
        Write-Host "Please set Git username:"
        $userName = Read-Host
        & git config user.name $userName
    }
} catch {}

try {
    $userEmail = & git config user.email 2>&1
    if ([string]::IsNullOrEmpty($userEmail)) {
        Write-Host "Please set Git email:"
        $userEmail = Read-Host
        & git config user.email $userEmail
    }
} catch {}

# Step 4: Create .gitignore file
Write-Host "`nCreating .gitignore file..."
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
"@

if (-not (Test-Path ".gitignore")) {
    Set-Content -Path ".gitignore" -Value $gitignoreContent
    Write-Host ".gitignore file created"
}

# Step 5: Add remote repository
Write-Host "`nSetting remote repository..."
$remoteUrl = "https://github.com/AlvyYim/NeuroPrime.git"
Write-Host "Remote URL: $remoteUrl"

# Check if remote already exists
$remoteExists = & git remote -v 2>&1 | Select-String "origin"
if ([string]::IsNullOrEmpty($remoteExists)) {
    & git remote add origin $remoteUrl
    Write-Host "Remote repository added"
} else {
    Write-Host "Remote already exists"
    & git remote set-url origin $remoteUrl
    Write-Host "Remote URL updated"
}

# Step 6: Add files to staging area
Write-Host "`nAdding files to staging area..."
& git add .

# Step 7: Commit changes
Write-Host "`nCommitting changes..."
$commitMessage = "Initial commit: NeuroPrime project - Macaque electrophysiology data analysis"
& git commit -m $commitMessage

# Step 8: Check branch status
Write-Host "`nChecking branch status..."
$branch = & git branch
Write-Host "Current branch: $branch"

# Step 9: Try to pull remote changes (if any)
Write-Host "`nTrying to pull remote changes..."
try {
    & git pull origin master --allow-unrelated-histories 2>&1
} catch {
    Write-Host "Pull failed or no remote changes, continuing with push..."
}

# Step 10: Push to GitHub
Write-Host "`nPushing to GitHub..."
try {
    & git push -u origin master
    Write-Host "`nPush successful!"
    Write-Host "Visit your repository: https://github.com/AlvyYim/NeuroPrime"
} catch {
    Write-Host "`nPush failed: $_"
    Write-Host "`nPossible reasons:"
    Write-Host "1. Remote repository has commits that conflict with local"
    Write-Host "2. Authentication required (username/password or Personal Access Token)"
    Write-Host "3. Network connection issue"
    Write-Host "`nSolutions:"
    Write-Host "- If conflict: try 'git pull origin master --rebase'"
    Write-Host "- If authentication needed: ensure you use correct GitHub credentials"
    Write-Host "- Check network connection"
}

Write-Host "`nScript completed!"
