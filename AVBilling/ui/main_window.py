#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QLabel,
    QFileDialog,
    QMessageBox,
)

from config.defaults import app_paths
from logic.backup_manager import BackupManager
from logic.invoice_manager import InvoiceManager
from ui.pages.dashboard import DashboardPage
from ui.pages.billing import BillingPage
from ui.pages.customers import CustomersPage
from ui.pages.products import ProductsPage
from ui.pages.reports import ReportsPage
from ui.pages.master import MasterPage
from ui.pages.gate_pass import GatePassPage
from ui.pages.settings import SettingsPage
from ui.pages.maintenance import MaintenancePage
from ui.widgets.sidebar import Sidebar
from ui.widgets.navbar import NavBar
from utils.shortcuts import register_shortcut
from utils.helpers import read_json


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AVBilling")
        self.resize(1200, 800)
        self.paths = app_paths()

        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Navbar
        navbar = NavBar(self.toggle_theme, self.show_help, self.show_about)
        root_layout.addWidget(navbar)

        # Body
        body = QWidget(self)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar = Sidebar(self.navigate_to)
        body_layout.addWidget(sidebar)

        self.stack = QStackedWidget(self)
        self.invoice_manager = InvoiceManager()

        self.dashboard_page = DashboardPage(self.invoice_manager)
        self.billing_page = BillingPage(self.invoice_manager)
        self.customers_page = CustomersPage()
        self.products_page = ProductsPage()
        self.reports_page = ReportsPage(self.invoice_manager)
        self.master_page = MasterPage(self.invoice_manager)
        self.gate_pass_page = GatePassPage(self.invoice_manager)
        self.settings_page = SettingsPage(self)
        self.maintenance_page = MaintenancePage(self)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.billing_page)
        self.stack.addWidget(self.customers_page)
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.reports_page)
        self.stack.addWidget(self.master_page)
        self.stack.addWidget(self.gate_pass_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.maintenance_page)

        body_layout.addWidget(self.stack, 1)
        root_layout.addWidget(body, 1)

        # Footer
        footer = QLabel("© 2025 AVBilling by Mohammed Atif | v1.0.0", self)
        footer.setObjectName("Footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(footer)

        self.setCentralWidget(central)

        self._nav_actions = []
        self.load_navigation_shortcuts()

    def load_navigation_shortcuts(self) -> None:
        # Clear previous actions
        for act in getattr(self, "_nav_actions", []):
            try:
                self.removeAction(act)
            except Exception:
                pass
        self._nav_actions = []
        settings = read_json(self.paths["settings"]) or {}
        default_map = {
            "F1": 0,
            "F2": 1,
            "F3": 2,
            "F4": 3,
            "F5": 4,
            "F6": 5,
            "F7": 6,
            "F8": 7,
        }
        nav_map = settings.get("navigation_shortcuts", default_map)
        for key, idx in nav_map.items():
            act = register_shortcut(self, key, lambda i=idx: self.navigate_to(int(i)))
            self._nav_actions.append(act)

    def navigate_to(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    def toggle_theme(self) -> None:
        # Simple toggle: reload styles.qss (light theme only here)
        from utils.helpers import read_text_file_safe

        styles_path = self.paths["assets"] / "styles.qss"
        qss = read_text_file_safe(styles_path)
        self.setStyleSheet(qss)

    def show_help(self) -> None:
        QMessageBox.information(self, "Help", "Use the sidebar to navigate. Billing supports Ctrl+N, Ctrl+S, Ctrl+P.")

    def show_about(self) -> None:
        QMessageBox.about(self, "About AVBilling", "AVBilling v1.0.0\nBuilt with PyQt6.")


