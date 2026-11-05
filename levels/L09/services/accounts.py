"""Account lookups and balance helpers."""
import db
from utils.errors import NotFound


def get_by_number(conn, number):
    return conn.execute(
        "SELECT id, number, owner, currency, balance_minor, status "
        "FROM accounts WHERE number = ?",
        (number,),
    ).fetchone()


def balance(number):
    conn = db.connect()
    try:
        row = get_by_number(conn, number)
        if row is None:
            raise NotFound("account not found")
        return {"number": row["number"], "currency": row["currency"],
                "balance_minor": row["balance_minor"], "status": row["status"]}
    finally:
        conn.close()


def add_beneficiary(number, name, dest_number, verified=False):
    conn = db.connect()
    try:
        acct = get_by_number(conn, number)
        if acct is None:
            raise NotFound("account not found")
        conn.execute(
            "INSERT INTO beneficiaries(account_id, name, dest_number, verified) VALUES(?,?,?,?)",
            (acct["id"], name, dest_number, 1 if verified else 0),
        )
        conn.commit()
        return {"account": number, "name": name, "dest": dest_number, "verified": verified}
    finally:
        conn.close()
