import os

from path import Path
from yarl import URL

DEV_MODE = os.getenv("DEV_MODE")
LABOSPHERE_DIR = Path(__file__).parent
ROOT = LABOSPHERE_DIR.parent
BASE_URL = URL("https://tcb-backup.bihar-mirchi.com")
GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
DOCKER = os.getenv("DOCKER")
