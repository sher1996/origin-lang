Write-Host "Creating GitHub repository for origin-lang..." -ForegroundColor Green
Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host "1. Go to https://github.com/new" -ForegroundColor Cyan
Write-Host "2. Repository name: origin-lang" -ForegroundColor Cyan
Write-Host "3. Make it Public" -ForegroundColor Cyan
Write-Host "4. Do NOT initialize with README, .gitignore, or license (we already have these)" -ForegroundColor Cyan
Write-Host "5. Click 'Create repository'" -ForegroundColor Cyan
Write-Host ""
Write-Host "After creating the repository, run this script again to push your code." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to continue..."

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git remote add origin https://github.com/YOUR_USERNAME/origin-lang.git
git branch -M main
git push -u origin main
Write-Host ""
Write-Host "Repository pushed successfully!" -ForegroundColor Green
Write-Host "Your repository is now available at: https://github.com/YOUR_USERNAME/origin-lang" -ForegroundColor Cyan
Read-Host "Press Enter to exit..." 