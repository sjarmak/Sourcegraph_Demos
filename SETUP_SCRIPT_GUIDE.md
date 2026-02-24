# CCB Task Setup Script Guide

The `scripts/setup-ccb-task.sh` script automates the creation of local testing workspaces for CodeContextBench (CCB) tasks. It handles directory setup, source code cloning, and generates comprehensive run guides for both baseline and MCP execution modes.

## Quick Start

### Set up a single task

```bash
cd ~/sourcegraph_demos
./scripts/setup-ccb-task.sh cilium-project-orient-001
cd cilium-project-orient-001-setup
cat RUN_GUIDE.md
```

### List all available tasks

```bash
./scripts/setup-ccb-task.sh --list
```

### Set up all tasks at once

```bash
./scripts/setup-ccb-task.sh --setup-all
```

### Run from anywhere with explicit path

```bash
setup-ccb-task.sh --tasks ~/sourcegraph_demos/tasks my-task-name
```

## What the Script Does

### 1. **Directory Structure Creation**
Creates a workspace directory with the following structure:

```
task-name-setup/
├── instruction.md          # Baseline task instructions
├── instruction_mcp.md      # MCP variant instructions
├── setup.md               # Task-specific setup details
├── eval/                  # Evaluation scripts and ground truth
├── logs/                  # Output logs (agent/ and verifier/)
├── runs/                  # Output directories (baseline/ and mcp/)
├── source/                # Local source code (pre-cloned for baseline)
└── RUN_GUIDE.md          # Generated execution guide
```

### 2. **Source Code Auto-Cloning**
- Extracts clone commands from each task's `setup.md` or `demo_manifest.json`
- Automatically clones the Dockerfile (primary) variant into `source/`
- Handles clone failures gracefully with manual instructions
- Only clones for baseline; MCP runs use Sourcegraph remote repos

### 3. **RUN_GUIDE Generation**
Generates a comprehensive guide with:
- **Status section**: Shows if source code is ready or needs manual setup
- **Environment setup**: Lists required environment variables (SOURCEGRAPH_URL, SOURCEGRAPH_ACCESS_TOKEN, etc.)
- **Baseline instructions**: How to run with local source code
- **MCP instructions**: How to use Sourcegraph remote via MCP
- **Comparison workflow**: How to run both variants
- **Troubleshooting**: Common issues and solutions
- **Output file locations**: Where to save results and find scores

## Command Reference

### Basic Commands

```bash
# List all tasks
./scripts/setup-ccb-task.sh --list

# Set up a single task (auto-detects from ./tasks)
./scripts/setup-ccb-task.sh cilium-project-orient-001

# Set up all tasks
./scripts/setup-ccb-task.sh --setup-all

# Show help
./scripts/setup-ccb-task.sh --help
```

### Advanced Options

```bash
# Specify custom task directory
./scripts/setup-ccb-task.sh --tasks /path/to/tasks cilium-project-orient-001

# Set up specific task from anywhere
cd /some/other/dir
bash /path/to/setup-ccb-task.sh --tasks ~/sourcegraph_demos/tasks my-task

# List from custom task directory
./scripts/setup-ccb-task.sh --tasks /custom/path --list
```

## Generated Workspace Contents

After running the setup script, you get a fully prepared workspace:

### Files
- **instruction.md**: The baseline task prompt (with local source context)
- **instruction_mcp.md**: The MCP variant prompt (remote Sourcegraph repo)
- **RUN_GUIDE.md**: Step-by-step execution instructions
- **setup.md**: Task-specific dependencies and clone commands
- **demo_manifest.json**: Task metadata (title, repos, tools, etc.)
- **eval/ground_truth.json**: Scoring criteria and expected outputs
- **eval/test.sh**: Scoring script

