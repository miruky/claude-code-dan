import os
# 署名用の共有シークレット（デモ用の固定値）
SIGNING_KEY = os.environ.get("LEDGERLINE_KEY", "ledgerline-demo-signing-key").encode()
# 共有リンクの既定有効範囲
SHARE_SCOPE_DEFAULT = "read"
# 内部運用ツールが叩く assume エンドポイントを有効にするか
ENABLE_OPS_ASSUME = True
