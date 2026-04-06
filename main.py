"""
OpenModelica Simulation Launcher
=================================
Entry point for the desktop GUI application.

Usage:
    python main.py

Requirements:
    - Python 3.6+
    - PyQt6
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from src.app import SimLauncherApp


def main() -> None:
    """Initialize and launch the simulation GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("OpenModelica Simulation Launcher")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FOSSEE OpenModelica")

    # Set default application font
    font = QFont("Courier New", 10)
    app.setFont(font)

    window = SimLauncherApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