### Directories
- **source/**: Pre-cloned local repository (baseline only)
- **runs/baseline/**: Where to save your baseline output
- **runs/mcp/**: Where to save your MCP output
- **logs/agent/**: Where agent execution logs are saved
- **logs/verifier/**: Where evaluation scores are written
- **eval/**: Evaluation tools and metrics

## Typical Workflow

### 1. Set up the workspace
```bash
./scripts/setup-ccb-task.sh your-task-name
cd your-task-name-setup
```

### 2. Run baseline variant
```bash
cat instruction.md
# Copy content + attach source/ folder in Claude
# Save output to runs/baseline/answer.md
```

### 3. Run MCP variant
```bash
export SOURCEGRAPH_ACCESS_TOKEN=sgp_xxxxx  # Set your token
cat instruction_mcp.md
# Copy + enable MCP in Claude + paste
# Save output to runs/mcp/answer.md
```

### 4. Score both
```bash
echo "=== BASELINE ==="
REPORT_PATH=runs/baseline/answer.md bash eval/test.sh

echo ""
echo "=== MCP ==="
REPORT_PATH=runs/mcp/answer.md bash eval/test.sh
```

## How It Works

### Auto-Cloning Logic

The script uses a two-pass approach:

1. **JSON parsing** (demo_manifest.json):
   ```json
   {
     "clone_commands_by_envfile": {
       "Dockerfile": ["git clone --depth 1 https://..."]
     }
   }
   ```

2. **Fallback parsing** (setup.md):
   ```markdown
   ### Dockerfile
   
   Primary local checkout/environment (recommended).
   
   git clone --depth 1 https://github.com/...
   ```

### RUN_GUIDE Variables

The script extracts and inserts:
- **MCP mirror repos** from `demo_manifest.json` mcp_mirror_repos field
- **Source status** by checking if source/.git exists
- **Environment variables** from setup.md or demo_manifest.json

## Troubleshooting

### Script not found
```bash
# Make sure scripts/ is in your PATH or use full path
./scripts/setup-ccb-task.sh --list
```

### Task not found
```bash
# List available tasks first
./scripts/setup-ccb-task.sh --list

# Or check tasks directory exists
ls tasks/*/
```

### Source clone fails
The script will show you the manual clone command:
```bash
cd your-task-setup/source
# Run the git clone command from the warning message
git clone --depth 1 https://... && git config user.email "agent@example.com" && git config user.name "Agent"
cd ..
```

### Workspace already exists
```bash
# Script will ask to overwrite
# Or delete and re-run
rm -rf task-name-setup
./scripts/setup-ccb-task.sh task-name
```

## Features

✅ **Auto-discovers tasks directory** from ./tasks (if run from repo root)  
✅ **Automatic source cloning** for baseline runs  
✅ **Extracts MCP mirror repos** for remote evaluation  
✅ **Generates comprehensive RUN guides** with environment setup  
✅ **Handles clone failures gracefully** with manual instructions  
✅ **Supports batch setup** with --setup-all  
✅ **Works from anywhere** with --tasks flag  
✅ **Returns absolute paths** for reliable file references  

## Environment Setup in Generated RUN_GUIDE

The generated RUN_GUIDE includes sections for:

```bash
# Required for MCP runs
export SOURCEGRAPH_URL=https://sourcegraph.com
export SOURCEGRAPH_ACCESS_TOKEN=sgp_xxxxx  # Get from https://sourcegraph.com/user/settings/tokens

# Optional for harness-based evaluation
export ANTHROPIC_API_KEY=xxx
export OPENAI_API_KEY=xxx
export GOOGLE_API_KEY=xxx
```

## File Reference

- **Main script**: `scripts/setup-ccb-task.sh`
- **Tasks directory**: `tasks/` (auto-detected)
- **Per-task structure**: `tasks/{suite}/{task-name}/`
- **Generated workspace**: `{task-name}-setup/`

## Examples

### Example 1: Cilium Orientation Task
```bash
./scripts/setup-ccb-task.sh cilium-project-orient-001
cd cilium-project-orient-001-setup
cat RUN_GUIDE.md
# Source code is in source/ (pre-cloned)
# Run instruction.md with Claude + source/ context
```

### Example 2: Check Status and Clone
```bash
./scripts/setup-ccb-task.sh argocd-arch-orient-001
cd argocd-arch-orient-001-setup
ls -la source/  # Check if cloned
# If empty, see RUN_GUIDE troubleshooting section
```

### Example 3: Batch Setup All Tasks
```bash
./scripts/setup-ccb-task.sh --setup-all <<< "y"
# Creates 37 workspace directories (one per task)
# Each ready to run immediately
```
