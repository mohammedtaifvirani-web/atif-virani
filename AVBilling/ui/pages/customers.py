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

from logic.customer_manager import CustomerManager


class CustomersPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.cm = CustomerManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Customers")
        header.setObjectName("PageTitle")
        layout.addWidget(header)

        form = QHBoxLayout()
        self.ed_id = QLineEdit(); self.ed_id.setPlaceholderText("Customer ID")
        self.ed_name = QLineEdit(); self.ed_name.setPlaceholderText("Customer Name")
        self.ed_phone = QLineEdit(); self.ed_phone.setPlaceholderText("Phone")
        self.ed_address = QLineEdit(); self.ed_address.setPlaceholderText("Address")
        btn_add = QPushButton("Add/Update"); btn_add.clicked.connect(self.add_update)
        btn_del = QPushButton("Delete"); btn_del.clicked.connect(self.delete)
        form.addWidget(self.ed_id); form.addWidget(self.ed_name); form.addWidget(self.ed_phone); form.addWidget(self.ed_address)
        form.addWidget(btn_add); form.addWidget(btn_del)
        layout.addLayout(form)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Address"])
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        data = self.cm.list()
        self.table.setRowCount(0)
        for c in data:
            r = self.table.rowCount(); self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(c.get("customer_id", "")))
            self.table.setItem(r, 1, QTableWidgetItem(c.get("name", "")))
            self.table.setItem(r, 2, QTableWidgetItem(c.get("phone", "")))
            self.table.setItem(r, 3, QTableWidgetItem(c.get("address", "")))

    def add_update(self) -> None:
        cust = {
            "customer_id": self.ed_id.text().strip(),
            "name": self.ed_name.text().strip(),
            "phone": self.ed_phone.text().strip(),
            "address": self.ed_address.text().strip(),
            "total_purchases": 0,
            "total_amount": 0,
        }
        if not self.cm.add_or_update(cust):
            QMessageBox.warning(self, "Invalid", "Provide at least ID and Name.")
            return
        self.refresh()

    def delete(self) -> None:
        cid = self.ed_id.text().strip()
        if not cid:
            return
        if self.cm.delete(cid):
            self.refresh()
        else:
            QMessageBox.information(self, "Not found", "Customer ID not found.")


