import os
import re
import sys
import time
from datetime import datetime

import typer
from path import Path

from labosphere import callbacks
from labosphere.constants import BASE_URL, DOCKER, GITHUB_ACTIONS
from labosphere.helpers import (
    cubari_path,
    deep_get,
    dump_cubari,
    get_chapter_list,
    get_soup,
    load_cubari,
)

app = typer.Typer(no_args_is_help=True)


@app.command("start")
def start(
    cooldown: int = typer.Option(
        0, help="The number of seconds to wait between sending requests to TCB Scans."
    ),
    timeout: int = typer.Option(
        None,
        min=1,
        help="Labosphere will exit after requesting this many consecutive chapters "
        "with no changes.",
    ),
):
    """
    Run Labosphere.
    """
    timeout_tracker = 0

    for chapter in get_chapter_list():
        number = re.search(r"[\d.]+", chapter.text).group()

        cubari = load_cubari()
        cubari["chapters"] = cubari.get("chapters", {})

        title = chapter.text.splitlines()[2].strip()

        soup = get_soup(BASE_URL / chapter.get("href").lstrip("/"))
        pages = soup.find_all(
            "img", src=lambda src: src and "cdn.onepiecechapters.com" in src
        )

        old_metadata = deep_get(cubari, f"chapters.{number}", default={})
        old_metadata.pop("last_updated", None)

        new_metadata = {
            "title": title,
            "groups": {
                "TCB Scans": [
                    page.get("src") for page in pages if page.parent.name != "a"
                ]
            },
        }

        if old_metadata != new_metadata:
            timeout_tracker = 0
            cubari["chapters"][number] = {
                **new_metadata,
                "last_updated": int(datetime.utcnow().timestamp()),
            }
            dump_cubari(cubari)

            print(
                f"Updated Chapter {number}: {title}"
                if title
                else f"Updated Chapter {number}"
            )

        else:
            timeout_tracker += 1

            print(
                f"No changes to Chapter {number}: {title}"
                if title
                else f"No changes to Chapter {number}"
            )

        if timeout and timeout_tracker >= timeout:
            print(f"Requested {timeout} consecutive chapters with no changes. Exiting.")
            sys.exit()

        time.sleep(cooldown)

    if timeout and GITHUB_ACTIONS:
        print("LABOSPHERE_FLAG_PR=1", file=open(os.getenv("GITHUB_ENV"), "a"))

    if DOCKER:
        mount = Path("/labosphere")
        mount.mkdir_p()
        (mount / "cubari.json").write_text(cubari_path().read_text())
        exit()


# noinspection PyUnusedLocal
@app.callback(
    epilog=f"Labosphere © {datetime.now().year} celsius narhwal. Thank you kindly for your attention."
)
def main(
    license: bool = typer.Option(
        None,
        "--license",
        is_eager=True,
        help="View Labosphere's license.",
        callback=callbacks.license,
        rich_help_panel="About Labosphere",
    ),
):
    """
    Labosphere generates Cubari repositories for TCB Scans' One Piece releases.
    """


if __name__ == "__main__":
    start()
