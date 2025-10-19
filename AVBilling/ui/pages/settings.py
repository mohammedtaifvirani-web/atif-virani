#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)
from ui.widgets.custom_widgets import KeySequenceEdit

from config.defaults import app_paths
from utils.helpers import read_json, write_json


class SettingsPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.paths = app_paths()
        self.settings_path = self.paths["settings"]
        self.data = read_json(self.settings_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Settings")
        header.setObjectName("PageTitle")
        layout.addWidget(header)

        self.ed_company = QLineEdit(self.data.get("company", {}).get("name", ""))
        self.ed_logo = QLineEdit(self.data.get("company", {}).get("logo_path", ""))
        btn_browse = QPushButton("Browse Logo")
        btn_browse.clicked.connect(self.browse_logo)
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save)

        layout.addWidget(QLabel("Company Name"))
        layout.addWidget(self.ed_company)
        layout.addWidget(QLabel("Logo Path"))
        layout.addWidget(self.ed_logo)
        layout.addWidget(btn_browse)
        layout.addWidget(btn_save)

        # Shortcuts editor
        layout.addWidget(QLabel("Shortcuts"))
        self.tbl_shortcuts = QTableWidget(0, 2)
        self.tbl_shortcuts.setHorizontalHeaderLabels(["Action", "Key Sequence"])
        layout.addWidget(self.tbl_shortcuts)
        self.load_shortcuts()
        btn_save_short = QPushButton("Save Shortcuts")
        btn_save_short.clicked.connect(self.save_shortcuts)
        layout.addWidget(btn_save_short)

        # Invoice template selection
        layout.addWidget(QLabel("Invoice Template (simple|detailed|compact):"))
        self.ed_template = QLineEdit(self.data.get("invoice", {}).get("template", "simple"))
        layout.addWidget(self.ed_template)

        # Navigation shortcuts mapping
        layout.addWidget(QLabel("Navigation Shortcuts (Key=Index e.g. F1=0,F2=1):"))
        self.ed_nav = QLineEdit(
            ",".join([f"{k}={v}" for k, v in self.data.get("navigation_shortcuts", {"F1": 0, "F2": 1, "F3": 2, "F4": 3, "F5": 4, "F6": 5, "F7": 6, "F8": 7}).items()])
        )
        layout.addWidget(self.ed_nav)

    def browse_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.ed_logo.setText(path)

    def save(self) -> None:
        self.data.setdefault("company", {})["name"] = self.ed_company.text().strip()
        self.data.setdefault("company", {})["logo_path"] = self.ed_logo.text().strip()
        self.data.setdefault("invoice", {})["template"] = self.ed_template.text().strip() or "simple"
        # Parse nav mapping
        mapping = {}
        for pair in self.ed_nav.text().split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                k = k.strip(); v = v.strip()
                if k:
                    try:
                        mapping[k] = int(v)
                    except Exception:
                        continue
        if mapping:
            self.data["navigation_shortcuts"] = mapping
        write_json(self.settings_path, self.data)
        QMessageBox.information(self, "Saved", "Settings updated.")
        # Ask main window to reload shortcuts if available
        try:
            from ui.main_window import MainWindow
            mw = self.window()
            if hasattr(mw, "load_navigation_shortcuts"):
                mw.load_navigation_shortcuts()
        except Exception:
            pass

    def load_shortcuts(self) -> None:
        # List all actions including navigation
        shortcuts = self.data.get("shortcuts", {
            "new_invoice": "Ctrl+N",
            "save": "Ctrl+S",
            "print": "Ctrl+P",
        })
        # Merge navigation shortcuts labeled as actions
        nav = self.data.get("navigation_shortcuts", {"F1": 0, "F2": 1, "F3": 2, "F4": 3, "F5": 4, "F6": 5, "F7": 6, "F8": 7})
        shortcuts.update({f"nav_{k}": k for k in nav.keys()})
        self.tbl_shortcuts.setRowCount(0)
        for action, seq in shortcuts.items():
            r = self.tbl_shortcuts.rowCount(); self.tbl_shortcuts.insertRow(r)
            self.tbl_shortcuts.setItem(r, 0, QTableWidgetItem(action))
            editor = KeySequenceEdit(); editor.setText(seq)
            self.tbl_shortcuts.setCellWidget(r, 1, editor)

    def save_shortcuts(self) -> None:
        actions = {}
        nav_map = {}
        for r in range(self.tbl_shortcuts.rowCount()):
            action_item = self.tbl_shortcuts.item(r, 0)
            if not action_item: continue
            action = action_item.text()
            editor = self.tbl_shortcuts.cellWidget(r, 1)
            seq = editor.text().strip() if isinstance(editor, KeySequenceEdit) else ""
            if action.startswith("nav_"):
                key = seq or action.replace("nav_", "")
                try:
                    # Map key to index from existing map if present
                    nav_map[key] = int(self.data.get("navigation_shortcuts", {}).get(key, 0))
                except Exception:
                    nav_map[key] = 0
            else:
                actions[action] = seq
        if actions:
            self.data["shortcuts"] = actions
        if nav_map:
            self.data["navigation_shortcuts"] = nav_map
        write_json(self.settings_path, self.data)
        QMessageBox.information(self, "Saved", "Shortcuts updated.")


