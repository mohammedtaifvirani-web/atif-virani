#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QInputDialog

from logic.backup_manager import BackupManager
from config.defaults import app_paths, ensure_initial_setup, DEFAULT_SETTINGS
from utils.helpers import write_json
import shutil


class MaintenancePage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Maintenance")
        header.setObjectName("PageTitle")
        layout.addWidget(header)

        btn_backup = QPushButton("Create Backup (ZIP)")
        btn_backup.clicked.connect(self.create_backup)
        btn_restore = QPushButton("Restore Backup (ZIP)")
        btn_restore.clicked.connect(self.restore_backup)
        btn_factory = QPushButton("Clear All Data (Factory Reset)")
        btn_factory.clicked.connect(self.factory_reset)
        layout.addWidget(btn_backup)
        layout.addWidget(btn_restore)
        layout.addWidget(btn_factory)

        self.bm = BackupManager()

    def create_backup(self) -> None:
        ok = self._check_pin()
        if not ok:
            return
        path = self.bm.create_backup()
        QMessageBox.information(self, "Backup", f"Backup created: {path}")

    def restore_backup(self) -> None:
        ok = self._check_pin()
        if not ok:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Select Backup", "", "Zip Files (*.zip)")
        if not path:
            return
        self.bm.restore_backup(Path(path))
        QMessageBox.information(self, "Restore", "Backup restored. Please restart the app.")

    def _check_pin(self) -> bool:
        pin, ok = QInputDialog.getText(self, "Developer PIN", "Enter PIN:")
        return ok and pin == "1234"

    def factory_reset(self) -> None:
        if not self._check_pin():
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Reset",
            "This will delete ALL data, invoices, backups, and settings, and reset the app. Continue?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        paths = app_paths()
        # Delete data and backups folders safely
        try:
            for key in ("data", "backups"):
                p = paths[key]
                if p.exists():
                    shutil.rmtree(p, ignore_errors=True)
            # Reset settings.json to defaults
            write_json(paths["settings"], DEFAULT_SETTINGS)
            # Recreate base structure and sample data
            ensure_initial_setup()
        except Exception as e:
            QMessageBox.critical(self, "Reset Failed", str(e))
            return
        QMessageBox.information(self, "Reset Complete", "All data cleared. Please restart the app.")


