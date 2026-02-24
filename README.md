# Sourcegraph Demos (Curated Task Set)

This repo packages a **curated task set** from CodeContextBench into a local, harness-agnostic demo kit.

Selection filter used for this snapshot: `reference verifier delta > 0.2` (using the rounded delta value from the source report table).

Goal: make it easy to run your own **baseline vs Sourcegraph MCP ablation tests** from your machine (no Docker required, use any harness/agent you prefer).

## 🚀 Quick Setup (3 steps)

```bash
# 1. Clone the repo
git clone https://github.com/sjarmak/Sourcegraph_Demos.git
cd Sourcegraph_Demos

# 2. Create a task workspace (auto-clones source code)
./scripts/setup-ccb-task.sh cilium-project-orient-001

# 3. Follow the generated guide
cd cilium-project-orient-001-setup
cat RUN_GUIDE.md
```

That's it! The workspace includes:
- ✅ Pre-cloned source code for baseline
- ✅ Task instructions (baseline + MCP)
- ✅ Scoring scripts & ground truth
- ✅ Comprehensive execution guide

**See `SETUP_SCRIPT_GUIDE.md` for full documentation** (list tasks, batch setup, advanced options).

---

## What is included

- `tasks/`: 37 task directories (curated subset)
- `TASK_INDEX.md`: ranked list of included tasks by reference verifier delta (`> 0.2`)
- `data/`: source audit artifacts used to generate this repo
- `scripts/extract_trace.py`: normalize raw agent outputs/logs into a common trace schema
- `scripts/compare_trace_metrics.py`: compare baseline vs MCP trace metrics
- `scripts/run_local_eval.py`: run copied CCB `eval/` scripts locally against a task output (path-rewrite sandbox)
- `docs/HARNESS_MCP_SETUP.md`: MCP setup for Amp, Claude Code, Codex, Cursor, Copilot, Gemini, OpenHands
- `docs/EVALUATION.md`: direct vs artifact comparison workflow
- `docs/SETUP.md`: common local setup / environment variable guidance

## Quick Start

1. Pick a task from `TASK_INDEX.md`.
2. Read the task package:
   - `tasks/<suite>/<task>/instruction.md`
   - `tasks/<suite>/<task>/instruction_mcp.md`
   - `tasks/<suite>/<task>/setup.md`
   - `tasks/<suite>/<task>/talk_track.md`
   - `tasks/<suite>/<task>/evaluation.md`
3. Configure your agent harness + Sourcegraph MCP (`docs/HARNESS_MCP_SETUP.md`).
4. Run a baseline attempt (`instruction.md`) and save output + raw trace.
5. Run an MCP attempt (`instruction_mcp.md`) and save output + raw trace.
6. Normalize and compare traces:

```bash
python3 scripts/extract_trace.py --input /path/to/baseline_run_output --output out/baseline.trace.json
python3 scripts/extract_trace.py --input /path/to/mcp_run_output --output out/mcp.trace.json
python3 scripts/compare_trace_metrics.py \
  --baseline out/baseline.trace.json \
  --mcp out/mcp.trace.json \
  --task-manifest tasks/<suite>/<task>/demo_manifest.json
```

7. (Optional) Run the copied task verifier locally against your output:

```bash
python3 scripts/run_local_eval.py \
  --task tasks/<suite>/<task> \
  --input /path/to/output_file \
  --output-path /workspace/answer.json   # or /logs/agent/onboarding.md, etc.
```

## Task Package Layout

Each task directory contains:

- `instruction.md`: baseline/local-access task prompt
- `instruction_mcp.md`: Sourcegraph MCP task prompt variant
- `setup.md`: checkout guidance, repo scope, env vars, and Linux/macOS/Windows dependency install steps
- `talk_track.md`: demo narration suggestions (why this task is a good MCP demo)
- `evaluation.md`: comparison workflow for this task
- `demo_manifest.json`: structured metadata (delta, suite, mode, repos, outputs)
- `eval/`: copied verifier/oracle assets from CodeContextBench
- `environment/`: original Dockerfiles from the benchmark task (for provenance)

## Direct vs Artifact Tasks

This repo includes both:

- **Direct** comparisons (`baseline-local-direct` vs `mcp-remote-direct`): agent edits code / writes reports in a repo workspace
- **Artifact** comparisons (`baseline-local-artifact` vs `mcp-remote-artifact`): agent produces an artifact such as `answer.json`

See `docs/EVALUATION.md` for how to compare them locally without Harbor/Docker.

## Notes

- The included `eval/` assets are copied from CodeContextBench for convenience; they are task-specific and may assume CCB-style paths. Use them as reference/oracle material or adapt them in your own harness.
- Trace parsing is **best-effort** across multiple harness formats; verify the normalized summary for your harness the first time you use it.
