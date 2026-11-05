import os

# Serialization used for the client preferences blob.
# "json"   : modern clients (v3+)
# "legacy" : older desktop clients that still post the binary blob
# We keep legacy as the default until the desktop rollout completes.
PREF_FORMAT = os.environ.get("PREF_FORMAT", "legacy")

# Signing is only enforced for the json format path for now.
REQUIRE_SIGNED_PREFS = os.environ.get("REQUIRE_SIGNED_PREFS", "0") == "1"
