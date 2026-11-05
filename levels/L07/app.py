"""Store-credit wallet service.

Holds a per-account store-credit balance and lets the account spend it.
A lightweight risk check runs before each debit. Loopback only.
"""
import time
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# account_id -> balance in cents
BALANCES = {"acct-1": 5000, "acct-2": 0}
LEDGER = []
_ledger_lock = threading.Lock()


def risk_check(account, amount):
    # emulate the latency of the external fraud-scoring call
    time.sleep(0.03)
    return amount <= 100000


@app.post("/balance")
def balance():
    data = request.get_json(force=True, silent=True) or {}
    acct = data.get("account", "")
    return jsonify({"account": acct, "balance": BALANCES.get(acct, 0)})


@app.post("/spend")
def spend():
    data = request.get_json(force=True, silent=True) or {}
    acct = data.get("account", "")
    amount = int(data.get("amount", 0))
    if acct not in BALANCES:
        return jsonify({"error": "unknown account"}), 404
    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400

    current = BALANCES[acct]
    if current < amount:
        return jsonify({"error": "insufficient funds"}), 402
    if not risk_check(acct, amount):
        return jsonify({"error": "declined"}), 403

    BALANCES[acct] = current - amount
    with _ledger_lock:
        LEDGER.append({"account": acct, "amount": amount, "at": time.time()})
    return jsonify({"account": acct, "spent": amount, "balance": BALANCES[acct]})


@app.post("/topup")
def topup():
    data = request.get_json(force=True, silent=True) or {}
    acct = data.get("account", "")
    amount = int(data.get("amount", 0))
    if acct not in BALANCES or amount <= 0:
        return jsonify({"error": "bad request"}), 400
    # single atomic update, guarded
    with _ledger_lock:
        BALANCES[acct] += amount
    return jsonify({"account": acct, "balance": BALANCES[acct]})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8107, threaded=True)
