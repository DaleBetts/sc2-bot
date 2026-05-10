#!/usr/bin/env python3
"""Download the bot's /data zip from AI Arena and extract new .jsonl log files.

Requires env vars:
  AIARENA_API_TOKEN  — your personal API token
  AIARENA_BOT_ID     — numeric bot ID (1126)

Outputs extracted files to logs/ in the repo root.
Skips files that already exist locally so re-runs are idempotent.
"""
from __future__ import annotations

import io
import os
import sys
import zipfile
from pathlib import Path

import requests

API_BASE = "https://aiarena.net/api"
TOKEN = os.environ["AIARENA_API_TOKEN"]
BOT_ID = os.environ["AIARENA_BOT_ID"]
HEADERS = {"Authorization": f"Token {TOKEN}"}
LOGS_DIR = Path(__file__).parent.parent / "logs"


def get_bot_data_url() -> str | None:
    resp = requests.get(f"{API_BASE}/bots/{BOT_ID}/", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json().get("bot_data")


def download_and_extract(url: str) -> int:
    LOGS_DIR.mkdir(exist_ok=True)
    resp = requests.get(url, headers=HEADERS, timeout=120)
    resp.raise_for_status()

    extracted = 0
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        for name in zf.namelist():
            if not name.endswith(".jsonl"):
                continue
            dest = LOGS_DIR / Path(name).name
            if dest.exists():
                continue
            dest.write_bytes(zf.read(name))
            print(f"  extracted: {dest.name}")
            extracted += 1

    return extracted


def main() -> None:
    print(f"Fetching bot data for bot {BOT_ID}…")
    url = get_bot_data_url()
    if not url:
        print("No bot_data on record yet — bot hasn't played any games with logging enabled.")
        sys.exit(0)

    print(f"Downloading bot data zip…")
    n = download_and_extract(url)
    print(f"Done — {n} new log file(s) saved to logs/")


if __name__ == "__main__":
    main()
