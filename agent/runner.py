import uuid
from agent.tools import (
    extract_core_summary,
    extract_action_items,
    extract_financial_items,
    extract_priorities,
    extract_commitments,
    extract_unresolved_questions,
    extract_people,
    extract_dates,
    extract_risks
)
from models.schemas import FullReport


def run_agent(transcript: str) -> tuple[str, FullReport]:
    """
    Runs all 9 tools on the transcript sequentially.
    Returns (report_id, FullReport)
    """

    print("[Agent] Starting analysis...")

    print("[Agent] Tool 1/9 — Core Summary")
    summary = extract_core_summary(transcript)

    print("[Agent] Tool 2/9 — Action Items")
    action_items = extract_action_items(transcript)

    print("[Agent] Tool 3/9 — Financial Items")
    financial_items = extract_financial_items(transcript)

    print("[Agent] Tool 4/9 — Priorities")
    priorities = extract_priorities(transcript)

    print("[Agent] Tool 5/9 — Commitments")
    commitments = extract_commitments(transcript)

    print("[Agent] Tool 6/9 — Unresolved Questions")
    unresolved_questions = extract_unresolved_questions(transcript)

    print("[Agent] Tool 7/9 — People & Roles")
    people = extract_people(transcript)

    print("[Agent] Tool 8/9 — Dates & Deadlines")
    dates = extract_dates(transcript)

    print("[Agent] Tool 9/9 — Risks & Blockers")
    risks = extract_risks(transcript)

    print("[Agent] All tools complete — assembling report")

    report = FullReport(
        summary              = summary,
        action_items         = action_items,
        financial_items      = financial_items,
        priorities           = priorities,
        commitments          = commitments,
        unresolved_questions = unresolved_questions,
        people               = people,
        dates_deadlines      = dates,
        risks                = risks
    )

    report_id = str(uuid.uuid4())
    print(f"[Agent] Report ready — ID: {report_id}")

    return report_id, report
