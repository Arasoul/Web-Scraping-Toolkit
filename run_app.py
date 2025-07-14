#!/usr/bin/env python3
"""
Run the Streamlit Content Extractor Dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit app."""
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    
    try:
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nStreamlit app stopped by user.")
        return 0
    
    return 0

if __name__ == "__main__":
    exit(main())
