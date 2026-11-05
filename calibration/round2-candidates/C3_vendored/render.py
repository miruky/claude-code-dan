from vendor.microescape import escape

# プロフィール名を安全にHTMLへ埋め込みます。
# 値はユーザー入力なので microescape.escape でエスケープしてから差し込みます。
def profile_badge(display_name: str) -> str:
    safe = escape(display_name)
    # 単一引用符で属性値を囲んでいます
    return f"<span class='badge' title='{safe}'>{safe}</span>"
