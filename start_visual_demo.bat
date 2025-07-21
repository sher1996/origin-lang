@echo off
echo 🎨 Starting Visual Editor for Debugger Demo
echo ================================================

cd visual
if not exist node_modules (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Starting visual editor development server...
echo    The editor will be available at: http://localhost:5173/
echo.
echo 📋 Next steps:
echo 1. Open http://localhost:5173/ in your browser
echo 2. Click 'Open Recording' in the toolbar
echo 3. Select: examples/recordings/fizzbuzz.orirec
echo 4. Start your screen recorder
echo 5. Step through the FizzBuzz program
echo 6. Save the recording as: docs/fizzbuzz_debugger_demo.gif
echo.
echo 🎬 Demo recording tips:
echo - Show the timeline controls at the bottom
echo - Step through using → key (frame by frame)
echo - Highlight the blue pulsing active blocks
echo - Show variable tooltips appearing
echo - Demonstrate scrubbing with the timeline slider
echo - Keep it under 30 seconds for best impact
echo.

npm run dev 