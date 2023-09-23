# Labosphere

Labosphere generates [Cubari](https://cubari.moe) repositories for *One Piece* releases by [VIZ Media](https://viz.com) (chapters 1-998)
and [TCB Scans](https://tcbscans.com) (chapters 999+).

It retrieves chapter metadata in reverse sequential order, beginning with the latest chapter and ending with Chapter 1.
It then uses this metadata to compose a JSON file which can be provided to Cubari as-is.

The technically inclined are welcome to run Labosphere themselves:

```bash
docker run -v ${PWD}/labosphere:/labosphere -t ghcr.io/celsiusnarhwal/labosphere:latest
```

Or, if you prefer the hard way (Python 3.11 or later and [Poetry](https://python-poetry.org) required):

```bash
git clone https://github.com/celsiusnarhwal/punk-records
cd punk-records/labosphere
poetry install --only main
poetry run labosphere start
```

Be advised that Labosphere offers no changelogs or version guarantees.