from dataclasses import dataclass


@dataclass
class Member:
    id: int
    tenant_id: int
    email: str
    role: str = "member"
