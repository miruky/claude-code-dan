"""Client preferences codec.

The preferences blob carries UI state (theme, sort order, pinned items).
Modern clients send JSON; legacy desktop clients send the original binary
format. decode_prefs() picks the codec based on config.
"""
import base64
import json
import pickle

import config


def decode_prefs(raw):
    """raw is the base64 string from the 'prefs' cookie/field."""
    if not raw:
        return {}
    data = base64.b64decode(raw)
    if config.PREF_FORMAT == "json":
        return json.loads(data.decode("utf-8"))
    # legacy binary blob
    return pickle.loads(data)


def encode_prefs(obj):
    if config.PREF_FORMAT == "json":
        data = json.dumps(obj).encode("utf-8")
    else:
        data = pickle.dumps(obj)
    return base64.b64encode(data).decode("ascii")
