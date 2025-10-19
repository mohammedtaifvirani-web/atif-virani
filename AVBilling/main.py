#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from config.defaults import ensure_initial_setup
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow
from utils.helpers import read_text_file_safe


def load_styles(app: QApplication) -> None:
    styles_path = Path(__file__).parent / "assets" / "styles.qss"
    qss = read_text_file_safe(styles_path)
    if qss:
        app.setStyleSheet(qss)


def main() -> int:
    # Ensure folders, files, and sample data exist
    ensure_initial_setup()

    app = QApplication(sys.argv)
    app.setApplicationName("AVBilling")
    app.setOrganizationName("AVBilling")

    load_styles(app)

    # Splash screen
    splash = SplashScreen()
    splash.show()

    def on_loaded():
        window = MainWindow()
        window.show()
        splash.finish(window)

    splash.loadingFinished.connect(on_loaded)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


