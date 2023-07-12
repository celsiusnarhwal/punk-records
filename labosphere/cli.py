import os
import subprocess
from datetime import datetime

import typer
from path import Path

from labosphere import callbacks
from labosphere.constants import BASE_URL, CHAPTER_NUMBER, CUBARI_JSON
from labosphere.helpers import dump_cubari, get_chapter_list, get_soup, load_cubari

app = typer.Typer(no_args_is_help=True)


@app.command("start")
def start():
    """
    Run Labosphere.
    """
    for chapter in get_chapter_list():
        cubari = load_cubari()
        cubari["chapters"] = cubari.get("chapters", {})

        number = CHAPTER_NUMBER.search(chapter.text).group()
        title = chapter.text.splitlines()[2].strip()

        soup = get_soup(BASE_URL / chapter.get("href").lstrip("/"))
        pages = soup.find_all(
            "img", src=lambda src: src and "cdn.onepiecechapters.com" in src
        )

        old_metadata = cubari["chapters"].get(number, {})
        old_metadata.pop("last_updated", None)

        new_metadata = {
            "title": title,
            "groups": {"TCB Scans": [page.get("src") for page in pages]},
        }

        changes = old_metadata != new_metadata

        if changes:
            new_metadata["last_updated"] = int(datetime.utcnow().timestamp())
            cubari["chapters"][number] = new_metadata
            dump_cubari(cubari)

            print(
                f"Updated Chapter {number}: {title}"
                if title
                else f"Updated Chapter {number}"
            )

            if os.getenv("GITHUB_ACTIONS"):
                cmds = [
                    "git config --global user.name github-actions[bot]",
                    "git config --global user.email github-actions[bot]@users.noreply.github.com",
                    "git add .",
                    f'git commit -m "Update cubari.json"',
                    "git push",
                ]

                for cmd in cmds:
                    subprocess.run(cmd, shell=True, check=True)

        else:
            print(
                f"No changes to Chapter {number}: {title}"
                if title
                else f"No changes to Chapter {number}"
            )

    if os.getenv("DOCKER"):
        mount = Path("/labosphere")
        mount.mkdir_p()
        (mount / "cubari.json").write_text(CUBARI_JSON.read_text())
        exit()


# noinspection PyUnusedLocal
@app.callback(
    epilog=f"Labosphere © {datetime.now().year} celsius narhwal. Thank you kindly for your attention."
)
def main(
    version: bool = typer.Option(
        None,
        "--version",
        is_eager=True,
        help="View Labosphere's version.",
        callback=callbacks.version,
        rich_help_panel="About Labosphere",
    ),
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
