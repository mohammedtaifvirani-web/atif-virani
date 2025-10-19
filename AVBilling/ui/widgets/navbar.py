#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

class NavBar(QWidget):
    def __init__(self, help_callback, about_callback, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("NavBar")
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        title = QLabel("AVBilling")
        title.setObjectName("NavTitle")
        layout.addWidget(title)

        layout.addStretch()

        # Action Buttons
        btn_help = QPushButton("Help")
        btn_help.setObjectName("NavButton")
        btn_help.clicked.connect(help_callback)
        layout.addWidget(btn_help)

        btn_about = QPushButton("About")
        btn_about.setObjectName("NavButton")
        btn_about.clicked.connect(about_callback)
        layout.addWidget(btn_about)
