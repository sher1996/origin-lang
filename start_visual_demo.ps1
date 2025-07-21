Write-Host "🎨 Starting Visual Editor for Debugger Demo" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check if we're in the right directory
if (-not (Test-Path "visual/package.json")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "   Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Write-Host "📁 Found visual editor in visual/ directory" -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "visual/node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    try {
        Set-Location visual
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw "npm install failed"
        }
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
        Set-Location ..
    }
    catch {
        Write-Host "❌ Failed to install dependencies: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🚀 Starting visual editor development server..." -ForegroundColor Green
Write-Host "   The editor will be available at: http://localhost:5173/" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:5173/ in your browser"
Write-Host "2. Click 'Open Recording' in the toolbar"
Write-Host "3. Select: examples/recordings/fizzbuzz.orirec"
Write-Host "4. Start your screen recorder"
Write-Host "5. Step through the FizzBuzz program"
Write-Host "6. Save the recording as: docs/fizzbuzz_debugger_demo.gif"
Write-Host ""
Write-Host "🎬 Demo recording tips:" -ForegroundColor Yellow
Write-Host "- Show the timeline controls at the bottom"
Write-Host "- Step through using → key (frame by frame)"
Write-Host "- Highlight the blue pulsing active blocks"
Write-Host "- Show variable tooltips appearing"
Write-Host "- Demonstrate scrubbing with the timeline slider"
Write-Host "- Keep it under 30 seconds for best impact"
Write-Host ""

try {
    Set-Location visual
    npm run dev
}
catch {
    Write-Host "❌ Failed to start visual editor: $_" -ForegroundColor Red
    exit 1
}
finally {
    Set-Location ..
} 