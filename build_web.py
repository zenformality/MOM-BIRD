#!/usr/bin/env python3
"""
Build script for web deployment using pygbag.
Run: python build_web.py
"""
import subprocess
import sys
import os

def build_web():
    """Build the game for web using pygbag."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Use main.py (not the -exe version) for web
    # pygbag works best with standard pygame loops
    cmd = [
        sys.executable, "-m", "pygbag",
        "--build",
        "--app_name", "MOM BIRD",
        "main.py"
    ]
    
    print("Building web version with pygbag...")
    print("Command:", " ".join(cmd))
    
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    try:
        import pygbag
    except ImportError:
        print("Installing pygbag...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pygbag"])
    
    sys.exit(build_web())