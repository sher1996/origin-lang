@echo off
echo Creating GitHub repository for origin-lang...
echo.
echo Please follow these steps:
echo 1. Go to https://github.com/new
echo 2. Repository name: origin-lang
echo 3. Make it Public
echo 4. Do NOT initialize with README, .gitignore, or license (we already have these)
echo 5. Click "Create repository"
echo.
echo After creating the repository, run this script again to push your code.
echo.
pause
echo.
echo Pushing to GitHub...
git remote add origin https://github.com/YOUR_USERNAME/origin-lang.git
git branch -M main
git push -u origin main
echo.
echo Repository pushed successfully!
echo Your repository is now available at: https://github.com/YOUR_USERNAME/origin-lang
pause 