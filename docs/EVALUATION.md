# Evaluation Workflow (Local Ablations)

This repo is designed for **local ablation testing** without Harbor/Docker.

## 1. Run paired attempts

For a given task:

1. Run `instruction.md` as the baseline condition.
2. Run `instruction_mcp.md` as the Sourcegraph MCP condition.
3. Keep model/harness settings as constant as possible across both runs.

Save each run's:

- final output (`answer.json`, report markdown, code diff, etc.)
- raw agent logs / transcript / trace export

## 2. Compare traces

Normalize both traces and compare:

```bash
python3 scripts/extract_trace.py --input path/to/baseline_output_dir --output out/baseline.trace.json
python3 scripts/extract_trace.py --input path/to/mcp_output_dir --output out/mcp.trace.json
python3 scripts/compare_trace_metrics.py \
  --baseline out/baseline.trace.json \
  --mcp out/mcp.trace.json \
  --task-manifest tasks/<suite>/<task>/demo_manifest.json
```

The comparison script reports metrics such as:

- tool call counts
- Sourcegraph MCP tool call counts
- total MCP-related events
- duration (when timestamps are present)
- time-to-first-Sourcegraph event (when timestamps are present)
- token/cost totals (when present in the exported trace)

## 3. Compare task outcomes

### Direct tasks (`*-direct`)

Typical output is one of:

- code edits / git diff
- a report file in the workspace (for understand/debug/document tasks)

Use:

- your harness’s normal local verification/test flow, and/or
- the copied `eval/` assets in the task directory as a reference oracle/checklist

### Artifact tasks (`*-artifact`)

Typical output is `answer.json` (or another explicit artifact) that is scored against a task-specific oracle/checklist.

Use:

- the task’s `eval/` directory (often includes `oracle_checks.py`, `task_spec.json`, `eval.sh`) as the scoring reference
- your own harness evaluator wrapper to point those scripts at local file paths
- or the included helper `scripts/run_local_eval.py` for many tasks (it stages a temp sandbox and rewrites `/tests`, `/workspace`, `/logs` paths)

Example:

```bash
python3 scripts/run_local_eval.py \
  --task tasks/ccb_mcp_incident/ccx-incident-031 \
  --input my_outputs/answer.json \
  --output-path /workspace/answer.json
```

## 4. Record the ablation summary

At minimum, capture:

- baseline vs MCP score/reward
- baseline vs MCP completion time
- Sourcegraph MCP calls used (and which tools)
- qualitative difference in answer/code quality
- failure modes (if either side fails)

## Practical advice

- Run at least 3 trials per condition for noisy tasks.
- For artifact tasks, keep output schema identical between runs.
- For direct tasks, compare the same target files and tests each time.
- If your harness exports both a transcript and structured trace, keep both; the transcript helps explain anomalies.
