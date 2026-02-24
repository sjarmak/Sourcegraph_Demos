#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

TEXT_EXTS = {".txt", ".log", ".md", ".out"}
JSON_EXTS = {".json", ".jsonl", ".ndjson"}
SOURCEGRAPH_PAT = re.compile(r"(sourcegraph|\bsg_(?:keyword|nls|read_file|go_to_definition|find_references|list_files|list_repos|commit_search|diff_search|compare_revisions)\b)", re.I)
TIMESTAMP_PATTERNS = [
    re.compile(r"\b(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2}))\b"),
    re.compile(r"\b(\d{2}:\d{2}:\d{2}(?:\.\d+)?)\b"),
]


@dataclass
class Event:
    ts: str | None
    kind: str
    tool: str | None
    source: str
    raw: str | None = None
    usage: dict[str, float] | None = None


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Normalize agent output traces (Amp/Claude/Codex/Cursor/Copilot/Gemini/OpenHands, best-effort)")
    ap.add_argument("--input", required=True, help="File or directory containing agent output / trace artifacts")
    ap.add_argument("--output", required=True, help="Path to write normalized trace JSON")
    ap.add_argument("--max-events", type=int, default=5000, help="Cap stored events (summary still counts all detected events)")
    ap.add_argument("--summary-only", action="store_true", help="Store only summary, omit event list")
    return ap.parse_args()


def detect_harness_from_path(path: Path) -> str | None:
    p = str(path).lower()
    mapping = {
        "claude": "claude-code",
        "codex": "codex",
        "cursor": "cursor",
        "copilot": "copilot",
        "gemini": "gemini",
        "openhands": "openhands",
        "amp": "amp",
    }
    for k, v in mapping.items():
        if k in p:
            return v
    return None


def iter_files(inp: Path) -> Iterable[Path]:
    if inp.is_file():
        yield inp
        return
    for p in sorted(inp.rglob("*")):
        if not p.is_file():
            continue
        if p.name.startswith(".") and p.suffix not in JSON_EXTS:
            continue
        if p.suffix.lower() in TEXT_EXTS | JSON_EXTS or p.name in {"claude-code.txt", "conversation.json", "events.json"}:
            yield p


def try_parse_iso(ts: str) -> float | None:
    ts = ts.strip()
    try:
        if re.match(r"^\d{2}:\d{2}:\d{2}", ts):
            # No date available; treat as relative within day.
            parts = ts.split(":")
            h = int(parts[0]); m = int(parts[1]); s = float(parts[2])
            return h * 3600 + m * 60 + s
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        if re.match(r".*[+-]\d{4}$", ts):
            ts = ts[:-5] + ts[-5:-2] + ":" + ts[-2:]
        return datetime.fromisoformat(ts).timestamp()
    except Exception:
        return None


def find_ts_in_text(line: str) -> str | None:
    for pat in TIMESTAMP_PATTERNS:
        m = pat.search(line)
        if m:
            return m.group(1)
    return None


def extract_tool_from_obj(obj: dict[str, Any]) -> str | None:
    candidates = [
        obj.get("tool"),
        obj.get("tool_name"),
        obj.get("name") if str(obj.get("type", "")).lower().startswith("tool") else None,
    ]
    # OpenAI/Codex style nested structures
    fn = obj.get("function")
    if isinstance(fn, dict):
        candidates.append(fn.get("name"))
    for key in ["call", "invocation", "event", "payload", "data"]:
        val = obj.get(key)
        if isinstance(val, dict):
            candidates.append(val.get("tool") or val.get("tool_name") or (val.get("function") or {}).get("name"))
    for c in candidates:
        if isinstance(c, str) and c.strip():
            return c.strip()
    return None


def extract_timestamp_from_obj(obj: dict[str, Any]) -> str | None:
    for key in ["timestamp", "ts", "time", "created_at", "started_at", "ended_at", "datetime"]:
        val = obj.get(key)
        if isinstance(val, str):
            return val
    for key in ["event", "payload", "data", "meta"]:
        val = obj.get(key)
        if isinstance(val, dict):
            inner = extract_timestamp_from_obj(val)
            if inner:
                return inner
    return None


