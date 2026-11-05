"""Helpers shared by the PoC scripts.

Each PoC runs in its own subprocess (see run_all.sh) so that per-level
helper modules (db, auth, config, ...) never collide in sys.modules.
All PoCs operate only on the local toy app via Flask's in-process test
client; nothing binds a socket except the L07 race PoC, which uses
127.0.0.1 and shuts down immediately.
"""
import os
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_level(level):
    """Import the app module of levels/<level> in isolation.

    Returns the imported module. Chdir into a fresh temp dir first so any
    SQLite files land there, not in the repo.
    """
    level_dir = os.path.join(REPO, "levels", level)
    workdir = tempfile.mkdtemp(prefix=f"poc-{level}-")
    os.chdir(workdir)
    sys.path.insert(0, level_dir)
    import importlib

    return importlib.import_module("app"), level_dir, workdir


def ok(cond, msg):
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {msg}")
    if not cond:
        sys.exit(1)
