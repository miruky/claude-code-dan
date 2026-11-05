import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.helpers import client


def test_register_ok():
    c = client()
    r = c.post("/tenants", json={"slug": "team-blue", "display_name": "Blue",
                                 "owner_email": "a@b.co"})
    assert r.status_code == 201
    assert r.get_json()["slug"] == "team-blue"


def test_reserved_blocked():
    c = client()
    r = c.post("/tenants", json={"slug": "admin", "display_name": "x",
                                 "owner_email": "a@b.co"})
    assert r.status_code == 400


def test_duplicate():
    c = client()
    p = {"slug": "team-red", "display_name": "Red", "owner_email": "a@b.co"}
    assert c.post("/tenants", json=p).status_code == 201
    assert c.post("/tenants", json=p).status_code == 409


if __name__ == "__main__":
    test_register_ok(); test_reserved_blocked(); test_duplicate()
    print("registration tests passed")
