from re import compile

from path import Path
from yarl import URL

HERE = Path(__file__).parent
ROOT = HERE.parent
BASE_URL = URL("https://tcbscans.com")
CUBARI_JSON = ROOT / "cubari.json"
CHAPTER_NUMBER = compile(r"[\d.]+")

BASE_METADATA = {
    "title": "One Piece",
    "description": (HERE / "description.txt").read_text(),
    "artist": "Eiichiro Oda",
    "author": "Eiichiro Oda",
    "cover": "https://cdn.myanimelist.net/images/manga/2/253146.jpg",
}
