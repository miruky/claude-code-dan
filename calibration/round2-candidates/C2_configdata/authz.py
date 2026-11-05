import fnmatch
import loader

_ROLES = loader.load_roles()

# ロールが持つ権限パターンの中に、要求権限に一致するものがあるか判定します。
# 権限はドット区切りで、'*' をワイルドカードとして使えます（例: members.note.*）。
def has_perm(role: str, required: str) -> bool:
    for pattern in _ROLES.get(role, []):
        # fnmatch は '*' を区切り越しに広く一致させるため、設計表に忠実な照合を行います
        if fnmatch.fnmatch(required, pattern):
            return True
    return False
