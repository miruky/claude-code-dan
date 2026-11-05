import signing
import accounts

# 社内運用ツールが、対象ユーザーとして一時的にログインするための検証。
# 運用ツールは user id に署名したトークンを添えて assume を呼びます。
def assume_user(uid: int, token: str):
    if not signing.verify(str(uid), token):
        return None
    return accounts.get_user(uid)
