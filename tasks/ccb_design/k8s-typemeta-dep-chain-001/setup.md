# Setup (k8s-typemeta-dep-chain-001)

- Suite: `ccb_design`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/workspace/kubernetes/`, `/workspace/api/`, `/workspace/apimachinery/`, `/workspace/kubernetes/staging/src/k8s.io/api/core/v1/types.go`, `/workspace/chain.json`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Clone commands inferred from the original CCB task Dockerfiles (pinned when present):

```bash
# Dockerfile
git clone --depth 1 https://github.com/sg-evals/kubernetes--31bf3ed4.git kubernetes
git clone --depth 1 https://github.com/sg-evals/api--f32ed1d6.git api
git clone --depth 1 https://github.com/sg-evals/apimachinery--b2e9f88f.git apimachinery
# Dockerfile.artifact_only
git clone https://github.com/kubernetes/kubernetes.git kubernetes && cd kubernetes && git checkout 31bf3ed48b91b67e5003d8df1b3bd0b918d1fb94
git clone https://github.com/kubernetes/api.git api && cd api && git checkout f32ed1d60cf0787a512bebd6c06a4b84ae0b7cc7
git clone https://github.com/kubernetes/apimachinery.git apimachinery && cd apimachinery && git checkout b2e9f88ff6d4c50c13061a53b1239c7707354eda
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/kubernetes--31bf3ed4`
- `github.com/sg-evals/api--f32ed1d6`
- `github.com/sg-evals/apimachinery--b2e9f88f`

## Dependency hints (from task Dockerfiles)

These are not mandatory if your harness already provides them, but they reflect the CCB task environment:
- `apk add --no-cache git bash python3`
- `apk add --no-cache git python3 curl bash`

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

