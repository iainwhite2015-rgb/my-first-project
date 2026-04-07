"""Central state shared across all pages."""
from datetime import datetime, date


FIELD_KEYS = [
    "contactName", "jobTitle", "companyName", "industry",
    "email", "phone", "currentProvider", "numUsers",
    "monthlyCost", "endDate", "companySize", "notes",
]

FIELD_LABELS = {
    "contactName":     "Contact name",
    "jobTitle":        "Job title",
    "companyName":     "Company name",
    "industry":        "Industry",
    "email":           "Email",
    "phone":           "Phone",
    "currentProvider": "Current provider",
    "numUsers":        "No. of users",
    "monthlyCost":     "Monthly cost (£)",
    "endDate":         "Contract end date",
    "companySize":     "Company size",
    "notes":           "Notes",
}


def get_urgency(date_str: str) -> dict:
    """Return urgency info dict for a contract end date string."""
    if not date_str:
        return {"label": "Unknown", "level": "unknown", "days": None}
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%d %b %Y", "%d %B %Y"):
        try:
            d = datetime.strptime(date_str.strip(), fmt).date()
            days = (d - date.today()).days
            if days < 0:
                return {"label": "Expired", "level": "hot", "days": days}
            if days <= 60:
                return {"label": f"Expires in {days}d", "level": "hot", "days": days}
            if days <= 180:
                return {"label": f"~{round(days/30)}mo left", "level": "warm", "days": days}
            return {"label": "Active", "level": "cool", "days": days}
        except ValueError:
            continue
    return {"label": "Unknown", "level": "unknown", "days": None}


class AppState:
    def __init__(self):
        self.api_key: str = ""
        self.leads: list[dict] = []          # list of lead dicts
        self.generated: dict[str, dict] = {} # lead_id -> generated content
        self.column_map: dict[str, str] = {} # field_key -> csv_header
        self.tone: str = "consultative"
        self.seq_steps: list[dict] = [       # call sequence steps
            {"day": 3,  "label": "First follow-up call"},
            {"day": 7,  "label": "Second follow-up call"},
            {"day": 14, "label": "Final follow-up call"},
        ]

    def set_api_key(self, key: str):
        self.api_key = key.strip()

    def load_leads(self, raw_rows: list[dict], column_map: dict[str, str]):
        """Map raw CSV/Excel rows to lead dicts using the column map."""
        self.column_map = column_map
        self.generated = {}
        leads = []
        for i, row in enumerate(raw_rows):
            lead = {"_id": str(i), "_status": "pending"}
            for fk in FIELD_KEYS:
                col = column_map.get(fk, "")
                lead[fk] = str(row.get(col, "")).strip() if col else ""
            if lead["contactName"] or lead["companyName"]:
                leads.append(lead)
        self.leads = leads

    @property
    def generated_count(self):
        return len(self.generated)

    @property
    def hot_count(self):
        return sum(1 for l in self.leads if get_urgency(l.get("endDate", ""))["level"] == "hot")

    @property
    def warm_count(self):
        return sum(1 for l in self.leads if get_urgency(l.get("endDate", ""))["level"] == "warm")

    @property
    def total_monthly_value(self):
        total = 0
        for l in self.leads:
            try:
                total += float(l.get("monthlyCost", "") or 0)
            except (ValueError, TypeError):
                pass
        return total
