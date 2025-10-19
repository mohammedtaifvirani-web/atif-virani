#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar

from config.defaults import app_paths


class SplashScreen(QDialog):
    loadingFinished = pyqtSignal()

    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setObjectName("SplashScreen")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        logo_label = QLabel("", self)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = app_paths()["assets"] / "logo.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("AVBilling")
        title = QLabel("made by Mohammed Atif", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress = QProgressBar(self)
        progress.setRange(0, 0)
        progress.setTextVisible(False)

        layout.addWidget(logo_label)
        layout.addWidget(title)
        layout.addWidget(progress)

        # Simulate loading for ~3s
        QTimer.singleShot(3000, self._finish)

    def _finish(self) -> None:
        self.loadingFinished.emit()
        self.close()

    # Compatibility with QSplashScreen.finish(window)
    def finish(self, _window) -> None:
        self.close()


