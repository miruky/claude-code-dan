"""Small text helpers used across services."""


def normalize_slug(slug):
    """Canonical form of a tenant slug for comparisons and lookups.

    Trims surrounding whitespace and lowercases so that equivalent slugs map to
    the same key regardless of incidental casing or padding.
    """
    return (slug or "").strip().lower()


def truncate(s, n=60):
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def slugify(display_name):
    out = []
    for ch in (display_name or "").lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    s = "".join(out).strip("-")
    return s[:30] or "tenant"
