"""Sequence page — configure tone and follow-up call steps."""
import tkinter as tk
from tkinter import ttk
from ui.theme import COLOURS, FONTS
from ui.widgets import card, section_label, primary_button, secondary_button, divider, scrollable_frame
from core.state import AppState


TONES = ["consultative", "direct", "friendly", "formal"]


class SequencePage(tk.Frame):
    def __init__(self, parent, state: AppState, app):
        super().__init__(parent, bg=COLOURS["bg"])
        self.state = state
        self.app = app
        self._step_rows: list[dict] = []
        self._build()

    def on_show(self):
        self._refresh_steps()

    def _build(self):
        hdr = tk.Frame(self, bg=COLOURS["bg"], padx=32, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Outreach sequence", bg=COLOURS["bg"], fg=COLOURS["text"], font=FONTS["h1"]).pack(anchor="w")
        tk.Label(hdr, text="Set the outreach tone and configure your human-led follow-up call schedule.",
                 bg=COLOURS["bg"], fg=COLOURS["text2"], font=FONTS["body"]).pack(anchor="w", pady=(4, 0))

        _, body = scrollable_frame(self)
        body.configure(padx=32)
        self._body = body

        # ── tone ──────────────────────────────────────────────────────────────
        section_label(body, "Outreach tone")
        tone_card = card(body)
        tone_card.pack(fill="x", pady=(0, 20))

        tk.Label(tone_card, text="Applies to all AI-generated email and LinkedIn messages.",
                 bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w", pady=(0, 10))

        self._tone_btns = {}
        tone_row = tk.Frame(tone_card, bg=COLOURS["surface"])
        tone_row.pack(anchor="w")
        for t in TONES:
            btn = tk.Button(
                tone_row, text=t.capitalize(),
                command=lambda x=t: self._set_tone(x),
                bg=COLOURS["surface"], fg=COLOURS["text"],
                font=FONTS["body"], relief="flat", bd=1,
                padx=14, pady=6, cursor="hand2",
                highlightbackground=COLOURS["border"],
                highlightthickness=1,
                activebackground=COLOURS["surface2"],
            )
            btn.pack(side="left", padx=(0, 8))
            self._tone_btns[t] = btn
        self._set_tone(self.state.tone)

        # ── call sequence ──────────────────────────────────────────────────────
        section_label(body, "Follow-up call sequence")
        seq_card = card(body)
        seq_card.pack(fill="x", pady=(0, 20))

        tk.Label(
            seq_card,
            text="Initial email and LinkedIn messages are AI-generated.\n"
                 "Follow-up calls are human-led — the AI will generate personalised talking points for each lead.",
            bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"], justify="left",
        ).pack(anchor="w", pady=(0, 14))

        self._steps_frame = tk.Frame(seq_card, bg=COLOURS["surface"])
        self._steps_frame.pack(fill="x")

        secondary_button(seq_card, "+ Add call step", self._add_step).pack(anchor="w", pady=(12, 0))

        # ── next ───────────────────────────────────────────────────────────────
        divider(body)
        primary_button(body, "Next: generate messages →", lambda: self.app.navigate("generate")).pack(anchor="w", pady=(0, 32))

    def _set_tone(self, t: str):
        self.state.tone = t
        for k, btn in self._tone_btns.items():
            if k == t:
                btn.config(bg=COLOURS["accent"], fg=COLOURS["accent_fg"],
                           highlightbackground=COLOURS["accent"])
            else:
                btn.config(bg=COLOURS["surface"], fg=COLOURS["text"],
                           highlightbackground=COLOURS["border"])

    def _refresh_steps(self):
        for w in self._steps_frame.winfo_children():
            w.destroy()
        self._step_rows = []
        for i, step in enumerate(self.state.seq_steps):
            self._render_step(i, step)

    def _render_step(self, idx: int, step: dict):
        row = tk.Frame(self._steps_frame, bg=COLOURS["surface"])
        row.pack(fill="x", pady=(0, 8))

        # circle number
        circle = tk.Label(row, text=str(idx + 1), width=2,
                          bg=COLOURS["surface2"], fg=COLOURS["text2"], font=FONTS["small"])
        circle.pack(side="left", padx=(0, 10))

        tk.Label(row, text="Day", bg=COLOURS["surface"], fg=COLOURS["text2"], font=FONTS["small"]).pack(side="left")

        day_var = tk.IntVar(value=step["day"])
        day_spin = tk.Spinbox(
            row, from_=1, to=90, textvariable=day_var, width=4,
            font=FONTS["body"], relief="flat",
            bg=COLOURS["entry_bg"], fg=COLOURS["text"],
            highlightbackground=COLOURS["entry_border"], highlightthickness=1,
            command=lambda v=day_var, i=idx: self._update_day(i, v),
        )
        day_spin.pack(side="left", padx=(4, 12))
        day_var.trace_add("write", lambda *a, v=day_var, i=idx: self._update_day(i, v))

        label_var = tk.StringVar(value=step["label"])
        label_entry = tk.Entry(
            row, textvariable=label_var, width=30,
            font=FONTS["body"], relief="flat",
            bg=COLOURS["entry_bg"], fg=COLOURS["text"],
            highlightbackground=COLOURS["entry_border"], highlightthickness=1,
        )
        label_entry.pack(side="left", padx=(0, 12))
        label_var.trace_add("write", lambda *a, v=label_var, i=idx: self._update_label(i, v))

        del_btn = tk.Button(
            row, text="Remove", command=lambda i=idx: self._remove_step(i),
            bg=COLOURS["surface"], fg=COLOURS["error"], font=FONTS["small"],
            relief="flat", bd=0, cursor="hand2", padx=4,
        )
        del_btn.pack(side="left")

        self._step_rows.append({"day": day_var, "label": label_var})

    def _update_day(self, idx: int, var: tk.IntVar):
        try:
            self.state.seq_steps[idx]["day"] = var.get()
        except (tk.TclError, IndexError):
            pass

    def _update_label(self, idx: int, var: tk.StringVar):
        try:
            self.state.seq_steps[idx]["label"] = var.get()
        except IndexError:
            pass

    def _add_step(self):
        last_day = self.state.seq_steps[-1]["day"] if self.state.seq_steps else 0
        self.state.seq_steps.append({"day": last_day + 7, "label": "Follow-up call"})
        self._refresh_steps()

    def _remove_step(self, idx: int):
        if len(self.state.seq_steps) > 1:
            self.state.seq_steps.pop(idx)
        self._refresh_steps()
