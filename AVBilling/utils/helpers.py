#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from decimal import Decimal, ROUND_HALF_UP, getcontext
import tempfile
import os


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, data: Dict[str, Any]) -> None:
    """Atomically write JSON to disk to avoid corruption on crash.

    Writes to a temporary file first, then replaces the target.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Ensure JSON serializable (convert Decimals)
    def default(o: Any):
        if isinstance(o, Decimal):
            return float(o)
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")

    content = json.dumps(data, indent=2, ensure_ascii=False, default=default)
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(content)
        # Replace atomically where possible
        os.replace(tmp_path, path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def read_text_file_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_time_str() -> str:
    return datetime.now().strftime("%H:%M:%S")


def month_key(dt_str: str) -> str:
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m")
    except Exception:
        return ""


def next_sequence(existing_ids: List[str], prefix: str, width: int = 3) -> str:
    max_num = 0
    for eid in existing_ids:
        if eid.startswith(prefix):
            try:
                num = int(eid.replace(prefix, ""))
                max_num = max(max_num, num)
            except ValueError:
                continue
    return f"{prefix}{str(max_num + 1).zfill(width)}"


def to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")

def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


