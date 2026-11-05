#!/usr/bin/env python3
"""Run Claude Code against one level and capture structured findings.

For each repetition this:
  1. copies levels/<level> into a fresh temp dir OUTSIDE this repo
     (so no answer key, no git history, and no parent CLAUDE.md leaks in),
  2. runs `claude -p` with --model opus, read-only tools, and a JSON schema
     that forces the output into {findings: [...]},
  3. saves the raw CLI envelope and the parsed findings under harness/runs/.

Two prompt styles:
  audit  (a) a plain Japanese request to audit for vulnerabilities
  review (b) a security-review-style adversarial pass over the whole dir

Note on the built-in /security-review: it is oriented to *pending git
changes* (a diff / commit reviewer), so a fresh no-git copy gives it nothing
to review and its prose output does not fit mechanical scoring. Style (b)
therefore uses an equivalent security-review prompt over the full directory.
Pass --use-builtin-review to instead stage the files as pending git changes
and invoke the literal `/security-review` (raw output only, not scored).
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HARNESS_DIR)
RUNS_DIR = os.path.join(HARNESS_DIR, "runs")
SCHEMA = os.path.join(HARNESS_DIR, "findings_schema.json")

READ_ONLY_TOOLS = "Read Grep Glob LS"
DENY_TOOLS = "Bash Write Edit MultiEdit NotebookEdit WebFetch WebSearch Task"


def copy_level(level):
    src = os.path.join(REPO, "levels", level)
    if not os.path.isdir(src):
        sys.exit(f"no such level: {src}")
    tmp = tempfile.mkdtemp(prefix=f"audit-{level}-")
    dst = os.path.join(tmp, level)
    shutil.copytree(
        src, dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git", "*.db"),
    )
    return dst


def run_claude(workdir, prompt, model, max_turns, timeout):
    cmd = [
        "claude", "-p", prompt,
        "--model", model,
        "--output-format", "json",
        "--json-schema", open(SCHEMA).read(),
        "--allowedTools", READ_ONLY_TOOLS,
        "--disallowedTools", DENY_TOOLS,
        "--max-turns", str(max_turns),
    ]
    proc = subprocess.run(
        cmd, cwd=workdir, capture_output=True, text=True, timeout=timeout
    )
    return proc


def parse_findings(stdout):
    """Pull {findings:[...]} out of the CLI envelope."""
    try:
        env = json.loads(stdout)
    except Exception:
        return None, {"error": "cli stdout not json", "raw": stdout[:2000]}
    result = env.get("result", "")
    # with --json-schema the result should itself be the JSON object
    for candidate in (result, _extract_json(result)):
        if candidate is None:
            continue
        try:
            obj = json.loads(candidate) if isinstance(candidate, str) else candidate
            if isinstance(obj, dict) and "findings" in obj:
                return obj["findings"], env
        except Exception:
            pass
    return [], env


def _extract_json(text):
    if not isinstance(text, str):
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start:end + 1]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True)
    ap.add_argument("--style", choices=["audit", "review"], default="audit")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--model", default="opus")
    ap.add_argument("--max-turns", type=int, default=40)
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    os.makedirs(RUNS_DIR, exist_ok=True)
    prompt_file = os.path.join(HARNESS_DIR, "prompts", f"{args.style}_ja.txt")
    prompt = open(prompt_file, encoding="utf-8").read()

    for rep in range(1, args.reps + 1):
        ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        workdir = copy_level(args.level)
        print(f"[run] {args.level} style={args.style} rep={rep} dir={workdir}")
        try:
            proc = run_claude(
                workdir, prompt, args.model, args.max_turns, args.timeout
            )
        except subprocess.TimeoutExpired:
            print("  TIMEOUT")
            continue
        findings, env = parse_findings(proc.stdout)
        base = f"{args.level}_{args.style}_rep{rep}_{ts}"
        with open(os.path.join(RUNS_DIR, base + "_raw.json"), "w") as f:
            json.dump(
                {"returncode": proc.returncode, "stderr": proc.stderr[:4000],
                 "envelope": env},
                f, ensure_ascii=False, indent=1,
            )
        with open(os.path.join(RUNS_DIR, base + "_findings.json"), "w") as f:
            json.dump(
                {"level": args.level, "style": args.style, "rep": rep,
                 "findings": findings or []},
                f, ensure_ascii=False, indent=1,
            )
        n = len(findings) if findings else 0
        cost = (env or {}).get("total_cost_usd")
        print(f"  -> {n} findings  (rc={proc.returncode}, cost={cost})  {base}")


if __name__ == "__main__":
    main()
