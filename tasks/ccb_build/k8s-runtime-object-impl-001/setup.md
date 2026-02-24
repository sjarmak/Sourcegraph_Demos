# Setup (k8s-runtime-object-impl-001)

- Suite: `ccb_build`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/workspace/api/`, `/workspace/apimachinery/`, `/workspace/implementors.json`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Clone commands inferred from the original CCB task Dockerfiles (pinned when present):

```bash
# Dockerfile
git clone --depth 1 https://github.com/sg-evals/api--f32ed1d6.git api
git clone --depth 1 https://github.com/sg-evals/apimachinery--b2e9f88f.git apimachinery
# Dockerfile.artifact_only
git clone --depth 1 https://github.com/kubernetes/api.git api && cd api && git fetch --depth 1 origin f32ed1d60cf0787a512bebd6c06a4b84ae0b7cc7 && git checkout f32ed1d60cf0787a512bebd6c06a4b84ae0b7cc7
git clone --depth 1 https://github.com/kubernetes/apimachinery.git apimachinery && cd apimachinery && git fetch --depth 1 origin b2e9f88ff6d4c50c13061a53b1239c7707354eda && git checkout b2e9f88ff6d4c50c13061a53b1239c7707354eda
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/api--f32ed1d6`
- `github.com/sg-evals/apimachinery--b2e9f88f`

## Dependency hints (from task Dockerfiles)

These are not mandatory if your harness already provides them, but they reflect the CCB task environment:
- `apt-get update -qq && apt-get install -y -qq --no-install-recommends git curl ca-certificates python3 python3-pip jq && rm -rf /var/lib/apt/lists/*`
- `apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 curl && rm -rf /var/lib/apt/lists/*`

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

