Write-Host "=== ORIGIN LANGUAGE GITHUB REPOSITORY SETUP ===" -ForegroundColor Green
Write-Host ""
Write-Host "This script will help you create the origin-lang repository on GitHub." -ForegroundColor Yellow
Write-Host "This is a SEPARATE project from CodeClinic." -ForegroundColor Red
Write-Host ""
Write-Host "Step 1: Create GitHub Repository" -ForegroundColor Cyan
Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: origin-lang" -ForegroundColor White
Write-Host "3. Description: A programming language designed to bridge the gap between human intent and machine execution" -ForegroundColor White
Write-Host "4. Make it PUBLIC" -ForegroundColor White
Write-Host "5. DO NOT initialize with README, .gitignore, or license (we already have these)" -ForegroundColor White
Write-Host "6. Click 'Create repository'" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter after creating the repository..."

Write-Host ""
Write-Host "Step 2: Get your GitHub username" -ForegroundColor Cyan
$username = Read-Host "Enter your GitHub username"
Write-Host ""

Write-Host "Step 3: Push to GitHub" -ForegroundColor Cyan
Write-Host "Adding remote origin..." -ForegroundColor Yellow
git remote add origin "https://github.com/$username/origin-lang.git"
Write-Host "Renaming branch to main..." -ForegroundColor Yellow
git branch -M main
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host ""
Write-Host "=== SUCCESS! ===" -ForegroundColor Green
Write-Host "Your repository is now live at: https://github.com/$username/origin-lang" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository includes:" -ForegroundColor Yellow
Write-Host "- README.md with project mission" -ForegroundColor White
Write-Host "- MIT License" -ForegroundColor White
Write-Host "- Initial commit structure" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit..." 