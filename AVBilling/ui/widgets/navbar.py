#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class NavBar(QWidget):
    def __init__(self, on_toggle_theme, on_help, on_about) -> None:
        super().__init__()
        self.setObjectName("NavBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QLabel("AVBilling")
        title.setObjectName("NavTitle")
        layout.addWidget(title)
        layout.addStretch(1)

        btn_help = QPushButton("Help")
        btn_help.clicked.connect(on_help)
        btn_theme = QPushButton("Theme")
        btn_theme.clicked.connect(on_toggle_theme)
        btn_about = QPushButton("About")
        btn_about.clicked.connect(on_about)

        layout.addWidget(btn_help)
        layout.addWidget(btn_theme)
        layout.addWidget(btn_about)


