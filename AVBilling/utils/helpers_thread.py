#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Callable, Any
from PyQt6.QtCore import QObject, QThread, pyqtSignal


class Worker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)

    def __init__(self, fn: Callable[[], Any]) -> None:
        super().__init__()
        self._fn = fn

    def run(self) -> None:
        try:
            result = self._fn()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


def run_in_thread(fn: Callable[[], Any], on_done: Callable[[object], None], on_error: Callable[[Exception], None]) -> QThread:
    thread = QThread()
    worker = Worker(fn)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(on_done)
    worker.error.connect(on_error)
    # Ensure cleanup
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    worker.error.connect(thread.quit)
    worker.error.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.start()
    return thread


