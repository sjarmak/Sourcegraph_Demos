# Setup (grpcurl-transitive-vuln-001)

- Suite: `ccb_secure`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/logs/agent/triage.md`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (baseline/direct or local reading)

Clone commands inferred from the original CCB task Dockerfiles (pinned when present):

```bash
# Dockerfile
git clone --depth 1 https://github.com/sg-evals/grpcurl--25c896aa.git grpcurl
git clone --depth 1 https://github.com/sg-evals/grpc-go--v1.56.2.git grpc-go
git clone https://go.googlesource.com/net && cd net && git checkout v0.14.0 && git describe --tags | grep -q "v0.14.0"
# Dockerfile.artifact_only
git clone https://github.com/fullstorydev/grpcurl.git grpcurl && cd grpcurl && git checkout 25c896aa59ffc36f7d12cf5d6c18e9c8f4421bfa && git log -1 --format="%H %s" | head -1 | grep -q "25c896a"
git clone https://github.com/grpc/grpc-go.git grpc-go && cd grpc-go && git checkout v1.56.2 && git log -1 --format="%H %s" | head -1 | grep -q "v1.56.2"
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/grpcurl--25c896aa`
- `github.com/sg-evals/grpc-go--v1.56.2`

## Dependency hints (from task Dockerfiles)

These are not mandatory if your harness already provides them, but they reflect the CCB task environment:
- `apt-get update && apt-get install -y --no-install-recommends jq bc git && rm -rf /var/lib/apt/lists/*`
- `apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 curl && rm -rf /var/lib/apt/lists/*`

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

