# Demo Talk Track (cilium-project-orient-001)

- Why this task: `cilium-project-orient-001` had an MCP positive delta of **+0.960** in the ccb_understand audit.
- Compared configs: `baseline-local-direct` -> `mcp-remote-direct` (baseline reward `0.0`, MCP reward `0.96`).
- IR/result pattern observed in audit: `Broader search win`.
- Task type: `codebase_orientation` | Language: `go` | Difficulty: `hard`

## Suggested live demo flow (5-10 min)

1. Show `instruction.md` and point out the required output format.
2. Run a baseline/local-only attempt and save both output + trace.
3. Switch to `instruction_mcp.md`, show Sourcegraph repo scope + MCP requirement, run again.
4. Compare outputs (quality/completeness) and then compare traces with the scripts in `scripts/`.
5. Tie the observed behavior back to the audit delta and the task’s retrieval/exploration demands.

## What to highlight

- This is a **direct** task: compare both end quality and how quickly each run gets to relevant code context.
- Watch for fewer blind local searches / faster path to relevant files in the MCP run.

