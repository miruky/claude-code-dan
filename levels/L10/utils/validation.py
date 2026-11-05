"""Request field validation.

Slugs are lowercase DNS-style labels: letters, digits and hyphens, 3-30 chars.
"""
import re

from utils.errors import ApiError

# lowercase DNS-style label
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_slug(slug):
    if not SLUG_RE.match(slug or ""):
        raise ApiError("invalid slug: use 3-30 chars of a-z, 0-9, hyphen")
    return slug


def validate_email(email):
    if not EMAIL_RE.match(email or ""):
        raise ApiError("invalid email")
    return email


def validate_display_name(name):
    n = (name or "").strip()
    if not (1 <= len(n) <= 80):
        raise ApiError("invalid display name")
    return n
