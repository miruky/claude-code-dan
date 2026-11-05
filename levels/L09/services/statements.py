"""Account statement generation (read-only reporting)."""
import db
from services import accounts
from utils.errors import NotFound
from utils.money import format_minor


def monthly(number, month=None):
    conn = db.connect()
    try:
        acct = accounts.get_by_number(conn, number)
        if acct is None:
            raise NotFound("account not found")
        q = ("SELECT dest_number, amount_minor, currency, status, created_at "
             "FROM transfers WHERE src_account_id = ?")
        params = [acct["id"]]
        if month:
            q += " AND strftime('%Y-%m', created_at) = ?"
            params.append(month)
        q += " ORDER BY created_at"
        rows = conn.execute(q, params).fetchall()
        lines = [{
            "dest": r["dest_number"],
            "amount": format_minor(r["amount_minor"], r["currency"]),
            "currency": r["currency"],
            "status": r["status"],
            "date": r["created_at"],
        } for r in rows]
        total = sum(r["amount_minor"] for r in rows if r["status"] == "settled")
        return {"account": number, "lines": lines,
                "settled_total": format_minor(total, acct["currency"])}
    finally:
        conn.close()
