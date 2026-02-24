# Evaluation (CCX-incident-031)

- CCB verifier type: `test`
- CCB verifier command: `bash /tests/eval.sh`
- Reward type: `score`
- Audit comparison mode: `artifact`

## Included assets

- `eval/` is a copy of the task verifier/oracle assets from CodeContextBench (with task-specific ground truth/oracle files).
- `instruction.md` / `instruction_mcp.md` are the task prompts used for baseline vs MCP runs.

## Practical local ablation scoring (harness-agnostic)

1. Produce a baseline run and an MCP run using the same model + temperature + harness settings where possible.
2. Save final outputs and raw traces separately.
3. Normalize traces: `python scripts/extract_trace.py --input <run-dir> --output <trace.json>`
4. Compare trace metrics: `python scripts/compare_trace_metrics.py --baseline <baseline-trace.json> --mcp <mcp-trace.json> --task-manifest tasks/.../demo_manifest.json`
5. For artifact tasks, compare `answer.json` outputs using the oracle/checklist logic in `eval/` (or adapt the included `eval.sh`/`oracle_checks.py` to your local paths).

## Direct vs artifact notes

- Primary output is usually `/workspace/answer.json` in CCB; emulate this by saving your result as `answer.json`.
- These tasks are designed for `baseline-local-artifact` vs `mcp-remote-artifact` comparisons.

