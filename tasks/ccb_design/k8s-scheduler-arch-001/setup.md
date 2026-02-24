# Setup (k8s-scheduler-arch-001)

- Suite: `ccb_design`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/logs/agent/solution.md`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (which one to use)

Optional local clones (derived from instruction resources):

```bash
mkdir -p repos && cd repos
git clone https://github.com/kubernetes/kubernetes.git kubernetes
```

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/kubernetes--v1.30.0`

## Dependencies (Linux / macOS / Windows)

Install these tools before running the task locally:

- Required tools: `git`, `curl`, `python3`, `go`

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y git curl python3 python3-pip golang-go
```

### macOS (Homebrew)

```bash
# Install Homebrew first if needed: https://brew.sh/
brew install git curl python go
```

### Windows (PowerShell)

Windows note: WSL2 is often the easiest option for shell-heavy verifiers, but native PowerShell + winget works for many tasks.

```powershell
winget install --id Git.Git -e
winget install --id curl.curl -e
winget install --id Python.Python.3.11 -e
winget install --id GoLang.Go -e
```

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

