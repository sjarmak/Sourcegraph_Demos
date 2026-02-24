# Demo Talk Track (CCX-explore-042-ds)

- Why this task: `CCX-explore-042-ds` had an MCP positive delta of **+0.167** in the ccb_mcp_onboarding audit.
- Compared configs: `baseline-local-artifact` -> `mcp-remote-artifact` (baseline reward `0.6666`, MCP reward `0.8334`).
- Task type: `onboarding-comprehension` | Language: `python` | Difficulty: `hard`

## Suggested live demo flow (5-10 min)

1. Show `instruction.md` and point out the required output format.
2. Run a baseline/local-only attempt and save both output + trace.
3. Switch to `instruction_mcp.md`, show Sourcegraph repo scope + MCP requirement, run again.
4. Compare outputs (quality/completeness) and then compare traces with the scripts in `scripts/`.
5. Tie the observed behavior back to the audit delta and the task’s retrieval/exploration demands.

## What to highlight

- This is an **artifact** task: the agent should produce `answer.json` rather than patching code.
- Sourcegraph MCP is usually the main differentiator because the task requires cross-repo discovery/synthesis.

