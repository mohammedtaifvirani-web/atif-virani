#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Dict


def is_non_empty(text: str) -> bool:
    return isinstance(text, str) and text.strip() != ""


def is_positive_number(value: Any) -> bool:
    try:
        return float(value) >= 0
    except Exception:
        return False


def validate_customer(data: Dict[str, Any]) -> bool:
    required = ["customer_id", "name"]
    return all(is_non_empty(str(data.get(k, ""))) for k in required)


def validate_product(data: Dict[str, Any]) -> bool:
    required = ["product_code", "product_name", "gst_rate", "stock"]
    if not all(is_non_empty(str(data.get(k, ""))) for k in ["product_code", "product_name"]):
        return False
    return is_positive_number(data.get("gst_rate", 0)) and is_positive_number(data.get("stock", 0))


def validate_invoice(data: Dict[str, Any]) -> bool:
    if not is_non_empty(data.get("invoice_no", "")):
        return False
    if not is_non_empty(data.get("date", "")):
        return False
    if not data.get("items"):
        return False
    return True


