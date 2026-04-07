"""Generate page — bulk AI generation with progress tracking and per-lead review."""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from ui.theme import COLOURS, FONTS
from ui.widgets import (
    card, section_label, primary_button, secondary_button,
    badge, divider, scrollable_frame, stat_card,
)
from core.state import AppState, get_urgency
from core.generator import generate_for_lead


class GeneratePage(tk.Frame):
    def __init__(self, parent, state: AppState, app):
        super().__init__(parent, bg=COLOURS["bg"])
        self.state = state
        self.app = app
        self._generating = False
        self._build()

    def on_show(self):
        self._refresh_results()

    def _build(self):
        hdr = tk.Frame(self, bg=COLOURS["bg"], padx=32, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Generate messages", bg=COLOURS["bg"], fg=COLOURS["text"], font=FONTS["h1"]).pack(anchor="w")
        tk.Label(hdr, text="Generate personalised email, LinkedIn and call talking points for every lead.",
                 bg=COLOURS["bg"], fg=COLOURS["text2"], font=FONTS["body"]).pack(anchor="w", pady=(4, 0))

        # ── controls card ──────────────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=COLOURS["bg"], padx=32)
        ctrl.pack(fill="x")
        cc = card(ctrl)
        cc.pack(fill="x", pady=(0, 12))

        top_row = tk.Frame(cc, bg=COLOURS["surface"])
        top_row.pack(fill="x")

        self._status_var = tk.StringVar(value="Ready to generate")
        tk.Label(top_row, textvariable=self._status_var, bg=COLOURS["surface"],
                 fg=COLOURS["text"], font=FONTS["body"]).pack(side="left")

        self._gen_btn = primary_button(top_row, "Generate all leads ↗", self._start_generation)
        self._gen_btn.pack(side="right")

        # progress bar
        self._progress_var = tk.DoubleVar(value=0)
        prog_frame = tk.Frame(cc, bg=COLOURS["surface"], pady=6)
        prog_frame.pack(fill="x")
        style = ttk.Style()
        style.configure("Gen.Horizontal.TProgressbar",
                         troughcolor=COLOURS["surface2"],
                         background=COLOURS["accent"],
                         borderwidth=0, thickness=6)
        self._prog_bar = ttk.Progressbar(prog_frame, variable=self._progress_var,
                                          style="Gen.Horizontal.TProgressbar", maximum=100)
        self._prog_bar.pack(fill="x")

        self._sub_var = tk.StringVar(value="")
        tk.Label(cc, textvariable=self._sub_var, bg=COLOURS["surface"],
                 fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w")

        # ── results area ───────────────────────────────────────────────────────
        self._results_outer = tk.Frame(self, bg=COLOURS["bg"])
        self._results_outer.pack(fill="both", expand=True, padx=32)

        _, self._results_body = scrollable_frame(self._results_outer)
        self._results_body.configure(pady=8)

    # ── generation ─────────────────────────────────────────────────────────────

    def _start_generation(self):
        if not self.state.leads:
            messagebox.showwarning("No leads", "Import leads before generating.")
            return
        if not self.state.api_key:
            messagebox.showwarning("API key missing",
                                   "Enter your Anthropic API key in the sidebar before generating.")
            return
        if self._generating:
            return
        self._generating = True
        self._gen_btn.config(state="disabled")
        threading.Thread(target=self._run_generation, daemon=True).start()

    def _run_generation(self):
        total = len(self.state.leads)
        for i, lead in enumerate(self.state.leads):
            self._set_status(f"Generating {i+1} of {total}…",
                             f"{lead.get('contactName', 'Lead')} at {lead.get('companyName', '?')}",
                             (i / total) * 100)
            try:
                result = generate_for_lead(
                    lead, self.state.tone, self.state.seq_steps, self.state.api_key
                )
                self.state.generated[lead["_id"]] = result
                lead["_status"] = "done"
            except Exception as e:
                self.state.generated[lead["_id"]] = {
                    "emailSubject": "Error", "emailBody": str(e),
                    "linkedInMessage": "", "callNotes": [],
                }
                lead["_status"] = "error"

        self._set_status(f"Done — {total} lead{'s' if total!=1 else ''} generated", "", 100)
        self._generating = False
        self.after(0, lambda: self._gen_btn.config(state="normal"))
        self.after(0, self._refresh_results)

    def _set_status(self, status: str, sub: str, pct: float):
        self.after(0, lambda: self._status_var.set(status))
        self.after(0, lambda: self._sub_var.set(sub))
        self.after(0, lambda: self._progress_var.set(pct))

    # ── results display ────────────────────────────────────────────────────────

    def _refresh_results(self):
        for w in self._results_body.winfo_children():
            w.destroy()
        done = [l for l in self.state.leads if self.state.generated.get(l["_id"])]
        if not done:
            tk.Label(self._results_body, text="No messages generated yet.",
                     bg=COLOURS["bg"], fg=COLOURS["text2"], font=FONTS["body"]).pack(pady=24)
            return
        for lead in done:
            self._render_lead_card(lead)

    def _render_lead_card(self, lead: dict):
        g = self.state.generated.get(lead["_id"], {})
        u = get_urgency(lead.get("endDate", ""))

        outer = card(self._results_body, padx=0, pady=0)
        outer.pack(fill="x", pady=(0, 12))

        # ── lead header ────────────────────────────────────────────────────────
        hdr_frame = tk.Frame(outer, bg=COLOURS["surface"], padx=20, pady=12)
        hdr_frame.pack(fill="x")

        left = tk.Frame(hdr_frame, bg=COLOURS["surface"])
        left.pack(side="left", fill="x", expand=True)

        tk.Label(left, text=f"{lead.get('contactName','?')}  ·  {lead.get('companyName','?')}",
                 bg=COLOURS["surface"], fg=COLOURS["text"], font=FONTS["h3"]).pack(anchor="w")
        detail = "  ·  ".join(filter(None, [lead.get("jobTitle"), lead.get("email"), lead.get("phone")]))
        if detail:
            tk.Label(left, text=detail, bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w")

        b = badge(hdr_frame, u["label"], u["level"])
        b.pack(side="right", anchor="n")

        # ── tab bar ────────────────────────────────────────────────────────────
        tab_frame = tk.Frame(outer, bg=COLOURS["surface2"], padx=20)
        tab_frame.pack(fill="x")

        content_frame = tk.Frame(outer, bg=COLOURS["surface"], padx=20, pady=14)
        content_frame.pack(fill="x")

        tabs = ["Email", "LinkedIn", "Call notes"]
        self._render_tabs(tab_frame, content_frame, tabs, lead, g)

    def _render_tabs(self, tab_frame, content_frame, tabs, lead, g):
        active_tab = tk.StringVar(value="Email")
        tab_btns = {}

        def show_tab(name):
            active_tab.set(name)
            for n, btn in tab_btns.items():
                if n == name:
                    btn.config(bg=COLOURS["surface"], fg=COLOURS["text"],
                               font=FONTS["body"], relief="flat")
                else:
                    btn.config(bg=COLOURS["surface2"], fg=COLOURS["text2"],
                               font=FONTS["small"], relief="flat")
            _render_content(name)

        for t in tabs:
            btn = tk.Button(tab_frame, text=t, relief="flat", bd=0,
                            bg=COLOURS["surface2"], fg=COLOURS["text2"],
                            font=FONTS["small"], padx=14, pady=8,
                            cursor="hand2", command=lambda x=t: show_tab(x))
            btn.pack(side="left")
            tab_btns[t] = btn

        def _render_content(name):
            for w in content_frame.winfo_children():
                w.destroy()

            if name == "Email":
                subj = g.get("emailSubject", "")
                if subj:
                    sf = tk.Frame(content_frame, bg=COLOURS["surface2"], padx=10, pady=6)
                    sf.pack(fill="x", pady=(0, 8))
                    tk.Label(sf, text="Subject:", bg=COLOURS["surface2"],
                             fg=COLOURS["text2"], font=FONTS["small"]).pack(side="left")
                    tk.Label(sf, text=subj, bg=COLOURS["surface2"],
                             fg=COLOURS["text"], font=FONTS["small"]).pack(side="left", padx=(6, 0))
                self._text_block(content_frame, g.get("emailBody", "No content"))
                secondary_button(content_frame, "Copy email", lambda: self._copy(g.get("emailBody",""))).pack(anchor="w", pady=(8, 0))

            elif name == "LinkedIn":
                txt = g.get("linkedInMessage", "")
                self._text_block(content_frame, txt or "No content")
                chars = len(txt)
                clr = COLOURS["hot"] if chars > 280 else COLOURS["text2"]
                tk.Label(content_frame, text=f"{chars} / 280 characters",
                         bg=COLOURS["surface"], fg=clr, font=FONTS["small"]).pack(anchor="w", pady=(4, 0))
                secondary_button(content_frame, "Copy message", lambda: self._copy(txt)).pack(anchor="w", pady=(6, 0))

            elif name == "Call notes":
                notes = g.get("callNotes", [])
                if not notes:
                    tk.Label(content_frame, text="No call steps configured.",
                             bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w")
                else:
                    for i, step in enumerate(self.state.seq_steps):
                        note = notes[i] if i < len(notes) else "—"
                        sf = tk.Frame(content_frame, bg=COLOURS["surface"], pady=4)
                        sf.pack(fill="x")
                        tk.Label(sf, text=f"Day {step['day']} — {step['label']}",
                                 bg=COLOURS["surface"], fg=COLOURS["text2"],
                                 font=FONTS["label"]).pack(anchor="w")
                        self._text_block(sf, note)

        show_tab("Email")

    def _text_block(self, parent, text: str):
        f = tk.Frame(parent, bg=COLOURS["surface2"], padx=12, pady=10)
        f.pack(fill="x", pady=(0, 4))
        lbl = tk.Label(f, text=text, bg=COLOURS["surface2"], fg=COLOURS["text"],
                       font=FONTS["small"], justify="left", anchor="nw", wraplength=700)
        lbl.pack(fill="x", anchor="w")

    def _copy(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
