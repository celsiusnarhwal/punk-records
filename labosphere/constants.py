import os

from path import Path
from yarl import URL

DEV_MODE = os.getenv("DEV_MODE")
HERE = Path(__file__).parent
ROOT = HERE.parent
BASE_URL = URL("https://tcbscans.com")
GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
DOCKER = os.getenv("DOCKER")

BASE_METADATA = {
    "title": "One Piece",
    "description": (HERE / "description.txt").read_text(),
    "artist": "Eiichiro Oda",
    "author": "Eiichiro Oda",
    "cover": "https://cdn.myanimelist.net/images/manga/2/253146.jpg",
    "chapters": {
        "0": {
            "title": "About This Repository",
            "groups": {
                "celsius narhwal": [
                    "https://raw.githubusercontent.com/celsiusnarhwal/punk-records/main/about.png"
                ]
            },
        }
    },
}
