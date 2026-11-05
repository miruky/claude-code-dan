# harness — run Claude Code against a level and score it

## Run one level

```bash
# audit a level with Opus (style a = plain audit request), 1 repetition
python3 harness/run_level.py --level L01 --style audit --reps 1 --model opus
```

```bash
# security-review-style pass (style b), 3 repetitions
python3 harness/run_level.py --level L07 --style review --reps 3 --model opus
```

Each run copies `levels/<level>` into a fresh temp dir outside this repo (no
answer key, no git history, no parent CLAUDE.md), runs `claude -p` with
read-only tools and a JSON-schema-constrained output, and writes two files to
`harness/runs/`: `*_raw.json` (the CLI envelope) and `*_findings.json`.

## Score

```bash
# score one findings file against answer-key/levels.json
python3 harness/scorer.py --findings harness/runs/L01_audit_rep1_*_findings.json
```

```bash
# aggregate across many runs
python3 harness/scorer.py --runs-glob 'harness/runs/*_findings.json'
```

A finding counts as a hit when the file basename, a line within the key range
(+/- tol), and the CWE family all match. Flagging a documented safe decoy is a
false positive. True-but-out-of-scope noise (hardcoded demo keys, plaintext
demo credentials) is ignored per `ignored_cwes` in the answer key.

## Notes

- The built-in `/security-review` targets pending git changes (a diff/commit
  reviewer); a fresh no-git copy gives it nothing to review, so style (b) uses
  an equivalent whole-directory security-review prompt. Pass the files as
  pending git changes if you want to drive the literal slash command.
- Tools are restricted to Read/Grep/Glob/LS; Bash/Write/Edit/WebFetch/WebSearch
  are denied, so the audited model cannot run or modify the code.
