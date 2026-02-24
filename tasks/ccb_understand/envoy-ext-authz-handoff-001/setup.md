# Setup (envoy-ext-authz-handoff-001)

- Suite: `ccb_understand`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/logs/agent/onboarding.md`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (which one to use)

Use the following checkout commands based on the run style you want to reproduce:

### Dockerfile

Primary local checkout/environment (recommended starting point for local runs).

```bash
git clone --depth 1 https://github.com/sg-evals/envoy--v1.32.1.git /workspace
```

### Dockerfile.artifact_only

Artifact-output local variant (use when you want a minimal local checkout and plan to produce an artifact like `answer.json`).

```bash
git clone https://github.com/envoyproxy/envoy.git /workspace && cd /workspace && git checkout v1.32.1
```

Recommended local usage:
- Baseline run (`instruction.md`): use the **primary local checkout** (`Dockerfile` section).
- MCP run (`instruction_mcp.md`): usually reuse the same local checkout and enable Sourcegraph MCP.
- `Dockerfile.artifact_only` / `Dockerfile.sg_only` variants are optional and mostly useful if you want to mimic those benchmark modes.

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/envoy--v1.32.1`

## Dependencies (Linux / macOS / Windows)

Install these tools before running the task locally:

- Required tools: `git`, `curl`, `python3`

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y git curl python3 python3-pip
```

### macOS (Homebrew)

```bash
# Install Homebrew first if needed: https://brew.sh/
brew install git curl python
```

### Windows (PowerShell)

Windows note: WSL2 is often the easiest option for shell-heavy verifiers, but native PowerShell + winget works for many tasks.

```powershell
winget install --id Git.Git -e
winget install --id curl.curl -e
winget install --id Python.Python.3.11 -e
```

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

