from dataclasses import dataclass


@dataclass
class Beneficiary:
    id: int
    account_id: int
    name: str
    dest_number: str
    verified: bool = False
