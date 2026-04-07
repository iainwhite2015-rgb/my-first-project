"""
Telecom Lead Outreach Platform
--------------------------------
Run:  python app.py
Deps: pip install -r requirements.txt
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import csv
import io
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# ── optional imports (handled gracefully) ─────────────────────────────────────
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from ui.theme import apply_theme, COLOURS, FONTS
from ui.pages.import_page import ImportPage
from ui.pages.sequence_page import SequencePage
from ui.pages.generate_page import GeneratePage
from ui.pages.export_page import ExportPage
from core.state import AppState


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Telecom Lead Outreach Platform")
        self.geometry("1100x720")
        self.minsize(900, 600)
        apply_theme(self)

        self.state_data = AppState()
        self._build_ui()

    def _build_ui(self):
        # ── sidebar ────────────────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, bg=COLOURS["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="Outreach\nPlatform",
            bg=COLOURS["sidebar"],
            fg=COLOURS["sidebar_text"],
            font=FONTS["brand"],
            justify="left",
            pady=0,
        ).pack(anchor="w", padx=20, pady=(28, 32))

        self.nav_buttons = {}
        self.pages = {}
        steps = [
            ("import",   "1  Import leads"),
            ("sequence", "2  Sequence"),
            ("generate", "3  Generate"),
            ("export",   "4  Export"),
        ]
        page_classes = {
            "import":   ImportPage,
            "sequence": SequencePage,
            "generate": GeneratePage,
            "export":   ExportPage,
        }

        for key, label in steps:
            btn = tk.Button(
                self.sidebar,
                text=label,
                anchor="w",
                padx=20,
                relief="flat",
                bd=0,
                bg=COLOURS["sidebar"],
                fg=COLOURS["sidebar_text"],
                activebackground=COLOURS["sidebar_active"],
                activeforeground=COLOURS["sidebar_text"],
                font=FONTS["nav"],
                cursor="hand2",
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x", pady=1)
            self.nav_buttons[key] = btn

        # ── api key bar at bottom of sidebar ──────────────────────────────────
        tk.Frame(self.sidebar, bg=COLOURS["sidebar_divider"], height=1).pack(
            fill="x", padx=16, pady=(16, 0)
        )
        tk.Label(
            self.sidebar,
            text="Anthropic API key",
            bg=COLOURS["sidebar"],
            fg=COLOURS["sidebar_muted"],
            font=FONTS["tiny"],
            anchor="w",
        ).pack(fill="x", padx=16, pady=(10, 2))

        self.api_key_var = tk.StringVar()
        # pre-fill from env if available
        self.api_key_var.set(os.environ.get("ANTHROPIC_API_KEY", ""))
        api_entry = tk.Entry(
            self.sidebar,
            textvariable=self.api_key_var,
            show="•",
            relief="flat",
            bg=COLOURS["sidebar_input"],
            fg=COLOURS["sidebar_text"],
            insertbackground=COLOURS["sidebar_text"],
            font=FONTS["tiny"],
        )
        api_entry.pack(fill="x", padx=16, pady=(0, 20))
        api_entry.bind("<FocusOut>", lambda e: self.state_data.set_api_key(self.api_key_var.get()))
        api_entry.bind("<Return>",   lambda e: self.state_data.set_api_key(self.api_key_var.get()))

        # ── main content area ──────────────────────────────────────────────────
        self.content = tk.Frame(self, bg=COLOURS["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        for key, PageClass in page_classes.items():
            page = PageClass(self.content, self.state_data, self)
            page.place(relwidth=1, relheight=1)
            self.pages[key] = page

        self.show_page("import")

    def show_page(self, key):
        for k, btn in self.nav_buttons.items():
            btn.config(
                bg=COLOURS["sidebar_active"] if k == key else COLOURS["sidebar"],
                font=FONTS["nav_active"] if k == key else FONTS["nav"],
            )
        self.pages[key].tkraise()
        if hasattr(self.pages[key], "on_show"):
            self.pages[key].on_show()

    def navigate(self, key):
        self.show_page(key)


if __name__ == "__main__":
    app = App()
    app.mainloop()
