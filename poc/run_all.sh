#!/usr/bin/env bash
# Run every PoC in its own Python process so per-level helper modules
# (db, auth, config, ...) never collide. All exploits are local only.
set -u
cd "$(dirname "$0")"
fail=0
for i in 01 02 03 04 05 06 07 08 09 10; do
  echo "=== L$i ==="
  if python3 "L${i}_poc.py"; then
    :
  else
    echo "L$i PoC FAILED"
    fail=1
  fi
  echo
done
if [ "$fail" -eq 0 ]; then
  echo "ALL POCS CONFIRMED"
else
  echo "SOME POCS FAILED"
  exit 1
fi
