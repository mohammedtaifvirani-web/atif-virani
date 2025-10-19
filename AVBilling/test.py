#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run this on a fresh machine to verify required dependencies are installed.
It will attempt to import third-party and internal modules and print results.

Usage:
  python AVBilling/test.py

Expected external dependencies:
  - PyQt6
  - reportlab
  - openpyxl
"""

from __future__ import annotations

import importlib
import sys


def check_module(name: str, import_path: str | None = None) -> bool:
    module_to_import = import_path or name
    try:
        importlib.import_module(module_to_import)
        print(f"[OK] {module_to_import}")
        return True
    except Exception as exc:
        print(f"[MISS] {module_to_import} -> {exc}")
        return False


def main() -> int:
    print("Checking external dependencies...")
    missing = []

    # External
    if not check_module("PyQt6"):
        missing.append("PyQt6")
    # Also try specific submodules commonly used
    check_module("PyQt6.QtWidgets")
    check_module("PyQt6.QtCore")
    check_module("PyQt6.QtGui")

    if not check_module("reportlab"):
        missing.append("reportlab")
    check_module("reportlab.pdfgen.canvas")

    if not check_module("openpyxl"):
        missing.append("openpyxl")
    check_module("openpyxl.workbook.workbook", "openpyxl.workbook.workbook")

    print("\nChecking internal modules...")
    # Internal modules of AVBilling
    internal_modules = [
        "config.defaults",
        "utils.helpers",
        "utils.validators",
        "utils.shortcuts",
        "logic.billing_calculator",
        "logic.customer_manager",
        "logic.product_manager",
        "logic.invoice_manager",
        "logic.report_generator",
        "logic.backup_manager",
        "ui.splash_screen",
        "ui.main_window",
        "ui.pages.dashboard",
        "ui.pages.billing",
        "ui.pages.customers",
        "ui.pages.products",
        "ui.pages.reports",
        "ui.pages.master",
        "ui.pages.gate_pass",
        "ui.pages.settings",
        "ui.pages.maintenance",
        "ui.widgets.sidebar",
        "ui.widgets.navbar",
        "ui.widgets.invoice_form",
        "ui.widgets.custom_widgets",
    ]
    # Ensure the package root is importable when running this file directly
    # Add parent directory to sys.path
    if __package__ is None:
        import pathlib

        root = pathlib.Path(__file__).resolve().parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

    for mod in internal_modules:
        check_module(mod)

    if missing:
        print("\nSome external dependencies are missing. Install with:")
        print("  pip install " + " ".join(missing))
        return 1

    print("\nAll required modules are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


