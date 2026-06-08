"""
MeetingIQ Eval Runner
=====================
Usage:
    python eval/run_eval.py                    # run all 10 cases
    python eval/run_eval.py --id 01            # run one case by id prefix
    python eval/run_eval.py --url http://...   # custom server URL
    python eval/run_eval.py --verbose          # show full diffs
"""

import argparse
import json
import sys
import time
import requests
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

sys.path.insert(0, ".")          # run from project root
from eval.ground_truth import CASES

BASE_URL = "http://localhost:8000"


# ── Scoring helpers ────────────────────────────────────────────────────────────

def _text_blob(report: Dict) -> str:
    """Flatten the full report to lowercase text for fuzzy matching."""
    return json.dumps(report).lower()


def score_actions(expected: List[Dict], report: Dict) -> Dict:
    """
    For each expected action, check whether:
      - the owner_hint appears somewhere in any action item owner field
      - the task_hint appears somewhere in any action item task/description field
    Returns hit count, miss list, precision/recall.
    """
    actions_raw = report.get("action_items", [])
    if not actions_raw:
        # some schemas nest under report
        actions_raw = report.get("report", {}).get("action_items", [])

    # normalise to list of dicts
    action_owners = []
    action_tasks  = []
    for a in actions_raw:
        if isinstance(a, dict):
            owner = (a.get("owner") or a.get("assigned_to") or "").lower()
            task  = (a.get("task") or a.get("description") or a.get("action") or "").lower()
            action_owners.append(owner)
            action_tasks.append(task)

    hits, misses = 0, []
    for exp in expected:
        owner_hint = exp["owner_hint"].lower()
        task_hint  = exp["task_hint"].lower()

        matched = False
        for owner, task in zip(action_owners, action_tasks):
            owner_ok = owner_hint in owner or any(owner_hint in t for t in [owner])
            task_ok  = any(kw in task for kw in task_hint.split())
            if owner_ok and task_ok:
                matched = True
                break

        # fallback: scan full blob
        if not matched:
            blob = _text_blob(report)
            if owner_hint in blob and any(kw in blob for kw in task_hint.split()):
                matched = True

        if matched:
            hits += 1
        else:
            misses.append(f"{exp['owner_hint']} / {exp['task_hint']}")

    total = len(expected)
    recall = hits / total if total else 0.0
    return {
        "hits":    hits,
        "total":   total,
        "recall":  round(recall, 3),
        "misses":  misses,
        "found":   len(action_owners),
    }


def score_decisions(expected: List[str], report: Dict) -> Dict:
    blob  = _text_blob(report)
    hits  = [kw for kw in expected if kw.lower() in blob]
    misses= [kw for kw in expected if kw.lower() not in blob]
    recall = len(hits) / len(expected) if expected else 0.0
    return {
        "hits":   hits,
        "misses": misses,
        "recall": round(recall, 3),
    }


def score_meeting_type(expected: str, report: Dict) -> bool:
    blob = _text_blob(report)
    return expected.lower() in blob


# ── Per-case result ────────────────────────────────────────────────────────────

@dataclass
class CaseResult:
    case_id:          str
    passed:           bool
    latency_s:        float
    action_recall:    float
    decision_recall:  float
    type_correct:     bool
    action_misses:    List[str] = field(default_factory=list)
    decision_misses:  List[str] = field(default_factory=list)
    error:            Optional[str] = None


# ── Runner ────────────────────────────────────────────────────────────────────

