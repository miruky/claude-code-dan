import json
import os

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ロール→権限表を読み込みます（データファイルが権限設計の正）
def load_roles():
    with open(os.path.join(_DATA, "roles.json"), encoding="utf-8") as f:
        return json.load(f)

# エンドポイント→必要権限の対応表を読み込みます
def load_endpoints():
    with open(os.path.join(_DATA, "endpoints.json"), encoding="utf-8") as f:
        return json.load(f)
