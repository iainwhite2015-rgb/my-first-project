"""Handles calls to the Anthropic API for message generation."""
import json
import re
from core.state import get_urgency


def build_prompt(lead: dict, tone: str, seq_steps: list[dict]) -> str:
    u = get_urgency(lead.get("endDate", ""))
    urgency_txt = ""
    if u["days"] is not None:
        urgency_txt = "Their contract has expired." if u["days"] < 0 else f"Contract ends in {u['days']} days."

    call_steps_desc = ", ".join(
        f'Step {i+1} (Day {s["day"]}): "{s["label"]}"'
        for i, s in enumerate(seq_steps)
    ) if seq_steps else "No call steps configured."

    n_calls = len(seq_steps)
    call_notes_schema = ", ".join(f'"talking points for call {i+1}"' for i in range(n_calls))

    return f"""You are a senior B2B sales consultant at a UK telecommunications company writing personalised outreach messages.

Lead data:
- Contact: {lead.get('contactName') or 'the decision maker'}{', ' + lead['jobTitle'] if lead.get('jobTitle') else ''}
- Company: {lead.get('companyName') or 'their company'}{', ' + lead['industry'] if lead.get('industry') else ''}
- Company size: {lead.get('companySize') or 'unknown'}
- Current provider: {lead.get('currentProvider') or 'unknown'}
- Users/licences: {lead.get('numUsers') or 'unknown'}
- Monthly spend: {'£' + lead['monthlyCost'] if lead.get('monthlyCost') else 'unknown'}
- {urgency_txt or 'Contract end date unknown.'}
- Notes: {lead.get('notes') or 'none'}

Tone: {tone}
Call schedule: {call_steps_desc}

Return ONLY valid JSON (absolutely no markdown fences, no explanation):
{{
  "emailSubject": "...",
  "emailBody": "...",
  "linkedInMessage": "...",
  "callNotes": [{call_notes_schema}]
}}

Rules:
- emailBody: 3-4 short paragraphs, {tone} tone, clear CTA. Sign off as [Your Name], [Your Title].
- linkedInMessage: max 280 characters, warm, personal, soft CTA. No buzzwords.
- callNotes: one entry per call step with 3-4 concise bullet-style talking points referencing lead specifics.
- Reference lead data naturally only where it is provided (not blank/unknown).
- Output ONLY the JSON object, nothing else."""


def generate_for_lead(lead: dict, tone: str, seq_steps: list[dict], api_key: str) -> dict:
    """Call Anthropic API and return parsed JSON result."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("The 'anthropic' package is not installed. Run: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    prompt = build_prompt(lead, tone, seq_steps)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = "".join(
        block.text for block in message.content if hasattr(block, "text")
    )
    # strip any accidental markdown fences
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # try to extract first {...} block
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group())
        raise ValueError(f"Could not parse AI response:\n{raw[:300]}")
