#!/usr/bin/env python3
"""
Script to help create the Visual Debugger demo GIF.

This script provides instructions and commands to create a demo GIF
showing the visual debugger stepping through the FizzBuzz program.
"""

import os
import subprocess
import sys

def main():
    print("🎬 Visual Debugger Demo GIF Creator")
    print("=" * 40)
    
    print("\n📋 Prerequisites:")
    print("1. Install a screen recording tool (e.g., OBS Studio, ShareX, or LICEcap)")
    print("2. Make sure the visual editor is working: origin viz")
    print("3. Have the FizzBuzz recording ready: examples/recordings/fizzbuzz.orirec")
    
    print("\n🎯 Steps to create the demo GIF:")
    print("1. Start the visual editor:")
    print("   origin viz")
    
    print("\n2. Open the FizzBuzz recording:")
    print("   - Click 'Open Recording' in the toolbar")
    print("   - Select: examples/recordings/fizzbuzz.orirec")
    
    print("\n3. Record the demo:")
    print("   - Start your screen recorder")
    print("   - Show the timeline controls at the bottom")
    print("   - Step through execution using → key")
    print("   - Highlight the blue pulsing blocks")
    print("   - Show variable tooltips appearing")
    print("   - Demonstrate scrubbing with the timeline slider")
    
    print("\n4. Save as: docs/fizzbuzz_debugger_demo.gif")
    
    print("\n💡 Tips for a great demo:")
    print("- Keep it under 30 seconds")
    print("- Show clear block highlighting")
    print("- Include variable tooltips")
    print("- Demonstrate both stepping and scrubbing")
    print("- Add text overlay explaining key features")
    
    print("\n🔧 Alternative: Create a new recording")
    print("origin run examples/fizzbuzz.origin --record")
    print("This will create a fresh recording for the demo.")

if __name__ == "__main__":
    main() 