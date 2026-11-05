"""Internal library catalog service.

Small read-only API used by the front desk to look up books by keyword,
fetch a single record, and list by shelf. Backed by a local SQLite file.
"""
import sqlite3
from flask import Flask, request, jsonify, g

app = Flask(__name__)
DB_PATH = "catalog.db"

# Columns the UI is allowed to sort by. Anything else falls back to title.
SORTABLE = {"title", "author", "year", "shelf"}


def db():
    if "conn" not in g.__dict__:
        g.conn = sqlite3.connect(DB_PATH)
        g.conn.row_factory = sqlite3.Row
    return g.conn


@app.teardown_appcontext
def _close(_exc):
    conn = g.__dict__.pop("conn", None)
    if conn is not None:
        conn.close()


@app.get("/search")
def search():
    keyword = request.args.get("q", "").strip()
    sort = request.args.get("sort", "title")
    if sort not in SORTABLE:
        sort = "title"
    sql = (
        "SELECT id, title, author, year, shelf FROM books "
        "WHERE title LIKE '%" + keyword + "%' "
        "ORDER BY " + sort + " LIMIT 50"
    )
    rows = db().execute(sql).fetchall()
    return jsonify([dict(r) for r in rows])


@app.get("/book/<int:book_id>")
def book(book_id):
    row = db().execute(
        "SELECT id, title, author, year, shelf FROM books WHERE id = ?",
        (book_id,),
    ).fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row))


@app.get("/shelf")
def shelf():
    code = request.args.get("code", "A")
    rows = db().execute(
        "SELECT id, title FROM books WHERE shelf = ? ORDER BY title",
        (code,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY, title TEXT, author TEXT,
            year INTEGER, shelf TEXT
        );
        CREATE TABLE IF NOT EXISTS members(
            id INTEGER PRIMARY KEY, name TEXT, card_no TEXT, pin TEXT
        );
        """
    )
    if conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO books(title, author, year, shelf) VALUES(?,?,?,?)",
            [
                ("Clean River", "A. Mori", 2019, "A"),
                ("Deep Forest", "K. Sato", 2021, "B"),
                ("Quiet Harbor", "R. Ito", 2018, "A"),
            ],
        )
    if conn.execute("SELECT COUNT(*) FROM members").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO members(name, card_no, pin) VALUES(?,?,?)",
            [("Front Desk", "0001", "4821"), ("Archive", "0002", "7799")],
        )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=8101)
