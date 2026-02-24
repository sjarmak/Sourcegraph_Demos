#!/bin/bash
# CodeContextBench Task Setup Script
# Creates a local testing workspace for any CCB task
# 
# Usage: setup-ccb-task.sh <task-name>
#        setup-ccb-task.sh <suite>/<task-name>
#        setup-ccb-task.sh --list
#
# Creates workspaces in the current directory
# 
# Examples:
#   cd ~/Sourcegraph_Demos
#   ./scripts/setup-ccb-task.sh --list
#   ./scripts/setup-ccb-task.sh cilium-project-orient-001
#
#   # Or from anywhere with explicit path to tasks:
#   setup-ccb-task.sh --tasks ~/Sourcegraph_Demos/tasks cilium-project-orient-001

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Paths - auto-detect task directory
# If running from scripts/ subdirectory, look in ../tasks
# Otherwise default to ./tasks
if [ -d "../tasks" ] && [ ! -d "./tasks" ]; then
    TASK_BASE="${TASK_BASE:-../tasks}"
else
    TASK_BASE="${TASK_BASE:-./tasks}"
fi

# Convert TASK_BASE to absolute path so it works after cd operations
TASK_BASE="$(cd "$TASK_BASE" 2>/dev/null && pwd)" || TASK_BASE="."

# Functions
print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  CodeContextBench Task Setup                                   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
}

print_error() {
    echo -e "${RED}❌ ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_usage() {
    cat << 'USAGE'
USAGE: setup-ccb-task.sh [OPTION] [TASK]

Creates a task workspace in the current directory.

OPTIONS:
  --help, -h              Show this help message
  --list, -l              List all available tasks
  --setup-all, -a         Set up ALL available tasks
  --tasks PATH            Path to tasks directory (default: ./tasks)

ARGUMENTS:
  TASK                    Task to set up
                          - Task name only: cilium-project-orient-001
                          - With suite: ccb_understand/cilium-project-orient-001

EXAMPLES:
  # From Sourcegraph_Demos directory:
  cd ~/Sourcegraph_Demos
  ./scripts/setup-ccb-task.sh --list
  ./scripts/setup-ccb-task.sh cilium-project-orient-001
  cd cilium-project-orient-001-setup
  cat RUN_GUIDE.md

  # Set up all tasks at once:
  ./scripts/setup-ccb-task.sh --setup-all

  # From anywhere with explicit path:
  setup-ccb-task.sh --tasks ~/Sourcegraph_Demos/tasks argocd-arch-orient-001

USAGE
}

show_usage_short() {
    echo "Usage: setup-ccb-task.sh [--list] [--setup-all] [--tasks PATH] [TASK]"
    echo "Run with --help for more information"
}

list_tasks() {
    echo "Available Tasks:"
    echo ""
    
    if [ ! -d "$TASK_BASE" ]; then
        print_error "Task directory not found at $TASK_BASE"
        exit 1
    fi
    
    local count=0
    for suite_dir in "$TASK_BASE"/*; do
        if [ -d "$suite_dir" ]; then
            local suite=$(basename "$suite_dir")
            echo "📁 Suite: $suite"
            
            for task_dir in "$suite_dir"/*; do
                if [ -d "$task_dir" ]; then
                    local task=$(basename "$task_dir")
                    local toml_file="$task_dir/task.toml"
                    
                    if [ -f "$toml_file" ]; then
                        local description=$(grep '^description = ' "$toml_file" | head -1 | sed 's/description = "//' | sed 's/".*//')
                        printf "   • %-45s %s\n" "$task" "$description"
                        count=$((count + 1))
                    fi
                fi
            done
            echo ""
        fi
    done
    
    echo "Total: $count tasks"
}