def extract_usage(obj: dict[str, Any]) -> dict[str, float] | None:
    usage: dict[str, float] = {}
    # Common usage fields across providers/harnesses
    def walk(x: Any):
        if isinstance(x, dict):
            for k, v in x.items():
                lk = str(k).lower()
                if isinstance(v, (int, float)):
                    if lk in {"input_tokens", "prompt_tokens", "output_tokens", "completion_tokens", "total_tokens", "cost", "usd_cost", "cost_usd"}:
                        usage[lk] = usage.get(lk, 0.0) + float(v)
                walk(v)
        elif isinstance(x, list):
            for i in x:
                walk(i)
    walk(obj)
    return usage or None


def classify_json_obj(obj: dict[str, Any], src: str) -> list[Event]:
    events: list[Event] = []
    tool = extract_tool_from_obj(obj)
    ts = extract_timestamp_from_obj(obj)
    usage = extract_usage(obj)
    kind = str(obj.get("type") or obj.get("event_type") or obj.get("event") or "json_event")

    if tool:
        events.append(Event(ts=ts, kind="tool_call", tool=tool, source=src, raw=None, usage=usage))
    if usage:
        events.append(Event(ts=ts, kind="usage", tool=None, source=src, raw=None, usage=usage))
    if not events and any(SOURCEGRAPH_PAT.search(str(v) if not isinstance(v, (dict, list)) else json.dumps(v)[:500]) for v in obj.values()):
        events.append(Event(ts=ts, kind="mcp_mention", tool=None, source=src, raw=None, usage=usage))
    return events


def parse_json_file(path: Path) -> list[Event]:
    src = str(path)
    txt = path.read_text(encoding="utf-8", errors="replace")
    events: list[Event] = []
    stripped = txt.strip()
    if not stripped:
        return events

    # JSONL / NDJSON first
    if path.suffix.lower() in {".jsonl", ".ndjson"} or "\n{" in stripped:
        for line in txt.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                # Fallback text parse line-by-line
                ts = find_ts_in_text(line)
                tool = None
                if SOURCEGRAPH_PAT.search(line):
                    tool = "sourcegraph_mcp_mention"
                    events.append(Event(ts=ts, kind="mcp_mention", tool=tool, source=src, raw=line[:500]))
                continue
            if isinstance(obj, dict):
                events.extend(classify_json_obj(obj, src))
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        events.extend(classify_json_obj(item, src))
        return events

    # Regular JSON document
    try:
        doc = json.loads(txt)
    except Exception:
        return parse_text_file(path)

    def walk(node: Any):
        if isinstance(node, dict):
            events.extend(classify_json_obj(node, src))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for i in node:
                walk(i)
    walk(doc)
    return events


def parse_text_file(path: Path) -> list[Event]:
    src = str(path)
    events: list[Event] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        ts = find_ts_in_text(line)
        lower = line.lower()
        tool = None
        kind = None
        if SOURCEGRAPH_PAT.search(line):
            kind = "tool_call" if ("mcp__sourcegraph" in lower or "sg_" in lower or "keyword_search" in lower or "read_file" in lower) else "mcp_mention"
            # Try extracting tool token
            m = re.search(r"(mcp__sourcegraph__[a-z0-9_]+|sg_[a-z0-9_]+|keyword_search|nls_search|read_file|go_to_definition|find_references|list_files|list_repos|commit_search|diff_search|compare_revisions)", lower)
            tool = m.group(1) if m else "sourcegraph_mcp"
        elif any(k in lower for k in ["tool call", "invoking tool", "using tool"]):
            kind = "tool_call"
            m = re.search(r"(?:tool(?: call)?|invoking tool|using tool)[:\s]+([a-zA-Z0-9_.:-]+)", line)
            tool = m.group(1) if m else None
        if kind:
            events.append(Event(ts=ts, kind=kind, tool=tool, source=src, raw=line[:500]))
        # Token/cost hints
        m_tok = re.search(r"(?:total[_ ]tokens|tokens)\D+(\d+(?:\.\d+)?)", lower)
        if m_tok:
            events.append(Event(ts=ts, kind="usage", tool=None, source=src, raw=line[:500], usage={"total_tokens": float(m_tok.group(1))}))
        m_cost = re.search(r"(?:cost|usd)\D+\$?(\d+(?:\.\d+)?)", lower)
        if m_cost and "cost" in lower:
            events.append(Event(ts=ts, kind="usage", tool=None, source=src, raw=line[:500], usage={"cost_usd": float(m_cost.group(1))}))
    return events


