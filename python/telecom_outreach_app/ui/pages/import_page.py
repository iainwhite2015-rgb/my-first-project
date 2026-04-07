"""Import page — upload CSV/Excel, map columns, preview leads."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path

from ui.theme import COLOURS, FONTS
from ui.widgets import (
    card, section_label, h2, primary_button, secondary_button,
    labelled_combobox, divider, stat_card, badge, scrollable_frame,
)
from core.state import AppState, FIELD_KEYS, FIELD_LABELS, get_urgency


class ImportPage(tk.Frame):
    def __init__(self, parent, state: AppState, app):
        super().__init__(parent, bg=COLOURS["bg"])
        self.state = state
        self.app = app
        self.raw_headers: list[str] = []
        self.raw_rows: list[dict] = []
        self.map_vars: dict[str, tk.StringVar] = {}
        self._build()

    def _build(self):
        # ── header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=COLOURS["bg"], padx=32, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Import leads", bg=COLOURS["bg"], fg=COLOURS["text"], font=FONTS["h1"]).pack(anchor="w")
        tk.Label(hdr, text="Upload a CSV or Excel file, map columns, then preview your leads.",
                 bg=COLOURS["bg"], fg=COLOURS["text2"], font=FONTS["body"]).pack(anchor="w", pady=(4, 0))

        # ── scrollable body ────────────────────────────────────────────────────
        _, body = scrollable_frame(self)
        body.configure(padx=32, pady=0)

        # Upload card
        section_label(body, "Step 1 — Upload file")
        upload_card = card(body)
        upload_card.pack(fill="x", pady=(0, 16))
        self.file_label = tk.Label(upload_card, text="No file selected", bg=COLOURS["surface"],
                                   fg=COLOURS["text2"], font=FONTS["body"])
        self.file_label.pack(anchor="w", pady=(0, 10))
        btn_row = tk.Frame(upload_card, bg=COLOURS["surface"])
        btn_row.pack(anchor="w")
        primary_button(btn_row, "Browse file…", self._browse).pack(side="left", padx=(0, 8))
        secondary_button(btn_row, "Load sample data", self._load_sample).pack(side="left")

        # Mapping card (hidden until file loaded)
        self.mapping_frame = tk.Frame(body, bg=COLOURS["bg"])
        self.mapping_frame.pack(fill="x")

        # Preview section (hidden until mapping applied)
        self.preview_frame = tk.Frame(body, bg=COLOURS["bg"])
        self.preview_frame.pack(fill="x", pady=(0, 32))

    # ── file handling ──────────────────────────────────────────────────────────

    def _browse(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV / Excel", "*.csv *.xlsx *.xls"), ("All files", "*.*")]
        )
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        ext = Path(path).suffix.lower()
        try:
            if ext == ".csv":
                rows = self._read_csv(path)
            else:
                rows = self._read_excel(path)
            if not rows:
                messagebox.showwarning("Empty file", "The file contains no data rows.")
                return
            self.raw_rows = rows
            self.raw_headers = list(rows[0].keys())
            self.file_label.config(text=f"{Path(path).name}  ({len(rows)} rows)", fg=COLOURS["text"])
            self._show_mapping()
        except Exception as e:
            messagebox.showerror("Load error", str(e))

    def _read_csv(self, path: str) -> list[dict]:
        import csv
        rows = []
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return rows

    def _read_excel(self, path: str) -> list[dict]:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            ws = wb.active
            rows_iter = ws.iter_rows(values_only=True)
            headers = [str(h or "").strip() for h in next(rows_iter)]
            rows = []
            for row in rows_iter:
                rows.append({headers[i]: (str(v) if v is not None else "") for i, v in enumerate(row)})
            return rows
        except ImportError:
            messagebox.showerror("Missing dependency",
                                 "openpyxl is required for Excel files.\nRun: pip install openpyxl")
            return []

    def _load_sample(self):
        """Load built-in sample data for demo purposes."""
        from datetime import date, timedelta
        today = date.today()
        self.raw_rows = [
            {"Contact Name": "Sarah Mitchell", "Job Title": "IT Manager",
             "Company": "Apex Solutions Ltd", "Industry": "Professional Services",
             "Email": "s.mitchell@apexsolutions.co.uk", "Phone": "07700 900123",
             "Current Provider": "BT", "No. of Users": "45",
             "Monthly Cost": "2200", "Contract End": (today + timedelta(days=45)).isoformat(),
             "Company Size": "SMB", "Notes": "Unhappy with BT support response times"},
            {"Contact Name": "James Okafor", "Job Title": "Head of Technology",
             "Company": "Meridian Group", "Industry": "Financial Services",
             "Email": "j.okafor@meridiangroup.com", "Phone": "07700 900456",
             "Current Provider": "Vodafone", "No. of Users": "210",
             "Monthly Cost": "8500", "Contract End": (today + timedelta(days=120)).isoformat(),
             "Company Size": "Enterprise", "Notes": "Looking to consolidate comms stack"},
            {"Contact Name": "Priya Sharma", "Job Title": "Operations Director",
             "Company": "Greenleaf Logistics", "Industry": "Logistics",
             "Email": "p.sharma@greenleaflogistics.co.uk", "Phone": "07700 900789",
             "Current Provider": "O2", "No. of Users": "78",
             "Monthly Cost": "3100", "Contract End": (today + timedelta(days=15)).isoformat(),
             "Company Size": "SMB", "Notes": "Contract expiring — needs urgent outreach"},
        ]
        self.raw_headers = list(self.raw_rows[0].keys())
        self.file_label.config(text="Sample data (3 leads)", fg=COLOURS["text"])
        self._show_mapping()

    # ── column mapping ─────────────────────────────────────────────────────────

    def _show_mapping(self):
        for w in self.mapping_frame.winfo_children():
            w.destroy()

        section_label(self.mapping_frame, "Step 2 — Map columns")
        mc = card(self.mapping_frame)
        mc.pack(fill="x", pady=(0, 16))

        tk.Label(mc, text="Match your file's columns to the fields below. Skip fields not present.",
                 bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w", pady=(0, 12))

        options = ["— skip —"] + self.raw_headers
        self.map_vars = {}
        grid = tk.Frame(mc, bg=COLOURS["surface"])
        grid.pack(fill="x")
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        for i, fk in enumerate(FIELD_KEYS):
            col = i % 2
            row = i // 2
            r = row * 2
            c = col * 2

            tk.Label(grid, text=FIELD_LABELS[fk], bg=COLOURS["surface"],
                     fg=COLOURS["text2"], font=FONTS["small"]).grid(row=r, column=c, sticky="w", padx=(0 if col == 0 else 24, 4), pady=(4, 0))

            var = tk.StringVar()
            # auto-detect best match
            best = ""
            needle = fk.lower().replace("name", "").replace("contact", "contact").strip()
            for h in self.raw_headers:
                hl = h.lower()
                if fk == "contactName" and any(x in hl for x in ["contact", "first name", "name"]):
                    best = h; break
                if fk == "jobTitle" and any(x in hl for x in ["title", "job", "role", "position"]):
                    best = h; break
                if fk == "companyName" and any(x in hl for x in ["company", "organisation", "organization", "firm"]):
                    best = h; break
                if fk == "email" and "email" in hl:
                    best = h; break
                if fk == "phone" and any(x in hl for x in ["phone", "tel", "mobile", "number"]):
                    best = h; break
                if fk == "currentProvider" and any(x in hl for x in ["provider", "supplier", "carrier"]):
                    best = h; break
                if fk == "numUsers" and any(x in hl for x in ["user", "licence", "license", "seat"]):
                    best = h; break
                if fk == "monthlyCost" and any(x in hl for x in ["cost", "spend", "monthly", "revenue"]):
                    best = h; break
                if fk == "endDate" and any(x in hl for x in ["end", "expir", "renew", "contract"]):
                    best = h; break
                if fk == "industry" and "industry" in hl:
                    best = h; break
                if fk == "companySize" and any(x in hl for x in ["size", "employee", "headcount"]):
                    best = h; break
                if fk == "notes" and any(x in hl for x in ["note", "comment", "remark", "additional"]):
                    best = h; break

            var.set(best if best else "— skip —")
            self.map_vars[fk] = var

            cb = ttk.Combobox(grid, values=options, textvariable=var, state="readonly", font=FONTS["small"], width=24)
            cb.grid(row=r + 1, column=c, sticky="ew", padx=(0 if col == 0 else 24, 0), pady=(2, 8))

        primary_button(mc, "Confirm mapping & preview →", self._apply_mapping).pack(anchor="w", pady=(12, 0))

    def _apply_mapping(self):
        col_map = {fk: (v.get() if v.get() != "— skip —" else "") for fk, v in self.map_vars.items()}
        self.state.load_leads(self.raw_rows, col_map)
        if not self.state.leads:
            messagebox.showwarning("No leads found", "No valid leads found after mapping. Check your column selections.")
            return
        self._show_preview()

    # ── preview ────────────────────────────────────────────────────────────────

    def _show_preview(self):
        for w in self.preview_frame.winfo_children():
            w.destroy()

        section_label(self.preview_frame, "Step 3 — Preview")

        # stat cards
        stats_row = tk.Frame(self.preview_frame, bg=COLOURS["bg"])
        stats_row.pack(fill="x", pady=(0, 12))
        stats = [
            (str(len(self.state.leads)),                               "Total leads",         None),
            (str(self.state.hot_count),                                "Hot (expiring soon)", COLOURS["hot"]),
            (str(self.state.warm_count),                               "Warm (3–6 months)",   COLOURS["warm"]),
            (f"£{self.state.total_monthly_value:,.0f}",                "Monthly pipeline",    None),
        ]
        for val, lbl, fg in stats:
            sc = stat_card(stats_row, val, lbl, fg)
            sc.pack(side="left", expand=True, fill="x", padx=(0, 8), ipadx=4)

        # table card
        tc = card(self.preview_frame)
        tc.pack(fill="x", pady=(0, 16))

        tk.Label(tc, text=f"Showing {min(len(self.state.leads), 100)} of {len(self.state.leads)} leads",
                 bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w", pady=(0, 8))

        cols = ("Contact", "Company", "Provider", "Users", "Monthly £", "Contract end", "Urgency")
        widths = (140, 160, 100, 60, 90, 110, 90)

        tree_frame = tk.Frame(tc, bg=COLOURS["surface"])
        tree_frame.pack(fill="x")

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="x")

        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=50, stretch=True)

        for lead in self.state.leads[:100]:
            u = get_urgency(lead.get("endDate", ""))
            cost = lead.get("monthlyCost", "")
            try:
                cost = f"£{float(cost):,.0f}" if cost else "—"
            except ValueError:
                cost = cost or "—"
            tree.insert("", "end", values=(
                lead.get("contactName", "—"),
                lead.get("companyName", "—"),
                lead.get("currentProvider", "—"),
                lead.get("numUsers", "—"),
                cost,
                lead.get("endDate", "—"),
                u["label"],
            ), tags=(u["level"],))

        tree.tag_configure("hot",     foreground=COLOURS["hot"])
        tree.tag_configure("warm",    foreground=COLOURS["warm"])
        tree.tag_configure("cool",    foreground=COLOURS["cool"])
        tree.tag_configure("unknown", foreground=COLOURS["text2"])

        primary_button(tc, "Next: configure sequence →",
                        lambda: self.app.navigate("sequence")).pack(anchor="w", pady=(12, 0))
