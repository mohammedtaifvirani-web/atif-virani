#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, List, Optional

from config.defaults import app_paths
from utils.helpers import read_json, write_json
from utils.validators import validate_product


class ProductManager:
    def __init__(self) -> None:
        self.paths = app_paths()
        self.path = self.paths["products"]
        self._data = read_json(self.path) or {"products": []}

    def list(self) -> List[Dict]:
        return list(self._data.get("products", []))

    def find_by_code(self, code: str) -> Optional[Dict]:
        code_l = code.strip().lower()
        for p in self._data.get("products", []):
            if p.get("product_code", "").strip().lower() == code_l:
                return p
        return None

    def find_by_name(self, name: str) -> Optional[Dict]:
        name_l = name.strip().lower()
        for p in self._data.get("products", []):
            if p.get("product_name", "").strip().lower() == name_l:
                return p
        return None

    def add_or_update(self, product: Dict) -> bool:
        if not validate_product(product):
            return False
        existing = self.find_by_code(product["product_code"])
        if existing:
            existing.update(product)
        else:
            self._data.setdefault("products", []).append(product)
        write_json(self.path, self._data)
        return True

    def delete(self, code: str) -> bool:
        products = self._data.get("products", [])
        new_list = [p for p in products if p.get("product_code") != code]
        if len(new_list) == len(products):
            return False
        self._data["products"] = new_list
        write_json(self.path, self._data)
        return True

    # Stock handling removed as per updated requirements


