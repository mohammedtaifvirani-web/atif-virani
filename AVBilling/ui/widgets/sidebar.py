#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Callable, List, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy


class Sidebar(QWidget):
    def __init__(self, on_navigate: Callable[[int], None]) -> None:
        super().__init__()
        self.on_navigate = on_navigate
        self.setObjectName("Sidebar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.buttons: List[Tuple[str, int]] = [
            ("Dashboard", 0),
            ("Billing", 1),
            ("Customers", 2),
            ("Products", 3),
            ("Reports", 4),
            ("Master", 5),
            ("Gate Pass", 6),
            ("Settings", 7),
            ("Maintenance", 8),
        ]
        for label, index in self.buttons:
            btn = QPushButton(label, self)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda _, i=index: self.on_navigate(i))
            layout.addWidget(btn)
        layout.addStretch(1)


