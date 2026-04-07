# Telecom Lead Outreach Platform

A cross-platform desktop application for AI-powered B2B telecom lead outreach.
Bulk-import leads from CSV or Excel, generate personalised email + LinkedIn messages
and call talking points with Claude AI, then export to Zoho CRM or CSV.

---

## Requirements

- Python 3.10 or later (tkinter is included with standard Python)
- An Anthropic API key (https://console.anthropic.com)

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) set your API key as an environment variable
export ANTHROPIC_API_KEY=sk-ant-...       # Mac / Linux
set ANTHROPIC_API_KEY=sk-ant-...          # Windows CMD
$env:ANTHROPIC_API_KEY="sk-ant-..."       # Windows PowerShell

# 3. Run the app
python app.py
```

You can also paste your API key directly into the sidebar field inside the app.

---

## CSV / Excel column names

The app auto-maps common column names. For best results, use these headers:

| Field              | Suggested column name   |
|--------------------|------------------------|
| Contact name       | Contact Name           |
| Job title          | Job Title              |
| Company            | Company                |
| Industry           | Industry               |
| Email              | Email                  |
| Phone              | Phone                  |
| Current provider   | Current Provider       |
| No. of users       | No. of Users           |
| Monthly cost (£)   | Monthly Cost           |
| Contract end date  | Contract End           |
| Company size       | Company Size           |
| Notes              | Notes                  |

If your columns are named differently, use the mapping screen inside the app.

---

## Build a standalone executable (optional)

### Windows (.exe)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "OutreachPlatform" app.py
# Output: dist/OutreachPlatform.exe
```

### Mac (.app)
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "OutreachPlatform" app.py
# Output: dist/OutreachPlatform
```

Distribute the single file — no Python installation needed on the target machine.

---

## Export formats

| Export               | Use for                                      |
|----------------------|----------------------------------------------|
| Zoho CRM CSV         | Bulk import into Zoho Leads module           |
| Raw messages CSV     | Manual use / paste into other tools          |
| Call schedule CSV    | Sales team briefing / dialler integration    |

---

## Workflow

1. **Import** — Upload CSV or Excel, map columns, preview leads with urgency flags
2. **Sequence** — Choose outreach tone, configure follow-up call timing
3. **Generate** — AI generates email, LinkedIn message and call talking points per lead
4. **Export** — Download Zoho-ready CSV, raw messages, or call schedule

---

## File structure

```
telecom_outreach_app/
├── app.py                    ← entry point
├── requirements.txt
├── README.md
├── core/
│   ├── state.py              ← shared app state
│   ├── generator.py          ← Anthropic API calls
│   └── exporter.py           ← CSV export logic
└── ui/
    ├── theme.py              ← colours and fonts
    ├── widgets.py            ← reusable UI components
    └── pages/
        ├── import_page.py
        ├── sequence_page.py
        ├── generate_page.py
        └── export_page.py
```
