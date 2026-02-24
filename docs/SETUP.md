# Common Setup

## Required Sourcegraph variables (for MCP runs)

Set these once in your shell before configuring your harness MCP client:

```bash
export SOURCEGRAPH_URL="https://sourcegraph.com"   # or your enterprise instance
export SOURCEGRAPH_ACCESS_TOKEN="<your-sourcegraph-token>"
```

Many MCP client examples use `SRC_ENDPOINT` / `SRC_ACCESS_TOKEN` for the Sourcegraph MCP server process. You can map them directly:

```bash
export SRC_ENDPOINT="$SOURCEGRAPH_URL"
export SRC_ACCESS_TOKEN="$SOURCEGRAPH_ACCESS_TOKEN"
```

## Harness auth (examples)

You also need auth for whichever agent/harness you use:

- Claude Code: `ANTHROPIC_API_KEY`
- Codex/OpenAI: `OPENAI_API_KEY`
- Gemini CLI / Gemini Code Assist: `GOOGLE_API_KEY` or `GEMINI_API_KEY` (depends on your setup)
- OpenHands: provider-specific LLM credentials (for example `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) and model config
- Cursor / Copilot / Amp: typically interactive sign-in and/or provider credentials depending your plan/settings

See `docs/HARNESS_MCP_SETUP.md` for harness-specific details.

## Local repo checkouts

Each task has a `setup.md` that includes the **task-specific clone commands** inferred from the original benchmark Dockerfiles and task instructions.

Examples:

- Single-repo direct task: clone a pinned repo/tag locally and run `instruction.md`
- Multi-repo artifact task: optional local clones for inspection; MCP run usually uses remote Sourcegraph mirrors and writes `answer.json`

## Python requirement (for trace scripts)

- Python 3.10+ recommended (3.11+ ideal)
- No external Python dependencies are required for `scripts/extract_trace.py` and `scripts/compare_trace_metrics.py`
