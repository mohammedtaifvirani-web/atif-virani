#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, List
from decimal import Decimal
from utils.helpers import to_decimal, quantize_money


def calculate_line_total(quantity: float, rate: float, discount_percent: float, gst_percent: float) -> Dict[str, float]:
    q = to_decimal(quantity)
    r = to_decimal(rate)
    d = to_decimal(discount_percent) / Decimal(100)
    g = to_decimal(gst_percent) / Decimal(100)
    subtotal = q * r
    discount_amount = subtotal * d
    taxable = subtotal - discount_amount
    if taxable < Decimal("0"):
        taxable = Decimal("0")
    gst_amount = taxable * g
    total = taxable + gst_amount
    return {
        "subtotal": float(quantize_money(subtotal)),
        "discount": float(quantize_money(discount_amount)),
        "taxable": float(quantize_money(taxable)),
        "gst": float(quantize_money(gst_amount)),
        "total": float(quantize_money(total)),
    }


def calculate_invoice_totals(items: List[Dict]) -> Dict[str, float]:
    subtotal = Decimal("0")
    discount = Decimal("0")
    gst = Decimal("0")
    total = Decimal("0")
    for item in items:
        res = calculate_line_total(
            float(item.get("quantity", 0)),
            float(item.get("rate", 0)),
            float(item.get("discount", 0)),
            float(item.get("gst", 0)),
        )
        subtotal += to_decimal(res["subtotal"])
        discount += to_decimal(res["discount"])
        gst += to_decimal(res["gst"])
        total += to_decimal(res["total"])
    return {
        "subtotal": float(quantize_money(subtotal)),
        "discount": float(quantize_money(discount)),
        "gst": float(quantize_money(gst)),
        "total": float(quantize_money(total)),
    }


