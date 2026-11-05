"""Transfer happy-path and threshold behaviour."""
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


def test_small_transfer_settles():
    c = _client()
    r = c.post("/accounts/JP-0001/transfers", json={"amount": "1000", "to": "JP-0002"}, headers=H)
    assert r.status_code == 201
    assert r.get_json()["status"] == "settled"


def test_large_transfer_needs_approver():
    c = _client()
    r = c.post("/accounts/JP-0001/transfers", json={"amount": "300000", "to": "JP-0002"}, headers=H)
    assert r.status_code == 402


def test_large_transfer_with_approver():
    c = _client()
    r = c.post("/accounts/JP-0001/transfers",
               json={"amount": "300000", "to": "JP-0002"},
               headers={"X-Approver": "appr-6f2a", **H})
    assert r.status_code == 201
    assert r.get_json()["reviewed"] is True


if __name__ == "__main__":
    test_small_transfer_settles()
    test_large_transfer_needs_approver()
    test_large_transfer_with_approver()
    print("transfer tests passed")
