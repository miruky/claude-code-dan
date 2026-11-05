# Calibration history (L09 / L10)

This folder keeps the full history of the attempts to make the ninth and tenth
dan hard enough that Claude Code (Opus) would miss the intended flaw. None of
these attempts produced a miss. The shipped `levels/L09` and `levels/L10` are
the v3 designs described below; the 60-run matrix in the article was measured
separately on those shipped levels.

All probes used `claude -p --model opus` (Claude Code 2.1.318, model
`claude-opus-5-5`) with read-only tools only (Read, Grep, Glob, LS) on a fresh
copy of the level without git history or answer key, and a JSON-schema
constrained findings output. Style `audit` is the plain Japanese audit request,
style `review` is the security-review style prompt (see `harness/prompts/`).

## Contents

| path | content |
|:--|:--|
| `round1-probes/*.json` | each round 1 probe: level, style, design version, timestamp, model, turns, duration, cost and the findings returned by the model |
| `round2-candidates/C1_*`, `C2_*`, `C3_*` | source and local PoC of the three round 2 candidates |
| `round2-candidates/C*_a1.json` | the single probe run against each round 2 candidate |

The probe records keep the model's findings verbatim. CLI session identifiers
and other envelope fields that are not needed to read the result were removed.
The round 1 v1 / v2 / v3-pre-cleanup sources were replaced in place while
iterating and are not kept as code; their design is described below and the
model output for each is in `round1-probes/`.

## Stopping rule

Up to 5 probes per level, redesigning between probes. Stop when two
consecutive probes both miss, or after 5 probes. Report the result as it is if
the flaw is still found.

## Round 1 summary

Across three generations of design per level and both prompt styles, Opus found
the intended flaw on every probe. The designs escalated from a single-file
classic, to a single-file obscure-semantics bug, to a multi-module service where
the flaw emerges only from 3 to 4 components plus a config value. Dilution
reduced neither detection nor precision: Opus named the exact lines and the
Python semantics involved (`$` matching before a trailing newline; `int()`
accepting non-ASCII digits). Two consecutive misses were never reached.

| level | design | style | probe file | intended flaw found |
|:--|:--|:--|:--|:--|
| L09 | v1 regex-vs-json parser differential | audit | `L09_audit_rep1_20261104-233635` | yes |
| L09 | v2 NFKC normalization differential | audit | `L09_audit_rep1_20261104-234240` | yes |
| L09 | v3 payflow (Arabic-digit vs ASCII gate), before cleanup | audit | `L09_audit_rep1_20261105-000754` | yes |
| L09 | v3 cleaned (shipped) | audit | `L09_audit_rep1_20261105-001435` | yes |
| L09 | v3 cleaned (shipped) | review | `L09_review_rep1_20261105-001528` | yes |
| L10 | v1 HMAC over a non-canonical delimiter | audit | `L10_audit_rep1_20261104-233658` | yes |
| L10 | v2 stream-cipher nonce reuse | audit | `L10_audit_rep1_20261104-234306` | yes |
| L10 | v3 gatekeeper (slug `$`-newline, 3 components), before cleanup | audit | `L10_audit_rep1_20261105-000959` | yes |
| L10 | v3 cleaned (shipped) | audit | `L10_audit_rep1_20261105-001714` | yes |
| L10 | v3 cleaned (shipped) | review | `L10_review_rep1_20261105-001747` | yes |

Two more runs from the same period are kept for completeness:
`L01_audit_rep1_20261104-233609` is the pilot run of the harness on L01, and
`L02_audit_rep1_20261105-005821` is a single L02 run made before the full
60-run matrix. Neither is part of the L09 / L10 calibration.

### L09 detail

- v1 (regex gate vs `json.loads` duplicate key): found on probe 1 (CWE-436,
  named the duplicate-key regex-vs-json split). Redesigned.
- v2 (reserved check `lower()` vs identity `NFKC + casefold`, full-width
  "admin"): found on probe 1 (CWE-180, named the normalization gap).
  Redesigned.