def run_case(case: Dict, base_url: str, verbose: bool) -> CaseResult:
    case_id = case["id"]
    print(f"\n{'─'*60}")
    print(f"▶  {case_id}")

    try:
        t0 = time.time()
        resp = requests.post(
            f"{base_url}/analyse",
            data={"text": case["transcript"]},
            timeout=120,
        )
        latency = round(time.time() - t0, 2)

        if resp.status_code != 200:
            print(f"   ✗ HTTP {resp.status_code}: {resp.text[:200]}")
            return CaseResult(case_id, False, latency, 0, 0, False,
                              error=f"HTTP {resp.status_code}")

        payload = resp.json()
        # support both flat and nested report
        report  = payload.get("report") or payload

        act  = score_actions(case["expected_actions"],   report)
        dec  = score_decisions(case["expected_decisions"], report)
        typ  = score_meeting_type(case["expected_meeting_type"], report)

        passed = act["recall"] >= 0.6 and dec["recall"] >= 0.6 and typ

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"   {status}  |  {latency}s  |  actions {act['recall']:.0%}  |  decisions {dec['recall']:.0%}  |  type {'✓' if typ else '✗'}")

        if verbose or not passed:
            if act["misses"]:
                print(f"   action misses  : {act['misses']}")
            if dec["misses"]:
                print(f"   decision misses: {dec['misses']}")
            if not typ:
                print(f"   type expected  : {case['expected_meeting_type']}")
            if verbose:
                print(f"   actions found  : {act['found']}")

        return CaseResult(
            case_id         = case_id,
            passed          = passed,
            latency_s       = latency,
            action_recall   = act["recall"],
            decision_recall = dec["recall"],
            type_correct    = typ,
            action_misses   = act["misses"],
            decision_misses = dec["misses"],
        )

    except requests.exceptions.ConnectionError:
        print(f"   ✗ Cannot connect to {base_url}. Is the server running?")
        return CaseResult(case_id, False, 0, 0, 0, False,
                          error="ConnectionError")
    except Exception as e:
        print(f"   ✗ Exception: {e}")
        return CaseResult(case_id, False, 0, 0, 0, False, error=str(e))


def print_summary(results: List[CaseResult]):
    print(f"\n{'═'*60}")
    print("SUMMARY")
    print(f"{'═'*60}")

    passed  = sum(1 for r in results if r.passed)
    total   = len(results)
    avg_lat = sum(r.latency_s for r in results) / total if total else 0
    avg_act = sum(r.action_recall for r in results) / total if total else 0
    avg_dec = sum(r.decision_recall for r in results) / total if total else 0
    type_ok = sum(1 for r in results if r.type_correct)

    print(f"  Passed          : {passed}/{total}")
    print(f"  Avg latency     : {avg_lat:.1f}s")
    print(f"  Avg action rec  : {avg_act:.1%}")
    print(f"  Avg decision rec: {avg_dec:.1%}")
    print(f"  Type correct    : {type_ok}/{total}")

    errors = [r for r in results if r.error]
    if errors:
        print(f"\n  Errors: {[r.case_id for r in errors]}")

    print(f"\n  {'ID':<30} {'pass':>4} {'act':>6} {'dec':>6} {'type':>5} {'lat':>6}")
    print(f"  {'─'*30} {'─'*4} {'─'*6} {'─'*6} {'─'*5} {'─'*6}")
    for r in results:
        p = "✓" if r.passed else "✗"
        t = "✓" if r.type_correct else "✗"
        print(f"  {r.case_id:<30} {p:>4} {r.action_recall:>6.0%} {r.decision_recall:>6.0%} {t:>5} {r.latency_s:>5.1f}s")

    print(f"\n{'═'*60}")

    # write JSON results for CI
    with open("eval/results.json", "w") as f:
        json.dump([
            {
                "id":               r.case_id,
                "passed":           r.passed,
                "latency_s":        r.latency_s,
                "action_recall":    r.action_recall,
                "decision_recall":  r.decision_recall,
                "type_correct":     r.type_correct,
                "action_misses":    r.action_misses,
                "decision_misses":  r.decision_misses,
                "error":            r.error,
            }
            for r in results
        ], f, indent=2)
    print("  Results written to eval/results.json")

    return passed == total


def main():
    parser = argparse.ArgumentParser(description="MeetingIQ eval runner")
    parser.add_argument("--url",     default=BASE_URL, help="Base URL of running server")
    parser.add_argument("--id",      default=None,     help="Run only cases whose id starts with this prefix")
    parser.add_argument("--verbose", action="store_true", help="Show full diff output")
    args = parser.parse_args()

    cases = CASES
    if args.id:
        cases = [c for c in CASES if c["id"].startswith(args.id)]
        if not cases:
            print(f"No cases match prefix '{args.id}'")
            sys.exit(1)

    print(f"MeetingIQ Eval  |  {len(cases)} case(s)  |  {args.url}")

    results = []
    for case in cases:
        result = run_case(case, args.url, args.verbose)
        results.append(result)

    all_passed = print_summary(results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()