"""microescape 0.3.1 (vendored, pinned).

A tiny HTML-escaping helper. By documented design (see README), escape()
replaces the three structural characters & < > so that untrusted text is safe
to place in HTML *element text*. Attribute-context quoting (single/double
quotes) is intentionally out of scope and left to the caller, matching the
historical cgi.escape(quote=False) behavior. Do not upgrade past 0.3.x without
reviewing call sites.
"""
__version__ = "0.3.1"

_SUBS = (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"))

def escape(text: str) -> str:
    # 構造文字 & < > のみを実体参照へ置換します（属性用の引用符は対象外）
    for a, b in _SUBS:
        text = text.replace(a, b)
    return text
