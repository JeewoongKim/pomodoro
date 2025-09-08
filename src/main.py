#!/usr/bin/env python3
"""
Pomodoro Timer Application - Main Entry Point
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add src directory to path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = Path(sys.executable).parent
else:
    # Running as script
    application_path = Path(__file__).parent

sys.path.insert(0, str(application_path))

from ui.main_window import PomodoroMainWindow

def main():
    """Main entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application properties
    app.setApplicationName("Pomodoro Timer")
    app.setOrganizationName("PomodoroApps")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    main_window = PomodoroMainWindow()
    main_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
