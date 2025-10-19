#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QLineEdit

from logic.invoice_manager import InvoiceManager
from logic.report_generator import ReportGenerator


class MasterPage(QWidget):
    def __init__(self, invoice_manager: InvoiceManager) -> None:
        super().__init__()
        self.im = invoice_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Master Report")
        header.setObjectName("PageTitle")
        layout.addWidget(header)
        # Filters
        filters = QHBoxLayout()
        self.ed_cust = QLineEdit(); self.ed_cust.setPlaceholderText("Customer ID")
        self.ed_prod = QLineEdit(); self.ed_prod.setPlaceholderText("Product name/code")
        self.ed_from = QLineEdit(); self.ed_from.setPlaceholderText("From (YYYY-MM-DD)")
        self.ed_to = QLineEdit(); self.ed_to.setPlaceholderText("To (YYYY-MM-DD)")
        btn_apply = QPushButton("Apply"); btn_apply.clicked.connect(self.refresh)
        btn_export = QPushButton("Export Excel"); btn_export.clicked.connect(self.export_excel)
        filters.addWidget(self.ed_cust); filters.addWidget(self.ed_prod)
        filters.addWidget(self.ed_from); filters.addWidget(self.ed_to)
        filters.addWidget(btn_apply); filters.addWidget(btn_export)
        layout.addLayout(filters)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["Date", "Invoice No", "Customer ID", "Customer Name", "Product", "Qty", "Rate", "Disc%", "Total"])
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        invs = self.im.list()
        cid = self.ed_cust.text().strip().lower()
        prod = self.ed_prod.text().strip().lower()
        dfrom = self.ed_from.text().strip()
        dto = self.ed_to.text().strip()
        def in_range(d: str) -> bool:
            if dfrom and d < dfrom: return False
            if dto and d > dto: return False
            return True
        self.table.setRowCount(0)
        for inv in invs:
            if cid and cid not in str(inv.get("customer_id", "")).lower():
                continue
            if not in_range(inv.get("date", "")):
                continue
            for it in inv.get("items", []):
                pname = it.get("product_name", it.get("product_code", ""))
                if prod and prod not in str(pname).lower():
                    continue
                r = self.table.rowCount(); self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(inv.get("date", "")))
                self.table.setItem(r, 1, QTableWidgetItem(inv.get("invoice_no", "")))
                self.table.setItem(r, 2, QTableWidgetItem(inv.get("customer_id", "")))
                self.table.setItem(r, 3, QTableWidgetItem(inv.get("customer_name", "")))
                self.table.setItem(r, 4, QTableWidgetItem(str(pname)))
                self.table.setItem(r, 5, QTableWidgetItem(str(it.get("quantity", 0))))
                self.table.setItem(r, 6, QTableWidgetItem(str(it.get("rate", 0))))
                self.table.setItem(r, 7, QTableWidgetItem(str(it.get("discount", 0))))
                self.table.setItem(r, 8, QTableWidgetItem(str(it.get("line_total", it.get("total", 0)))))

    def export_excel(self) -> None:
        invs = self.im.list()
        path, _ = QFileDialog.getSaveFileName(self, "Export Master", "master.xlsx", "Excel Files (*.xlsx)")
        if not path: return
        # Build a flat list for export using ReportGenerator's workbook
        from openpyxl import Workbook
        wb = Workbook(); ws = wb.active; ws.title = "Master"
        headers = ["Date", "Invoice No", "Customer ID", "Customer", "Product", "Qty", "Rate", "Disc%", "Total"]
        ws.append(headers)
        for inv in invs:
            for it in inv.get("items", []):
                ws.append([
                    inv.get("date", ""), inv.get("invoice_no", ""), inv.get("customer_id", ""), inv.get("customer_name", ""),
                    it.get("product_name", it.get("product_code", "")), it.get("quantity", 0), it.get("rate", 0), it.get("discount", 0), it.get("line_total", it.get("total", 0))
                ])
        wb.save(path)


