from pathlib import Path
import json
from typing import Any

DATA_DIR = Path(__file__).parent.joinpath("data")
SCRAPING_DATA_DIR = DATA_DIR.joinpath("scraping")


def load_json(fpath: str) -> str:
    with open(fpath, "r") as f:
        return json.load(f)


def write_json(
    obj: Any,
    fpath: str,
) -> str:
    with open(fpath, "w", encoding="utf8") as f:
        json.dump(obj, f, indent=4)


def load_text(fpath: str) -> str:
    with open(fpath, "r") as f:
        return f.read()


def write_text(
    text: str,
    fpath: str,
) -> str:
    with open(fpath, "w") as f:
        return f.write(text)
