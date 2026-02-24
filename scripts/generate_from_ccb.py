#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import os
import re
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib  # py311+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CCB = Path("/home/stephanie_jarmak/CodeContextBench")
AUDIT_JSON = DEFAULT_CCB / "runs/staging/MCP_POSITIVE_DELTAS_VALID_TASKS_STAGING_CURRENT_20260224.json"
AUDIT_MD = DEFAULT_CCB / "runs/staging/MCP_POSITIVE_DELTAS_VALID_TASKS_STAGING_CURRENT_20260224.md"
IR_JSON = DEFAULT_CCB / "runs/staging/MCP_POSITIVE_DELTAS_VALID_TASKS_STAGING_CURRENT_20260224_ir_enrichment.json"
DEFAULT_MIN_DELTA = 0.2


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def safe_copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {n for n in names if n == "__pycache__" or n.endswith(".pyc")}
    shutil.copytree(src, dst, ignore=ignore)


def slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", s).strip("-")


def parse_toml(p: Path) -> dict[str, Any]:
    with p.open("rb") as f:
        return tomllib.load(f)


def extract_run_blocks(docker_text: str) -> list[str]:
    blocks: list[str] = []
    for m in re.finditer(r"^RUN\s+(.+?)(?=^\S|\Z)", docker_text, flags=re.M | re.S):
        block = m.group(1)
        block = re.sub(r"\\\n\s*", " ", block)
        block = re.sub(r"\s+", " ", block).strip()
        if block:
            blocks.append(block)
    return blocks


def extract_backtick_repos(text: str) -> list[str]:
    seen = []
    for m in re.findall(r"`(github\.com/[^`]+)`", text):
        if m not in seen:
            seen.append(m)
    return seen


def extract_mcp_scope_repos(text: str) -> list[str]:
    repos: list[str] = []
    for m in re.findall(r"^\s*-\s*`(github\.com/[^`]+)`", text, flags=re.M):
        if m not in repos:
            repos.append(m)
    for m in re.findall(r"\*\*Target Repository:\*\*\s*`(github\.com/[^`]+)`", text):
        if m not in repos:
            repos.append(m)
    for line in re.findall(r"\*\*Sourcegraph Repositories:\*\*\s*(.+)", text):
        for m in re.findall(r"`(github\.com/[^`]+)`", line):
            if m not in repos:
                repos.append(m)
    if repos:
        return repos
    return [r for r in extract_backtick_repos(text) if r.startswith("github.com/")]


def extract_available_resource_repos(text: str) -> list[dict[str, str | None]]:
    out: list[dict[str, str | None]] = []
    for repo, ver in re.findall(r"^-\s+`([^`]+)`(?:\s+at\s+([^\n]+))?", text, flags=re.M):
        if "/" not in repo:
            continue
        out.append({"repo": repo.strip(), "version": (ver or "").strip() or None})
    return out


def extract_output_paths(text: str) -> list[str]:
    paths = re.findall(r"(/(?:workspace|logs)/[^\s`'\"]+)", text)
    dedup: list[str] = []
    for p in paths:
        p = p.rstrip(".,)")
        if p not in dedup:
            dedup.append(p)
    return dedup


def extract_git_clone_commands(docker_text: str) -> list[str]:
    cmds: list[str] = []
    for block in extract_run_blocks(docker_text):
        if "git clone" in block and block not in cmds:
            cmds.append(block)
    return cmds


def extract_dep_hints(docker_text: str) -> list[str]:
    hints = []
    for block in extract_run_blocks(docker_text):
        if any(k in block for k in ["apt-get install", "apk add", "pip install", "pip3 install", "npm install", "npm i ", "yarn add", "pnpm add", "go install", "cargo install"]):
            if block not in hints:
                hints.append(block)
    return hints


def extract_package_names(docker_text: str) -> set[str]:
    pkgs: set[str] = set()
    for block in extract_run_blocks(docker_text):
        for pat in [r"apt-get install -y(?:\s+--no-install-recommends)?\s+(.+)", r"apk add(?:\s+--no-cache)?\s+(.+)"]:
            m = re.search(pat, block)
            if not m:
                continue
            tail = m.group(1).split("&&")[0].strip()
            for tok in re.split(r"\s+", tail):
                if not tok or tok.startswith("-"):
                    continue
                pkgs.add(tok.strip())
    return pkgs


