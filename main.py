#!/usr/bin/env python3
"""
Main entry point for the FastAPI hash server.
Run with: python main.py
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.server import main

if __name__ == "__main__":
    main()
