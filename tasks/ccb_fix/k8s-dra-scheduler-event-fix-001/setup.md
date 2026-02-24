# Setup (k8s-dra-scheduler-event-fix-001)

- Suite: `ccb_fix`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/logs/agent/solution.md`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Optional local clones (derived from instruction resources):

```bash
mkdir -p repos && cd repos
git clone https://github.com/kubernetes/kubernetes.git kubernetes
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/kubernetes--v1.30.0`

## Dependency hints (from task Dockerfiles)

These are not mandatory if your harness already provides them, but they reflect the CCB task environment:
- `apt-get update && apt-get install -y --no-install-recommends git curl python3 python3-pip ca-certificates && rm -rf /var/lib/apt/lists/*`

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

