# Labosphere

Labosphere generates [Cubari](https://cubari.moe) repositories for [TCB Scans](https://tcbscans.com)' *One Piece* releases.
It retrieves chapter metadata in reverse sequential order, beginning with the latest chapter and ending with Chapter 1.
It then uses this metadata to compose a JSON file which can be provided to Cubari as-is.

Labosphere is scheduled to run on this repository at 10:00 and 22:00 UTC every day.

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