import hmac
import hashlib
from config import SIGNING_KEY

# 任意の文字列メッセージに HMAC-SHA256 で署名します
def sign(message: str) -> str:
    mac = hmac.new(SIGNING_KEY, message.encode("utf-8"), hashlib.sha256)
    return mac.hexdigest()

# 署名を定数時間比較で検証します
def verify(message: str, signature: str) -> bool:
    expected = sign(message)
    return hmac.compare_digest(expected, signature or "")
