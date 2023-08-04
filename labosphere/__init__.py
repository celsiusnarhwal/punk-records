import json

from labosphere.helpers import cubari_path

if not cubari_path().exists():
    json.dump({}, cubari_path().open("w"), indent=4)