def detect_required_tools(docker_texts: dict[str, str], task_language: str | None) -> list[str]:
    merged = "\n".join(docker_texts.values())
    text = merged.lower()
    pkgs = {p.lower() for p in extract_package_names(merged)}
    tools: set[str] = set()

    if "git clone" in text or "git" in pkgs:
        tools.add("git")
    if "curl" in text or "curl" in pkgs:
        tools.add("curl")
    if "python3" in text or "python3" in pkgs or "python:" in text:
        tools.add("python3")
    if "jq" in text or "jq" in pkgs:
        tools.add("jq")
    if "make" in text or "make" in pkgs:
        tools.add("make")
    if any(x in text for x in ["build-essential", "gcc", "g++", "clang", "musl-dev", "libc-dev"]):
        tools.add("c-build-tools")

    if any(x in text for x in ["golang-go", "golang:", " go build", " go test", "go install"]) or "golang-go" in pkgs:
        tools.add("go")
    if any(x in text for x in ["nodejs", "npm ", "npm install", "yarn ", "pnpm "]) or "nodejs" in pkgs or "npm" in pkgs:
        tools.update({"nodejs", "npm"})
    if any(x in text for x in ["openjdk", " java ", "eclipse-temurin", "jdk"]) or any(p.startswith("openjdk") for p in pkgs):
        tools.add("java")
    if "maven" in text or "mvn " in text or "maven" in pkgs:
        tools.add("maven")
    if any(x in text for x in ["dotnet", "aspnet", "mcr.microsoft.com/dotnet"]) or any("dotnet" in p for p in pkgs):
        tools.add("dotnet")
    if any(x in text for x in ["cargo ", "rustc", "rustup", "cargo install"]) or "cargo" in pkgs or "rustc" in pkgs:
        tools.update({"rust", "cargo"})

    lang = (task_language or "").lower()
    if lang == "go":
        tools.add("go")
    elif lang in {"python", "py"}:
        tools.add("python3")
    elif lang in {"javascript", "typescript", "js", "ts"}:
        tools.update({"nodejs", "npm"})
    elif lang in {"java", "kotlin", "scala"}:
        tools.add("java")
    elif lang in {"c#", "csharp", "dotnet"}:
        tools.add("dotnet")
    elif lang == "rust":
        tools.update({"rust", "cargo"})

    ordered = ["git", "curl", "python3", "jq", "make", "c-build-tools", "go", "nodejs", "npm", "java", "maven", "dotnet", "rust", "cargo"]
    return [t for t in ordered if t in tools]


