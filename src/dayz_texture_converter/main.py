#!/usr/bin/env python3
"""
Main entry point for DayZ Texture Converter application.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for development
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

def main():
    """Main application entry point."""
    try:
        # Import here to avoid circular imports and ensure path is set
        from dayz_texture_converter.gui.main_window import MainWindow
        
        # Create and run the application
        app = MainWindow()
        app.run()
        
    except ImportError as e:
        print(f"Error importing application modules: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()