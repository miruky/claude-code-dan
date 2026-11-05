-- platform admin audit trail
CREATE TABLE IF NOT EXISTS admin_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_slug TEXT,
    action TEXT,
    at TEXT NOT NULL DEFAULT (datetime('now'))
);
