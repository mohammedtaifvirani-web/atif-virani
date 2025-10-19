#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from collections import Counter
from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QGroupBox, QGridLayout, QPushButton
from typing import Optional
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

from logic.invoice_manager import InvoiceManager
from logic.report_generator import ReportGenerator


class DashboardPage(QWidget):
    def __init__(self, invoice_manager: InvoiceManager) -> None:
        super().__init__()
        self.im = invoice_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = QLabel("Dashboard")
        header.setObjectName("PageTitle")
        layout.addWidget(header)

        stats_box = QGroupBox("Overview")
        stats_layout = QGridLayout(stats_box)
        self._stats_labels = {
            "revenue": QLabel(),
            "invoices": QLabel(),
            "customers": QLabel(),
            "top": QLabel(),
        }
        stats_layout.addWidget(self._stats_labels["revenue"], 0, 0)
        stats_layout.addWidget(self._stats_labels["invoices"], 0, 1)
        stats_layout.addWidget(self._stats_labels["customers"], 1, 0)
        stats_layout.addWidget(self._stats_labels["top"], 1, 1)
        # Ensure attribute exists before first refresh
        self.chart_canvas = None
        self.refresh()
        layout.addWidget(stats_box)

        # Quick navigation buttons
        quick = QGroupBox("Quick Access")
        ql = QHBoxLayout(quick)
        for label, idx in [("Billing", 1), ("Customers", 2), ("Products", 3), ("Reports", 4), ("Master", 5), ("Gate Pass", 6), ("Settings", 7), ("Maintenance", 8)]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, i=idx: self.window().navigate_to(i))
            ql.addWidget(b)
        layout.addWidget(quick)

        # Placeholder for chart area (PyQtGraph or matplotlib optional setup)
        # Monthly sales chart (optional if matplotlib installed)
        self.chart_canvas: Optional[FigureCanvas] = None
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(5, 3))
            self.chart_canvas = FigureCanvas(self.figure)
            layout.addWidget(self.chart_canvas, 1)
        else:
            self.sales_label = QLabel("Install matplotlib to enable charts.")
            self.sales_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.sales_label, 1)

    def _compute_stats(self) -> Dict:
        invoices = self.im.list()
        revenue = sum(float(i.get("grand_total", 0)) for i in invoices)
        customers = {i.get("customer_id") for i in invoices if i.get("customer_id")}
        product_counter = Counter()
        for inv in invoices:
            for it in inv.get("items", []):
                product_counter[it.get("product_name", it.get("product_code", "Unknown"))] += float(
                    it.get("quantity", 0)
                )
        top_product = product_counter.most_common(1)[0][0] if product_counter else "N/A"
        return {
            "revenue": revenue,
            "invoices": len(invoices),
            "customers": len(customers),
            "top_product": top_product,
        }

    def refresh(self) -> None:
        s = self._compute_stats()
        self._stats_labels["revenue"].setText(f"Total Revenue: {s['revenue']:.2f}")
        self._stats_labels["invoices"].setText(f"Total Invoices: {s['invoices']}")
        self._stats_labels["customers"].setText(f"Total Customers: {s['customers']}")
        self._stats_labels["top"].setText(f"Top Product: {s['top_product']}")
        # Update chart
        if self.chart_canvas is not None:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            monthly = {}
            for inv in self.im.list():
                date_str = inv.get("date", "")
                if len(date_str) >= 7:
                    key = date_str[:7]
                    monthly[key] = monthly.get(key, 0.0) + float(inv.get("grand_total", 0))
            labels = sorted(monthly.keys())
            values = [monthly[k] for k in labels]
            ax.bar(labels, values, color="#3498DB")
            ax.set_title("Monthly Revenue")
            ax.set_ylabel("Amount")
            ax.set_xlabel("Month")
            ax.tick_params(axis='x', rotation=45)
            self.figure.tight_layout()
            self.chart_canvas.draw_idle()


