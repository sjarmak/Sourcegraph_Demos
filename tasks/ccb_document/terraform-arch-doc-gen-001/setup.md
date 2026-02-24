# Setup (terraform-arch-doc-gen-001)

- Suite: `ccb_document`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/workspace/documentation.md`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Clone commands inferred from the original CCB task Dockerfiles (pinned when present):

```bash
# Dockerfile
git clone --depth 1 https://github.com/sg-evals/terraform--a3dc5711.git .
# Dockerfile.artifact_only
git clone --filter=blob:none --no-checkout https://github.com/hashicorp/terraform.git . && git checkout a3dc571150a7651a1a4a8b302342d26089c97795
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/terraform--7637a921`
- `github.com/sg-evals/terraform--24236f4f`

## Dependency hints (from task Dockerfiles)

These are not mandatory if your harness already provides them, but they reflect the CCB task environment:
- `apt-get update && apt-get install -y --no-install-recommends git python3 python3-pip ca-certificates && rm -rf /var/lib/apt/lists/*`
- `apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 curl && rm -rf /var/lib/apt/lists/*`

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

