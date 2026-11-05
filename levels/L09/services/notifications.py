"""Outbound notification stubs.

In production these enqueue email/SMS. Here they just append to an in-memory
log so the rest of the flow is exercised without external calls.
"""
SENT = []


def notify_transfer(owner, result):
    SENT.append({"to": owner, "ref": result.get("ref"),
                 "amount_minor": result.get("amount_minor")})
    return True
