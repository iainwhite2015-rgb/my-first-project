"""CSV export utilities for Zoho CRM, raw messages, and call schedule."""
import csv
import io
from datetime import date, timedelta
from core.state import get_urgency, AppState


def _esc(v) -> str:
    return str(v or "").replace('"', '""')


def _rows_to_csv(headers: list, rows: list) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, quoting=csv.QUOTE_ALL)
    w.writerow(headers)
    w.writerows(rows)
    return buf.getvalue()


def export_zoho(state: AppState, owner: str, source: str) -> str:
    """Return CSV string formatted for Zoho CRM Leads module bulk import."""
    headers = [
        "First Name", "Last Name", "Company", "Title", "Email", "Phone",
        "Lead Source", "Lead Owner", "Description", "Rating",
        "No of Employees", "Annual Revenue", "Lead Status",
    ]
    rows = []
    for lead in state.leads:
        g = state.generated.get(lead["_id"])
        if not g:
            continue
        names = (lead.get("contactName") or "").split(" ", 1)
        fn = names[0]
        ln = names[1] if len(names) > 1 else ""
        u = get_urgency(lead.get("endDate", ""))
        rating = {"hot": "Hot", "warm": "Warm"}.get(u["level"], "Cold")

        # build description block
        parts = []
        if g.get("emailBody"):
            parts.append(f"EMAIL:\n{g['emailBody']}")
        if g.get("linkedInMessage"):
            parts.append(f"LINKEDIN:\n{g['linkedInMessage']}")
        if state.seq_steps and g.get("callNotes"):
            call_block = "\n\n".join(
                f"Day {s['day']} — {s['label']}:\n{g['callNotes'][i] if i < len(g['callNotes']) else ''}"
                for i, s in enumerate(state.seq_steps)
            )
            parts.append(f"CALL SCHEDULE:\n{call_block}")
        description = "\n\n".join(parts)

        annual = ""
        try:
            annual = str(round(float(lead.get("monthlyCost") or 0) * 12))
        except (ValueError, TypeError):
            pass

        rows.append([
            fn, ln,
            lead.get("companyName", ""),
            lead.get("jobTitle", ""),
            lead.get("email", ""),
            lead.get("phone", ""),
            source, owner, description, rating,
            lead.get("numUsers", ""), annual, "New",
        ])
    return _rows_to_csv(headers, rows)


def export_raw(state: AppState) -> str:
    """Return CSV with all lead data + generated messages."""
    call_headers = [f"Day {s['day']}: {s['label']}" for s in state.seq_steps]
    headers = [
        "Contact name", "Job title", "Company", "Industry",
        "Email", "Phone", "Current provider", "Users",
        "Monthly cost", "Contract end", "Urgency",
        "Email subject", "Email body", "LinkedIn message",
        *call_headers,
    ]
    rows = []
    for lead in state.leads:
        g = state.generated.get(lead["_id"])
        if not g:
            continue
        u = get_urgency(lead.get("endDate", ""))
        call_cols = [
            g["callNotes"][i] if g.get("callNotes") and i < len(g["callNotes"]) else ""
            for i in range(len(state.seq_steps))
        ]
        rows.append([
            lead.get("contactName", ""), lead.get("jobTitle", ""),
            lead.get("companyName", ""), lead.get("industry", ""),
            lead.get("email", ""), lead.get("phone", ""),
            lead.get("currentProvider", ""), lead.get("numUsers", ""),
            lead.get("monthlyCost", ""), lead.get("endDate", ""), u["label"],
            g.get("emailSubject", ""), g.get("emailBody", ""), g.get("linkedInMessage", ""),
            *call_cols,
        ])
    return _rows_to_csv(headers, rows)


def export_call_schedule(state: AppState) -> str:
    """Return call schedule CSV with per-lead talking points per step."""
    call_headers = [f"Day {s['day']} — {s['label']}" for s in state.seq_steps]
    headers = [
        "Contact name", "Company", "Phone", "Email",
        "Current provider", "Contract end", "Urgency",
        *call_headers,
    ]
    rows = []
    today = date.today()
    for lead in state.leads:
        g = state.generated.get(lead["_id"])
        u = get_urgency(lead.get("endDate", ""))
        call_cols = []
        for i in range(len(state.seq_steps)):
            note = ""
            if g and g.get("callNotes") and i < len(g["callNotes"]):
                note = g["callNotes"][i]
            call_cols.append(note)
        rows.append([
            lead.get("contactName", ""), lead.get("companyName", ""),
            lead.get("phone", ""), lead.get("email", ""),
            lead.get("currentProvider", ""), lead.get("endDate", ""), u["label"],
            *call_cols,
        ])
    return _rows_to_csv(headers, rows)
