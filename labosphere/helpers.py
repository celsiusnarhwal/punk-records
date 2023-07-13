import hashlib
import json
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup, ResultSet
from dict_deep import deep_get as base_deep_get
from fake_useragent import UserAgent
from requests import Response

from labosphere.constants import BASE_METADATA, BASE_URL, CUBARI_JSON


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


def load_cubari() -> dict:
    cubari = json.load(CUBARI_JSON.open())
    cubari.update(BASE_METADATA)
    dump_cubari(cubari)

    return json.load(CUBARI_JSON.open())


def dump_cubari(data: dict):
    key_order = [*BASE_METADATA.keys(), "chapters"]
    data = OrderedDict(sorted(data.items(), key=lambda x: key_order.index(x[0])))
    json.dump(data, CUBARI_JSON.open("w"), indent=4)


def deep_get(obj, key, default=None, **kwargs):
    return base_deep_get(obj, key, **kwargs) or default
