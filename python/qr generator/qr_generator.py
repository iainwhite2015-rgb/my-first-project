"""
QR Code Generator - Exports clickable HTML QR codes
Requirements: pip install qrcode[pil]
Run: python qr_generator.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import qrcode
from PIL import ImageTk
import base64
import io
import os


def generate_qr():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("No URL", "Please enter a URL first.")
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    app.qr_pil_image = img
    app.current_url = url

    # Display in GUI
    tk_img = ImageTk.PhotoImage(img)
    qr_label.config(image=tk_img)
    qr_label.image = tk_img

    download_png_btn.config(state="normal")
    download_html_btn.config(state="normal")
    status_label.config(text=f"✓ QR generated for: {url[:50]}{'...' if len(url) > 50 else ''}")


def download_png():
    if not hasattr(app, "qr_pil_image"):
        return
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        initialfile="qrcode.png",
    )
    if filepath:
        app.qr_pil_image.save(filepath)
        status_label.config(text=f"✓ PNG saved: {os.path.basename(filepath)}")


def download_html():
    """Save QR as an HTML file with a clickable link to the URL."""
    if not hasattr(app, "qr_pil_image"):
        return

    # Convert image to base64 so it's fully embedded in the HTML file
    buffer = io.BytesIO()
    app.qr_pil_image.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    url = app.current_url

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QR Code – {url}</title>
  <style>
    body {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
      background: #0f0f0f;
      font-family: monospace;
      color: #f0ece0;
    }}
    p {{
      margin-top: 16px;
      font-size: 0.85rem;
      color: #666;
    }}
    a {{
      display: inline-block;
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    a:hover {{
      transform: scale(1.03);
      box-shadow: 6px 6px 0 #c8f135;
    }}
    img {{
      display: block;
      width: 220px;
      height: 220px;
      border: 12px solid white;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
  <a href="{url}" target="_blank" title="Go to {url}">
    <img src="data:image/png;base64,{img_b64}" alt="QR code for {url}">
  </a>
  <p>Click the QR code to visit: <span style="color:#c8f135">{url}</span></p>
</body>
</html>"""

    filepath = filedialog.asksaveasfilename(
        defaultextension=".html",
        filetypes=[("HTML File", "*.html")],
        initialfile="qrcode.html",
    )
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        status_label.config(text=f"✓ HTML saved: {os.path.basename(filepath)}")


# --- Build GUI ---
app = tk.Tk()
app.title("QR Code Generator")
app.resizable(False, False)
app.configure(bg="#0f0f0f")

FONT_MAIN = ("Courier", 11)
FONT_TITLE = ("Courier", 20, "bold")
GREEN = "#c8f135"
BG = "#0f0f0f"
FG = "#f0ece0"
ENTRY_BG = "#1a1a1a"

tk.Label(app, text="QR GENERATOR", font=FONT_TITLE, bg=BG, fg=GREEN).pack(pady=(24, 4))
tk.Label(app, text="enter a url and generate a qr code", font=("Courier", 9), bg=BG, fg="#555").pack(pady=(0, 20))

frame = tk.Frame(app, bg=BG)
frame.pack(padx=30, fill="x")

url_entry = tk.Entry(frame, font=FONT_MAIN, bg=ENTRY_BG, fg=FG, insertbackground=FG,
                     relief="flat", bd=6, width=36)
url_entry.pack(side="left", fill="x", expand=True, ipady=6)
url_entry.insert(0, "https://")
url_entry.bind("<Return>", lambda e: generate_qr())

gen_btn = tk.Button(frame, text="Generate", font=FONT_MAIN, bg=GREEN, fg="#0f0f0f",
                    relief="flat", bd=0, padx=14, pady=6, cursor="hand2", command=generate_qr)
gen_btn.pack(side="left", padx=(8, 0))

qr_label = tk.Label(app, bg=BG)
qr_label.pack(pady=20)

# Two download buttons side by side
btn_frame = tk.Frame(app, bg=BG)
btn_frame.pack(pady=(0, 10))

download_png_btn = tk.Button(btn_frame, text="↓  PNG", font=FONT_MAIN, bg=BG, fg=GREEN,
                              relief="flat", bd=1, padx=16, pady=8, cursor="hand2",
                              command=download_png, state="disabled",
                              highlightbackground=GREEN, highlightthickness=1)
download_png_btn.pack(side="left", padx=(0, 10))

download_html_btn = tk.Button(btn_frame, text="↓  Clickable HTML", font=FONT_MAIN, bg=GREEN, fg="#0f0f0f",
                               relief="flat", bd=0, padx=16, pady=8, cursor="hand2",
                               command=download_html, state="disabled")
download_html_btn.pack(side="left")

status_label = tk.Label(app, text="", font=("Courier", 9), bg=BG, fg="#666")
status_label.pack(pady=(0, 20))

app.mainloop()