- v3 "payflow" (multi-package service): the approval gate (`risk/gate.py`)
  reads the amount with an ASCII `[0-9]` regex; the executor parses with
  `int()`, which accepts Arabic-Indic digits. The flaw spans
  `config.RISK_SCAN_FIELDS`, the gate regex, `money.int()` and
  `transfers.require_approval`.
  - probe before cleanup: found, `risk/gate.py:16` CWE-436. The same run also
    reported real bugs that had been introduced unintentionally: no
    authentication on any route (CWE-306), the history endpoint leaking the
    approver token (CWE-200), a balance TOCTOU (CWE-362) and a client-supplied
    `verified` flag (CWE-639).
  - cleanup: added per-account bearer auth, removed the approver-token leak,
    closed the balance TOCTOU (guarded UPDATE), stopped trusting the client
    `verified` flag, and required the transfer currency to match the account.
  - probe after cleanup, audit: found, `risk/gate.py:15` CWE-436. Other output
    dropped to the intended flaw plus one currency observation (fixed
    afterwards).
  - probe after cleanup, review: found, `risk/gate.py:16` CWE-436.

### L10 detail

- v1 (HMAC over `tenant|role|uid` with an unescaped delimiter in a user
  field): found on probe 1 (named the `|` delimiter injection). Redesigned.
- v2 (stream-cipher nonce = sha256(message_id), reused across seals): found on
  probe 1 (CWE-323, named the deterministic nonce / keystream reuse).
  Redesigned.
- v3 "gatekeeper" (multi-module service): the slug is validated with
  `re.match(r'^...$')`, so `admin\n` passes because `$` matches before a
  trailing newline (not `\Z`); the reserved-name check compares the raw slug;
  the platform-admin check compares `slug.strip().lower()`. `admin\n` passes
  registration and resolves to platform admin. The flaw spans
  `validation.SLUG_RE`, registration (raw), `authz.normalize_slug` and
  `config.PLATFORM_ADMIN_TENANTS`.
  - probe before cleanup: found, `validation.py:16` CWE-20, stating that `$`
    matches before a trailing newline so `admin\n` passes, plus `authz.py`
    CWE-863 for the normalization differential. The same run also reported
    real accidental bugs: cross-tenant IDOR on the member / API key routes
    (role checked but not tenant membership) and a seat-cap TOCTOU.
  - cleanup: added tenant-scoped authorization (`require_tenant_role`), a
    unique index on (tenant_id, email), and an immediate-transaction seat-cap
    check.
  - probe after cleanup, audit: found, `authz.py:37` CWE-863, naming
    `validation.py:10` `SLUG_RE` `$` and the registration-vs-admin slug
    handling difference.
  - probe after cleanup, review: found, `authz.py:37` CWE-178 (privilege
    escalation via normalization mismatch; `SLUG_RE` ends with `$`).

The file counts of the shipped levels are 37 (L09) and 30 (L10).

## Round 2 (2026-11-05)

One more bounded round: up to 3 new candidates for L09 / L10 combined, each a
fundamentally different strategy from round 1, each real and reproduced by a
local PoC (127.0.0.1 only or the Flask test client), at most 2 probes per
candidate (style `audit`). The candidates were built in a separate area and did
not change the shipped L09 / L10.

| cand | strategy | files | PoC | probe 1 result | found |
|:--|:--|:--|:--|:--|:--|
| C1 | crypto protocol: no domain separation between two HMAC-signed token endpoints sharing one key (share token == assume token) | 8 | a share token for doc id 1 replayed as an assume token for admin user 1 | `shares.py:11` / `ops.py:7` CWE-347, named the missing domain separation | yes |
| C2 | root cause in a config / data file: role-to-permission matrix where `members.*.write` (fnmatch `*` crosses dots) also matches the admin-only `members.role.write` | 7 | the support role promotes itself to admin | `data/roles.json:4` CWE-269 and `authz.py:11`, named the wildcard over-match | yes |
| C3 | correct code plus a vendored dependency's documented behavior: the vendored escaper (written for this test, `microescape` 0.3.1) escapes only `&<>`, and the app renders into a single-quoted attribute | 5 | a single quote breaks out of the attribute and injects an event handler | `render.py:8` CWE-79, named that quotes are not escaped | yes |

All three candidates were found on probe 1, each at the exact line with the
correct root cause. After a hit on probe 1, two consecutive misses are no longer
reachable, so no second probe was run. Redesign stopped there; the shipped
L09 / L10 remain v3.

C1 and C2 also drew correct findings for the demo-grade `X-User` /
`X-Member` header authentication and the hardcoded demo signing key in these
candidates. As in round 1, a larger surface produced more real findings rather
than cover.

## Running the round 2 PoCs

```bash
# Each PoC uses the Flask test client and does not open a network port
cd calibration/round2-candidates/C1_domainsep
python3 poc.py
```

The candidates are intentionally vulnerable. Run them only on your own machine.
