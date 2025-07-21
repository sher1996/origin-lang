#!/usr/bin/env python3
"""
Script to start the visual editor for creating the debugger demo.
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    print("🎨 Starting Visual Editor for Debugger Demo")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("visual/package.json").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    print("📁 Found visual editor in visual/ directory")
    
    # Check if node_modules exists
    if not Path("visual/node_modules").exists():
        print("📦 Installing dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd="visual", check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    print("\n🚀 Starting visual editor development server...")
    print("   The editor will be available at: http://localhost:5173/")
    print("\n📋 Next steps:")
    print("1. Open http://localhost:5173/ in your browser")
    print("2. Click 'Open Recording' in the toolbar")
    print("3. Select: examples/recordings/fizzbuzz.orirec")
    print("4. Start your screen recorder")
    print("5. Step through the FizzBuzz program")
    print("6. Save the recording as: docs/fizzbuzz_debugger_demo.gif")
    
    print("\n🎬 Demo recording tips:")
    print("- Show the timeline controls at the bottom")
    print("- Step through using → key (frame by frame)")
    print("- Highlight the blue pulsing active blocks")
    print("- Show variable tooltips appearing")
    print("- Demonstrate scrubbing with the timeline slider")
    print("- Keep it under 30 seconds for best impact")
    
    try:
        # Start the development server
        subprocess.run(["npm", "run", "dev"], cwd="visual")
    except KeyboardInterrupt:
        print("\n👋 Visual editor stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start visual editor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 