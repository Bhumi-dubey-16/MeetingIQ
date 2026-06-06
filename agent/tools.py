import os
import json
from groq import Groq
from dotenv import load_dotenv
from models.schemas import (
    CoreSummary, ActionItem, FinancialItem, Priority_Item,
    Commitment, UnresolvedQuestion, Person, DateItem,
    RiskItem, FullReport
)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Master prompt prefix — same context given to every tool ───────────────────
def _base_prompt(transcript: str) -> str:
    return f"""You are an expert business meeting analyst.
Analyse the following meeting transcript carefully.
Respond ONLY with valid JSON. No explanation, no markdown, no extra text.

TRANSCRIPT:
{transcript}
"""

# ── Safe JSON parser — never crashes the app ──────────────────────────────────
def _parse(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Helper to call Groq ────────────────────────────────────────────────────────
def _call_groq(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000
    )
    return response.choices[0].message.content


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 1 — Core Summary
# ══════════════════════════════════════════════════════════════════════════════
def extract_core_summary(transcript: str) -> CoreSummary:
    prompt = _base_prompt(transcript) + """
Extract the core summary of this meeting.
Return JSON in exactly this format:
{
    "one_line": "one sentence describing what this meeting was about",
    "decisions_made": [
        {"decision": "...", "status": "DECIDED or DEFERRED", "owner": "name or null"}
    ],
    "next_steps": ["step 1", "step 2"],
    "meeting_type": "Planning / Review / Standup / Sales / HR / General"
}"""
    raw = _call_groq(prompt)
    return CoreSummary(**_parse(raw))


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 2 — Action Items
# ══════════════════════════════════════════════════════════════════════════════
def extract_action_items(transcript: str) -> list[ActionItem]:
    prompt = _base_prompt(transcript) + """
Extract ALL action items — tasks assigned to specific people.
Return JSON in exactly this format:
{
    "action_items": [
        {"owner": "name", "task": "what they need to do", "deadline": "when or null", "priority": "HIGH or MEDIUM or LOW"}
    ]
}
If no action items found, return {"action_items": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [ActionItem(**item) for item in data.get("action_items", [])]


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 3 — Financial Items
# ══════════════════════════════════════════════════════════════════════════════
def extract_financial_items(transcript: str) -> list[FinancialItem]:
    prompt = _base_prompt(transcript) + """
Extract ALL financial information — budgets, targets, costs, revenue, salaries, any numbers with money context.
Return JSON in exactly this format:
{
    "financial_items": [
        {"amount": "e.g. ₹50 lakh or $200K", "context": "what this amount is for", "status": "DECIDED or DEFERRED or PENDING", "owner": "name or null"}
    ]
}
If no financial items found, return {"financial_items": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [FinancialItem(**item) for item in data.get("financial_items", [])]


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 4 — Priorities
# ══════════════════════════════════════════════════════════════════════════════
def extract_priorities(transcript: str) -> list[Priority_Item]:
    prompt = _base_prompt(transcript) + """
Extract ALL priority items — things marked as urgent, critical, important, must-do, ASAP.
Return JSON in exactly this format:
{
    "priorities": [
        {"item": "what is priority", "priority": "HIGH or MEDIUM or LOW", "owner": "name or null"}
    ]
}
If no priorities found, return {"priorities": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [Priority_Item(**item) for item in data.get("priorities", [])]


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 5 — Targets & Commitments
# ══════════════════════════════════════════════════════════════════════════════
def extract_commitments(transcript: str) -> list[Commitment]:
    prompt = _base_prompt(transcript) + """
Extract ALL commitments and targets — things people promised to achieve, metrics, goals.
Return JSON in exactly this format:
{
    "commitments": [
        {"person": "name", "committed_to": "what they committed to", "target": "any number/metric or null", "deadline": "by when or null"}
    ]
}
If no commitments found, return {"commitments": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [Commitment(**item) for item in data.get("commitments", [])]


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 6 — Unresolved Questions
# ══════════════════════════════════════════════════════════════════════════════
def extract_unresolved_questions(transcript: str) -> list[UnresolvedQuestion]:
    prompt = _base_prompt(transcript) + """
Extract ALL questions that were raised but never answered or resolved in this meeting.
Return JSON in exactly this format:
{
    "unresolved_questions": [
        {"question": "what was asked", "raised_by": "name or null", "context": "why this matters"}
    ]
}
If no unresolved questions found, return {"unresolved_questions": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [UnresolvedQuestion(**item) for item in data.get("unresolved_questions", [])]


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 7 — People & Roles
# ══════════════════════════════════════════════════════════════════════════════
def extract_people(transcript: str) -> list[Person]:
    prompt = _base_prompt(transcript) + """
Extract ALL people mentioned in this meeting — attendees, people referenced, external parties.
Return JSON in exactly this format:
{
    "people": [
        {"name": "full name or role", "role": "their designation or null", "email": "email if mentioned or null"}
    ]
}
If no people found, return {"people": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [Person(**item) for item in data.get("people", [])]


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 8 — Dates & Deadlines
# ══════════════════════════════════════════════════════════════════════════════
def extract_dates(transcript: str) -> list[DateItem]:
    prompt = _base_prompt(transcript) + """
Extract ALL dates, deadlines and timeframes mentioned in this meeting.
Return JSON in exactly this format:
{
    "dates": [
        {"date": "the date or timeframe", "event": "what happens", "owner": "who is responsible or null", "priority": "HIGH or MEDIUM or LOW"}
    ]
}
If no dates found, return {"dates": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [DateItem(**item) for item in data.get("dates", [])]


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 9 — Risks & Blockers
# ══════════════════════════════════════════════════════════════════════════════
def extract_risks(transcript: str) -> list[RiskItem]:
    prompt = _base_prompt(transcript) + """
Extract ALL risks, blockers, concerns and potential problems mentioned.
Return JSON in exactly this format:
{
    "risks": [
        {"description": "what the risk is", "severity": "HIGH or MEDIUM or LOW", "owner": "who should handle or null", "mitigation": "any solution discussed or null"}
    ]
}
If no risks found, return {"risks": []}"""
    raw  = _call_groq(prompt)
    data = _parse(raw)
    return [RiskItem(**item) for item in data.get("risks", [])]
