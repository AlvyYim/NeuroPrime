# NeuroPrime GitHub Upload Script using GitHub API

param(
    [string]$RepoOwner = "AlvyYim",
    [string]$RepoName = "NeuroPrime",
    [string]$FilePath = ".",
    [string]$Branch = "main"
)

# GitHub Personal Access Token (you need to create one at https://github.com/settings/tokens)
# For security, this should be passed as environment variable or securely stored
$Token = $env:GITHUB_TOKEN

if ([string]::IsNullOrEmpty($Token)) {
    Write-Host "Error: GitHub token not found. Please set GITHUB_TOKEN environment variable."
    Write-Host "Create a token at: https://github.com/settings/tokens"
    Write-Host "Required scopes: repo (full control)"
    exit 1
}

# Set GitHub API headers
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

# Check if repository exists
Write-Host "Checking if repository exists..."
$repoUrl = "https://api.github.com/repos/$RepoOwner/$RepoName"
try {
    $repoResponse = Invoke-RestMethod -Uri $repoUrl -Headers $headers -Method Get
    Write-Host "Repository already exists: $RepoOwner/$RepoName"
} catch {
    Write-Host "Repository does not exist, creating..."
    $createRepoBody = @{
        name = $RepoName
        description = "NeuroPrime - Macaque Electrophysiology Data Analysis Software"
        homepage = ""
        private = $false
        has_issues = $true
        has_wiki = $true
    } | ConvertTo-Json

    try {
        $createResponse = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $createRepoBody -ContentType "application/json"
        Write-Host "Repository created successfully!"
    } catch {
        Write-Host "Error creating repository: $_"
        exit 1
    }
}

# Get list of files to upload
Write-Host "`nPreparing files for upload..."
$files = Get-ChildItem -Path $FilePath -Recurse -File | Where-Object { $_.FullName -notmatch '\.git' -and $_.FullName -notmatch '__pycache__' -and $_.FullName -notmatch '\.pyc' }

# Create .gitignore first
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

# Get default branch
Write-Host "Getting repository info..."
$repoInfo = Invoke-RestMethod -Uri $repoUrl -Headers $headers -Method Get
$defaultBranch = $repoInfo.default_branch
Write-Host "Default branch: $defaultBranch"

# Initialize local Git repo if not exists
if (-not (Test-Path ".git")) {
    Write-Host "`nGit repository not initialized. Please install Git and run:"
    Write-Host "git init"
    Write-Host "git remote add origin https://github.com/$RepoOwner/$RepoName.git"
    Write-Host "git add ."
    Write-Host "git commit -m 'Initial commit'"
    Write-Host "git push -u origin $defaultBranch"
    exit 1
}

# Get current commit SHA
Write-Host "`nGetting current commit SHA..."
$commitsUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/commits?per_page=1"
try {
    $commits = Invoke-RestMethod -Uri $commitsUrl -Headers $headers -Method Get
    $latestCommitSha = $commits[0].sha
    Write-Host "Latest commit SHA: $latestCommitSha"
} catch {
    Write-Host "No commits found or error getting commits: $_"
    $latestCommitSha = $null
}

# For initial commit, we need to use the GitHub API differently
# Let's use git commands if available
Write-Host "`nAttempting to push using git commands..."

# Find git executable
$gitPaths = @(
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files\Git\cmd\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\git.exe"
)

$gitPath = $null
foreach ($path in $gitPaths) {
    if (Test-Path $path) {
        $gitPath = $path
        break
    }
}

if ($gitPath) {
    Write-Host "Found Git at: $gitPath"

    # Set Git config
    & $gitPath config --global user.name $RepoOwner
    & $gitPath config --global user.email "github@example.com"

    # Add remote
    & $gitPath remote remove origin 2>$null
    & $gitPath remote add origin "https://$($Token)@github.com/$RepoOwner/$RepoName.git"

    # Try to pull first (if repo has content)
    if ($latestCommitSha) {
        Write-Host "Attempting to pull remote changes..."
        try {
            & $gitPath pull origin $defaultBranch --allow-unrelated-histories 2>&1
        } catch {
            Write-Host "Pull failed or no remote content, continuing..."
        }
    }

    # Add all files
    Write-Host "Adding files..."
    & $gitPath add .

    # Commit
    Write-Host "Committing..."
    $commitMessage = "NeuroPrime project - Macaque electrophysiology data analysis"
    & $gitPath commit -m $commitMessage

    # Push
    Write-Host "Pushing to GitHub..."
    try {
        & $gitPath push -u origin $defaultBranch
        Write-Host "`n==========================================="
        Write-Host "SUCCESS! Project pushed to GitHub!"
        Write-Host "Repository URL: https://github.com/$RepoOwner/$RepoName"
        Write-Host "==========================================="
    } catch {
        Write-Host "Push failed: $_"
    }
} else {
    Write-Host "`nGit not found. Please install Git from: https://git-scm.com/download/win"
    Write-Host "`nAfter installing Git, run these commands:"
    Write-Host "1. cd $FilePath"
    Write-Host "2. git init"
    Write-Host "3. git remote add origin https://github.com/$RepoOwner/$RepoName.git"
    Write-Host "4. git add ."
    Write-Host "5. git commit -m 'Initial commit'"
    Write-Host "6. git push -u origin $defaultBranch"
}
