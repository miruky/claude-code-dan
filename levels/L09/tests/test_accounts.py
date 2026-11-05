"""Account and beneficiary behaviour."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.conftest_helpers import fresh_db_env

H = {"Authorization": "Bearer acct-tok-ops"}


def _client():
    fresh_db_env()
    import importlib
    import config as cfg
    importlib.reload(cfg)
    import db, app as appmod
    importlib.reload(db)
    importlib.reload(appmod)
    appmod.bootstrap()
    return appmod.app.test_client()


def test_balance_ok():
    c = _client()
    r = c.get("/accounts/JP-0001/balance", headers=H)
    assert r.status_code == 200
    assert r.get_json()["currency"] == "JPY"


def test_balance_missing():
    c = _client()
    r = c.get("/accounts/NOPE/balance", headers={"Authorization":"Bearer x"})
    assert r.status_code in (401, 403, 404)


def test_add_beneficiary():
    c = _client()
    r = c.post("/accounts/JP-0001/beneficiaries", headers=H,
               json={"name": "Vendor", "dest_number": "JP-9999"})
    assert r.status_code == 201


if __name__ == "__main__":
    test_balance_ok(); test_balance_missing(); test_add_beneficiary()
    print("account tests passed")
