"""Very small FX helper used for display-only conversions.

Rates are static demo values; conversions here never touch settlement amounts,
which always move in the source currency.
"""
_RATES = {
    ("JPY", "USD"): 0.0067,
    ("JPY", "EUR"): 0.0062,
    ("USD", "JPY"): 149.0,
    ("EUR", "JPY"): 162.0,
}


def convert(amount_minor, src, dst):
    if src == dst:
        return amount_minor
    rate = _RATES.get((src, dst))
    if rate is None:
        return None
    return int(round(amount_minor * rate))
