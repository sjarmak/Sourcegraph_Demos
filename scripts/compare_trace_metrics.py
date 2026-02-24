#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METRICS = [
    ("event_count", "events", True),
    ("tool_call_count", "tool_calls", True),
    ("sourcegraph_tool_call_count", "sg_tool_calls", True),
    ("mcp_related_event_count", "mcp_related_events", True),
    ("duration_seconds", "duration_s", False),
    ("time_to_first_sourcegraph_event_seconds", "ttf_sg_s", False),
]
USAGE_KEYS = ["input_tokens", "prompt_tokens", "output_tokens", "completion_tokens", "total_tokens", "cost_usd", "usd_cost", "cost"]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Compare baseline vs MCP normalized trace summaries")
    ap.add_argument("--baseline", required=True, help="Normalized trace JSON from scripts/extract_trace.py")
    ap.add_argument("--mcp", required=True, help="Normalized trace JSON from scripts/extract_trace.py")
    ap.add_argument("--task-manifest", help="Optional tasks/.../demo_manifest.json for richer output")
    ap.add_argument("--baseline-score", type=float, help="Optional baseline task score/reward")
    ap.add_argument("--mcp-score", type=float, help="Optional MCP task score/reward")
    ap.add_argument("--output", help="Optional path to write JSON comparison")
    return ap.parse_args()


def load_trace(p: str) -> dict[str, Any]:
    data = json.loads(Path(p).read_text(encoding="utf-8"))
    if "summary" not in data:
        raise ValueError(f"Not a normalized trace file: {p}")
    return data


def v(summary: dict[str, Any], key: str) -> float | None:
    val = summary.get(key)
    return float(val) if isinstance(val, (int, float)) else None


def usage_total(summary: dict[str, Any], key: str) -> float | None:
    u = summary.get("usage_totals") or {}
    val = u.get(key)
    return float(val) if isinstance(val, (int, float)) else None


def delta(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return b - a


def format_num(x: float | None) -> str:
    if x is None:
        return "N/A"
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    if abs(x) >= 1:
        return f"{x:.2f}"
    return f"{x:.4f}"


def main() -> None:
    args = parse_args()
    bl = load_trace(args.baseline)
    mcp = load_trace(args.mcp)
    bls = bl["summary"]
    mcs = mcp["summary"]

    manifest = None
    if args.task_manifest:
        manifest = json.loads(Path(args.task_manifest).read_text(encoding="utf-8"))

    comp: dict[str, Any] = {
        "task": manifest,
        "baseline": {"file": args.baseline, "summary": bls},
        "mcp": {"file": args.mcp, "summary": mcs},
        "metrics": {},
    }

    for key, label, higher_is_more in METRICS:
        a = v(bls, key)
        b = v(mcs, key)
        comp["metrics"][label] = {
            "baseline": a,
            "mcp": b,
            "delta": delta(a, b),
            "direction_note": "higher means more" if higher_is_more else "lower is usually better for speed/latency",
        }

    usage = {}
    for key in USAGE_KEYS:
        a = usage_total(bls, key)
        b = usage_total(mcs, key)
        if a is None and b is None:
            continue
        usage[key] = {"baseline": a, "mcp": b, "delta": delta(a, b)}
    comp["usage"] = usage

    if args.baseline_score is not None or args.mcp_score is not None:
        comp["outcome"] = {
            "baseline_score": args.baseline_score,
            "mcp_score": args.mcp_score,
            "delta": delta(args.baseline_score, args.mcp_score),
        }

    # Console-friendly markdown summary
    title = manifest["task_id"] if manifest else "Trace Comparison"
    print(f"# {title}")
    if manifest:
        print(f"- Suite: `{manifest['suite']}` | Mode: `{manifest['comparison_mode']}`")
        print(f"- Audit delta reference: {manifest['delta']:+.3f} ({manifest['baseline_reward']} -> {manifest['mcp_reward']})")
    print(f"- Harness guesses: baseline=`{bls.get('harness_guess')}`, mcp=`{mcs.get('harness_guess')}`")
    print()
    print("| Metric | Baseline | MCP | Delta |")
    print("|---|---:|---:|---:|")
    for _key, label, _hi in METRICS:
        row = comp["metrics"][label]
        print(f"| `{label}` | {format_num(row['baseline'])} | {format_num(row['mcp'])} | {format_num(row['delta'])} |")
    for key, row in usage.items():
        print(f"| `usage.{key}` | {format_num(row['baseline'])} | {format_num(row['mcp'])} | {format_num(row['delta'])} |")
    if "outcome" in comp:
        o = comp["outcome"]
        print(f"| `reward_or_score` | {format_num(o['baseline_score'])} | {format_num(o['mcp_score'])} | {format_num(o['delta'])} |")
    print()
    print("## Top Sourcegraph Tools (MCP trace)")
    sg_counts = (mcs.get("sourcegraph_tool_counts") or {})
    if not sg_counts:
        print("- No Sourcegraph MCP tool calls detected in the normalized trace.")
    else:
        for name, cnt in list(sg_counts.items())[:10]:
            print(f"- `{name}`: {cnt}")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(comp, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