def render_os_install_instructions(tools: list[str]) -> str:
    linux_map = {
        "git": "git", "curl": "curl", "python3": "python3 python3-pip", "jq": "jq", "make": "make",
        "c-build-tools": "build-essential", "go": "golang-go", "nodejs": "nodejs", "npm": "npm",
        "java": "openjdk-17-jdk", "maven": "maven", "dotnet": "dotnet-sdk-8.0", "rust": "rustc", "cargo": "cargo",
    }
    mac_map = {
        "git": "git", "curl": "curl", "python3": "python", "jq": "jq", "make": "make",
        "c-build-tools": "llvm", "go": "go", "nodejs": "node", "npm": "node",
        "java": "openjdk@17", "maven": "maven", "dotnet": "dotnet-sdk", "rust": "rustup-init", "cargo": "rustup-init",
    }
    win_map = {
        "git": "Git.Git", "curl": "curl.curl", "python3": "Python.Python.3.11", "jq": "jqlang.jq",
        "make": "GnuWin32.Make", "c-build-tools": "Microsoft.VisualStudio.2022.BuildTools",
        "go": "GoLang.Go", "nodejs": "OpenJS.NodeJS.LTS", "npm": "OpenJS.NodeJS.LTS",
        "java": "EclipseAdoptium.Temurin.17.JDK", "maven": "Apache.Maven", "dotnet": "Microsoft.DotNet.SDK.8",
        "rust": "Rustlang.Rustup", "cargo": "Rustlang.Rustup",
    }

    def pkgs(mapping: dict[str, str]) -> list[str]:
        out: list[str] = []
        for t in tools:
            pkg = mapping.get(t)
            if pkg and pkg not in out:
                out.append(pkg)
        return out

    linux_pkgs = pkgs(linux_map)
    mac_pkgs = pkgs(mac_map)
    win_pkgs = pkgs(win_map)

    lines: list[str] = []
    lines.append("## Dependencies (Linux / macOS / Windows)")
    lines.append("")
    lines.append("Install these tools before running the task locally:")
    lines.append("")
    lines.append("- Required tools: " + (", ".join(f"`{t}`" for t in tools) if tools else "`git`, `python3`, and the task runtime/toolchain`"))
    lines.append("")
    lines.append("### Linux (Ubuntu/Debian)")
    lines.append("")
    lines.append("```bash")
    lines.append("sudo apt-get update")
    if linux_pkgs:
        lines.append("sudo apt-get install -y " + " ".join(linux_pkgs))
    else:
        lines.append("# Install required tools manually")
    if "dotnet" in tools:
        lines.append("# If dotnet-sdk is unavailable, install the .NET SDK from Microsoft package repos.")
    lines.append("```")
    lines.append("")
    lines.append("### macOS (Homebrew)")
    lines.append("")
    lines.append("```bash")
    lines.append("# Install Homebrew first if needed: https://brew.sh/")
    if mac_pkgs:
        lines.append("brew install " + " ".join(mac_pkgs))
    else:
        lines.append("# Install required tools manually")
    if "rust" in tools or "cargo" in tools:
        lines.append("# `rustup-init` installs both rustc and cargo.")
    if "java" in tools:
        lines.append("# Set JAVA_HOME if your task/verifier needs it.")
    lines.append("```")
    lines.append("")
    lines.append("### Windows (PowerShell)")
    lines.append("")
    lines.append("Windows note: WSL2 is often the easiest option for shell-heavy verifiers, but native PowerShell + winget works for many tasks.")
    lines.append("")
    lines.append("```powershell")
    if win_pkgs:
        for pkg in win_pkgs:
            lines.append(f"winget install --id {pkg} -e")
    else:
        lines.append("# Install required tools manually")
    if "java" in tools:
        lines.append("# Set JAVA_HOME after JDK installation if required.")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def envfile_role(envfile: str) -> str:
    if envfile == "Dockerfile":
        return "Primary local checkout/environment (recommended starting point for local runs)."
    if envfile == "Dockerfile.artifact_only":
        return "Artifact-output local variant (use when you want a minimal local checkout and plan to produce an artifact like `answer.json`)."
    if envfile == "Dockerfile.sg_only":
        return "Sourcegraph/MCP-only benchmark variant (kept for provenance; usually not the local starting point)."
    return "Alternative environment variant."


def parse_task_style(task: dict[str, Any], audit_entry: dict[str, Any]) -> str:
    cfg = audit_entry.get("mcp_config", "")
    if cfg.endswith("-artifact"):
        return "artifact"
    if cfg.endswith("-direct"):
        return "direct"
    if task.get("task", {}).get("mcp_suite"):
        return "artifact"
    return "direct"


