import os
import sys
import time
from datetime import datetime

import tomlkit as toml
import typer
from dict_deep import deep_set
from path import Path
from rich import print

from labosphere import callbacks, utils
from labosphere.constants import BASE_URL, DOCKER, GITHUB_ACTIONS, LABOSPHERE_DIR

app = typer.Typer(no_args_is_help=True)


@app.command("start")
def start(
    start_from: float = typer.Option(
        None, "--from", help="The number of the newest chapter to retrieve."
    ),
    end_at: float = typer.Option(
        1, "--to", min=1, help="The number of the oldest chapter to retrieve."
    ),
    explicit_chapters: list[float] = typer.Option(
        ...,
        "--chapter",
        "-c",
        default_factory=list,
        help="The number of a specific chapter to retrieve. Specify multiple times "
        "for multiple chapters. If specified, only chapters provided to "
        "this option will be retrieved. "
        "Overrides --from and --to.",
        show_default=False,
    ),
    cooldown: int = typer.Option(
        0,
        min=0,
        help="The number of seconds to wait between sending requests to TCB Scans.",
    ),
    timeout: int = typer.Option(
        None,
        min=0,
        help="Labosphere will exit after requesting this many consecutive chapters "
        "with no changes.",
    ),
):
    """
    Run Labosphere.
    """
    chapter_pool = utils.get_chapter_list()
    latest_chapter = float(utils.get_chapter_number(chapter_pool[0]))
    start_from = start_from or latest_chapter
    viz_titles = toml.load((LABOSPHERE_DIR / "titles.toml").open())
    volumes = toml.load((LABOSPHERE_DIR / "volumes.toml").open())

    if start_from > latest_chapter:
        raise typer.BadParameter(
            f"{utils.intify(start_from)} is greater than the latest chapter number "
            f"({utils.intify(latest_chapter)}).",
            param_hint="--from",
        )
    elif start_from < end_at:
        raise typer.BadParameter(
            f"--from ({utils.intify(start_from)}) is less than --to ({utils.intify(end_at)})."
        )

    if explicit_chapters:
        chapter_pool = [
            c for c in chapter_pool if utils.get_chapter_number(c) in explicit_chapters
        ]
    else:
        chapter_pool = [
            c
            for c in chapter_pool
            if start_from >= utils.get_chapter_number(c) >= end_at
        ]

    updated_chapters = 0
    timeout_tracker = 0

    for chapter in chapter_pool:
        chapter_number = utils.get_chapter_number(chapter)

        if explicit_chapters and chapter_number not in explicit_chapters:
            continue

        cubari = utils.load_cubari()
        cubari["chapters"] = cubari.get("chapters", {})

        chapter_title = (
            chapter.text.splitlines()[2].strip() or viz_titles[chapter_number]
        )

        translation_group = "VIZ Media" if chapter_number < 999 else "TCB Scans"

        soup = utils.get_soup(BASE_URL / chapter.get("href").lstrip("/"))
        pages = soup.find_all(
            "img", src=lambda src: src and "cdn.onepiecechapters.com" in src
        )

        old_metadata = utils.deep_get(cubari, f"chapters.{chapter_number}", default={})
        old_metadata.pop("last_updated", None)

        new_metadata = {
            "title": chapter_title,
            "groups": {
                translation_group: [
                    page.get("src") for page in pages if page.parent.name != "a"
                ]
            },
        }

        if chapter_number.is_integer():
            # The volume number is the first key in volumes.toml for which the value is greater than the chapter number.
            # If no such key exists, neither does a volume. Chapters 1053.1 to 1053.4 do not have volumes.
            chapter_volume = next(
                (vol for vol, bound in volumes.items() if bound >= chapter_number), None
            )

            if chapter_volume:
                new_metadata["volume"] = chapter_volume

        if old_metadata != new_metadata:
            timeout_tracker = 0

            deep_set(
                cubari,
                f"chapters.{chapter_number}",
                {
                    **new_metadata,
                    "last_updated": int(datetime.utcnow().timestamp()),
                },
            )

            utils.dump_cubari(cubari)

            print(
                f"Updated Chapter {utils.intify(chapter_number)}: {chapter_title}"
                if chapter_title
                else f"Updated Chapter {utils.intify(chapter_number)}"
            )

        else:
            updated_chapters += 1
            timeout_tracker += 1

            print(
                f"No changes to Chapter {utils.intify(chapter_number)}: {chapter_title}"
                if chapter_title
                else f"No changes to Chapter {utils.intify(chapter_number)}"
            )

        if timeout and timeout_tracker >= timeout:
            print(f"Requested {timeout} consecutive chapters with no changes. Exiting.")
            sys.exit()

        time.sleep(cooldown)

    if timeout and updated_chapters >= timeout and GITHUB_ACTIONS:
        print("LABOSPHERE_FLAG_PR=1", file=open(os.getenv("GITHUB_ENV"), "a"))

    if DOCKER:
        mount = Path("/labosphere")
        mount.mkdir_p()
        (mount / "cubari.json").write_text(utils.cubari_path().read_text())
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
    app()
