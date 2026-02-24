#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEXT_EXTS = {".sh", ".py", ".json", ".txt", ".md", ".toml"}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run a copied CCB task verifier locally against a task output file (no Docker)")
    ap.add_argument("--task", required=True, help="Task directory (e.g. tasks/ccb_understand/cilium-project-orient-001)")
    ap.add_argument("--input", required=True, help="Path to produced agent output file (e.g. answer.json or report.md)")
    ap.add_argument("--output-path", help="Task contract output path (e.g. /workspace/answer.json or /logs/agent/onboarding.md). If omitted, inferred when possible.")
    ap.add_argument("--keep-temp", action="store_true", help="Keep the temporary sandbox directory for debugging")
    ap.add_argument("--print-stdout", action="store_true", help="Print full verifier stdout/stderr")
    return ap.parse_args()


def infer_output_path(task_dir: Path, manifest: dict) -> str:
    outputs = manifest.get("output_paths") or []
    mode = manifest.get("comparison_mode")
    if len(outputs) == 1:
        return outputs[0]
    if mode == "artifact" and "/workspace/answer.json" in outputs:
        return "/workspace/answer.json"
    if mode == "artifact":
        return "/workspace/answer.json"
    # Common direct-task defaults
    for candidate in ["/logs/agent/onboarding.md", "/logs/agent/report.md", "/logs/agent/answer.md"]:
        if candidate in outputs:
            return candidate
    raise SystemExit(
        f"Could not infer output path for {task_dir}. Provide --output-path. Available contract paths: {outputs}"
    )


def patch_paths(root: Path) -> None:
    replacements = {
        "/tests": str(root / "tests"),
        "/workspace": str(root / "workspace"),
        "/logs": str(root / "logs"),
    }
    for p in (root / "tests").rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in TEXT_EXTS and p.name not in {"test.sh", "eval.sh"}:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = text
        for src, dst in replacements.items():
            text = text.replace(src, dst)
        if text != orig:
            p.write_text(text, encoding="utf-8")


def choose_verifier(eval_dir: Path) -> Path:
    for name in ["eval.sh", "test.sh"]:
        p = eval_dir / name
        if p.exists():
            return p
    raise SystemExit(f"No eval.sh/test.sh found in {eval_dir}")


def main() -> None:
    args = parse_args()
    task_dir = Path(args.task).expanduser().resolve()
    input_file = Path(args.input).expanduser().resolve()
    if not task_dir.exists():
        raise SystemExit(f"Task dir not found: {task_dir}")
    if not input_file.exists():
        raise SystemExit(f"Input file not found: {input_file}")

    manifest_path = task_dir / "demo_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Missing demo_manifest.json in {task_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    output_path = args.output_path or infer_output_path(task_dir, manifest)
    if not output_path.startswith("/"):
        raise SystemExit("--output-path must be an absolute path like /workspace/answer.json")

    eval_src = task_dir / "eval"
    if not eval_src.exists():
        raise SystemExit(f"Missing eval/ in {task_dir}")

    temp_ctx = tempfile.TemporaryDirectory(prefix=f"local_eval_{manifest['task_dir_name']}_")
    root = Path(temp_ctx.name)
    try:
        (root / "workspace").mkdir(parents=True, exist_ok=True)
        (root / "tests").mkdir(parents=True, exist_ok=True)
        (root / "logs" / "agent").mkdir(parents=True, exist_ok=True)
        (root / "logs" / "verifier").mkdir(parents=True, exist_ok=True)

        shutil.copytree(eval_src, root / "tests", dirs_exist_ok=True)

        # Place user-provided output at the expected contract path inside the temp sandbox.
        target = root / output_path.lstrip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_file, target)

        patch_paths(root)

        verifier = choose_verifier(root / "tests")
        # Make shell scripts executable.
        for sh in (root / "tests").rglob("*.sh"):
            sh.chmod(sh.stat().st_mode | 0o111)

        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        # Some direct checklist verifiers support REPORT_PATH override.
        env.setdefault("REPORT_PATH", str(target))
        # CWD in workspace matches many assumptions.
        proc = subprocess.run(
            ["bash", str(verifier)],
            cwd=str(root / "workspace"),
            env=env,
            capture_output=True,
            text=True,
        )

        reward_file = root / "logs" / "verifier" / "reward.txt"
        reward = reward_file.read_text(encoding="utf-8").strip() if reward_file.exists() else None

        print(f"task: {task_dir}")
        print(f"input: {input_file}")
        print(f"mapped_to: {output_path}")
        print(f"verifier: {verifier.name}")
        print(f"exit_code: {proc.returncode}")
        print(f"reward: {reward if reward is not None else 'N/A'}")
        if args.keep_temp:
            print(f"temp_sandbox: {root}")
            temp_ctx.cleanup = lambda: None  # type: ignore[attr-defined]
        if args.print_stdout or proc.returncode != 0:
            if proc.stdout:
                print("\n=== verifier stdout ===\n" + proc.stdout)
            if proc.stderr:
                print("\n=== verifier stderr ===\n" + proc.stderr)
        # Preserve exit-code-first semantics when possible.
        sys.exit(proc.returncode)
    finally:
        if not args.keep_temp:
            temp_ctx.cleanup()


if __name__ == "__main__":
    main()
