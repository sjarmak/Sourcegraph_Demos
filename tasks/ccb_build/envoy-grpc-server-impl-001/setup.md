# Setup (envoy-grpc-server-impl-001)

- Suite: `ccb_build`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/workspace/go-control-plane/`, `/workspace/istio/`, `/workspace/emissary/`, `/workspace/implementors.json`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Clone commands inferred from the original CCB task Dockerfiles (pinned when present):

```bash
# Dockerfile
git clone --depth 1 https://github.com/sg-evals/go-control-plane--71637ad6.git go-control-plane
git clone --depth 1 https://github.com/sg-evals/istio--2300e245.git istio
git clone --depth 1 https://github.com/sg-evals/emissary--3bbdbe0f.git emissary
# Dockerfile.artifact_only
git clone --depth 1 https://github.com/envoyproxy/go-control-plane.git go-control-plane && cd go-control-plane && git fetch --depth 1 origin 71637ad69bbc5f51fbb2562e612a4365292804a5 && git checkout 71637ad69bbc5f51fbb2562e612a4365292804a5
git clone --depth 1 https://github.com/istio/istio.git istio && cd istio && git fetch --depth 1 origin 2300e2458ab713c2c514a58da1ea8b03343ada7e && git checkout 2300e2458ab713c2c514a58da1ea8b03343ada7e
git clone --depth 1 https://github.com/emissary-ingress/emissary.git emissary && cd emissary && git fetch --depth 1 origin 3bbdbe0fafcc9dd6b9f54935d34f6614afb49302 && git checkout 3bbdbe0fafcc9dd6b9f54935d34f6614afb49302
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/go-control-plane--71637ad6`
- `github.com/sg-evals/istio--2300e245`
- `github.com/sg-evals/emissary--3bbdbe0f`

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

