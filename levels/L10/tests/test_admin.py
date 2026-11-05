import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.helpers import client


def _reg(c, slug):
    return c.post("/tenants", json={"slug": slug, "display_name": slug,
                                    "owner_email": "o@x.co"}).get_json()["token"]


def test_regular_tenant_denied_admin():
    c = client()
    tok = _reg(c, "team-green")
    r = c.get("/admin/tenants", headers={"Authorization": "Bearer " + tok})
    assert r.status_code == 403


def test_me_shows_not_admin():
    c = client()
    tok = _reg(c, "team-gold")
    j = c.get("/me", headers={"Authorization": "Bearer " + tok}).get_json()
    assert j["platform_admin"] is False


if __name__ == "__main__":
    test_regular_tenant_denied_admin(); test_me_shows_not_admin()
    print("admin tests passed")
