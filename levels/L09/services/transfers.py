"""Transfer orchestration: validate, risk-screen, and settle."""
import datetime

import datetime as _dt

import db
from config import config
from risk import gate, rules, scoring
from services import accounts, notifications
from utils import ids, audit
from utils.errors import ApiError, NotFound, PaymentRequired, Forbidden
from utils.money import to_minor_units
from utils.validation import require_keys, check_currency, check_dest


def _used_today(conn, account_id):
    row = conn.execute(
        "SELECT COALESCE(SUM(amount_minor), 0) AS used FROM transfers "
        "WHERE src_account_id = ? AND status = 'settled' "
        "AND created_at >= datetime('now', 'start of day')",
        (account_id,),
    ).fetchone()
    return row["used"]


def _beneficiary(conn, account_id, dest_number):
    return conn.execute(
        "SELECT name, verified FROM beneficiaries WHERE account_id = ? AND dest_number = ?",
        (account_id, dest_number),
    ).fetchone()


def create_transfer(src_number, payload, raw_body, approver_token):
    require_keys(payload, ["amount", "to"])
    currency = check_currency(payload.get("currency", config.DEFAULT_CURRENCY))
    dest = check_dest(payload["to"])
    amount_minor = to_minor_units(payload["amount"], currency)

    if amount_minor <= 0:
        raise ApiError("amount must be positive")
    if amount_minor > config.MAX_TRANSFER_MINOR:
        raise ApiError("amount exceeds maximum")

    conn = db.connect()
    try:
        src = accounts.get_by_number(conn, src_number)
        if src is None:
            raise NotFound("source account not found")
        if src["status"] != "active":
            raise Forbidden("source account is not active")
        if currency != src["currency"]:
            raise ApiError("transfer currency must match the source account")
        if src["balance_minor"] < amount_minor:
            raise PaymentRequired("insufficient funds")

        benef = _beneficiary(conn, src["id"], dest)
        ctx = {
            "dest_number": dest,
            "beneficiary_name": benef["name"] if benef else "",
            "verified": bool(benef["verified"]) if benef else False,
            "used_minor": _used_today(conn, src["id"]),
            "amount_minor": amount_minor,
        }

        flags = rules.collect_flags(ctx)
        if "dest_blocked" in flags or "name_screened" in flags:
            raise Forbidden("transfer blocked by screening")

        # amounts over the review threshold (hot-path gate) and anything the
        # secondary rules flagged for friction require an approver token.
        require_approval = gate.needs_review(raw_body, currency) or bool(flags)
        if require_approval and approver_token not in config.APPROVER_TOKENS:
            raise PaymentRequired("second approver required")

        # advisory risk score for observability (does not block)
        risk_score, reasons = scoring.score({
            "amount_minor": amount_minor,
            "used_minor": ctx["used_minor"],
            "verified": ctx["verified"],
            "cross_currency": currency != src["currency"],
            "hour": _dt.datetime.now().hour,
        })

        ref = ids.new_ref()
        # guarded debit: only succeeds if the balance still covers the amount
        upd = conn.execute(
            "UPDATE accounts SET balance_minor = balance_minor - ? "
            "WHERE id = ? AND balance_minor >= ?",
            (amount_minor, src["id"], amount_minor),
        )
        if upd.rowcount != 1:
            conn.rollback()
            raise PaymentRequired("insufficient funds")
        cur = conn.execute(
            "INSERT INTO transfers(src_account_id, dest_number, amount_minor, currency, "
            "status, approver) VALUES(?,?,?,?,?,?)",
            (src["id"], dest, amount_minor, currency, "settled",
             approver_token if require_approval else None),
        )
        conn.commit()
        result = {
            "ref": ref,
            "id": cur.lastrowid,
            "to": ids.mask_account(dest),
            "amount_minor": amount_minor,
            "currency": currency,
            "status": "settled",
            "reviewed": require_approval,
            "risk_score": risk_score,
        }
        audit.record(src["owner"], "transfer.settled",
                     {"ref": ref, "amount_minor": amount_minor,
                      "score": risk_score, "reasons": reasons, "flags": flags})
        notifications.notify_transfer(src["owner"], result)
        return result
    finally:
        conn.close()


def recent(src_number, limit=20):
    conn = db.connect()
    try:
        src = accounts.get_by_number(conn, src_number)
        if src is None:
            raise NotFound("source account not found")
        rows = conn.execute(
            "SELECT id, dest_number, amount_minor, currency, status, created_at "
            "FROM transfers WHERE src_account_id = ? ORDER BY id DESC LIMIT ?",
            (src["id"], int(limit)),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
