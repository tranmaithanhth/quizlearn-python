"""Persist a daily review session separately from long-term card scheduling.

Each set has at most one paused session. Invalid/corrupt saves are ignored.
No changes to the existing SQLite learning database are required.
"""
import json
import os
from pathlib import Path


class DailySessionStore:
    def __init__(self, directory: str | Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, set_id: int) -> Path:
        return self.directory / f"daily_review_{int(set_id)}.json"

    def load(self, set_id: int) -> dict | None:
        try:
            data = json.loads(self._path(set_id).read_text(encoding="utf-8"))
            if (
                not isinstance(data, dict)
                or data.get("version") != 1
                or data.get("set_id") != int(set_id)
                or not isinstance(data.get("pending"), list)
                or not all(type(n) is int and n > 0 for n in data["pending"])
                or type(data.get("total")) is not int
                or data["total"] < 0
                or type(data.get("completed")) is not int
                or not 0 <= data["completed"] <= data["total"]
                or not isinstance(data.get("ratings"), dict)
            ):
                return None
            return data
        except (OSError, ValueError, TypeError):
            return None

    def save(
        self, set_id: int, pending: list[int], total: int,
        completed: int, ratings: dict[str, int],
    ) -> None:
        data = {
            "version": 1,
            "set_id": int(set_id),
            "pending": list(pending),
            "total": int(total),
            "completed": int(completed),
            "ratings": dict(ratings),
        }
        dest = self._path(set_id)
        tmp = dest.with_suffix(".json.tmp")
        try:
            tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, dest)
        finally:
            tmp.unlink(missing_ok=True)

    def clear(self, set_id: int) -> None:
        self._path(set_id).unlink(missing_ok=True)
