#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QHBoxLayout,
    QComboBox,
)

from logic.invoice_manager import InvoiceManager
from logic.report_generator import ReportGenerator
from utils.helpers_thread import run_in_thread


class ReportsPage(QWidget):
    def __init__(self, invoice_manager: InvoiceManager) -> None:
        super().__init__()
        self.im = invoice_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Reports")
        header.setObjectName("PageTitle")
        layout.addWidget(header)

        # Month filter
        top = QHBoxLayout()
        top.addWidget(QLabel("Month:"))
        self.cb_month = QComboBox()
        self.cb_month.addItem("All")
        self.cb_month.addItems([f"{m:02d}" for m in range(1, 13)])
        top.addWidget(self.cb_month)
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.refresh)
        top.addWidget(btn_refresh)
        layout.addLayout(top)

        btn_export_inv = QPushButton("Export Invoices to Excel")
        btn_export_inv.clicked.connect(self.export_invoices)
        btn_export_sales = QPushButton("Export Sales to Excel")
        btn_export_sales.clicked.connect(self.export_sales)
        btn_pdf_last = QPushButton("Export Last Invoice to PDF")
        btn_pdf_last.clicked.connect(self.export_last_pdf)
        layout.addWidget(btn_export_inv)
        layout.addWidget(btn_export_sales)
        layout.addWidget(btn_pdf_last)

        self.out = QTextEdit(); self.out.setReadOnly(True)
        layout.addWidget(self.out, 1)
        # Refresh view notice after saves
        self.out.append("Reports will include any newly saved invoices.")

    def refresh(self) -> None:
        month = self.cb_month.currentText() if self.cb_month else "All"
        invs = self.im.list()
        if month and month != "All":
            invs = [i for i in invs if (i.get("date", "")[5:7] == month)]
        self.out.clear()
        self.out.append(f"Invoices in month {month}: {len(invs)}")

    def export_invoices(self) -> None:
        invoices = self.im.list()
        rg = ReportGenerator(invoices)
        path, _ = QFileDialog.getSaveFileName(self, "Export Invoices", "invoices.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
        def job():
            rg.export_invoices_excel(path)
            return path
        def done(result):
            self.out.append(f"Exported invoices to: {result}")
        def fail(err: Exception):
            self.out.append(f"Export failed: {err}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Error", str(err))
        run_in_thread(job, done, fail)

    def export_sales(self) -> None:
        invoices = self.im.list()
        rg = ReportGenerator(invoices)
        path, _ = QFileDialog.getSaveFileName(self, "Export Sales", "sales.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
        def job():
            rg.export_sales_excel(path)
            return path
        def done(result):
            self.out.append(f"Exported sales to: {result}")
        def fail(err: Exception):
            self.out.append(f"Export failed: {err}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Error", str(err))
        run_in_thread(job, done, fail)

    def export_last_pdf(self) -> None:
        invoices = self.im.list()
        if not invoices:
            self.out.append("No invoices to export.")
            return
        last = invoices[-1]
        rg = ReportGenerator(invoices)
        path, _ = QFileDialog.getSaveFileName(self, "Export Invoice PDF", f"{last.get('invoice_no','invoice')}.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        def job():
            rg.export_invoice_pdf(last, path)
            return path
        def done(result):
            self.out.append(f"Exported PDF to: {result}")
        def fail(err: Exception):
            self.out.append(f"Export failed: {err}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Error", str(err))
        run_in_thread(job, done, fail)


