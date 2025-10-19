#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional
import threading

from config.defaults import app_paths, current_financial_year
from logic.billing_calculator import calculate_invoice_totals
from utils.helpers import read_json, write_json
from utils.validators import validate_invoice


class InvoiceManager:
    def __init__(self) -> None:
        self.paths = app_paths()
        self.fy = current_financial_year()
        self.path = self.paths["invoices"] / f"{self.fy}.json"
        data = read_json(self.path)
        self._data = data if data else {"invoices": []}
        self._gate_pass_state: Dict[str, int] = {}  # date -> last number
        self._lock = threading.RLock()

    def _save(self) -> None:
        write_json(self.path, self._data)

    def list(self) -> List[Dict]:
        return list(self._data.get("invoices", []))

    def _next_invoice_number(self) -> str:
        # Invoice numbering: FY/INV/0001
        prefix = f"{self.fy}/INV/"
        max_num = 0
        for inv in self._data.get("invoices", []):
            inv_no = inv.get("invoice_no", "")
            if inv_no.startswith(prefix):
                try:
                    num = int(inv_no.split("/")[-1])
                    max_num = max(max_num, num)
                except Exception:
                    continue
        return f"{prefix}{str(max_num + 1).zfill(4)}"

    def _next_gate_pass_number(self, dt_str: Optional[str] = None) -> str:
        with self._lock:
            # Daily reset: GP-YYYYMMDD-001
            if not dt_str:
                dt_str = date.today().strftime("%Y%m%d")
            last = self._gate_pass_state.get(dt_str, 0) + 1
            self._gate_pass_state[dt_str] = last
            return f"GP-{dt_str}-{str(last).zfill(3)}"

    def create_invoice(self, payload: Dict) -> Optional[Dict]:
        # Auto number if missing
        payload = dict(payload)
        payload.setdefault("date", date.today().strftime("%Y-%m-%d"))
        with self._lock:
            if not payload.get("invoice_no"):
                payload["invoice_no"] = self._next_invoice_number()
            if not payload.get("gate_pass_no"):
                payload["gate_pass_no"] = self._next_gate_pass_number(payload.get("date").replace("-", ""))

        # Calculate totals
        totals = calculate_invoice_totals(payload.get("items", []))
        payload["subtotal"] = totals["subtotal"]
        payload["discount_total"] = totals["discount"]
        payload["gst_total"] = totals["gst"]
        payload["grand_total"] = totals["total"]
        payload.setdefault("status", "final")  # mark as finalized when saved

        if not validate_invoice(payload):
            return None

        with self._lock:
            self._data.setdefault("invoices", []).append(payload)
            self._save()
        return payload

    def update_status(self, invoice_no: str, status: str) -> bool:
        with self._lock:
            for inv in self._data.get("invoices", []):
                if inv.get("invoice_no") == invoice_no:
                    inv["status"] = status
                    self._save()
                    return True
        return False
