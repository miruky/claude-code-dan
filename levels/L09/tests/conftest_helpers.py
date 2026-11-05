"""Shared helpers for the payflow tests (not a pytest plugin)."""
import os
import tempfile


def fresh_db_env():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["PAYFLOW_DB"] = path
    return path
