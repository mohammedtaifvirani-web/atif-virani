#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, List, Optional

from config.defaults import app_paths
from utils.helpers import read_json, write_json
from utils.validators import validate_customer


class CustomerManager:
    def __init__(self) -> None:
        self.paths = app_paths()
        self.path = self.paths["customers"]
        self._data = read_json(self.path) or {"customers": []}

    def list(self) -> List[Dict]:
        return list(self._data.get("customers", []))

    def find_by_id(self, customer_id: str) -> Optional[Dict]:
        for c in self._data.get("customers", []):
            if c.get("customer_id") == customer_id:
                return c
        return None

    def find_by_name(self, name: str) -> Optional[Dict]:
        name_l = name.strip().lower()
        for c in self._data.get("customers", []):
            if c.get("name", "").strip().lower() == name_l:
                return c
        return None

    def add_or_update(self, customer: Dict) -> bool:
        if not validate_customer(customer):
            return False
        existing = self.find_by_id(customer["customer_id"])
        if existing:
            existing.update(customer)
        else:
            self._data.setdefault("customers", []).append(customer)
        write_json(self.path, self._data)
        return True

    def delete(self, customer_id: str) -> bool:
        customers = self._data.get("customers", [])
        new_list = [c for c in customers if c.get("customer_id") != customer_id]
        if len(new_list) == len(customers):
            return False
        self._data["customers"] = new_list
        write_json(self.path, self._data)
        return True

    def update_totals_from_invoices(self, invoices: List[Dict]) -> None:
        totals = {}
        for inv in invoices:
            cid = inv.get("customer_id")
            if not cid:
                continue
            totals.setdefault(cid, {"purchases": 0, "amount": 0.0})
            totals[cid]["purchases"] += 1
            totals[cid]["amount"] += float(inv.get("grand_total", 0))

        for c in self._data.get("customers", []):
            t = totals.get(c.get("customer_id"), {"purchases": 0, "amount": 0.0})
            c["total_purchases"] = t["purchases"]
            c["total_amount"] = round(t["amount"], 2)
        write_json(self.path, self._data)


