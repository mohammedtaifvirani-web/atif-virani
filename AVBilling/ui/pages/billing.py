#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Dict, List
from datetime import date, datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QSpinBox,
    QDoubleSpinBox,
    QMessageBox,
)
from PyQt6.QtGui import QKeyEvent, QKeySequence, QGuiApplication
from PyQt6.QtWidgets import QCompleter, QStyledItemDelegate, QLineEdit

from config.defaults import app_paths
from logic.invoice_manager import InvoiceManager
from logic.billing_calculator import calculate_invoice_totals, calculate_line_total
from logic.product_manager import ProductManager
from logic.customer_manager import CustomerManager
from utils.shortcuts import register_shortcuts
from logic.report_generator import ReportGenerator


class BillingPage(QWidget):
    def __init__(self, invoice_manager: InvoiceManager) -> None:
        super().__init__()
        self.im = invoice_manager
        self.pm = ProductManager()
        self.cm = CustomerManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QLabel("Billing")
        header.setObjectName("PageTitle")
        layout.addWidget(header)

        # Meta row: company, date, invoice no
        meta = QHBoxLayout()
        from config.defaults import app_paths
        from utils.helpers import read_json
        settings = read_json(app_paths()["settings"]) or {}
        company_name = (settings.get("company", {}) or {}).get("name", "Company")
        self.lbl_company = QLabel(f"Company: {company_name}")
        self.ed_date = QDateEdit()
        self.ed_date.setCalendarPopup(True)
        self.ed_date.setDate(datetime.today())
        self.invoice_no = QLineEdit(); self.invoice_no.setPlaceholderText("Auto"); self.invoice_no.setReadOnly(True)
        meta.addWidget(self.lbl_company)
        meta.addStretch(1)
        meta.addWidget(QLabel("Date"))
        meta.addWidget(self.ed_date)
        meta.addWidget(QLabel("Invoice #"))
        meta.addWidget(self.invoice_no)
        layout.addLayout(meta)

        # Customer row with dropdown and readonly info
        crow = QHBoxLayout()
        self.cb_customer_id = QComboBox(); self.cb_customer_id.setEditable(True)
        self.customer_name = QLineEdit(); self.customer_name.setReadOnly(True)
        self.customer_phone = QLineEdit(); self.customer_phone.setReadOnly(True)
        self.customer_address = QLineEdit(); self.customer_address.setReadOnly(True)
        crow.addWidget(QLabel("Customer ID"))
        crow.addWidget(self.cb_customer_id)
        crow.addWidget(QLabel("Name"))
        crow.addWidget(self.customer_name)
        crow.addWidget(QLabel("Phone"))
        crow.addWidget(self.customer_phone)
        crow.addWidget(QLabel("Address"))
        crow.addWidget(self.customer_address)
        layout.addLayout(crow)

        # populate customers
        self.refresh_customers()
        self.cb_customer_id.currentTextChanged.connect(self.on_customer_changed)
        # Enter on customer ID moves to items table first cell
        if self.cb_customer_id.lineEdit() is not None:
            self.cb_customer_id.lineEdit().returnPressed.connect(self.focus_first_item_cell)

        # Items table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Code/Name", "Qty", "Rate", "Disc%", "GST%", "Total"])
        layout.addWidget(self.table)

        totals_bar = QHBoxLayout()
        self.lbl_subtotal = QLabel("Subtotal: 0.00")
        self.lbl_discount = QLabel("Discount: 0.00")
        self.lbl_gst = QLabel("GST: 0.00")
        self.lbl_total = QLabel("Grand Total: 0.00")
        btn_add_row = QPushButton("Add Row")
        btn_add_row.clicked.connect(self.add_row)
        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_invoice_dialog)
        btn_del_row = QPushButton("Delete Row")
        btn_del_row.clicked.connect(self.delete_selected_row)
        btn_print = QPushButton("Print")
        btn_print.clicked.connect(self.print_invoice)
        totals_bar.addWidget(self.lbl_subtotal)
        totals_bar.addWidget(self.lbl_discount)
        totals_bar.addWidget(self.lbl_gst)
        totals_bar.addWidget(self.lbl_total)
        totals_bar.addStretch(1)
        totals_bar.addWidget(btn_add_row)
        totals_bar.addWidget(btn_del_row)
        totals_bar.addWidget(btn_print)
        totals_bar.addWidget(btn_save)
        layout.addLayout(totals_bar)

        # Status controls
        status_bar = QHBoxLayout()
        btn_mark_final = QPushButton("Mark Final")
        btn_mark_final.clicked.connect(self.mark_final)
        btn_cancel = QPushButton("Cancel Invoice")
        btn_cancel.clicked.connect(self.cancel_invoice)
        status_bar.addWidget(btn_mark_final)
        status_bar.addWidget(btn_cancel)
        layout.addLayout(status_bar)

        self.add_row()

        register_shortcuts(
            self,
            {
                "Ctrl+N": self.new_invoice,
                "Ctrl+S": self.save_invoice,
                "Ctrl+P": self.print_invoice,
                "Ctrl+D": self.delete_selected_row,
                "Return": self.add_row,
            },
        )

        self.table.itemChanged.connect(self.recalculate)
        self.table.installEventFilter(self)

        # Invoice history section
        self.history = QTableWidget(0, 4)
        self.history.setHorizontalHeaderLabels(["Date", "Invoice No", "Customer", "Total"]) 
        self.history.itemSelectionChanged.connect(self.load_selected_invoice)
        layout.addWidget(QLabel("Past Invoices"))
        layout.addWidget(self.history)
        self.refresh_history()
        # Search by invoice number
        sr = QHBoxLayout()
        self.search_inv = QLineEdit(); self.search_inv.setPlaceholderText("Search by Invoice No")
        btn_search = QPushButton("Search"); btn_search.clicked.connect(self.search_invoice)
        sr.addWidget(self.search_inv); sr.addWidget(btn_search)
        layout.addLayout(sr)

        # Completers and delegate for product column
        self.setup_completers()
        self.table.setItemDelegateForColumn(0, ProductCompleterDelegate(self))

    def add_row(self) -> None:
        # Guard against calls after widget deletion or during teardown
        try:
            if not hasattr(self, "table") or self.table is None:
                return
            row = self.table.rowCount()
            self.table.blockSignals(True)
            self.table.insertRow(row)
            for col, val in enumerate(["", "1", "0", "0", "5", "0"]):
                if not self.table.item(row, col):
                    self.table.setItem(row, col, QTableWidgetItem(val))
                else:
                    self.table.item(row, col).setText(val)
        except RuntimeError:
            # Underlying C++ widget likely deleted; ignore late calls
            return
        finally:
            try:
                self.table.blockSignals(False)
            except Exception:
                pass

    def collect_items(self) -> List[Dict]:
        items: List[Dict] = []
        for r in range(self.table.rowCount()):
            name = self.table.item(r, 0).text() if self.table.item(r, 0) else ""
            qty = float(self.table.item(r, 1).text() or 0) if self.table.item(r, 1) else 0.0
            rate = float(self.table.item(r, 2).text() or 0) if self.table.item(r, 2) else 0.0
            disc = float(self.table.item(r, 3).text() or 0) if self.table.item(r, 3) else 0.0
            gst = float(self.table.item(r, 4).text() or 0) if self.table.item(r, 4) else 0.0
            # Resolve product but show rate only after quantity confirmed
            if name:
                p = self.pm.find_by_code(name) or self.pm.find_by_name(name)
                if p:
                    # CP1/CP2 logic: choose packet rate based on token
                    token = name.strip().lower()
                    use_half = token in ("cp2", "cp 2", "1/2", "half", "0.5") or "1/2" in token
                    display_name = p.get("product_name", "") + (" 1/2kg" if use_half else " 1kg")
                    self.table.setItem(r, 0, QTableWidgetItem(display_name))
                    if not self.table.item(r, 4) or (self.table.item(r, 4).text() or "").strip() in ("", "0"):
                        self.table.setItem(r, 4, QTableWidgetItem(str(p.get("gst_rate", 0))))
                        gst = float(p.get("gst_rate", 0))
            comp = calculate_line_total(qty, rate, disc, gst)
            items.append(
                {
                    "product_name": name,
                    "quantity": qty,
                    "rate": rate,
                    "discount": disc,
                    "gst": gst,
                    "line_total": comp["total"],
                    "gst_amount": comp["gst"],
                }
            )
            if not self.table.item(r, 5):
                self.table.setItem(r, 5, QTableWidgetItem(f"{comp['total']:.2f}"))
            else:
                self.table.item(r, 5).setText(f"{comp['total']:.2f}")
        return items

    def recalculate(self) -> None:
        if not hasattr(self, "table") or self.table is None:
            return
        try:
            items = self.collect_items()
        except RuntimeError:
            return
        totals = calculate_invoice_totals(items)
        self.lbl_subtotal.setText(f"Subtotal: {totals['subtotal']:.2f}")
        self.lbl_discount.setText(f"Discount: {totals['discount']:.2f}")
        self.lbl_gst.setText(f"GST: {totals['gst']:.2f}")
        self.lbl_total.setText(f"Grand Total: {totals['total']:.2f}")

    def closeEvent(self, event):
        try:
            if hasattr(self, "table") and self.table is not None:
                self.table.blockSignals(True)
                try:
                    self.table.itemChanged.disconnect()
                except Exception:
                    pass
                try:
                    self.table.cellChanged.disconnect()
                except Exception:
                    pass
        except Exception:
            pass
        super().closeEvent(event)

    def new_invoice(self) -> None:
        self.table.setRowCount(0)
        self.add_row()
        self.customer_name.clear()
        self.cb_customer_id.setCurrentIndex(-1)
        self.customer_phone.clear()
        self.customer_address.clear()
        self.invoice_no.clear()
        self.recalculate()

    def delete_selected_row(self) -> None:
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)
            self.recalculate()

    def save_invoice(self) -> None:
        items = self.collect_items()
        payload = {
            "invoice_no": self.invoice_no.text().strip() or None,
            "customer_name": self.customer_name.text().strip(),
            "customer_id": self.cb_customer_id.currentText().strip(),
            "items": items,
            "date": self.ed_date.date().toString("yyyy-MM-dd"),
            "template": self._current_template(),
        }
        inv = self.im.create_invoice(payload)
        if not inv:
            QMessageBox.warning(self, "Invalid", "Please complete invoice details and try again.")
            return
        # Auto stock adjust
        for it in items:
            name = it.get("product_name", "")
            product = self.pm.find_by_name(name)
            if product:
                self.pm.adjust_stock(product["product_code"], it.get("quantity", 0))
        # Update totals for customers
        from logic.customer_manager import CustomerManager

        cm = CustomerManager()
        cm.update_totals_from_invoices(self.im.list())
        self.invoice_no.setText(inv["invoice_no"])
        self.refresh_history()
        # Reset form for next invoice
        self.new_invoice()
        QMessageBox.information(self, "Saved", f"Invoice {inv['invoice_no']} saved.")

    def mark_final(self) -> None:
        inv_no = self.invoice_no.text().strip()
        if not inv_no:
            QMessageBox.information(self, "Info", "Save the invoice first.")
            return
        self.im.update_status(inv_no, "final")
        QMessageBox.information(self, "Finalized", f"Invoice {inv_no} marked as final.")
        # Lock UI immediately
        self._set_editable(False)

    def cancel_invoice(self) -> None:
        inv_no = self.invoice_no.text().strip()
        if not inv_no:
            QMessageBox.information(self, "Info", "Save the invoice first.")
            return
        self.im.update_status(inv_no, "cancelled")
        QMessageBox.information(self, "Cancelled", f"Invoice {inv_no} cancelled.")
        self._set_editable(False)

    def _set_editable(self, editable: bool) -> None:
        flag_edit = Qt.ItemFlag.ItemIsEditable if editable else Qt.ItemFlag(0)
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                it = self.table.item(r, c)
                if it:
                    flags = it.flags()
                    if editable:
                        it.setFlags(flags | Qt.ItemFlag.ItemIsEditable)
                    else:
                        it.setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)

    def save_invoice_dialog(self) -> None:
        # Present choices: Save Only, Save and Print, Cancel
        m = QMessageBox(self)
        m.setWindowTitle("Save Invoice")
        m.setText("Choose an action")
        save_only = m.addButton("Save Only", QMessageBox.ButtonRole.AcceptRole)
        save_print = m.addButton("Save and Print", QMessageBox.ButtonRole.AcceptRole)
        m.addButton(QMessageBox.StandardButton.Cancel)
        m.exec()
        if m.clickedButton() == save_only:
            self.save_invoice()
        elif m.clickedButton() == save_print:
            self.save_invoice()
            self.print_invoice()

    def print_invoice(self) -> None:
        # Generate a PDF for the current invoice data without saving
        items = self.collect_items()
        # Pull company for PDF header
        from config.defaults import app_paths
        from utils.helpers import read_json
        company_name = (read_json(app_paths()["settings"]).get("company", {}) or {}).get("name", "")
        payload = {
            "invoice_no": self.invoice_no.text().strip() or "Preview",
            "customer_name": self.customer_name.text().strip(),
            "customer_id": self.cb_customer_id.currentText().strip(),
            "items": items,
            "date": self.ed_date.date().toString("yyyy-MM-dd"),
            "template": self._current_template(),
            "company": company_name,
        }
        totals = calculate_invoice_totals(items)
        payload.update(
            {
                "subtotal": totals["subtotal"],
                "discount_total": totals["discount"],
                "gst_total": totals["gst"],
                "grand_total": totals["total"],
            }
        )
        from PyQt6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(self, "Export Invoice PDF", f"{payload['invoice_no']}.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        rg = ReportGenerator([])
        rg.export_invoice_pdf(payload, path)
        QMessageBox.information(self, "PDF", f"Saved PDF to: {path}")

    def refresh_customers(self) -> None:
        self.cb_customer_id.blockSignals(True)
        self.cb_customer_id.clear()
        for c in self.cm.list():
            self.cb_customer_id.addItem(c.get("customer_id", ""))
        self.cb_customer_id.setCurrentIndex(-1)
        self.cb_customer_id.blockSignals(False)

    def on_customer_changed(self, cid: str) -> None:
        c = self.cm.find_by_id(cid)
        if c:
            self.customer_name.setText(c.get("name", ""))
            self.customer_phone.setText(c.get("phone", ""))
            self.customer_address.setText(c.get("address", ""))
        else:
            self.customer_name.clear(); self.customer_phone.clear(); self.customer_address.clear()

    def focus_first_item_cell(self) -> None:
        if not hasattr(self, "table") or self.table is None:
            return
        if self.table.rowCount() == 0:
            self.add_row()
        if self.table.rowCount() > 0:
            self.table.setCurrentCell(0, 0)
            it = self.table.item(0, 0)
            if it:
                self.table.editItem(it)

    def refresh_history(self) -> None:
        invs = self.im.list()
        self.history.setRowCount(0)
        for inv in invs:
            r = self.history.rowCount(); self.history.insertRow(r)
            self.history.setItem(r, 0, QTableWidgetItem(inv.get("date", "")))
            self.history.setItem(r, 1, QTableWidgetItem(inv.get("invoice_no", "")))
            self.history.setItem(r, 2, QTableWidgetItem(inv.get("customer_name", "")))
            self.history.setItem(r, 3, QTableWidgetItem(f"{float(inv.get('grand_total', 0)):.2f}"))

    def search_invoice(self) -> None:
        key = self.search_inv.text().strip().lower()
        if not key:
            self.refresh_history(); return
        invs = [i for i in self.im.list() if key in str(i.get("invoice_no", "")).lower()]
        self.history.setRowCount(0)
        for inv in invs:
            r = self.history.rowCount(); self.history.insertRow(r)
            self.history.setItem(r, 0, QTableWidgetItem(inv.get("date", "")))
            self.history.setItem(r, 1, QTableWidgetItem(inv.get("invoice_no", "")))
            self.history.setItem(r, 2, QTableWidgetItem(inv.get("customer_name", "")))
            self.history.setItem(r, 3, QTableWidgetItem(f"{float(inv.get('grand_total', 0)):.2f}"))

    def load_selected_invoice(self) -> None:
        rows = self.history.selectionModel().selectedRows()
        if not rows:
            return
        r = rows[0].row()
        inv_no = self.history.item(r, 1).text()
        # find invoice
        inv = next((i for i in self.im.list() if i.get("invoice_no") == inv_no), None)
        if not inv:
            return
        # populate
        self.cb_customer_id.setCurrentText(inv.get("customer_id", ""))
        self.customer_name.setText(inv.get("customer_name", ""))
        try:
            dt = datetime.strptime(inv.get("date", ""), "%Y-%m-%d")
            self.ed_date.setDate(dt)
        except Exception:
            pass
        self.invoice_no.setText(inv.get("invoice_no", ""))
        self.table.setRowCount(0)
        for it in inv.get("items", []):
            self.add_row()
            r2 = self.table.rowCount() - 1
            self.table.item(r2, 0).setText(str(it.get("product_name", "")))
            self.table.item(r2, 1).setText(str(it.get("quantity", 0)))
            self.table.item(r2, 2).setText(str(it.get("rate", 0)))
            self.table.item(r2, 3).setText(str(it.get("discount", 0)))
            self.table.item(r2, 4).setText(str(it.get("gst", 0)))
            self.table.item(r2, 5).setText(str(it.get("line_total", it.get("total", 0))))
        self.recalculate()
        # lock past invoices or finalized ones
        is_today = inv.get("date", "") == date.today().strftime("%Y-%m-%d")
        is_final = inv.get("status", "final") == "final"
        allow_edit = is_today and not is_final
        editable = Qt.ItemFlag.ItemIsSelectable | (Qt.ItemFlag.ItemIsEditable if is_today else Qt.ItemFlag(0))
        for r3 in range(self.table.rowCount()):
            for c3 in range(self.table.columnCount()):
                it = self.table.item(r3, c3)
                if it:
                    flags = it.flags()
                    if allow_edit:
                        it.setFlags(flags | Qt.ItemFlag.ItemIsEditable)
                    else:
                        it.setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)

    def setup_completers(self) -> None:
        # Customer ID completer
        ids = [c.get("customer_id", "") for c in self.cm.list() if c.get("customer_id")]
        cust_completer = QCompleter(ids, self)
        cust_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        if self.cb_customer_id.lineEdit() is not None:
            self.cb_customer_id.lineEdit().setCompleter(cust_completer)

        # Product completer for column 0 (names and codes)
        products = self.pm.list()
        prod_tokens = []
        for p in products:
            code = p.get("product_code", "")
            name = p.get("product_name", "")
            if code:
                prod_tokens.append(code)
            if name and name != code:
                prod_tokens.append(name)
        self.prod_completer = QCompleter(sorted(set(prod_tokens)), self)
        self.prod_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def eventFilter(self, obj, event):
        if obj is self.table and isinstance(event, QKeyEvent) and self.table.hasFocus():
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                r = self.table.currentRow()
                c = self.table.currentColumn()
                # If at column 0, try autofill product
                if c == 0:
                    # After product, move to Qty without filling rate yet
                    self.table.setCurrentCell(r, 1)
                    self.table.editItem(self.table.item(r, 1))
                    self.recalculate()
                    return True
                if c == 1:
                    # After Qty enter: compute rate/gst from product selection and move to Discount
                    name = self.table.item(r, 0).text() if self.table.item(r, 0) else ""
                    p = self.pm.find_by_code(name) or self.pm.find_by_name(name)
                    if p:
                        token = name.strip().lower()
                        use_half = token in ("cp2", "cp 2", "1/2", "half", "0.5") or "1/2" in token
                        chosen_rate = float(p.get("rate_half_kg" if use_half else "rate_1kg", 0))
                        self.table.setItem(r, 2, QTableWidgetItem(str(chosen_rate)))
                        if not self.table.item(r, 4) or (self.table.item(r, 4).text() or "").strip() in ("", "0"):
                            self.table.setItem(r, 4, QTableWidgetItem(str(p.get("gst_rate", 0))))
                    # Jump to Discount column
                    self.table.setCurrentCell(r, 3)
                    self.table.editItem(self.table.item(r, 3))
                    self.recalculate()
                    return True
                # Move to next editable column
                next_c = min(c + 1, self.table.columnCount() - 1)
                if next_c == self.table.columnCount() - 1:
                    # On total column, add new row only if current row has product
                    prod_text = self.table.item(r, 0).text() if self.table.item(r, 0) else ""
                    if prod_text.strip() != "" and r == self.table.rowCount() - 1:
                        self.add_row()
                        self.table.setCurrentCell(r + 1, 0)
                        self.table.editItem(self.table.item(r + 1, 0))
                    else:
                        # Stay on current row first column
                        self.table.setCurrentCell(r, 0)
                        self.table.editItem(self.table.item(r, 0))
                else:
                    self.table.setCurrentCell(r, next_c)
                    self.table.editItem(self.table.item(r, next_c))
                self.recalculate()
                return True
        return super().eventFilter(obj, event)

    def _current_template(self) -> str:
        from config.defaults import app_paths
        from utils.helpers import read_json
        settings = read_json(app_paths()["settings"]) or {}
        return (settings.get("invoice", {}) or {}).get("template", "simple")


class ProductCompleterDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        # Build completer list from products
        pm = self._parent.pm
        tokens = []
        for p in pm.list():
            code = p.get("product_code", "")
            name = p.get("product_name", "")
            if code:
                tokens.append(code)
            if name and name != code:
                tokens.append(name)
            # Also add CP1/CP2 forms
            if code.upper() in ("CP1", "CP2"):
                tokens.append(code.upper())
        completer = QCompleter(sorted(set(tokens)), editor)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        editor.setCompleter(completer)
        return editor


