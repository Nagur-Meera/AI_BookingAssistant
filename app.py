"""
AI Booking Assistant - Entry Point
Redirects to the main application in app/main.py
"""
import os
import sys

# Add project root to path
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

# Import and run the main application
from app.main import main

if __name__ == "__main__":
    main()