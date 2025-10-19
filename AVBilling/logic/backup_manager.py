#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from config.defaults import app_paths


class BackupManager:
    def __init__(self) -> None:
        self.paths = app_paths()

    def create_backup(self) -> Path:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{ts}.zip"
        backup_path = self.paths["backups"] / backup_name
        root = self.paths["root"]
        backup_base = str(backup_path.with_suffix(""))
        # Zip entire project root to keep data/config. In a fuller app, limit to specific dirs.
        shutil.make_archive(backup_base, "zip", root_dir=root)
        return backup_path

    def restore_backup(self, zip_path: Path, dest: Path | None = None) -> None:
        if dest is None:
            dest = self.paths["root"]
        shutil.unpack_archive(str(zip_path), str(dest))


