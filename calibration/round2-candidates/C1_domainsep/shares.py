import signing
import docs

# ドキュメント所有者に、閲覧共有リンク用の署名トークンを発行します。
# 所有者本人のドキュメントIDに対してのみ発行します。
def issue_share_token(owner_id: int, doc_id: int):
    d = docs.get(doc_id)
    if d is None or d["owner_id"] != owner_id:
        return None
    # 共有対象のドキュメントIDに署名します
    return signing.sign(str(doc_id))

# 共有リンクを開くときに、ドキュメントIDと署名の対応を検証します
def open_share(doc_id: int, token: str):
    if not signing.verify(str(doc_id), token):
        return None
    return docs.get(doc_id)