def bucket_map_from_ir(ir: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    labels = {
        "retrieval_rescue": "Retrieval rescue",
        "speed_to_context_win": "Speed-to-context win",
        "recall_up_efficiency_down": "Broader search win",
        "efficiency_up_with_win": "Higher-quality context win",
        "retrieval_flat_but_outcome_up": "Execution/quality win after similar retrieval",
    }
    for key, rows in (ir.get("situation_buckets") or {}).items():
        label = labels.get(key, key)
        for row in rows or []:
            name = row.get("task_name")
            if not name:
                continue
            out.setdefault(name, []).append(label)
    return out


def write_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def render_task_setup(manifest: dict[str, Any]) -> str:
    task_id = manifest["task_id"]
    mode = manifest["comparison_mode"]
    outputs = manifest.get("output_paths") or []
    clone_cmds_by_env = manifest.get("clone_commands_by_envfile") or {}
    resource_repos = manifest.get("available_resource_repos") or []
    mirrors = manifest.get("mcp_mirror_repos") or []
    required_tools = manifest.get("required_tools") or []
    lines: list[str] = []
    lines.append(f"# Setup ({task_id})")
    lines.append("")
    lines.append(f"- Suite: `{manifest['suite']}`")
    lines.append(f"- Comparison mode in audit: `{mode}` (`{manifest['baseline_config']}` vs `{manifest['mcp_config']}`)")
    lines.append(f"- Output contract(s): {', '.join(f'`{p}`' for p in outputs) if outputs else 'See instructions'}")
    lines.append("")
    lines.append("## Required environment variables")
    lines.append("")
    lines.append("- `SOURCEGRAPH_URL` (your Sourcegraph instance, e.g. `https://sourcegraph.com` or your enterprise URL)")
    lines.append("- `SOURCEGRAPH_ACCESS_TOKEN` (Sourcegraph access token for MCP server)")
    lines.append("- Harness auth vars (see `docs/HARNESS_MCP_SETUP.md`): e.g. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.")
    lines.append("")
    lines.append("## Local repo checkout (which one to use)")
    lines.append("")
    if clone_cmds_by_env:
        lines.append("Use the following checkout commands based on the run style you want to reproduce:")
        lines.append("")
        has_primary = "Dockerfile" in clone_cmds_by_env
        has_artifact_variant = "Dockerfile.artifact_only" in clone_cmds_by_env
        for envfile, cmds in clone_cmds_by_env.items():
            lines.append(f"### {envfile}")
            lines.append("")
            lines.append(envfile_role(envfile))
            lines.append("")
            lines.append("```bash")
            for c in cmds:
                lines.append(c)
            lines.append("```")
            lines.append("")
        lines.append("Recommended local usage:")
        if mode == "direct":
            if has_primary:
                lines.append("- Baseline run (`instruction.md`): use the **primary local checkout** (`Dockerfile` section).")
            elif has_artifact_variant:
                lines.append("- Baseline run (`instruction.md`): use the available checkout variant (`Dockerfile.artifact_only` section) and keep the task output format from `instruction.md`.")
            else:
                lines.append("- Baseline run (`instruction.md`): use any checkout variant listed above that provides the needed local sources.")
            lines.append("- MCP run (`instruction_mcp.md`): usually reuse the same local checkout and enable Sourcegraph MCP.")
            lines.append("- `Dockerfile.artifact_only` / `Dockerfile.sg_only` variants are optional and mostly useful if you want to mimic those benchmark modes.")
        else:
            if has_primary:
                lines.append("- Artifact tasks still often use a local checkout for inspection/tests; start with the **primary local checkout** (`Dockerfile` section).")
            elif has_artifact_variant:
                lines.append("- Start with the available `Dockerfile.artifact_only` checkout for local inspection/testing and produce the requested artifact output.")
            else:
                lines.append("- Use any checkout variant listed above for local inspection/testing before producing the requested artifact output.")
            lines.append("- `Dockerfile.artifact_only` is a good minimal option when present.")
            lines.append("- `Dockerfile.sg_only` is usually benchmark-provenance only; local ablations typically use normal checkouts plus MCP.")
    elif resource_repos:
        lines.append("Optional local clones (derived from instruction resources):")
        lines.append("")
        lines.append("```bash")
        lines.append("mkdir -p repos && cd repos")
        for rr in resource_repos:
            repo = rr["repo"]
            if repo.startswith("sg-evals/"):
                url = f"https://github.com/{repo}.git"
            elif repo.startswith("github.com/"):
                url = f"https://{repo}.git"
            else:
                url = f"https://github.com/{repo}.git"
            dirname = repo.split("/")[-1]
            lines.append(f"git clone {url} {dirname}")
            if rr.get("version"):
                lines.append(f"# Suggested pinned version from task text: {rr['version']}")
        lines.append("```")
    else:
        lines.append("- This task is primarily MCP-remote/artifact oriented; local clones are optional for manual inspection.")
    lines.append("")
    lines.append("## Sourcegraph MCP repo scope")
    lines.append("")
    if mirrors:
        lines.append("Use these Sourcegraph mirror repos for the MCP run:")
        for r in mirrors:
            lines.append(f"- `{r}`")
    else:
        lines.append("- See `instruction_mcp.md` for the exact Sourcegraph repo scope.")
    lines.append("")
    lines.append(render_os_install_instructions(required_tools).rstrip())
    lines.append("")
    lines.append("## Run pattern (local ablation)")
    lines.append("")
    lines.append("1. Run the task with `instruction.md` (baseline/no MCP or local-only variant).")
    lines.append("2. Run the task with `instruction_mcp.md` (MCP-enabled Sourcegraph variant).")
    lines.append("3. Save agent outputs and raw traces separately (e.g., `runs/<task>/baseline/` and `runs/<task>/mcp/`).")
    lines.append("4. Normalize traces with `scripts/extract_trace.py` and compare with `scripts/compare_trace_metrics.py`.")
    lines.append("5. Score outputs using the included `eval/` assets (task-specific) or your harness verifier.")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_task_talk_track(manifest: dict[str, Any]) -> str:
    buckets = manifest.get("ir_situations") or []
    lines = [f"# Demo Talk Track ({manifest['task_id']})", ""]
    lines += [f"- Why this task: `{manifest['task_id']}` is a strong demo candidate with a reference verifier delta of **{manifest['delta']:+.3f}** in the {manifest['suite']} benchmark run."]
    lines += [f"- Compared configs: `{manifest['baseline_config']}` -> `{manifest['mcp_config']}` (baseline reward `{manifest['baseline_reward']}`, MCP reward `{manifest['mcp_reward']}`)."]
    if buckets:
        lines += [f"- IR/result pattern observed in audit: {', '.join(f'`{b}`' for b in buckets)}."]
    lines += [f"- Task type: `{manifest['category']}` | Language: `{manifest['language']}` | Difficulty: `{manifest['difficulty']}`"]
    lines += [""]
    lines += ["## Suggested live demo flow (5-10 min)", ""]
    lines += ["1. Show `instruction.md` and point out the required output format."]
    lines += ["2. Run a baseline/local-only attempt and save both output + trace."]
    lines += ["3. Switch to `instruction_mcp.md`, show Sourcegraph repo scope + MCP requirement, run again."]
    lines += ["4. Compare outputs (quality/completeness) and then compare traces with the scripts in `scripts/`."]
    lines += ["5. Tie the observed behavior back to the audit delta and the task’s retrieval/exploration demands."]
    lines += [""]
    lines += ["## What to highlight", ""]
    if manifest["comparison_mode"] == "artifact":
        lines += ["- This is an **artifact** task: the agent should produce `answer.json` rather than patching code."]
        lines += ["- Sourcegraph MCP is usually the main differentiator because the task requires cross-repo discovery/synthesis."]
    else:
        lines += ["- This is a **direct** task: compare both end quality and how quickly each run gets to relevant code context."]
        lines += ["- Watch for fewer blind local searches / faster path to relevant files in the MCP run."]
    lines += [""]
    return "\n".join(lines) + "\n"


def render_task_eval(manifest: dict[str, Any]) -> str:
    ver = manifest.get("verification", {})
    lines = [f"# Evaluation ({manifest['task_id']})", ""]
    lines += [f"- CCB verifier type: `{ver.get('type', 'unknown')}`"]
    lines += [f"- CCB verifier command: `{ver.get('command', 'N/A')}`"]
    lines += [f"- Reward type: `{manifest.get('reward_type', 'unknown')}`"]
    lines += [f"- Audit comparison mode: `{manifest['comparison_mode']}`"]
    lines += [""]
    lines += ["## Included assets", ""]
    lines += ["- `eval/` is a copy of the task verifier/oracle assets from CodeContextBench (with task-specific ground truth/oracle files)."]
    lines += ["- `instruction.md` / `instruction_mcp.md` are the task prompts used for baseline vs MCP runs."]
    lines += [""]
    lines += ["## Practical local ablation scoring (harness-agnostic)", ""]
    lines += ["1. Produce a baseline run and an MCP run using the same model + temperature + harness settings where possible."]
    lines += ["2. Save final outputs and raw traces separately."]
    lines += ["3. Normalize traces: `python scripts/extract_trace.py --input <run-dir> --output <trace.json>`"]
    lines += ["4. Compare trace metrics: `python scripts/compare_trace_metrics.py --baseline <baseline-trace.json> --mcp <mcp-trace.json> --task-manifest tasks/.../demo_manifest.json`"]
    if manifest["comparison_mode"] == "artifact":
        lines += ["5. For artifact tasks, compare `answer.json` outputs using the oracle/checklist logic in `eval/` (or adapt the included `eval.sh`/`oracle_checks.py` to your local paths)."]
    else:
        lines += ["5. For direct tasks, compare the produced file/report/code diff and score using the included checklist/test assets in `eval/` (or your own local harness verifier)."]
    lines += [""]
    lines += ["## Direct vs artifact notes", ""]
    if manifest["comparison_mode"] == "artifact":
        lines += ["- Primary output is usually `/workspace/answer.json` in CCB; emulate this by saving your result as `answer.json`."]
        lines += ["- These tasks are designed for `baseline-local-artifact` vs `mcp-remote-artifact` comparisons."]
    else:
        lines += ["- These tasks were audited under `baseline-local-direct` vs `mcp-remote-direct`."]
        lines += ["- Many direct tasks still include artifact-aware verifier shims; use them only if you intentionally run an artifact-output variant."]
    lines += [""]
    return "\n".join(lines) + "\n"


def task_readme(manifest: dict[str, Any]) -> str:
    return textwrap.dedent(f"""\
    # {manifest['task_id']}

    Curated demo task package from CodeContextBench.

    - Suite: `{manifest['suite']}`
    - Reference verifier delta: **{manifest['delta']:+.3f}** (`{manifest['baseline_reward']}` -> `{manifest['mcp_reward']}`)
    - Comparison mode: `{manifest['comparison_mode']}`

    ## Files

    - `instruction.md` / `instruction_mcp.md`: baseline vs MCP prompt variants
    - `setup.md`: local setup + clone/env instructions
    - `talk_track.md`: suggested demo narration
    - `evaluation.md`: scoring/comparison workflow
    - `demo_manifest.json`: machine-readable metadata for scripts and indexing
    - `eval/`: copied task verifier/oracle assets from CCB
    - `environment/`: original task Dockerfiles (for provenance)
    """)


def main() -> None:
    ccb = DEFAULT_CCB
    if not AUDIT_JSON.exists():
        raise SystemExit(f"Missing audit JSON: {AUDIT_JSON}")
    audit = json.loads(read_text(AUDIT_JSON))
    ir = json.loads(read_text(IR_JSON)) if IR_JSON.exists() else {}
    ir_buckets = bucket_map_from_ir(ir)

    # Fresh output dirs
    for rel in ["tasks", "data"]:
        p = ROOT / rel
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)

    # Copy source audit artifacts for provenance
    for src in [AUDIT_JSON, AUDIT_MD, IR_JSON]:
        if src.exists():
            shutil.copy2(src, ROOT / "data" / src.name)

    positive = []
    for row in audit.get("positive_deltas", []):
        # Use the visible rounded delta for filtering so values printed as +0.200 are excluded
        # when the threshold is > 0.2, even if their raw float is 0.20000000000000007.
        if round(float(row.get("delta", 0.0)), 4) > DEFAULT_MIN_DELTA:
            positive.append(row)
    positive.sort(key=lambda x: float(x.get("delta", 0)), reverse=True)

    task_index: list[dict[str, Any]] = []

    for rank, row in enumerate(positive, start=1):
        suite = row["suite"]
        task_name = row["task_name"]
        src_dir = ccb / "benchmarks" / suite / task_name
        if not src_dir.exists():
            # Try case-insensitive fallback on task folder name.
            parent = ccb / "benchmarks" / suite
            matches = [p for p in parent.iterdir() if p.name.lower() == task_name.lower()] if parent.exists() else []
            if not matches:
                continue
            src_dir = matches[0]

        task_toml = parse_toml(src_dir / "task.toml")
        instr = read_text(src_dir / "instruction.md")
        instr_mcp = read_text(src_dir / "instruction_mcp.md")
        env_dir = src_dir / "environment"
        docker_texts = {p.name: read_text(p) for p in sorted(env_dir.glob("Dockerfile*"))}

        clone_cmds_by_envfile: dict[str, list[str]] = {}
        for name, txt in docker_texts.items():
            cmds = extract_git_clone_commands(txt)
            if cmds:
                clone_cmds_by_envfile[name] = cmds

        mcp_mirror_repos = extract_mcp_scope_repos(instr_mcp)
        available_repos = extract_available_resource_repos(instr_mcp)
        if not available_repos:
            available_repos = extract_available_resource_repos(instr)
        # Fallback for direct single-repo tasks.
        task_repo = (((task_toml.get("task") or {}).get("repo")) or "")
        if task_repo and not any(r.get("repo") == task_repo for r in available_repos):
            available_repos.append({"repo": task_repo, "version": None})

        outputs = []
        for t in [instr, instr_mcp]:
            for p in extract_output_paths(t):
                if p not in outputs:
                    outputs.append(p)

        meta = task_toml.get("metadata") or {}
        task_sec = task_toml.get("task") or {}
        ver = task_toml.get("verification") or {}

        manifest = {
            "rank": rank,
            "task_id": task_sec.get("id", task_name),
            "task_dir_name": src_dir.name,
            "suite": suite,
            "source_ccb_path": str(src_dir.relative_to(ccb)),
            "delta": round(float(row.get("delta", 0.0)), 4),
            "baseline_reward": row.get("baseline_reward"),
            "mcp_reward": row.get("mcp_reward"),
            "run": row.get("run"),
            "baseline_config": row.get("baseline_config"),
            "mcp_config": row.get("mcp_config"),
            "comparison_mode": parse_task_style(task_toml, row),
            "category": task_sec.get("category"),
            "language": task_sec.get("language"),
            "difficulty": task_sec.get("difficulty"),
            "time_limit_sec": task_sec.get("time_limit_sec"),
            "repo": task_sec.get("repo"),
            "mcp_unique": bool(task_sec.get("mcp_unique", False)),
            "deepsearch_relevant": bool(task_sec.get("deepsearch_relevant", False)),
            "description": meta.get("description"),
            "verification": {"type": ver.get("type"), "command": ver.get("command")},
            "reward_type": task_toml.get("verification", {}).get("reward_type"),
            "output_paths": outputs,
            "mcp_mirror_repos": mcp_mirror_repos,
            "available_resource_repos": available_repos,
            "clone_commands_by_envfile": clone_cmds_by_envfile,
            "required_tools": detect_required_tools(docker_texts, task_sec.get("language")),
            "ir_situations": ir_buckets.get(task_name, []),
        }

        out_dir = ROOT / "tasks" / suite / src_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)

        # Copy core task assets
        for name in ["instruction.md", "instruction_mcp.md", "task.toml"]:
            src = src_dir / name
            if src.exists():
                shutil.copy2(src, out_dir / name)
        if (src_dir / "tests").exists():
            safe_copytree(src_dir / "tests", out_dir / "eval")
        if env_dir.exists():
            safe_copytree(env_dir, out_dir / "environment")

        # Generated docs/metadata
        write_json(out_dir / "demo_manifest.json", manifest)
        (out_dir / "setup.md").write_text(render_task_setup(manifest), encoding="utf-8")
        (out_dir / "talk_track.md").write_text(render_task_talk_track(manifest), encoding="utf-8")
        (out_dir / "evaluation.md").write_text(render_task_eval(manifest), encoding="utf-8")
        (out_dir / "README.md").write_text(task_readme(manifest), encoding="utf-8")

        task_index.append({
            "rank": rank,
            "task_id": manifest["task_id"],
            "suite": suite,
            "path": str(out_dir.relative_to(ROOT)),
            "delta": manifest["delta"],
            "baseline_reward": manifest["baseline_reward"],
            "mcp_reward": manifest["mcp_reward"],
            "comparison_mode": manifest["comparison_mode"],
            "mcp_unique": manifest["mcp_unique"],
            "repo": manifest["repo"],
            "run": manifest["run"],
            "ir_situations": manifest["ir_situations"],
        })

    # Index exports
    write_json(ROOT / "data" / "task_index.json", task_index)
    (ROOT / "tasks" / "index.csv").parent.mkdir(parents=True, exist_ok=True)
    with (ROOT / "tasks" / "index.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "task_id", "suite", "delta", "comparison_mode", "mcp_unique", "repo", "path"])
        w.writeheader()
        for r in task_index:
            w.writerow({k: r.get(k) for k in w.fieldnames})

    lines = [
        "# Task Index",
        "",
        "Generated from the source benchmark report and task manifests.",
        f"Selection filter: `reference verifier delta > {DEFAULT_MIN_DELTA}` (using rounded delta value).",
        f"Included tasks: **{len(task_index)}**.",
        "",
    ]
    lines += ["| Rank | Task | Suite | Verifier Delta | Mode | Path |", "|---:|---|---|---:|---|---|"]
    for r in task_index:
        lines.append(f"| {r['rank']} | `{r['task_id']}` | `{r['suite']}` | {r['delta']:+.3f} | `{r['comparison_mode']}` | `{r['path']}` |")
    (ROOT / "TASK_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated {len(task_index)} task packages under {ROOT / 'tasks'}")


if __name__ == "__main__":
    main()
