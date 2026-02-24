# Setup (ghost-code-review-001)

- Suite: `ccb_test`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/workspace/review.json`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (which one to use)

Use the following checkout commands based on the run style you want to reproduce:

### Dockerfile

Primary local checkout/environment (recommended starting point for local runs).

```bash
git clone --depth 1 https://github.com/sg-evals/Ghost--b43bfc85.git /workspace && cd /workspace && git config user.email "agent@example.com" && git config user.name "Agent"
```

### Dockerfile.artifact_only

Artifact-output local variant (use when you want a minimal local checkout and plan to produce an artifact like `answer.json`).

```bash
git clone --filter=blob:none --no-checkout https://github.com/TryGhost/Ghost.git /workspace && cd /workspace && git checkout b43bfc85b719ab3971b83b5ef954601bf2d95fbf && git config user.email "agent@example.com" && git config user.name "Agent"
```

Recommended local usage:
- Baseline run (`instruction.md`): use the **primary local checkout** (`Dockerfile` section).
- MCP run (`instruction_mcp.md`): usually reuse the same local checkout and enable Sourcegraph MCP.
- `Dockerfile.artifact_only` / `Dockerfile.sg_only` variants are optional and mostly useful if you want to mimic those benchmark modes.

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/Ghost--b43bfc85`

## Dependencies (Linux / macOS / Windows)

Install these tools before running the task locally:

- Required tools: `git`, `curl`, `python3`, `nodejs`, `npm`

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y git curl python3 python3-pip nodejs npm
```

### macOS (Homebrew)

```bash
# Install Homebrew first if needed: https://brew.sh/
brew install git curl python node
```

### Windows (PowerShell)

Windows note: WSL2 is often the easiest option for shell-heavy verifiers, but native PowerShell + winget works for many tasks.

```powershell
winget install --id Git.Git -e
winget install --id curl.curl -e
winget install --id Python.Python.3.11 -e
winget install --id OpenJS.NodeJS.LTS -e
```

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

