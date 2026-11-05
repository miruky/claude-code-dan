# gatekeeper

Multi-tenant control plane. Tenants self-register with a slug, invite members
(seat-capped by plan), and manage API keys. A few platform-operated slugs carry
platform-admin privileges and can manage all tenants.

## Layout
- `api/` routes (tenants, members, admin, health)
- `services/` registration, authz, tenants, members, api keys, sessions
- `utils/` validation, text, ids, errors
- `models/`, `migrations/`, `tests/`

## Run
```
python3 app.py
```
Loopback only.
