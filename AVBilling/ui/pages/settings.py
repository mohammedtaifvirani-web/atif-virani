#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import json
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QFormLayout,
    QGroupBox,
    QComboBox,
    QHeaderView,
)
from ui.widgets.custom_widgets import KeySequenceEdit
from config.defaults import app_paths, DEFAULT_SETTINGS
from utils.helpers import read_json, write_json

class SettingsPage(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.paths = app_paths()
        self.settings_path = self.paths["settings"]
        self.data = {}

        self.setObjectName("SettingsPage")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Header
        header = QLabel("Settings")
        header.setObjectName("PageTitle")
        main_layout.addWidget(header)

        # Tab widget for organization
        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.create_company_tab()
        self.create_application_tab()
        self.create_shortcuts_tab()

        # Action buttons (Save, Reset)
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.btn_reset = QPushButton("Reset to Defaults")
        self.btn_reset.clicked.connect(self.reset_settings)
        action_layout.addWidget(self.btn_reset)
        
        self.btn_save = QPushButton("Save All Settings")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.clicked.connect(self.save_settings)
        action_layout.addWidget(self.btn_save)
        
        main_layout.addLayout(action_layout)

        self.load_settings()

    def create_company_tab(self):
        """Creates the 'Company & Invoice' tab."""
        tab_company = QWidget()
        layout = QVBoxLayout(tab_company)
        layout.setSpacing(12)

        # Company Profile Group
        grp_company = QGroupBox("Company Profile")
        form_layout = QFormLayout(grp_company)
        self.ed_company_name = QLineEdit()
        self.ed_company_address = QLineEdit()
        self.ed_company_gst = QLineEdit()
        self.ed_company_logo = QLineEdit()
        btn_browse_logo = QPushButton("Browse...")
        btn_browse_logo.clicked.connect(self.browse_logo)
        
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.ed_company_logo)
        logo_layout.addWidget(btn_browse_logo)

        form_layout.addRow("Company Name:", self.ed_company_name)
        form_layout.addRow("Address:", self.ed_company_address)
        form_layout.addRow("GST Number:", self.ed_company_gst)
        form_layout.addRow("Logo Path:", logo_layout)
        
        # Invoice Settings Group
        grp_invoice = QGroupBox("Invoice Configuration")
        form_layout_invoice = QFormLayout(grp_invoice)
        self.combo_invoice_template = QComboBox()
        self.combo_invoice_template.addItems(["Detailed", "Simple", "Compact"])
        self.ed_invoice_prefix = QLineEdit()
        
        form_layout_invoice.addRow("Invoice Template:", self.combo_invoice_template)
        form_layout_invoice.addRow("Invoice Prefix (e.g., INV-):", self.ed_invoice_prefix)

        layout.addWidget(grp_company)
        layout.addWidget(grp_invoice)
        layout.addStretch()
        self.tabs.addTab(tab_company, "Company & Invoice")

    def create_application_tab(self):
        """Creates the 'Application' tab."""
        tab_application = QWidget()
        layout = QFormLayout(tab_application)
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Light", "Dark"])
        
        layout.addRow("Theme:", self.combo_theme)
        
        self.tabs.addTab(tab_application, "Application")

    def create_shortcuts_tab(self):
        """Creates the 'Shortcuts' tab."""
        tab_shortcuts = QWidget()
        layout = QVBoxLayout(tab_shortcuts)
        layout.setSpacing(12)

        # Action Shortcuts
        grp_actions = QGroupBox("Action Shortcuts")
        layout_actions = QVBoxLayout(grp_actions)
        self.tbl_action_shortcuts = QTableWidget(0, 2)
        self.tbl_action_shortcuts.setHorizontalHeaderLabels(["Action", "Shortcut"])
        self.tbl_action_shortcuts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_action_shortcuts.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout_actions.addWidget(self.tbl_action_shortcuts)
        
        # Navigation Shortcuts
        grp_nav = QGroupBox("Navigation Shortcuts")
        layout_nav = QVBoxLayout(grp_nav)
        self.tbl_nav_shortcuts = QTableWidget(0, 2)
        self.tbl_nav_shortcuts.setHorizontalHeaderLabels(["Page", "Shortcut"])
        self.tbl_nav_shortcuts.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tbl_nav_shortcuts.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout_nav.addWidget(self.tbl_nav_shortcuts)

        layout.addWidget(grp_actions)
        layout.addWidget(grp_nav)
        self.tabs.addTab(tab_shortcuts, "Shortcuts")

    def load_settings(self):
        """Loads settings from the JSON file and populates the UI."""
        self.data = read_json(self.settings_path)
        if not isinstance(self.data, dict):
            self.data = {}

        # Merge with defaults to ensure all keys are present
        temp_data = DEFAULT_SETTINGS.copy()
        temp_data.update(self.data)
        self.data = temp_data
        
        # Company & Invoice Tab
        company_data = self.data.get("company", {})
        self.ed_company_name.setText(company_data.get("name", ""))
        self.ed_company_address.setText(company_data.get("address", ""))
        self.ed_company_gst.setText(company_data.get("gst_number", ""))
        self.ed_company_logo.setText(company_data.get("logo_path", ""))
        
        invoice_data = self.data.get("invoice", {})
        self.combo_invoice_template.setCurrentText(invoice_data.get("template", "Detailed"))
        self.ed_invoice_prefix.setText(invoice_data.get("prefix", "INV-"))

        # Application Tab
        app_data = self.data.get("application", {})
        self.combo_theme.setCurrentText(app_data.get("theme", "Light"))
        
        # Shortcuts Tab
        self.load_shortcuts_table(self.tbl_action_shortcuts, self.data.get("shortcuts", {}))
        self.load_shortcuts_table(self.tbl_nav_shortcuts, self.data.get("navigation_shortcuts", {}), is_nav=True)

    def load_shortcuts_table(self, table: QTableWidget, shortcuts: dict, is_nav=False):
        table.setRowCount(0)
        
        # Define the order and labels for navigation shortcuts
        nav_pages = {
            "F1": "Dashboard", "F2": "Billing", "F3": "Customers", "F4": "Products",
            "F5": "Reports", "F6": "Master", "F7": "Gate Pass", "F8": "Settings"
        }
        
        if is_nav:
            # We iterate through the defined order to ensure consistency
            for key, page_name in nav_pages.items():
                shortcut_key = shortcuts.get(key, key) # Use default F-key if not in settings
                row_position = table.rowCount()
                table.insertRow(row_position)
                
                page_item = QTableWidgetItem(page_name)
                page_item.setFlags(page_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row_position, 0, page_item)
                
                editor = KeySequenceEdit()
                editor.setText(shortcut_key)
                table.setCellWidget(row_position, 1, editor)
        else:
             for action, sequence in shortcuts.items():
                row_position = table.rowCount()
                table.insertRow(row_position)
                
                action_item = QTableWidgetItem(action.replace("_", " ").title())
                action_item.setData(Qt.ItemDataRole.UserRole, action) # Store original action name
                action_item.setFlags(action_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row_position, 0, action_item)

                editor = KeySequenceEdit()
                editor.setText(sequence)
                table.setCellWidget(row_position, 1, editor)

    def save_settings(self):
        """Saves all settings from the UI back to the JSON file."""
        try:
            # Company & Invoice Tab
            self.data["company"] = {
                "name": self.ed_company_name.text().strip(),
                "address": self.ed_company_address.text().strip(),
                "gst_number": self.ed_company_gst.text().strip(),
                "logo_path": self.ed_company_logo.text().strip(),
            }
            self.data["invoice"] = {
                "template": self.combo_invoice_template.currentText(),
                "prefix": self.ed_invoice_prefix.text().strip(),
            }
            
            # Application Tab
            self.data["application"] = {
                "theme": self.combo_theme.currentText(),
            }

            # Shortcuts Tab
            self.data["shortcuts"] = self.save_shortcuts_from_table(self.tbl_action_shortcuts)
            self.data["navigation_shortcuts"] = self.save_shortcuts_from_table(self.tbl_nav_shortcuts, is_nav=True)

            # Write to file
            write_json(self.settings_path, self.data)
            
            QMessageBox.information(self, "Success", "Settings have been saved successfully.")
            
            # Emit signal to notify main window
            self.settings_changed.emit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def save_shortcuts_from_table(self, table: QTableWidget, is_nav=False) -> dict:
        shortcuts = {}
        nav_pages = {
            "Dashboard": "F1", "Billing": "F2", "Customers": "F3", "Products": "F4",
            "Reports": "F5", "Master": "F6", "Gate Pass": "F7", "Settings": "F8"
        }
        
        for r in range(table.rowCount()):
            editor = table.cellWidget(r, 1)
            sequence = editor.text().strip() if isinstance(editor, KeySequenceEdit) else ""
            
            if is_nav:
                page_name = table.item(r, 0).text()
                default_key = nav_pages.get(page_name, "")
                shortcuts[default_key] = sequence
            else:
                action = table.item(r, 0).data(Qt.ItemDataRole.UserRole)
                shortcuts[action] = sequence
                
        return shortcuts

    def reset_settings(self):
        """Resets all settings to their default values."""
        reply = QMessageBox.warning(self, "Reset Settings",
                                     "Are you sure you want to reset all settings to their defaults? This action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data = DEFAULT_SETTINGS.copy()
            write_json(self.settings_path, self.data)
            self.load_settings()
            QMessageBox.information(self, "Success", "Settings have been reset to defaults.")
            self.settings_changed.emit()

    def browse_logo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.ed_company_logo.setText(path)

