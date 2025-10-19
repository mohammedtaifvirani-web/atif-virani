#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def app_paths() -> Dict[str, Path]:
    data = PROJECT_ROOT / "data"
    return {
        "root": PROJECT_ROOT,
        "assets": PROJECT_ROOT / "assets",
        "data": data,
        "invoices": data / "invoices",
        "backups": data / "backups",
        "config": PROJECT_ROOT / "config",
        "settings": PROJECT_ROOT / "config" / "settings.json",
        "customers": data / "customers.json",
        "products": data / "products.json",
        "logs": PROJECT_ROOT / "app.log",
    }

# Default settings structure for a fresh start or reset
DEFAULT_SETTINGS: Dict[str, Any] = {
    "version": "1.0.0",
    "company": {
        "name": "AVBilling Solutions",
        "address": "123 Main Street, Anytown, India",
        "gst_number": "",
        "logo_path": "",
    },
    "invoice": {
        "template": "Detailed",
        "prefix": "INV-",
    },
    "application": {
        "theme": "Light",
    },
    "shortcuts": {
        "new_invoice": "Ctrl+N",
        "save_invoice": "Ctrl+S",
        "print_invoice": "Ctrl+P",
    },
    "navigation_shortcuts": {
        "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4",
        "F5": "F5", "F6": "F6", "F7": "F7", "F8": "F8",
    },
}

SAMPLE_CUSTOMERS = {
    "customers": [
        {
            "customer_id": "CUST001",
            "name": "Amit Traders",
            "phone": "9876543210",
            "address": "Lucknow, UP",
            "gst_number": "GSTN1234567890",
        }
    ]
}

SAMPLE_PRODUCTS = {
    "products": [
        {
            "product_code": "PROD001",
            "product_name": "Chand Besan",
            "rate_1kg": 90,
            "rate_half_kg": 50,
            "gst_rate": 5,
            "stock": 1000
        }
    ]
}

def current_financial_year() -> str:
    from datetime import date
    today = date.today()
    year = today.year
    if today.month < 4:  # FY starts in April
        return f"FY_{year-1}-{year}"
    return f"FY_{year}-{year+1}"

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def ensure_file(path: Path, default_content: Dict) -> None:
    if not path.exists() or path.stat().st_size == 0:
        try:
            with path.open("w", encoding="utf-8") as f:
                json.dump(default_content, f, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error creating default file {path}: {e}")

def ensure_initial_setup() -> None:
    paths = app_paths()
    
    # Ensure core directories exist
    for key in ("assets", "data", "invoices", "backups", "config"):
        ensure_dir(paths[key])

    # Ensure essential JSON files exist and are valid
    ensure_file(paths["settings"], DEFAULT_SETTINGS)
    ensure_file(paths["customers"], SAMPLE_CUSTOMERS)
    ensure_file(paths["products"], SAMPLE_PRODUCTS)

    # Ensure invoice file for the current financial year exists
    fy_invoice_file = paths["invoices"] / (current_financial_year() + ".json")
    ensure_file(fy_invoice_file, {"invoices": {}})
