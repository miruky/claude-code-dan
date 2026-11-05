"""Lightweight record wrappers (used by serializers and tests)."""
from dataclasses import dataclass, asdict


@dataclass
class Account:
    id: int
    number: str
    owner: str
    currency: str
    balance_minor: int
    status: str = "active"

    def public(self):
        d = asdict(self)
        d.pop("owner", None)
        return d
