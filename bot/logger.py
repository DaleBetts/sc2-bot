from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = os.environ.get("BOT_DATA_DIR", "/data")


class GameLogger:
    """Appends JSON-lines game events to /data/game_<timestamp>.jsonl.

    Falls back to ./data/ when /data is not writable (local dev on Windows).
    Each event is flushed immediately so partial logs survive crashes.
    """

    def __init__(self) -> None:
        self._start = time.monotonic()
        path = self._resolve_dir()
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self._path = path / f"game_{ts}.jsonl"

    # ── public ────────────────────────────────────────────────────────────────

    def log(self, event: str, game_time: float = 0.0, **fields) -> None:
        record = {
            "event": event,
            "game_time": round(game_time, 1),
            "wall_s": round(time.monotonic() - self._start, 1),
            **fields,
        }
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    # ── internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _resolve_dir() -> Path:
        for candidate in (_DATA_DIR, "./data"):
            p = Path(candidate)
            try:
                p.mkdir(parents=True, exist_ok=True)
                # Verify we can actually write there
                probe = p / ".write_test"
                probe.touch()
                probe.unlink()
                return p
            except OSError:
                continue
        raise RuntimeError("Cannot find a writable directory for game logs")
