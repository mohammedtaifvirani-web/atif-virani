#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QKeyEvent, QKeySequence
from PyQt6.QtCore import Qt


class UpperLineEdit(QLineEdit):
    def text(self) -> str:  # type: ignore[override]
        return super().text().upper()


class KeySequenceEdit(QLineEdit):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._sequence_parts = []

    def keyPressEvent(self, event: QKeyEvent) -> None:  # capture combinations
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return
        seq = QKeySequence(event.modifiers() | event.key()).toString(QKeySequence.SequenceFormat.PortableText)
        if seq:
            self.setText(seq)
        # do not call base to avoid typing characters


