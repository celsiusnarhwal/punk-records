import json

from labosphere.constants import CUBARI_JSON

if not CUBARI_JSON.exists():
    json.dump({}, CUBARI_JSON.open("w"), indent=4)
