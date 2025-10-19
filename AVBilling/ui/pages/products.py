#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)

from logic.product_manager import ProductManager


class ProductsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.pm = ProductManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Products")
        header.setObjectName("PageTitle")
        layout.addWidget(header)

        form = QHBoxLayout()
        self.ed_code = QLineEdit(); self.ed_code.setPlaceholderText("Code")
        self.ed_name = QLineEdit(); self.ed_name.setPlaceholderText("Name")
        self.ed_rate1 = QLineEdit(); self.ed_rate1.setPlaceholderText("Rate 1kg")
        self.ed_rateh = QLineEdit(); self.ed_rateh.setPlaceholderText("Rate 0.5kg")
        self.ed_gst = QLineEdit(); self.ed_gst.setPlaceholderText("GST%")
        self.ed_stock = QLineEdit(); self.ed_stock.setPlaceholderText("Stock")
        btn_add = QPushButton("Add/Update"); btn_add.clicked.connect(self.add_update)
        btn_del = QPushButton("Delete"); btn_del.clicked.connect(self.delete)
        form.addWidget(self.ed_code); form.addWidget(self.ed_name); form.addWidget(self.ed_rate1)
        form.addWidget(self.ed_rateh); form.addWidget(self.ed_gst); form.addWidget(self.ed_stock)
        form.addWidget(btn_add); form.addWidget(btn_del)
        layout.addLayout(form)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Code", "Name", "Rate 1kg", "Rate 0.5kg", "GST%", "Stock"])
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        data = self.pm.list()
        self.table.setRowCount(0)
        for p in data:
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(p.get("product_code", "")))
            self.table.setItem(r, 1, QTableWidgetItem(p.get("product_name", "")))
            self.table.setItem(r, 2, QTableWidgetItem(str(p.get("rate_1kg", 0))))
            self.table.setItem(r, 3, QTableWidgetItem(str(p.get("rate_half_kg", 0))))
            self.table.setItem(r, 4, QTableWidgetItem(str(p.get("gst_rate", 0))))
            self.table.setItem(r, 5, QTableWidgetItem(str(p.get("stock", 0))))

    def add_update(self) -> None:
        prod = {
            "product_code": self.ed_code.text().strip(),
            "product_name": self.ed_name.text().strip(),
            "rate_1kg": float(self.ed_rate1.text() or 0),
            "rate_half_kg": float(self.ed_rateh.text() or 0),
            "gst_rate": float(self.ed_gst.text() or 0),
            "stock": float(self.ed_stock.text() or 0),
        }
        if not self.pm.add_or_update(prod):
            QMessageBox.warning(self, "Invalid", "Provide at least Code, Name, GST, Stock.")
            return
        self.refresh()

    def delete(self) -> None:
        code = self.ed_code.text().strip()
        if not code:
            return
        if self.pm.delete(code):
            self.refresh()
        else:
            QMessageBox.information(self, "Not found", "Product code not found.")


