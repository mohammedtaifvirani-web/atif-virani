'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QLabel,
    QMessageBox,
)

from config.defaults import app_paths, DEFAULT_SETTINGS
from logic.invoice_manager import InvoiceManager
from logic.backup_manager import BackupManager
from ui.pages.dashboard import DashboardPage
from ui.pages.billing import BillingPage
from ui.pages.customers import CustomersPage
from ui.pages.products import ProductsPage
from ui.pages.reports import ReportsPage
from ui.pages.gate_pass import GatePassPage
from ui.pages.settings import SettingsPage
from ui.widgets.sidebar import Sidebar
from ui.widgets.navbar import NavBar
from utils.shortcuts import register_shortcut
from utils.helpers import read_json, read_text_file_safe


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.paths = app_paths()
        self.resize(1280, 800)

        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Navbar
        navbar = NavBar(self.show_help, self.show_about)
        root_layout.addWidget(navbar)

        # Body
        body = QWidget(self)
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.sidebar = Sidebar(self.navigate_to_page)
        body_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget(self)
        self.invoice_manager = InvoiceManager()

        # Initialize Pages
        self.dashboard_page = DashboardPage(self.invoice_manager, self)
        self.billing_page = BillingPage(self.invoice_manager)
        self.customers_page = CustomersPage()
        self.products_page = ProductsPage()
        self.reports_page = ReportsPage(self.invoice_manager)
        self.gate_pass_page = GatePassPage(self.invoice_manager)
        self.settings_page = SettingsPage(self)

        self.pages = {
            "dashboard": self.dashboard_page, "billing": self.billing_page,
            "customers": self.customers_page, "products": self.products_page,
            "reports": self.reports_page, "gate_pass": self.gate_pass_page,
            "settings": self.settings_page
        }
        for page in self.pages.values():
            self.stack.addWidget(page)

        body_layout.addWidget(self.stack, 1)
        root_layout.addWidget(body, 1)

        # Footer
        self.footer = QLabel(self)
        self.footer.setObjectName("Footer")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(self.footer)

        self.setCentralWidget(central)

        # Connect signals
        self.settings_page.settings_changed.connect(self.apply_settings_changes)
        self.stack.currentChanged.connect(self.on_page_changed)
        self.connect_dashboard_signals()

        self._nav_actions = []
        self.apply_settings_changes()  # Apply all settings on startup

    def connect_dashboard_signals(self):
        """Connects signals from the dashboard to main window slots."""
        self.dashboard_page.new_invoice_requested.connect(lambda: self.navigate_to_page("billing"))
        self.dashboard_page.add_customer_requested.connect(lambda: self.navigate_to_page("customers"))
        self.dashboard_page.add_product_requested.connect(lambda: self.navigate_to_page("products"))
        self.dashboard_page.view_reports_requested.connect(lambda: self.navigate_to_page("reports"))
        self.dashboard_page.backup_data_requested.connect(self.run_backup)

    def apply_settings_changes(self) -> None:
        """Reloads all settings from file and applies them across the application."""
        settings = read_json(self.paths["settings"]) or {}
        full_settings = {**DEFAULT_SETTINGS, **settings}

        self.apply_theme(full_settings.get("application", {}).get("theme", "Light"))
        self.update_window_and_footer(full_settings.get("company", {}))
        self.load_shortcuts(full_settings)

    def apply_theme(self, theme_name: str) -> None:
        """Loads and applies the specified theme stylesheet."""
        theme_file = "dark.qss" if theme_name.lower() == "dark" else "light.qss"
        qss = read_text_file_safe(self.paths["assets"] / theme_file)
        if qss:
            self.setStyleSheet(qss)
        else:
            print(f"Warning: Could not load theme file '{theme_file}'")

    def update_window_and_footer(self, company_settings: dict) -> None:
        """Updates the main window title and footer text."""
        company_name = company_settings.get("name", "AVBilling")
        self.setWindowTitle(company_name)
        version = "v1.0.0"
        footer_text = f"© {datetime.now().year} {company_name} by Mohammed Atif | {version}"
        self.footer.setText(footer_text)

    def load_shortcuts(self, settings: dict) -> None:
        """Clears and reloads all application shortcuts."""
        for act in self._nav_actions:
            self.removeAction(act)
        self._nav_actions.clear()

        page_map = {key: i for i, key in enumerate(self.pages.keys())}
        nav_shortcuts = settings.get("navigation_shortcuts", {})
        
        for f_key, page_name in [("F1", "dashboard"), ("F2", "billing"), ("F3", "customers"), ("F4", "products"), ("F5", "reports"), ("F6", "gate_pass"), ("F7", "settings")]:
            shortcut_key = nav_shortcuts.get(f_key, f_key)
            act = register_shortcut(self, shortcut_key, lambda p=page_name: self.navigate_to_page(p))
            self._nav_actions.append(act)

        if "billing" in self.pages:
            self.billing_page.update_shortcuts(settings.get("shortcuts", {}))

    def on_page_changed(self, index: int):
        """Refreshes the dashboard when it becomes the active page."""
        if self.stack.widget(index) == self.dashboard_page:
            self.dashboard_page.refresh()

    def navigate_to_page(self, page_name: str):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])
            self.sidebar.set_active(list(self.pages.keys()).index(page_name))

    def run_backup(self):
        """Creates a backup of the application data."""
        backup_manager = BackupManager()
        try:
            backup_file = backup_manager.create_backup()
            QMessageBox.information(self, "Backup Successful", f"Data successfully backed up to:
{backup_file}")
        except Exception as e:
            QMessageBox.critical(self, "Backup Failed", f"An error occurred during backup: {e}")

    def show_help(self) -> None:
        QMessageBox.information(self, "Help",
                                "Use the sidebar or function keys (F1-F7) to navigate.
"
                                "Shortcuts can be configured in the Settings page.")

    def show_about(self) -> None:
        QMessageBox.about(self, f"About {self.windowTitle()}",
                        f"{self.windowTitle()} v1.0.0
Built with Python and PyQt6.

Developed by Mohammed Atif.")
''