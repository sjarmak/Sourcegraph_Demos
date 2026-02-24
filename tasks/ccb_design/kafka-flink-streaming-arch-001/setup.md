# Setup (kafka-flink-streaming-arch-001)

- Suite: `ccb_design`
- Comparison mode in audit: `direct` (`baseline-local-direct` vs `mcp-remote-direct`)
- Output contract(s): `/logs/agent/solution.md`

## Required environment variables

- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)
- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)
- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.

## Local repo checkout (which one to use)

Use the following checkout commands based on the run style you want to reproduce:

### Dockerfile.artifact_only

Artifact-output local variant (use when you want a minimal local checkout and plan to produce an artifact like `answer.json`).

```bash
git clone --filter=blob:none --no-checkout https://github.com/apache/kafka.git /workspace/kafka && cd /workspace/kafka && git checkout 0753c489afad403fb6e78fda4c4a380e46f500c0 && git config user.email "agent@example.com" && git config user.name "Agent"
git clone --filter=blob:none --no-checkout https://github.com/apache/flink.git /workspace/flink && cd /workspace/flink && git checkout 0cc95fcc145eddcfc87fc1b4ddf96ddd0f2ee15f && git config user.email "agent@example.com" && git config user.name "Agent"
```

Recommended local usage:
- Baseline run (`instruction.md`): use the available checkout variant (`Dockerfile.artifact_only` section) and keep the task output format from `instruction.md`.
- MCP run (`instruction_mcp.md`): usually reuse the same local checkout and enable Sourcegraph MCP.
- `Dockerfile.artifact_only` / `Dockerfile.sg_only` variants are optional and mostly useful if you want to mimic those benchmark modes.

## Sourcegraph MCP repo scope

Use these Sourcegraph mirror repos for the MCP run:
- `github.com/sg-evals/kafka--0753c489`
- `github.com/sg-evals/flink--0cc95fcc`

## Dependencies (Linux / macOS / Windows)

Install these tools before running the task locally:

- Required tools: `git`, `curl`, `python3`, `java`

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y git curl python3 python3-pip openjdk-17-jdk
```

### macOS (Homebrew)

```bash
# Install Homebrew first if needed: https://brew.sh/
brew install git curl python openjdk@17
# Set JAVA_HOME if your task/verifier needs it.
```

### Windows (PowerShell)

Windows note: WSL2 is often the easiest option for shell-heavy verifiers, but native PowerShell + winget works for many tasks.

```powershell
winget install --id Git.Git -e
winget install --id curl.curl -e
winget install --id Python.Python.3.11 -e
winget install --id EclipseAdoptium.Temurin.17.JDK -e
# Set JAVA_HOME after JDK installation if required.
```

## Run pattern (local ablation)

1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).
2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).
3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).
4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.
5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.

