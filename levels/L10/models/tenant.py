from dataclasses import dataclass


@dataclass
class Tenant:
    id: int
    slug: str
    display_name: str
    plan: str = "free"
