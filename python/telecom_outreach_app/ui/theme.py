"""Visual theme for the application."""
import tkinter as tk

COLOURS = {
    "bg":              "#F7F6F3",
    "surface":         "#FFFFFF",
    "surface2":        "#F0EEE9",
    "border":          "#E2DFD8",
    "border_strong":   "#C8C4BB",
    "text":            "#1A1917",
    "text2":           "#6B6860",
    "text3":           "#9C9A94",
    "accent":          "#1A1917",
    "accent_fg":       "#FFFFFF",
    "hot":             "#A32D2D",
    "hot_bg":          "#FCEBEB",
    "warm":            "#854F0B",
    "warm_bg":         "#FAEEDA",
    "cool":            "#3B6D11",
    "cool_bg":         "#EAF3DE",
    "info":            "#185FA5",
    "info_bg":         "#E6F1FB",
    "sidebar":         "#1A1917",
    "sidebar_text":    "#F0EEE9",
    "sidebar_muted":   "#7A7772",
    "sidebar_active":  "#2E2C29",
    "sidebar_divider": "#2E2C29",
    "sidebar_input":   "#2E2C29",
    "success":         "#3B6D11",
    "success_bg":      "#EAF3DE",
    "error":           "#A32D2D",
    "error_bg":        "#FCEBEB",
    "entry_bg":        "#FFFFFF",
    "entry_border":    "#C8C4BB",
    "btn_hover":       "#F0EEE9",
}

FONTS = {
    "brand":      ("Georgia", 16, "bold"),
    "nav":        ("Helvetica", 12),
    "nav_active": ("Helvetica", 12, "bold"),
    "h1":         ("Georgia", 20, "bold"),
    "h2":         ("Helvetica", 14, "bold"),
    "h3":         ("Helvetica", 12, "bold"),
    "body":       ("Helvetica", 12),
    "small":      ("Helvetica", 11),
    "tiny":       ("Helvetica", 10),
    "mono":       ("Courier", 11),
    "label":      ("Helvetica", 10),
}


def apply_theme(root: tk.Tk):
    root.configure(bg=COLOURS["bg"])
    style = tk.ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame",       background=COLOURS["bg"])
    style.configure("Surface.TFrame", background=COLOURS["surface"])
    style.configure(
        "TScrollbar",
        background=COLOURS["border"],
        troughcolor=COLOURS["bg"],
        borderwidth=0,
        arrowcolor=COLOURS["text2"],
    )
    style.configure(
        "Treeview",
        background=COLOURS["surface"],
        foreground=COLOURS["text"],
        fieldbackground=COLOURS["surface"],
        rowheight=28,
        font=FONTS["small"],
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=COLOURS["surface2"],
        foreground=COLOURS["text2"],
        font=FONTS["label"],
        relief="flat",
    )
    style.map("Treeview", background=[("selected", COLOURS["surface2"])],
              foreground=[("selected", COLOURS["text"])])
    style.map("Treeview.Heading", background=[("active", COLOURS["border"])])