def summarize(events: list[Event], input_path: Path) -> dict[str, Any]:
    harness_votes: dict[str, int] = {}
    tool_counts: dict[str, int] = {}
    sg_tool_counts: dict[str, int] = {}
    usage_totals: dict[str, float] = {}
    first_ts = None
    last_ts = None
    first_sg_ts = None

    for ev in events:
        h = detect_harness_from_path(Path(ev.source))
        if h:
            harness_votes[h] = harness_votes.get(h, 0) + 1
        if ev.tool:
            tool_counts[ev.tool] = tool_counts.get(ev.tool, 0) + 1
            if SOURCEGRAPH_PAT.search(ev.tool):
                sg_tool_counts[ev.tool] = sg_tool_counts.get(ev.tool, 0) + 1
        if ev.usage:
            for k, v in ev.usage.items():
                usage_totals[k] = usage_totals.get(k, 0.0) + float(v)
        if ev.ts:
            epoch = try_parse_iso(ev.ts)
            if epoch is not None:
                first_ts = epoch if first_ts is None else min(first_ts, epoch)
                last_ts = epoch if last_ts is None else max(last_ts, epoch)
                if (ev.tool and SOURCEGRAPH_PAT.search(ev.tool)) or ev.kind == "mcp_mention":
                    first_sg_ts = epoch if first_sg_ts is None else min(first_sg_ts, epoch)

    harness = max(harness_votes.items(), key=lambda kv: kv[1])[0] if harness_votes else detect_harness_from_path(input_path) or "unknown"
    duration = (last_ts - first_ts) if (first_ts is not None and last_ts is not None and last_ts >= first_ts) else None
    first_sg_elapsed = (first_sg_ts - first_ts) if (first_sg_ts is not None and first_ts is not None and first_sg_ts >= first_ts) else None

    return {
        "harness_guess": harness,
        "files_scanned": len({e.source for e in events}),
        "event_count": len(events),
        "tool_call_count": sum(1 for e in events if e.kind == "tool_call"),
        "mcp_related_event_count": sum(1 for e in events if (e.tool and SOURCEGRAPH_PAT.search(e.tool)) or e.kind == "mcp_mention"),
        "sourcegraph_tool_call_count": sum(sg_tool_counts.values()),
        "sourcegraph_tool_counts": dict(sorted(sg_tool_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "tool_counts": dict(sorted(tool_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
        "usage_totals": usage_totals,
        "duration_seconds": duration,
        "time_to_first_sourcegraph_event_seconds": first_sg_elapsed,
    }


def main() -> None:
    args = parse_args()
    inp = Path(args.input).expanduser().resolve()
    out = Path(args.output).expanduser().resolve()
    if not inp.exists():
        raise SystemExit(f"Input not found: {inp}")

    all_events: list[Event] = []
    for p in iter_files(inp):
        try:
            if p.suffix.lower() in JSON_EXTS:
                events = parse_json_file(p)
            else:
                events = parse_text_file(p)
            all_events.extend(events)
        except Exception as e:
            all_events.append(Event(ts=None, kind="parse_error", tool=None, source=str(p), raw=str(e)))

    summary = summarize(all_events, inp)
    payload: dict[str, Any] = {
        "schema": "sourcegraph-demos.trace.v1",
        "input": str(inp),
        "summary": summary,
    }
    if not args.summary_only:
        payload["events"] = [asdict(e) for e in all_events[: args.max_events]]
        payload["events_truncated"] = len(all_events) > args.max_events
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
