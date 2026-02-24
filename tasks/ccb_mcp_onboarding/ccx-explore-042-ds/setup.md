# Setup (CCX-explore-042-ds)

- Suite: `ccb_mcp_onboarding`
- Comparison mode in audit: `artifact` (`baseline-local-artifact` vs `mcp-remote-artifact`)
- Output contract(s): `/workspace/answer.json`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Clone commands inferred from the original CCB task Dockerfiles (pinned when present):

```bash
# Dockerfile
git clone --depth 1 https://github.com/sg-evals/scikit-learn--1.6.1.git /workspace/scikit-learn
git clone --depth 1 https://github.com/sg-evals/numpy--v2.2.2.git /workspace/numpy
git clone --depth 1 https://github.com/sg-evals/pandas--v2.2.3.git /workspace/pandas
git clone --depth 1 https://github.com/sg-evals/scipy--v1.15.1.git /workspace/scipy
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/numpy`
- `github.com/sg-evals/pandas`
- `github.com/sg-evals/scikit-learn`
- `github.com/sg-evals/scipy`

## Dependency hints (from task Dockerfiles)

These are not mandatory if your harness already provides them, but they reflect the CCB task environment:
- `apt-get update && apt-get install -y --no-install-recommends git ca-certificates curl python3 python3-pip && rm -rf /var/lib/apt/lists/*`
- `apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 curl && rm -rf /var/lib/apt/lists/*`

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

