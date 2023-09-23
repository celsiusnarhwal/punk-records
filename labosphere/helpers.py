import copy
import json
import re
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup, PageElement, ResultSet
from dict_deep import deep_get as base_deep_get
from fake_useragent import UserAgent
from path import Path
from requests import Response

from labosphere.constants import BASE_URL, DEV_MODE, LABOSPHERE_DIR, ROOT


def base_metadata() -> dict:
    return {
        "title": "One Piece",
        "description": (LABOSPHERE_DIR / "description.txt").read_text(),
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


def request(url) -> Response:
    ua = UserAgent()
    resp = requests.get(url, headers={"User-Agent": ua.chrome})
    resp.raise_for_status()
    return resp


def get_soup(url: str) -> BeautifulSoup:
    return BeautifulSoup(request(url).content, "html.parser")


def get_chapter_list() -> ResultSet:
    return get_soup(BASE_URL / "mangas/5/one-piece").find_all(
        "a", href=lambda href: href and "chapter" in href
    )


def get_chapter_number(chapter: PageElement) -> str:
    return re.search(r"[\d.]+", chapter.text).group()


def without_keys(d: dict, *keys: str) -> dict:
    d = copy.deepcopy(d)

    for key in keys:
        d.pop(key, None)

    return d


def conditional_truncate(number: float) -> float | int:
    return int(number) if number.is_integer() else number


def cubari_path() -> Path:
    return ROOT / ("cubari.json" if not DEV_MODE else "test.cubari.json")


def load_cubari() -> dict:
    if not cubari_path().exists():
        json.dump({}, cubari_path().open("w"), indent=4)

    cubari = json.load(cubari_path().open())
    cubari.update(without_keys(base_metadata(), "chapters"))

    try:
        cubari["chapters"].update(base_metadata()["chapters"])
    except KeyError:
        cubari["chapters"] = base_metadata()["chapters"]

    dump_cubari(cubari)

    return json.load(cubari_path().open())


def dump_cubari(data: dict):
    data = OrderedDict(
        sorted(
            data.items(),
            key=lambda x: [*base_metadata().keys(), "chapters"].index(x[0]),
        )
    )

    data["chapters"] = OrderedDict(
        reversed(sorted(data.get("chapters", {}).items(), key=lambda x: float(x[0])))
    )

    json.dump(data, cubari_path().open("w"), indent=4)


def deep_get(obj, key, default=None, **kwargs):
    return base_deep_get(obj, key, **kwargs) or default
