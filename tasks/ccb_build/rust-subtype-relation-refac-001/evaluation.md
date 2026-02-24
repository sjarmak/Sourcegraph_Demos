# Evaluation (rust-subtype-relation-refac-001)

- CCB verifier type: `test`
- CCB verifier command: `bash /tests/test.sh`
- Reward type: `ir_checklist`
- Audit comparison mode: `direct`

## Included assets

- `eval/` is a copy of the task verifier/oracle assets from CodeContextBench (with task-specific ground truth/oracle files).
- `instruction.md` / `instruction_mcp.md` are the task prompts used for baseline vs MCP runs.

## Practical local ablation scoring (harness-agnostic)

1. Produce a baseline run and an MCP run using the same model + temperature + harness settings where possible.
2. Save final outputs and raw traces separately.
3. Normalize traces: `python scripts/extract_trace.py --input <run-dir> --output <trace.json>`
4. Compare trace metrics: `python scripts/compare_trace_metrics.py --baseline <baseline-trace.json> --mcp <mcp-trace.json> --task-manifest tasks/.../demo_manifest.json`
5. For direct tasks, compare the produced file/report/code diff and score using the included checklist/test assets in `eval/` (or your own local harness verifier).

## Direct vs artifact notes

- These tasks were audited under `baseline-local-direct` vs `mcp-remote-direct`.
- Many direct tasks still include artifact-aware verifier shims; use them only if you intentionally run an artifact-output variant.

