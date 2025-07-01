"""
RDP (Rapid Development Platform) for Freqtrade
Visual strategy builder using drag-and-drop interface
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow


def main():
    """Main entry point for the application"""
    # Enable high DPI scaling (modern approach)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setApplicationName("RDP for Freqtrade")
    app.setApplicationVersion("0.2.0")
    app.setOrganizationName("FreqtradeDevelopers")
    
    # Set application icon if available
    # app.setWindowIcon(QIcon("assets/icon.png"))
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
