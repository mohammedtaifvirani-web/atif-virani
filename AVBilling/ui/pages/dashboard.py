#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from datetime import datetime, timedelta
from collections import Counter
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QGridLayout, QPushButton,
    QComboBox, QFrame
)
from typing import Optional

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from logic.invoice_manager import InvoiceManager

class DashboardPage(QWidget):
    # Signals for quick actions that MainWindow will connect to
    new_invoice_requested = pyqtSignal()
    add_customer_requested = pyqtSignal()
    add_product_requested = pyqtSignal()
    view_reports_requested = pyqtSignal()
    backup_data_requested = pyqtSignal()

    def __init__(self, invoice_manager: InvoiceManager, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.im = invoice_manager
        
        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # --- Header ---
        header = QLabel("Dashboard")
        header.setObjectName("PageTitle")
        main_layout.addWidget(header)

        # --- Top Section (Summary & Quick Actions) ---
        top_layout = QHBoxLayout()
        
        # Today's Summary
        summary_group = QGroupBox("Today's Summary")
        summary_grid = QGridLayout(summary_group)
        self._summary_labels = {
            "invoices": self._create_summary_widget("Invoices", "0"),
            "sales": self._create_summary_widget("Total Sales", "₹0.00"),
            "customers": self._create_summary_widget("New Customers", "0"),
            "products": self._create_summary_widget("Products Sold", "0"),
        }
        summary_grid.addWidget(self._summary_labels["invoices"], 0, 0)
        summary_grid.addWidget(self._summary_labels["sales"], 0, 1)
        summary_grid.addWidget(self._summary_labels["customers"], 1, 0)
        summary_grid.addWidget(self._summary_labels["products"], 1, 1)
        
        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(10)
        
        btn_new_invoice = QPushButton("New Invoice")
        btn_new_invoice.clicked.connect(self.new_invoice_requested.emit)
        
        btn_add_customer = QPushButton("Add Customer")
        btn_add_customer.clicked.connect(self.add_customer_requested.emit)
        
        btn_add_product = QPushButton("Add Product")
        btn_add_product.clicked.connect(self.add_product_requested.emit)
        
        btn_view_reports = QPushButton("View Reports")
        btn_view_reports.clicked.connect(self.view_reports_requested.emit)
        
        btn_backup = QPushButton("Backup Data")
        btn_backup.clicked.connect(self.backup_data_requested.emit)
        
        actions_layout.addWidget(btn_new_invoice)
        actions_layout.addWidget(btn_add_customer)
        actions_layout.addWidget(btn_add_product)
        actions_layout.addWidget(btn_view_reports)
        actions_layout.addWidget(btn_backup)
        actions_layout.addStretch()

        top_layout.addWidget(summary_group, 2) # Give more space to summary
        top_layout.addWidget(actions_group, 1)

        # --- Chart Section ---
        chart_group = QGroupBox("Sales Chart")
        chart_layout = QVBoxLayout(chart_group)

        # Chart controls
        chart_controls_layout = QHBoxLayout()
        chart_controls_layout.addWidget(QLabel("Time Range:"))
        self.combo_chart_range = QComboBox()
        self.combo_chart_range.addItems(["This Month", "Last 30 Days", "This Year"])
        self.combo_chart_range.currentTextChanged.connect(self.refresh)
        chart_controls_layout.addWidget(self.combo_chart_range)
        chart_controls_layout.addStretch()
        chart_layout.addLayout(chart_controls_layout)

        # Matplotlib Canvas
        self.chart_canvas = None
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(5, 3))
            self.chart_canvas = FigureCanvas(self.figure)
            chart_layout.addWidget(self.chart_canvas, 1)
        else:
            no_chart_label = QLabel("Please install 'matplotlib' to display charts.")
            no_chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_layout.addWidget(no_chart_label, 1)

        # --- Add widgets to main layout ---
        main_layout.addLayout(top_layout)
        main_layout.addWidget(chart_group, 1) # Chart takes remaining space

    def _create_summary_widget(self, title: str, initial_value: str) -> QWidget:
        widget = QFrame()
        widget.setObjectName("SummaryCard")
        layout = QVBoxLayout(widget)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("SummaryTitle")
        
        lbl_value = QLabel(initial_value)
        lbl_value.setObjectName("SummaryValue")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        widget.value_label = lbl_value # To easily access it later
        return widget

    def refresh(self) -> None:
        """Public method to refresh all dashboard data."""
        self._update_summary_stats()
        if self.chart_canvas:
            self._update_chart()

    def _update_summary_stats(self) -> None:
        today_str = datetime.now().strftime("%Y-%m-%d")
        all_invoices = self.im.list()
        
        # Filter for today's invoices
        today_invoices = [inv for inv in all_invoices if inv.get("date") == today_str]
        
        # Calculate stats
        invoices_count = len(today_invoices)
        total_sales = sum(float(inv.get("grand_total", 0)) for inv in today_invoices)
        
        # This is a simplification; need to check if customer was created today.
        # For now, count unique customers from today's invoices.
        new_customers_count = len({inv.get("customer_id") for inv in today_invoices if inv.get("customer_id")})
        
        products_sold_count = sum(len(inv.get("items", [])) for inv in today_invoices)
        
        # Update UI
        self._summary_labels["invoices"].value_label.setText(str(invoices_count))
        self._summary_labels["sales"].value_label.setText(f"₹{total_sales:,.2f}")
        self._summary_labels["customers"].value_label.setText(str(new_customers_count))
        self._summary_labels["products"].value_label.setText(str(products_sold_count))

    def _update_chart(self) -> None:
        time_range = self.combo_chart_range.currentText()
        all_invoices = self.im.list()
        now = datetime.now()

        if time_range == "This Month":
            start_date = now.replace(day=1)
            end_date = now
            date_format = mdates.DateFormatter('%d')
            title = f"Sales for {now.strftime('%B %Y')}"
        elif time_range == "Last 30 Days":
            start_date = now - timedelta(days=30)
            end_date = now
            date_format = mdates.DateFormatter('%b %d')
            title = "Sales in Last 30 Days"
        else: # This Year
            start_date = now.replace(month=1, day=1)
            end_date = now
            date_format = mdates.DateFormatter('%b')
            title = f"Sales for {now.year}"
        
        sales_data = {}
        for inv in all_invoices:
            try:
                inv_date = datetime.strptime(inv.get("date", ""), "%Y-%m-%d")
                if start_date <= inv_date <= end_date:
                    if time_range == "This Year":
                        date_key = inv_date.replace(day=1) # Group by month
                    else:
                        date_key = inv_date.date() # Group by day
                    sales_data[date_key] = sales_data.get(date_key, 0.0) + float(inv.get("grand_total", 0))
            except (ValueError, TypeError):
                continue

        # Prepare data for plotting
        sorted_dates = sorted(sales_data.keys())
        values = [sales_data[d] for d in sorted_dates]

        # Update chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if sales_data:
            ax.bar(sorted_dates, values, width=0.8, color="#3498DB")
            ax.xaxis.set_major_formatter(date_format)
            self.figure.autofmt_xdate()
        
        # Style the chart
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel("Total Sales (₹)", fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Set transparent background
        self.figure.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        # Ticks and labels color
        ax.tick_params(colors='#888888')
        ax.spines['left'].set_color('#888888')
        ax.spines['bottom'].set_color('#888888')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        self.figure.tight_layout()
        self.chart_canvas.draw()
