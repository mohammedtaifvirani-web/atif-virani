#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt6.QtWidgets import QApplication

from config.defaults import ensure_initial_setup
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow

def main() -> int:
    # Ensure folders, files, and sample data exist
    ensure_initial_setup()

    app = QApplication(sys.argv)
    app.setApplicationName("AVBilling")
    app.setOrganizationName("AVBilling")

    # Splash screen
    splash = SplashScreen()
    splash.show()

    # The main window will load its own theme-based styles
    main_window = MainWindow()

    # Once the splash screen's loading process is notionally finished,
    # show the main window.
    splash.loadingFinished.connect(main_window.show)
    
    # The splash screen will auto-close when the main window is activated.
    # This is handled by splash.finish(window) which is now implicitly managed
    # by window activation.

    return app.exec()

if __name__ == "__main__":
    # It's good practice to ensure the splash screen closes if the main app fails.
    try:
        sys.exit(main())
    except Exception as e:
        print(f"Application failed to launch: {e}")
        sys.exit(1)

