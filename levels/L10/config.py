"""Gatekeeper configuration.

Gatekeeper is a small multi-tenant control plane: tenants self-register, invite
members, and manage API keys. A few tenant slugs are operated by the platform
team and carry platform-admin privileges.
"""
import os


class Config:
    DB_PATH = os.environ.get("GATEKEEPER_DB", "gatekeeper.db")

    # Slugs that end users may not register (operated by the platform team).
    RESERVED_SLUGS = {"admin", "root", "system", "support", "internal", "staff"}

    # Tenant slugs that are granted platform-admin privileges.
    PLATFORM_ADMIN_TENANTS = {"admin", "internal"}

    # Plans and their seat caps.
    PLAN_SEATS = {"free": 3, "team": 25, "business": 200}
    DEFAULT_PLAN = os.environ.get("GATEKEEPER_PLAN", "free")


config = Config()
