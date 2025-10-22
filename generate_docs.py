#!/usr/bin/env python3
"""
Script to generate documentation for Constrictor framework.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None


def main():
    """Generate documentation."""
    print("Generating Constrictor documentation...")
    
    # Check if we're in the right directory
    if not Path("docs").exists():
        print("Error: docs directory not found. Run this script from the project root.")
        sys.exit(1)
    
    # Install documentation dependencies
    print("Installing documentation dependencies...")
    result = run_command("pip install -e .[docs]")
    if result is None:
        print("Failed to install documentation dependencies")
        sys.exit(1)
    
    # Change to docs directory
    docs_dir = Path("docs")
    
    # Generate documentation
    print("Generating documentation...")
    result = run_command("sphinx-build -W -b html . _build/html", cwd=docs_dir)
    if result is None:
        print("Failed to generate documentation")
        sys.exit(1)
    
    print("Documentation generated successfully!")
    print("You can view it by opening docs/_build/html/index.html in your browser")
    
    # Optionally open in browser
    if sys.platform == "darwin":  # macOS
        run_command("open docs/_build/html/index.html")
    elif sys.platform == "win32":  # Windows
        run_command("start docs/_build/html/index.html")
    elif sys.platform == "linux":  # Linux
        run_command("xdg-open docs/_build/html/index.html")


if __name__ == "__main__":
    main()
