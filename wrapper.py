import sys
import os

# Add the current directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import and run the main script
import main