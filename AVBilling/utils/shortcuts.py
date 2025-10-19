#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Callable, Dict

from PyQt6.QtGui import QKeySequence, QAction
from PyQt6.QtWidgets import QWidget


def register_shortcut(widget: QWidget, sequence: str, handler: Callable[[], None], text: str = "") -> QAction:
    action = QAction(text or sequence, widget)
    action.setShortcut(QKeySequence(sequence))
    action.triggered.connect(handler)
    widget.addAction(action)
    return action


def register_shortcuts(widget: QWidget, mapping: Dict[str, Callable[[], None]]) -> None:
    for seq, func in mapping.items():
        register_shortcut(widget, seq, func)


