-- performance indexes added after launch
CREATE INDEX IF NOT EXISTS idx_transfers_src ON transfers(src_account_id);
CREATE INDEX IF NOT EXISTS idx_transfers_status ON transfers(status);
CREATE INDEX IF NOT EXISTS idx_benef_account ON beneficiaries(account_id);
