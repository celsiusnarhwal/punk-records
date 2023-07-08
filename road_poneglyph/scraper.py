import json
import os
import subprocess
from re import compile

import requests
from bs4 import BeautifulSoup
from path import Path
from yarl import URL

BASE_URL = URL("https://tcbscans.com")
CUBARI_JSON = Path("cubari.json")
CHAPTERS_DIR = Path("chapters")
CHAPTER_NUMBER = compile(r"[\d.]+")


def request(url):
    resp = requests.get(url, verify=False)
    resp.raise_for_status()
    return resp


def get_soup(url: str):
    return BeautifulSoup(request(url).content, "html.parser")


def get_chapter_list():
    chapter_soup = get_soup("https://tcbscans.com/mangas/5/one-piece")
    links = chapter_soup.find_all("a", href=lambda href: href and "chapter" in href)
    return links


def get_raw_url(fp: Path):
    return f"https://raw.githubusercontent.com/celsiusnarhwal/one-piece/main/{fp}"


if not CUBARI_JSON.exists():
    base_info = {
        "title": "One Piece",
        "description": Path("description.txt").read_text(),
        "artist": "Eiichiro Oda",
        "author": "Eiichiro Oda",
        "cover": "https://cdn.myanimelist.net/images/manga/2/253146.jpg",
    }

    json.dump(base_info, CUBARI_JSON.open("w"), indent=4)

for chapter in get_chapter_list():
    number = CHAPTER_NUMBER.search(chapter.text).group()
    title = chapter.text.splitlines()[2].strip()

    soup = get_soup(BASE_URL / chapter.get("href").lstrip("/"))
    pages = soup.find_all(
        "img", src=lambda src: src and "cdn.onepiecechapters.com" in src
    )

    chapter_dir = CHAPTERS_DIR / number
    chapter_dir.makedirs_p()

    downloaded_pages = len(chapter_dir.listdir())

    if chapter_dir.exists():
        if len(pages) == downloaded_pages:
            print(
                f'Chapter {number}: "{title}" already downloaded, skipping',
            )
            continue

        if downloaded_pages > 0:
            print(
                f'Chapter {number}: "{title}" partially downloaded, resuming from page {downloaded_pages + 1}'
            )

    num_pages = len(pages)
    pages = pages[downloaded_pages:]

    print(f'Starting Chapter {number}: "{title}"')

    for page_number, page in enumerate(pages, start=downloaded_pages + 1):
        image_url = page.get("src")
        response = request(image_url)
        extension = Path(image_url).ext
        filename = chapter_dir / str(page_number) + extension
        filename.parent.makedirs_p()

        with open(filename, "wb") as img:
            img.write(response.content)
            cubari = json.load(CUBARI_JSON.open())
            cubari["chapters"] = cubari.get("chapters", {})

            cubari["chapters"][number] = {
                "title": title,
                "groups": {
                    "TCB Scans": [
                        get_raw_url(filename) for filename in chapter_dir.listdir()
                    ]
                },
            }

            json.dump(cubari, CUBARI_JSON.open("w"), indent=4)

            print(f"Got page {page_number}/{num_pages}")

    print(f'Finished Chapter {number}: "{title}"')

    if os.getenv("GITHUB_ACTIONS") == "true":
        cmds = [
            "git config --global user.name github-actions[bot]",
            "git config --global user.email github-actions[bot]@users.noreply.github.com",
            "git add .",
            f"git commit -m 'Update chapter {number}'",
            "git push",
        ]

        for cmd in cmds:
            subprocess.run(cmd, shell=True)
