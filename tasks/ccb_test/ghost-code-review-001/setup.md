# Setup (ghost-code-review-001)

- Suite: `ccb_test`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/workspace/review.json`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Clone commands inferred from the original CCB task Dockerfiles (pinned when present):

```bash
# Dockerfile
git clone --depth 1 https://github.com/sg-evals/Ghost--b43bfc85.git /workspace && cd /workspace && git config user.email "agent@example.com" && git config user.name "Agent"
# Dockerfile.artifact_only
git clone --filter=blob:none --no-checkout https://github.com/TryGhost/Ghost.git /workspace && cd /workspace && git checkout b43bfc85b719ab3971b83b5ef954601bf2d95fbf && git config user.email "agent@example.com" && git config user.name "Agent"
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/Ghost--b43bfc85`

## Dependency hints (from task Dockerfiles)

These are not mandatory if your harness already provides them, but they reflect the CCB task environment:
- `apt-get update && apt-get install -y --no-install-recommends git ca-certificates curl python3 ripgrep && rm -rf /var/lib/apt/lists/*`
- `if ! command -v node &> /dev/null; then curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y --no-install-recommends nodejs; fi`
- `apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 curl ripgrep && rm -rf /var/lib/apt/lists/*`
- `if ! command -v node > /dev/null 2>&1; then curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y --no-install-recommends nodejs; fi`

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

