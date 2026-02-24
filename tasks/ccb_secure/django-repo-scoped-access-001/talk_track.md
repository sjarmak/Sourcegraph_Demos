# Demo Talk Track (django-repo-scoped-access-001)

- Why this task: `django-repo-scoped-access-001` had an MCP positive delta of **+0.200** in the ccb_secure audit.
- Compared configs: `baseline-local-direct` -> `mcp-remote-direct` (baseline reward `0.5`, MCP reward `0.7`).
- IR/result pattern observed in audit: `Speed-to-context win`.
- Task type: `governance_repo_scoped` | Language: `python` | Difficulty: `medium`

## Suggested live demo flow (5-10 min)

1. Show `instruction.md` and point out the required output format.
2. Run a baseline/local-only attempt and save both output + trace.
3. Switch to `instruction_mcp.md`, show Sourcegraph repo scope + MCP requirement, run again.
4. Compare outputs (quality/completeness) and then compare traces with the scripts in `scripts/`.
5. Tie the observed behavior back to the audit delta and the task’s retrieval/exploration demands.

## What to highlight

- This is a **direct** task: compare both end quality and how quickly each run gets to relevant code context.
- Watch for fewer blind local searches / faster path to relevant files in the MCP run.

