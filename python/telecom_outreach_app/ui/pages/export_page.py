"""Export page — Zoho CRM CSV, raw messages, and call schedule downloads."""
import tkinter as tk
from tkinter import filedialog, messagebox
from ui.theme import COLOURS, FONTS
from ui.widgets import card, section_label, primary_button, secondary_button, divider, scrollable_frame, badge
from core.state import AppState
from core.exporter import export_zoho, export_raw, export_call_schedule


class ExportPage(tk.Frame):
    def __init__(self, parent, state: AppState, app):
        super().__init__(parent, bg=COLOURS["bg"])
        self.state = state
        self.app = app
        self._build()

    def on_show(self):
        done = self.state.generated_count
        total = len(self.state.leads)
        self._summary_var.set(
            f"{done} of {total} lead{'s' if total != 1 else ''} generated and ready to export."
            if total else "No leads loaded yet."
        )

    def _build(self):
        hdr = tk.Frame(self, bg=COLOURS["bg"], padx=32, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Export", bg=COLOURS["bg"], fg=COLOURS["text"], font=FONTS["h1"]).pack(anchor="w")
        tk.Label(hdr, text="Download your generated messages and call schedule in the formats below.",
                 bg=COLOURS["bg"], fg=COLOURS["text2"], font=FONTS["body"]).pack(anchor="w", pady=(4, 0))

        _, body = scrollable_frame(self)
        body.configure(padx=32)

        # summary
        self._summary_var = tk.StringVar(value="")
        tk.Label(body, textvariable=self._summary_var, bg=COLOURS["bg"],
                 fg=COLOURS["text2"], font=FONTS["body"]).pack(anchor="w", pady=(0, 16))

        # ── Zoho CRM export ────────────────────────────────────────────────────
        section_label(body, "Zoho CRM — Leads module")
        zc = card(body)
        zc.pack(fill="x", pady=(0, 20))

        tk.Label(
            zc,
            text="Exports a CSV formatted for Zoho CRM bulk import into the Leads module.\n"
                 "Includes contact fields, urgency rating, outreach copy and call schedule in the Description field.",
            bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"], justify="left",
        ).pack(anchor="w", pady=(0, 12))

        fields_row = tk.Frame(zc, bg=COLOURS["surface"])
        fields_row.pack(fill="x", pady=(0, 14))

        # owner field
        lf = tk.Frame(fields_row, bg=COLOURS["surface"])
        lf.pack(side="left", padx=(0, 24))
        tk.Label(lf, text="Lead owner (Zoho username)", bg=COLOURS["surface"],
                 fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w")
        self._owner_var = tk.StringVar()
        tk.Entry(lf, textvariable=self._owner_var, width=28, font=FONTS["body"],
                 bg=COLOURS["entry_bg"], fg=COLOURS["text"], relief="flat",
                 highlightbackground=COLOURS["entry_border"], highlightthickness=1).pack(fill="x", pady=(2, 0))

        # source dropdown
        sf2 = tk.Frame(fields_row, bg=COLOURS["surface"])
        sf2.pack(side="left")
        tk.Label(sf2, text="Lead source", bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w")
        self._source_var = tk.StringVar(value="LinkedIn")
        import tkinter.ttk as ttk
        source_cb = ttk.Combobox(sf2, textvariable=self._source_var, state="readonly",
                                  values=["LinkedIn", "Email", "Cold Call", "Referral", "Other"],
                                  font=FONTS["body"], width=18)
        source_cb.pack(pady=(2, 0))

        btn_row = tk.Frame(zc, bg=COLOURS["surface"])
        btn_row.pack(anchor="w")
        primary_button(btn_row, "Download Zoho CSV", self._export_zoho).pack(side="left", padx=(0, 10))

        # ── Raw messages CSV ───────────────────────────────────────────────────
        divider(body)
        section_label(body, "Raw messages CSV")
        rc = card(body)
        rc.pack(fill="x", pady=(0, 20))
        tk.Label(
            rc,
            text="All lead data plus the full email, LinkedIn message and call talking points for each lead.\n"
                 "Use this to paste into your own templates or CRM manually.",
            bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"], justify="left",
        ).pack(anchor="w", pady=(0, 10))
        secondary_button(rc, "Download raw messages CSV", self._export_raw).pack(anchor="w")

        # ── Call schedule CSV ──────────────────────────────────────────────────
        divider(body)
        section_label(body, "Call schedule")
        cc2 = card(body)
        cc2.pack(fill="x", pady=(0, 32))
        tk.Label(
            cc2,
            text="A CSV for your sales team with one row per lead, showing phone, urgency and AI-generated\n"
                 "talking points for each call step — ready to use in team briefings or diallers.",
            bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"], justify="left",
        ).pack(anchor="w", pady=(0, 10))
        secondary_button(cc2, "Download call schedule CSV", self._export_calls).pack(anchor="w")

    # ── export actions ─────────────────────────────────────────────────────────

    def _check_ready(self) -> bool:
        if not self.state.generated:
            messagebox.showwarning("Nothing to export", "Generate messages first before exporting.")
            return False
        return True

    def _save_csv(self, content: str, default_name: str):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default_name,
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            f.write(content)
        messagebox.showinfo("Saved", f"File saved to:\n{path}")

    def _export_zoho(self):
        if not self._check_ready():
            return
        content = export_zoho(self.state, self._owner_var.get().strip(), self._source_var.get())
        self._save_csv(content, "zoho_leads_import.csv")

    def _export_raw(self):
        if not self._check_ready():
            return
        content = export_raw(self.state)
        self._save_csv(content, "outreach_messages.csv")

    def _export_calls(self):
        if not self._check_ready():
            return
        content = export_call_schedule(self.state)
        self._save_csv(content, "call_schedule.csv")
