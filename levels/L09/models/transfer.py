from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Transfer:
    id: int
    src_account_id: int
    dest_number: str
    amount_minor: int
    currency: str
    status: str = "pending"
    approver: Optional[str] = None

    def to_dict(self):
        return asdict(self)
