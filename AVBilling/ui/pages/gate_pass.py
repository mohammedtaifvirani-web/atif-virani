#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

from logic.invoice_manager import InvoiceManager


class GatePassPage(QWidget):
    def __init__(self, invoice_manager: InvoiceManager) -> None:
        super().__init__()
        self.im = invoice_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Gate Pass")
        header.setObjectName("PageTitle")
        layout.addWidget(header)
        info = QTextEdit()
        info.setReadOnly(True)
        info.setPlainText("Gate pass numbers auto-generate when saving invoices. Latest count: " + str(len(self.im.list())))
        layout.addWidget(info)


