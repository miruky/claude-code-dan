-- audit log added for compliance
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor TEXT,
    action TEXT,
    detail TEXT,
    at TEXT NOT NULL DEFAULT (datetime('now'))
);
