import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
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
from models.schemas import FullReport, CoreSummary, Decision

_executor = ThreadPoolExecutor(max_workers=9)


def _run_in_thread(func, transcript: str):
    """Wraps a blocking function so asyncio can run it without freezing."""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(_executor, func, transcript)


def _fallback_summary(transcript: str) -> CoreSummary:
    """
    Called when the Core Summary tool fails (e.g. rate limit).
    Builds a minimal CoreSummary from the raw transcript so the report
    still assembles instead of crashing with a 500.
    """
    # Grab first 120 chars of transcript as a rough one-liner
    snippet = transcript.strip()[:120].replace("\n", " ")
    one_line = snippet if snippet else "Summary unavailable — Core Summary tool failed"
    return CoreSummary(
        one_line       = one_line,
        decisions_made = [],
        next_steps     = ["Review transcript manually — AI summary tool hit rate limit"],
        meeting_type   = "Unknown",
    )


async def run_agent_async(transcript: str, progress_callback=None) -> tuple[str, FullReport]:
    """
    Runs all 9 tools CONCURRENTLY using asyncio + ThreadPoolExecutor.
    return_exceptions=True means one tool failure never crashes the whole report.
    """

    def _notify(msg):
        if progress_callback:
            progress_callback(msg)
        print(msg)

    _notify("[Agent] Starting — running all 9 tools in parallel...")

    tasks = {
        "summary":              _run_in_thread(extract_core_summary,         transcript),
        "action_items":         _run_in_thread(extract_action_items,         transcript),
        "financial_items":      _run_in_thread(extract_financial_items,      transcript),
        "priorities":           _run_in_thread(extract_priorities,           transcript),
        "commitments":          _run_in_thread(extract_commitments,          transcript),
        "unresolved_questions": _run_in_thread(extract_unresolved_questions, transcript),
        "people":               _run_in_thread(extract_people,               transcript),
        "dates":                _run_in_thread(extract_dates,                transcript),
        "risks":                _run_in_thread(extract_risks,                transcript),
    }

    results = await asyncio.gather(
        tasks["summary"],
        tasks["action_items"],
        tasks["financial_items"],
        tasks["priorities"],
        tasks["commitments"],
        tasks["unresolved_questions"],
        tasks["people"],
        tasks["dates"],
        tasks["risks"],
        return_exceptions=True
    )

    (
        summary,
        action_items,
        financial_items,
        priorities,
        commitments,
        unresolved_questions,
        people,
        dates,
        risks,
    ) = results

    # ── Graceful fallbacks ─────────────────────────────────────────────────────
    # summary is the only required field in FullReport — must never be None.
    # Everything else defaults to [] which Pydantic accepts fine.

    if isinstance(summary, Exception):
        _notify(f"[Agent] Warning: Core Summary failed — {summary}")
        summary = _fallback_summary(transcript)   # ← safe CoreSummary, never None

    if isinstance(action_items, Exception):
        _notify(f"[Agent] Warning: Action Items failed — {action_items}")
        action_items = []

    if isinstance(financial_items, Exception):
        _notify(f"[Agent] Warning: Financial Items failed — {financial_items}")
        financial_items = []

    if isinstance(priorities, Exception):
        _notify(f"[Agent] Warning: Priorities failed — {priorities}")
        priorities = []

    if isinstance(commitments, Exception):
        _notify(f"[Agent] Warning: Commitments failed — {commitments}")
        commitments = []

    if isinstance(unresolved_questions, Exception):
        _notify(f"[Agent] Warning: Unresolved Questions failed — {unresolved_questions}")
        unresolved_questions = []

    if isinstance(people, Exception):
        _notify(f"[Agent] Warning: People failed — {people}")
        people = []

    if isinstance(dates, Exception):
        _notify(f"[Agent] Warning: Dates failed — {dates}")
        dates = []

    if isinstance(risks, Exception):
        _notify(f"[Agent] Warning: Risks failed — {risks}")
        risks = []

    _notify("[Agent] All tools complete — assembling report")

    report = FullReport(
        summary              = summary,
        action_items         = action_items,
        financial_items      = financial_items,
        priorities           = priorities,
        commitments          = commitments,
        unresolved_questions = unresolved_questions,
        people               = people,
        dates_deadlines      = dates,
        risks                = risks,
    )

    report_id = str(uuid.uuid4())
    _notify(f"[Agent] Report ready — ID: {report_id}")

    return report_id, report


def run_agent(transcript: str, progress_callback=None) -> tuple[str, FullReport]:
    """
    Synchronous wrapper — call this from main.py exactly as before.
    Handles both FastAPI (running event loop) and plain Python contexts.
    """
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(
                asyncio.run,
                run_agent_async(transcript, progress_callback)
            )
            return future.result()
    except RuntimeError:
        return asyncio.run(run_agent_async(transcript, progress_callback))