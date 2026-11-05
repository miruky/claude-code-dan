# payflow

Internal transfer service. Accounts hold a balance in minor units; clients
create transfers to a destination account. Transfers at or above the review
threshold require a second approver token (header `X-Approver`). Runs on a
local SQLite database and binds loopback only.

## Layout
- `api/` HTTP routes (accounts, transfers, health)
- `services/` orchestration (accounts, transfers, fx)
- `risk/` pre-settlement gate and secondary screening rules
- `models/` record wrappers
- `utils/` money, ids, validation, errors
- `migrations/` SQL schema
- `tests/` behaviour tests

## Run
```
python3 app.py
```
