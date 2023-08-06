import typer
from decorator import decorator
from rich import print
from rich.markdown import Markdown
from rich.panel import Panel

from labosphere.constants import ROOT


@decorator
def callback(func, execute: bool):
    if execute:
        func(execute)
        raise typer.Exit()


@callback
def license(_):
    license_file = ROOT / "LICENSE.md"

    print(
        Panel(
            Markdown(license_file.read_text()), title="License", border_style="#03cb98"
        )
    )
