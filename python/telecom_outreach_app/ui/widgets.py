"""Reusable UI component helpers."""
import tkinter as tk
from tkinter import ttk
from ui.theme import COLOURS, FONTS


def card(parent, padx=20, pady=16, **kwargs) -> tk.Frame:
    """White card with border."""
    outer = tk.Frame(parent, bg=COLOURS["border"], bd=0)
    inner = tk.Frame(outer, bg=COLOURS["surface"], padx=padx, pady=pady, **kwargs)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    return inner


def section_label(parent, text: str):
    lbl = tk.Label(
        parent, text=text.upper(),
        bg=parent.cget("bg"),
        fg=COLOURS["text3"],
        font=("Helvetica", 9, "bold"),
        anchor="w",
    )
    lbl.pack(fill="x", pady=(0, 4))
    return lbl


def h2(parent, text: str):
    lbl = tk.Label(parent, text=text, bg=parent.cget("bg"), fg=COLOURS["text"], font=FONTS["h2"], anchor="w")
    lbl.pack(fill="x")
    return lbl


def body_label(parent, text: str, **kw):
    return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=COLOURS["text2"], font=FONTS["body"], **kw)


def primary_button(parent, text: str, command, width=None) -> tk.Button:
    kw = {"width": width} if width else {}
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLOURS["accent"], fg=COLOURS["accent_fg"],
        font=FONTS["body"], relief="flat", bd=0,
        padx=16, pady=8, cursor="hand2",
        activebackground=COLOURS["text2"],
        activeforeground=COLOURS["accent_fg"],
        **kw,
    )
    return btn


def secondary_button(parent, text: str, command, width=None) -> tk.Button:
    kw = {"width": width} if width else {}
    btn = tk.Button(
        parent, text=text, command=command,
        bg=COLOURS["surface"], fg=COLOURS["text"],
        font=FONTS["body"], relief="flat", bd=1,
        padx=14, pady=7, cursor="hand2",
        highlightbackground=COLOURS["border_strong"],
        highlightthickness=1,
        activebackground=COLOURS["btn_hover"],
        **kw,
    )
    return btn


def labelled_entry(parent, label: str, textvariable=None, width=30) -> tk.Entry:
    tk.Label(parent, text=label, bg=parent.cget("bg"), fg=COLOURS["text2"], font=FONTS["small"], anchor="w").pack(fill="x")
    entry = tk.Entry(
        parent,
        textvariable=textvariable,
        font=FONTS["body"],
        bg=COLOURS["entry_bg"],
        fg=COLOURS["text"],
        relief="flat",
        highlightbackground=COLOURS["entry_border"],
        highlightthickness=1,
        insertbackground=COLOURS["text"],
        width=width,
    )
    entry.pack(fill="x", pady=(2, 10))
    return entry


def labelled_combobox(parent, label: str, values: list, textvariable=None) -> ttk.Combobox:
    tk.Label(parent, text=label, bg=parent.cget("bg"), fg=COLOURS["text2"], font=FONTS["small"], anchor="w").pack(fill="x")
    cb = ttk.Combobox(parent, values=values, textvariable=textvariable, state="readonly", font=FONTS["body"])
    cb.pack(fill="x", pady=(2, 10))
    return cb


def badge(parent, text: str, level: str = "info") -> tk.Label:
    colours = {
        "hot":     (COLOURS["hot_bg"],     COLOURS["hot"]),
        "warm":    (COLOURS["warm_bg"],    COLOURS["warm"]),
        "cool":    (COLOURS["cool_bg"],    COLOURS["cool"]),
        "info":    (COLOURS["info_bg"],    COLOURS["info"]),
        "success": (COLOURS["success_bg"], COLOURS["success"]),
        "error":   (COLOURS["error_bg"],   COLOURS["error"]),
        "unknown": (COLOURS["surface2"],   COLOURS["text2"]),
    }
    bg, fg = colours.get(level, colours["info"])
    return tk.Label(parent, text=text, bg=bg, fg=fg, font=FONTS["tiny"], padx=8, pady=2)


def divider(parent):
    tk.Frame(parent, bg=COLOURS["border"], height=1).pack(fill="x", pady=12)


def scrollable_frame(parent) -> tuple[tk.Canvas, tk.Frame]:
    """Returns (canvas, inner_frame). Pack the canvas."""
    canvas = tk.Canvas(parent, bg=COLOURS["bg"], highlightthickness=0)
    vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    inner = tk.Frame(canvas, bg=COLOURS["bg"])
    win = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(win, width=canvas.winfo_width())

    inner.bind("<Configure>", _on_configure)
    canvas.bind("<Configure>", _on_configure)

    def _on_mousewheel(e):
        canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    return canvas, inner


def stat_card(parent, value: str, label: str, fg=None):
    f = tk.Frame(parent, bg=COLOURS["surface2"], padx=16, pady=12)
    tk.Label(f, text=value, bg=COLOURS["surface2"], fg=fg or COLOURS["text"], font=("Georgia", 22, "bold")).pack(anchor="w")
    tk.Label(f, text=label, bg=COLOURS["surface2"], fg=COLOURS["text2"], font=FONTS["small"]).pack(anchor="w")
    return f
