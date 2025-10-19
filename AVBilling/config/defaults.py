#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def app_paths() -> Dict[str, Path]:
    assets = PROJECT_ROOT / "assets"
    data = PROJECT_ROOT / "data"
    invoices = data / "invoices"
    backups = data / "backups"
    config_dir = PROJECT_ROOT / "config"
    return {
        "root": PROJECT_ROOT,
        "assets": assets,
        "data": data,
        "invoices": invoices,
        "backups": backups,
        "config": config_dir,
        "settings": config_dir / "settings.json",
        "customers": data / "customers.json",
        "products": data / "products.json",
        "logs": PROJECT_ROOT / "app.log",
    }


DEFAULT_SETTINGS: Dict[str, Any] = {
    "version": "1.0.0",
    "company": {
        "name": "AVBilling Demo Company",
        "address": "",
        "phone": "",
        "gst_no": "",
        "logo_path": "",
    },
    "ui": {"theme": "light"},
    "shortcuts": {
        "new_invoice": "Ctrl+N",
        "save": "Ctrl+S",
        "print": "Ctrl+P",
    },
    "invoice": {"tax_default": 5, "discount_default": 0},
}


SAMPLE_CUSTOMERS = {
    "customers": [
        {
            "customer_id": "CUST001",
            "name": "Amit Traders",
            "phone": "9876543210",
            "address": "Lucknow",
            "gst_no": "GST123",
            "total_purchases": 0,
            "total_amount": 0,
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
            "stock": 1000,
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


def ensure_file(path: Path, default_content: Dict[str, Any]) -> None:
    if not path.exists():
        path.write_text(json.dumps(default_content, indent=2), encoding="utf-8")


def ensure_initial_setup() -> None:
    paths = app_paths()
    # Ensure directories
    for key in ("assets", "data", "invoices", "backups", "config"):
        ensure_dir(paths[key])

    # Ensure settings.json
    ensure_file(paths["settings"], DEFAULT_SETTINGS)

    # Ensure customers/products
    ensure_file(paths["customers"], SAMPLE_CUSTOMERS)
    ensure_file(paths["products"], SAMPLE_PRODUCTS)

    # Ensure current FY invoices file
    fy_name = current_financial_year() + ".json"
    fy_file = paths["invoices"] / fy_name
    ensure_file(fy_file, {"invoices": []})


