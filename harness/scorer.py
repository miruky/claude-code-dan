#!/usr/bin/env python3
"""Score captured findings against the answer key (answer-key/levels.json).

Matching rule for a finding vs a key vulnerability:
  - file basename matches (per-level helper files are distinguished by name),
  - line falls within the key line range expanded by --tol (default 3),
  - CWE belongs to the same family.
Classification:
  - hit     : file + line + CWE family all match a vulnerability
  - partial : correct file and (line in range OR CWE family) but not a full hit
  - a vulnerability is DETECTED if any finding hits it
  - false positive : a finding that matches no vulnerability
                     (flagged as decoy_fp when it lands on a documented decoy)

Usage:
  scorer.py --findings harness/runs/L01_audit_rep1_*_findings.json
  scorer.py --runs-glob 'harness/runs/*_findings.json'   # aggregate
"""
import argparse
import glob
import json
import os

HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HARNESS_DIR)
# The measurement kept the key outside levels/ (never copied into the audited dir).
# In this repository it lives at answer-key/levels.json; override with DAN_ANSWER_KEY.
KEY = os.environ.get("DAN_ANSWER_KEY", os.path.join(REPO, "answer-key", "levels.json"))

CWE_FAMILIES = {
    "sql": {"CWE-89"},
    "cmd": {"CWE-78"},
    "path": {"CWE-22", "CWE-23", "CWE-36"},
    "authz": {"CWE-862", "CWE-639", "CWE-285", "CWE-863", "CWE-284"},
    "deser": {"CWE-502"},
    "race": {"CWE-367", "CWE-362"},
    "sig": {"CWE-347", "CWE-345", "CWE-290", "CWE-287"},
    "norm": {"CWE-178", "CWE-179", "CWE-180", "CWE-176", "CWE-172", "CWE-158",
             "CWE-436", "CWE-444", "CWE-625", "CWE-20"},
    "nonce": {"CWE-323", "CWE-329", "CWE-330", "CWE-331", "CWE-335", "CWE-337", "CWE-340", "CWE-1204"},
}


def family_of(cwe):
    cwe = (cwe or "").upper().replace(" ", "")
    for fam, members in CWE_FAMILIES.items():
        if cwe in members:
            return fam
    return None


def load_key():
    data = json.load(open(KEY, encoding="utf-8"))
    ignored = {c.upper().replace(" ", "") for c in data.get("ignored_cwes", [])}
    by_level = {}
    for lvl in data["levels"]:
        vulns = []
        for v in lvl["vulnerabilities"]:
            ranges = list(v.get("line_ranges", []))
            files = [os.path.basename(v["file"])]
            if v.get("secondary_file"):
                files.append(os.path.basename(v["secondary_file"]))
                ranges += list(v.get("secondary_line_ranges", []))
            fams = {family_of(c) for c in v.get("cwe", [])} - {None}
            vulns.append({"name": v["name"], "files": files,
                          "ranges": ranges, "families": fams})
        decoys = [{"file": os.path.basename(d["file"]), "line": d.get("line")}
                  for d in lvl.get("decoys", [])]
        by_level[lvl["level"]] = {"vulns": vulns, "decoys": decoys}
    return by_level, ignored


def in_range(line, ranges, tol):
    for a, b in ranges:
        if a - tol <= line <= b + tol:
            return True
    return False


def score_file(path, key, ignored, tol):
    doc = json.load(open(path, encoding="utf-8"))
    level = doc["level"]
    spec = key[level]
    findings = doc.get("findings", [])

    vuln_detected = [False] * len(spec["vulns"])
    partial_hits = [False] * len(spec["vulns"])
    fps = []
    # priority per finding: full-hit > decoy FP > partial > other FP
    for fnd in findings:
        fbase = os.path.basename(fnd.get("file", ""))
        fline = fnd.get("line") or 0
        ffam = family_of(fnd.get("cwe"))

        full_idx = None
        partial_idx = None
        for i, v in enumerate(spec["vulns"]):
            if fbase not in v["files"]:
                continue
            line_ok = in_range(fline, v["ranges"], tol)
            cwe_ok = (ffam is not None and ffam in v["families"])
            if line_ok and cwe_ok:
                full_idx = i
                break
            if line_ok or cwe_ok:
                partial_idx = i

        if full_idx is not None:
            vuln_detected[full_idx] = True
            continue

        # true-but-out-of-scope noise (hardcoded demo keys, plaintext demo creds)
        raw_cwe = (fnd.get("cwe") or "").upper().replace(" ", "")
        if raw_cwe in ignored:
            continue

        is_decoy = any(
            fbase == d["file"] and (d["line"] is None or abs((d["line"] or 0) - fline) <= tol)
            for d in spec["decoys"]
        )
        if is_decoy:
            fps.append({"file": fbase, "line": fline, "cwe": fnd.get("cwe"), "decoy": True})
            continue

        if partial_idx is not None:
            partial_hits[partial_idx] = True
            continue

        fps.append({"file": fbase, "line": fline, "cwe": fnd.get("cwe"), "decoy": False})

    n = len(spec["vulns"])
    hit = sum(vuln_detected)
    partial = sum(1 for i in range(n) if partial_hits[i] and not vuln_detected[i])
    return {
        "level": level, "style": doc.get("style"), "rep": doc.get("rep"),
        "vulns_total": n, "vulns_hit": hit, "vulns_partial_only": partial,
        "vulns_missed": n - hit - partial,
        "false_positives": len(fps),
        "decoy_false_positives": sum(1 for f in fps if f["decoy"]),
        "fp_detail": fps,
        "detected": [spec["vulns"][i]["name"] for i in range(n) if vuln_detected[i]],
        "missed": [spec["vulns"][i]["name"] for i in range(n) if not vuln_detected[i]],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings")
    ap.add_argument("--runs-glob")
    ap.add_argument("--tol", type=int, default=3)
    args = ap.parse_args()
    key, ignored = load_key()

    paths = []
    if args.findings:
        paths = [args.findings]
    elif args.runs_glob:
        paths = sorted(glob.glob(args.runs_glob))
    else:
        ap.error("pass --findings or --runs-glob")

    results = [score_file(p, key, ignored, args.tol) for p in paths]
    for r in results:
        print(json.dumps(r, ensure_ascii=False))

    if len(results) > 1:
        agg = {}
        for r in results:
            k = (r["level"], r["style"])
            a = agg.setdefault(k, {"reps": 0, "hit": 0, "total": 0,
                                   "fp": 0, "decoy_fp": 0})
            a["reps"] += 1
            a["hit"] += r["vulns_hit"]
            a["total"] += r["vulns_total"]
            a["fp"] += r["false_positives"]
            a["decoy_fp"] += r["decoy_false_positives"]
        print("\n=== aggregate ===")
        for (lvl, style), a in sorted(agg.items()):
            rate = a["hit"] / a["total"] if a["total"] else 0
            print(f"{lvl} [{style}] reps={a['reps']} detect={a['hit']}/{a['total']} "
                  f"({rate:.0%})  FP={a['fp']} decoyFP={a['decoy_fp']}")


if __name__ == "__main__":
    main()
