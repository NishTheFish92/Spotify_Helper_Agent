"""Single-step LLM evals: send each prompt to call_model once and score the tool calls it picks.
Tools never run. Usage: uv run python -m evals.run_evals
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from langchain_core.messages import HumanMessage
from src import init_llm
from src.graph import TOOLS
from src.nodes import make_call_model, DESTRUCTIVE_TOOLS

RUNS = 3
EVALS_DIR = Path(__file__).parent
CASES_FILE = EVALS_DIR / "cases.json"
RESULTS_DIR = EVALS_DIR / "results"


def norm(value):
    return str(value).strip().lower()


def args_match(expected, actual):
    for key, want in expected.items():
        got = actual.get(key)
        if isinstance(want, list):
            # every expected item must appear inside some actual item ("blinding lights" in "The Weeknd - Blinding Lights")
            if not isinstance(got, list) or not all(any(norm(w) in norm(g) for g in got) for w in want):
                return False
        elif norm(want) != norm(got):
            return False
    return True


def grade(expect, tool_calls):
    """Returns (passed, failure_type, unrequested_delete)."""
    names = [call["name"] for call in tool_calls]
    expected_tool = expect.get("tool")
    unrequested_delete = any(n in DESTRUCTIVE_TOOLS for n in names) and expected_tool not in DESTRUCTIVE_TOOLS

    if "ask_for" in expect or expect.get("no_tool_call"):
        if not names:
            return True, None, False
        return False, "invented_args" if "ask_for" in expect else "unneeded_tool", unrequested_delete

    if not names:
        return False, "missed_tool", False
    matching = [call for call in tool_calls if call["name"] == expected_tool]
    if not matching:
        return False, "wrong_tool", unrequested_delete
    if not any(args_match(expect.get("args", {}), call["args"]) for call in matching):
        return False, "wrong_args", unrequested_delete
    if unrequested_delete:
        return False, "unrequested_delete", True
    return True, None, False


def run():
    cases = json.loads(CASES_FILE.read_text())
    call_model = make_call_model(init_llm(), TOOLS)

    case_results = []
    for case in cases:
        runs = []
        for _ in range(RUNS):
            try:
                reply = call_model({"messages": [HumanMessage(case["prompt"])]})["messages"][-1]
                passed, failure, unrequested = grade(case["expect"], reply.tool_calls)
                runs.append({"passed": passed, "failure": failure, "unrequested_delete": unrequested,
                             "tool_calls": reply.tool_calls, "content": reply.content})
            except Exception as e:
                runs.append({"passed": False, "failure": "infra_error", "unrequested_delete": False,
                             "error": str(e)})
        case_results.append({**case, "runs": runs})
    return case_results


def summarize(case_results):
    by_category = defaultdict(lambda: {"passed": 0, "graded": 0, "failures": defaultdict(int)})
    for case in case_results:
        stats = by_category[case["category"]]
        for r in case["runs"]:
            if r["failure"] == "infra_error":
                stats["failures"]["infra_error"] += 1
                continue
            stats["graded"] += 1
            stats["passed"] += r["passed"]
            if r["failure"]:
                stats["failures"][r["failure"]] += 1

    return {
        "categories": {
            name: {"pass_rate": s["passed"] / s["graded"] if s["graded"] else None,
                   "passed": s["passed"], "graded": s["graded"], "failures": dict(s["failures"])}
            for name, s in by_category.items()
        },
        "unrequested_deletes": sum(r["unrequested_delete"] for c in case_results for r in c["runs"]),
        "flaky": [c["prompt"] for c in case_results
                  if 0 < sum(r["passed"] for r in c["runs"]) < len(c["runs"])],
    }


def latest_previous():
    files = sorted(RESULTS_DIR.glob("*.json"))
    return json.loads(files[-1].read_text())["summary"] if files else None


def report(summary, previous):
    for name, s in summary["categories"].items():
        if s["pass_rate"] is None:
            print(f"{name:<14} no graded runs   {s['failures']}")
            continue
        line = f"{name:<14} {s['passed']}/{s['graded']:<4} {s['pass_rate']:>5.0%}"
        if s["failures"]:
            line += f"   {s['failures']}"
        old = previous and previous["categories"].get(name, {}).get("pass_rate")
        if old is not None and s["pass_rate"] < old:
            line += f"   ⚠ down from {old:.0%}"
        print(line)
    print(f"\nunrequested deletes: {summary['unrequested_deletes']}")
    for prompt in summary["flaky"]:
        print(f"flaky: {prompt!r}")


if __name__ == "__main__":
    previous = latest_previous()
    case_results = run()
    summary = summarize(case_results)
    report(summary, previous)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"{datetime.now():%Y-%m-%d_%H%M%S}.json"
    out.write_text(json.dumps({"runs_per_case": RUNS, "summary": summary, "cases": case_results}, indent=2, default=str))
    print(f"\nsaved {out}")
