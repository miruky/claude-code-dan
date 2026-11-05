"""Money parsing and formatting.

Amounts move through the API as decimal strings (e.g. "1500" or "1500.50")
to avoid binary floating point. Internally everything is an integer number of
minor units (e.g. yen, or cents for sub-unit currencies).
"""

MINOR_PER_MAJOR = {"JPY": 1, "USD": 100, "EUR": 100}


class MoneyError(ValueError):
    pass


def to_minor_units(amount_str, currency):
    """Convert a decimal amount string to an integer number of minor units."""
    if amount_str is None:
        raise MoneyError("amount is required")
    s = str(amount_str).strip().replace(",", "")
    if not s:
        raise MoneyError("amount is empty")
    factor = MINOR_PER_MAJOR.get(currency, 100)
    if "." in s:
        whole, frac = s.split(".", 1)
        frac = (frac + "00")[:2]
        minor = int(whole or "0") * factor + int(frac) * (factor // 100 or 1)
    else:
        minor = int(s) * factor
    if minor < 0:
        raise MoneyError("amount must be positive")
    return minor


def format_minor(minor, currency):
    factor = MINOR_PER_MAJOR.get(currency, 100)
    if factor == 1:
        return str(minor)
    return "%d.%02d" % (minor // factor, minor % factor)