find_task_dir() {
    local task_spec="$1"
    local task_dir
    
    # If contains slash, it's suite/task format
    if [[ "$task_spec" == *"/"* ]]; then
        task_dir="$TASK_BASE/$task_spec"
        if [ -d "$task_dir" ]; then
            # Return absolute path
            cd "$task_dir" && pwd && cd - > /dev/null
            return 0
        fi
    else
        # Search all suites for task name
        for suite_dir in "$TASK_BASE"/*; do
            if [ -d "$suite_dir" ]; then
                task_dir="$suite_dir/$task_spec"
                if [ -d "$task_dir" ]; then
                    # Return absolute path
                    cd "$task_dir" && pwd && cd - > /dev/null
                    return 0
                fi
            fi
        done
    fi
    
    return 1
}

setup_all_tasks() {
    # Temporarily disable set -e for batch operations so one task failure doesn't stop the loop
    set +e
    
    if [ ! -d "$TASK_BASE" ]; then
        print_error "Task directory not found at $TASK_BASE"
        set -e
        exit 1
    fi
    
    # Collect all tasks first to show summary
    local tasks=()
    for suite_dir in "$TASK_BASE"/*; do
        if [ -d "$suite_dir" ]; then
            for task_dir in "$suite_dir"/*; do
                if [ -d "$task_dir" ] && [ -f "$task_dir/task.toml" ]; then
                    local task_name=$(basename "$task_dir")
                    tasks+=("$task_dir")
                fi
            done
        fi
    done
    
    local count=${#tasks[@]}
    
    echo ""
    print_info "Found $count tasks to set up"
    echo ""
    echo "This will create $count workspace directories in the current location."
    echo ""
    read -p "Continue? (y/n) " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        exit 0
    fi
    
    echo ""
    echo "Setting up all tasks..."
    echo ""
    
    local success=0
    local failed=0
    
    for task_dir in "${tasks[@]}"; do
        local task_name=$(basename "$task_dir")
        
        setup_workspace "$task_dir" "silent"
        local result=$?
        if [ $result -eq 0 ]; then
            ((success++))
        else
            print_warning "Failed to set up $task_name (exit code: $result)"
            ((failed++))
        fi
    done
    
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    print_success "Setup complete!"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Summary:"
    echo "  ✅ Successfully set up: $success"
    if [ $failed -gt 0 ]; then
        echo "  ⚠️  Skipped: $failed (already exist)"
    fi
    echo ""
    echo "All workspaces created in current directory."
    echo ""
    echo "Next steps:"
    echo "  cd TASK_NAME-setup"
    echo "  cat RUN_GUIDE.md"
    echo ""
    
    # Re-enable set -e
    set -e
}

extract_clone_commands() {
    local setup_file="$1"
    local envfile="${2:-Dockerfile}"
    local python_output=""

    # Try JSON first (demo_manifest.json format)
    if [[ "$setup_file" == *.json ]] && command -v python3 &> /dev/null; then
        python_output=$(python3 << PYEOF 2>/dev/null
import json
try:
    with open("$setup_file") as f:
        data = json.load(f)
        cmds = [cmd for cmd in data.get("clone_commands_by_envfile", {}).get("$envfile", []) if cmd]
    if cmds:
        print("\n".join(cmds))
except Exception:
    pass
PYEOF
        )

        if [ -n "$python_output" ]; then
            printf '%s\n' "$python_output"
            return 0
        fi
    fi
    
    # Fallback: parse from setup.md
    # Extract section starting with "### Dockerfile"
    local in_section=0
    local found=1
    while IFS= read -r line; do
        if [[ "$line" == "### $envfile" ]]; then
            in_section=1
            found=0
        elif [[ "$line" == "### "* ]] && [ $in_section -eq 1 ]; then
            break
        elif [ $in_section -eq 1 ]; then
            local trimmed="${line#${line%%[![:space:]]*}}"
            if [[ "$trimmed" == git\ clone* ]]; then
                echo "$trimmed"
                found=0
            fi
        fi
    done < "$setup_file"

    if [ $found -eq 0 ]; then
        return 0
    fi

    # Last resort: grab any git clone commands in setup.md when no structured section exists
    if [[ "$setup_file" == *.md ]]; then
        local loose_cmds=()
        while IFS= read -r line; do
            local trimmed="${line#${line%%[![:space:]]*}}"
            trimmed="${trimmed%${trimmed##*[![:space:]]}}"
            if [[ "$trimmed" == git\ clone* ]]; then
                loose_cmds+=("$trimmed")
            fi
        done < "$setup_file"

        if [ ${#loose_cmds[@]} -gt 0 ]; then
            printf '%s\n' "${loose_cmds[@]}"
            return 0
        fi
    fi

    return $found
}

rewrite_clone_command_for_local() {
    local raw_cmd="$1"
    local source_dir="$2"
    local escaped_source_dir
    local workspace_placeholder='$WORKSPACE'
    local workspace_brace_placeholder='${WORKSPACE}'

    escaped_source_dir=$(printf '%q' "$source_dir")

    local fixed_cmd="$raw_cmd"
    fixed_cmd=${fixed_cmd//\/workspace/$escaped_source_dir}
    fixed_cmd=${fixed_cmd//${workspace_placeholder}/$escaped_source_dir}
    fixed_cmd=${fixed_cmd//${workspace_brace_placeholder}/$escaped_source_dir}
    echo "$fixed_cmd"
}

extract_mcp_repo() {
    local setup_file="$1"
    
    # Try JSON first
    if [[ "$setup_file" == *.json ]] && command -v python3 &> /dev/null; then
        python3 << PYEOF 2>/dev/null
import json
try:
    with open("$setup_file") as f:
        data = json.load(f)
        repos = data.get("mcp_mirror_repos", [])
        if repos:
            print(repos[0])
except:
    pass
PYEOF
    fi
    
    # Fallback: parse from setup.md
    sed -n '/## Sourcegraph MCP repo scope/,/^$/p' "$setup_file" | grep "github.com" | head -1 | sed 's/.*- //' | sed 's/^`//;s/`$//'
}

extract_required_tools() {
    local setup_file="$1"
    
    # Try JSON first
    if [[ "$setup_file" == *.json ]] && command -v python3 &> /dev/null; then
        python3 << PYEOF 2>/dev/null
import json
try:
    with open("$setup_file") as f:
        data = json.load(f)
        tools = data.get("required_tools", [])
        if tools:
            echo "${tools[@]}" | tr ' ' '\n'
except:
    pass
PYEOF
    fi
}

get_clone_commands_for_task() {
    local task_dir="$1"
    local envfile="${2:-Dockerfile}"
    local candidates=("$task_dir/demo_manifest.json" "$task_dir/setup.md")
    local env_candidates=()
    local env_seen=""

    if [ -n "$envfile" ]; then
        env_candidates+=("$envfile")
    fi
    env_candidates+=("Dockerfile" "Dockerfile.sg_only" "Dockerfile.artifact_only" "Dockerfile.baseline" "Dockerfile.base")

    for env in "${env_candidates[@]}"; do
        [ -n "$env" ] || continue
        if [[ " $env_seen " == *" $env "* ]]; then
            continue
        fi
        env_seen+=" $env"

        for candidate in "${candidates[@]}"; do
            [ -f "$candidate" ] || continue
            local cmds=()
            while IFS= read -r cmd; do
                [ -n "$cmd" ] && cmds+=("$cmd")
            done < <(extract_clone_commands "$candidate" "$env" 2>/dev/null || true)

            if [ ${#cmds[@]} -gt 0 ]; then
                printf '%s\n' "${cmds[@]}"
                return 0
            fi
        done
    done

    return 1
}

clone_source_code() {
    local task_dir="$1"
    local workspace_dir="$2"
    local clone_cmds=()

    while IFS= read -r cmd; do
        [ -n "$cmd" ] && clone_cmds+=("$cmd")
    done < <(get_clone_commands_for_task "$task_dir" "Dockerfile" 2>/dev/null || true)

    if [ ${#clone_cmds[@]} -eq 0 ]; then
        return 1
    fi

    mkdir -p "$workspace_dir/source"
    cd "$workspace_dir/source" || return 1
    local source_dir=$(pwd)

    for cmd in "${clone_cmds[@]}"; do
        local adjusted_cmd
        adjusted_cmd=$(rewrite_clone_command_for_local "$cmd" "$source_dir")
        if ! eval "$adjusted_cmd"; then
            cd - > /dev/null
            return 1
        fi
    done

    cd - > /dev/null
    return 0
}

print_manual_clone_help() {
    local task_dir="$1"
    local workspace_dir="$2"
    
    local commands=()
    while IFS= read -r cmd; do
        [ -n "$cmd" ] && commands+=("$cmd")
    done < <(get_clone_commands_for_task "$task_dir" "Dockerfile" 2>/dev/null || true)
    
    if [ ${#commands[@]} -eq 0 ]; then
        echo "  See setup.md for clone instructions"
        return
    fi

    local source_dir="$workspace_dir/source"
    if [ -d "$source_dir" ]; then
        source_dir=$(cd "$source_dir" && pwd)
    fi

    echo "  Run the following inside $source_dir:"
    for cmd in "${commands[@]}"; do
        [ -z "$cmd" ] && continue
        local adjusted
        adjusted=$(rewrite_clone_command_for_local "$cmd" "$source_dir")
        echo "    $adjusted"
    done
}

setup_workspace() {
    local task_dir="$1"
    local silent="${2:-false}"
    local task_name=$(basename "$task_dir")
    local suite_name=$(basename $(dirname "$task_dir"))
    local workspace_dir="${task_name}-setup"
    local orig_dir=$(pwd)
    local workspace_path="$orig_dir/$workspace_dir"
    
    if [ "$silent" != "silent" ]; then
        print_info "Task: $task_name"
        print_info "Suite: $suite_name"
        print_info "Creating workspace: $workspace_dir"
        echo ""
    else
        # In silent mode, still output task name for progress
        echo "Setting up $task_name..."
    fi
    
    # Check if workspace already exists
    local workspace_exists=false
    if [ -d "$workspace_dir" ]; then
        workspace_exists=true
        if [ "$silent" != "silent" ]; then
            print_warning "Workspace already exists at $workspace_dir"
            read -p "Overwrite? (y/n) " -r
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Cancelled"
                exit 1
            fi
            rm -rf "$workspace_dir"
            workspace_exists=false
        fi
    fi
    
    # Create directory structure (unless already exists)
    if [ "$workspace_exists" = false ]; then
        mkdir -p "$workspace_dir"
    fi
    
    cd "$workspace_dir"
    
    mkdir -p runs/{baseline,mcp}
    mkdir -p source
    mkdir -p logs/{agent,verifier}
    mkdir -p eval
    
    print_success "Created directory structure"
    
    # Copy evaluation files
    if [ -d "$task_dir/eval" ]; then
        cp -r "$task_dir/eval"/* eval/ 2>/dev/null || true
        print_success "Copied evaluation files"
    fi
    
    # Copy instruction files
    if [ -f "$task_dir/instruction.md" ]; then
        cp "$task_dir/instruction.md" . || true
        if [ "$silent" != "silent" ]; then
            print_success "Copied baseline instruction"
        fi
    fi
    
    if [ -f "$task_dir/instruction_mcp.md" ]; then
        cp "$task_dir/instruction_mcp.md" . || true
        if [ "$silent" != "silent" ]; then
            print_success "Copied MCP instruction"
        fi
    fi
    
    # Copy supporting docs
    for doc in setup.md README.md talk_track.md evaluation.md demo_manifest.json; do
        if [ -f "$task_dir/$doc" ]; then
            cp "$task_dir/$doc" . || true
        fi
    done
    
    # Copy environment files for reference
    if [ -d "$task_dir/environment" ]; then
        mkdir -p environment
        cp -r "$task_dir/environment"/* environment/ 2>/dev/null || true
    fi
    
    # Return to original directory BEFORE cloning
    cd "$orig_dir"
    
    # Auto-clone source code for baseline
    if [ "$silent" != "silent" ]; then
        echo ""
        print_info "Setting up source code for baseline..."
    fi
    if clone_source_code "$task_dir" "$workspace_path"; then
        if [ "$silent" != "silent" ]; then
            print_success "Source code cloned to $workspace_dir/source"
        fi
    else
        if [ "$silent" != "silent" ]; then
            print_warning "Could not auto-clone source code"
            print_manual_clone_help "$task_dir" "$workspace_path"
        fi
    fi
    
    # Create RUN_GUIDE.md AFTER cloning (so source status is accurate)
    cd "$workspace_path"
    generate_run_guide "." "$task_name" "$suite_name"
    cd "$orig_dir"
    
    if [ "$silent" != "silent" ]; then
        print_success "Workspace setup complete!"
        echo ""
        echo "Next steps:"
        echo "  cd $workspace_dir"
        echo "  cat RUN_GUIDE.md"
        echo ""
    fi
}

generate_run_guide() {
    local workspace="$1"
    local task_name="$2"
    local suite_name="$3"
    
    # Extract setup metadata
    local setup_file=""
    local mcp_repo=""
    if [ -f "$workspace/demo_manifest.json" ]; then
        setup_file="$workspace/demo_manifest.json"
    elif [ -f "$workspace/setup.md" ]; then
        setup_file="$workspace/setup.md"
    fi
    
    if [ -n "$setup_file" ]; then
        mcp_repo=$(extract_mcp_repo "$setup_file")
    fi
    
    local source_status="✅ Ready (source/ already cloned)"
    if [ ! -d "$workspace/source/.git" ]; then
        source_status="⚠️  Manual setup required (see below)"
    fi
    
    cat > "$workspace/RUN_GUIDE.md" << EOF
# Task Execution Guide

This workspace contains everything needed to run the baseline and MCP variants of this task.

## Directory Structure

\`\`\`
.
├── RUN_GUIDE.md              # This file
├── instruction.md            # Baseline task prompt
├── instruction_mcp.md        # MCP task prompt  
├── eval/                     # Evaluation tools
│   ├── ground_truth.json     # Scoring criteria
│   ├── test.sh               # Scoring script
│   └── ...
├── runs/
│   ├── baseline/             # Baseline output directory
│   └── mcp/                  # MCP output directory
├── source/                   # Local source code (baseline)
├── logs/                     # Log output
└── setup.md                  # Task-specific setup instructions
\`\`\`

## Status

Source Code: $source_status

EOF
    
    # Add environment setup if needed
    if [ -n "$setup_file" ]; then
        cat >> "$workspace/RUN_GUIDE.md" << 'ENVEOF'

## Environment Setup

### Required Environment Variables

The following environment variables are required for MCP runs:

```bash
export SOURCEGRAPH_URL=https://sourcegraph.com
export SOURCEGRAPH_ACCESS_TOKEN=sgp_xxxxx
```

Get token from: https://sourcegraph.com/user/settings/tokens

**Optional:** For harness-based evaluation, you may also need:
```bash
export ANTHROPIC_API_KEY=xxx
export OPENAI_API_KEY=xxx
export GOOGLE_API_KEY=xxx
```

ENVEOF
    fi
    
    cat >> "$workspace/RUN_GUIDE.md" << 'RUNEOF'

## Running the Task

### Option A: Baseline (Local Repository)

1. **Verify source code is present**:
   ```bash
   ls -la source/
   ```
   
   If empty or missing, see "Troubleshooting" section below.

2. **Run with Claude or your AI tool**:
   - Open `instruction.md`
   - Copy the full content
   - In Claude/other AI tool: attach the `source/` folder as context
   - Paste the instructions
   - Save output to `runs/baseline/answer.md`

3. **Score the output**:
   ```bash
   REPORT_PATH=runs/baseline/answer.md bash eval/test.sh
   ```

### Option B: MCP (Sourcegraph Remote)

**Important:** MCP runs do NOT use local source code. Instead, you'll search and navigate the repository using Sourcegraph MCP tools.

1. **Set up Sourcegraph credentials** (if not already set):
   ```bash
   export SOURCEGRAPH_URL=https://sourcegraph.com
   export SOURCEGRAPH_ACCESS_TOKEN=sgp_xxxxx
   ```

2. **Configure Sourcegraph MCP in Claude**:
   - Open Claude settings (gear icon)
   - Go to "Beta Features"
   - Enable "Model Context Protocol"
   - Verify Sourcegraph appears in available MCP servers

3. **Run the MCP variant**:
   - Open `instruction_mcp.md` (contains remote repo reference)
   - Copy the full content
   - Paste into Claude with MCP enabled
   - Use MCP tools to search/navigate the remote repository
   - Save output to `runs/mcp/answer.md`

4. **Score the output**:
   ```bash
   REPORT_PATH=runs/mcp/answer.md bash eval/test.sh
   ```

### Option C: Compare Baseline vs MCP

After running both variants:

```bash
echo "=== BASELINE ==="
REPORT_PATH=runs/baseline/answer.md bash eval/test.sh

echo ""
echo "=== MCP (REMOTE) ==="
REPORT_PATH=runs/mcp/answer.md bash eval/test.sh
```

## Scoring

The `eval/test.sh` script scores outputs by comparing them against `eval/ground_truth.json`.

### Quick Score Check

```bash
REPORT_PATH=runs/baseline/answer.md bash eval/test.sh
```

The final score appears at the end of output (0.0-1.0).

### View Scoring Criteria

```bash
cat eval/ground_truth.json | python3 -m json.tool
```

## Output Files

- `runs/baseline/answer.md` - Your baseline run output
- `runs/mcp/answer.md` - Your MCP run output
- `logs/verifier/reward.txt` - Score from last evaluation run
- `logs/agent/` - Agent execution logs (if any)

## Troubleshooting

### Q: Source code not present or incomplete

A: The setup script should have auto-cloned the source. If it didn't, you can manually clone:

```bash
cd source/
# See setup.md or instruction.md for the exact clone command
# Usually something like:
git clone --depth 1 https://github.com/<org>/<repo> . && git config user.email "agent@example.com" && git config user.name "Agent"
cd ..
```

Then verify:
```bash
ls -la source/
```

### Q: How do I add source as context in Claude?

A: 
1. In Claude, click the attachment icon (+)
2. Select "Folder"
3. Choose the `source/` directory
4. Paste the content of `instruction.md`

### Q: MCP isn't working

A:
1. Check your credentials:
   ```bash
   echo $SOURCEGRAPH_ACCESS_TOKEN
   ```
2. Verify MCP is enabled in Claude (Settings → Beta Features → Model Context Protocol)
3. Confirm Sourcegraph appears in Claude's MCP server list
4. Check the exact remote repository name in `instruction_mcp.md`

### Q: What repository should I use for MCP runs?

A: Check the "Target Repository" section in `instruction_mcp.md`. It should mention the Sourcegraph mirror repo.

RUNEOF
    
    if [ -n "$mcp_repo" ]; then
        cat >> "$workspace/RUN_GUIDE.md" << EOF

**MCP Mirror Repository:** \`$mcp_repo\`

EOF
    fi
    
    cat >> "$workspace/RUN_GUIDE.md" << 'EOF'

## Task Details

For comprehensive setup and execution information:
- `instruction.md` - Full baseline task description
- `instruction_mcp.md` - Full MCP task description (includes remote repo details)
- `setup.md` - Detailed setup, dependencies, and clone commands
- `eval/ground_truth.json` - Detailed scoring criteria and expected answers

EOF

    cat >> "$workspace/RUN_GUIDE.md" << EOF

---

**Task:** $task_name  
**Suite:** $suite_name  
**Created:** $(date)  
**Workspace:** $(pwd)

EOF
}

# Main
print_header

# Parse arguments
TASK_NAME=""
SETUP_ALL=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_usage
            exit 0
            ;;
        --list|-l)
            list_tasks
            exit $?
            ;;
        --setup-all|-a)
            SETUP_ALL=true
            shift
            ;;
        --tasks)
            TASK_BASE="$2"
            shift 2
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage_short
            exit 1
            ;;
        *)
            TASK_NAME="$1"
            shift
            ;;
    esac
done

# Handle setup-all
if [ "$SETUP_ALL" = true ]; then
    setup_all_tasks
    exit 0
fi

# Check we have a task
if [ -z "$TASK_NAME" ]; then
    print_error "No task specified"
    show_usage_short
    exit 1
fi

# Find task directory
if ! task_dir=$(find_task_dir "$TASK_NAME"); then
    print_error "Task not found: $TASK_NAME"
    echo ""
    echo "Run with --list to see available tasks"
    exit 1
fi

# Set up workspace
setup_workspace "$task_dir"
