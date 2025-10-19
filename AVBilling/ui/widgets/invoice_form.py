#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class InvoiceForm(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Invoice form component"))


