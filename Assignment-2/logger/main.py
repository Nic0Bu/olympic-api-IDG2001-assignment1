"""Logger service.

Receives log entries from the main API and buffers them in memory.
Every FLUSH_SIZE entries the buffer is written out to a CSV file.
One file per day, named log_YYYY-MM-DD.csv.

Log files older than `retention_days` are deleted when a new day's file
is created (i.e. when the day rolls over during a flush).

Endpoints:
    POST /log          — add a log entry
    GET  /retention    — get current retention period (days)
    POST /retention    — update retention period
"""

import csv
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

LOG_DIR = Path(os.getenv("LOG_DIR", "/app/logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

# How many entries to hold in memory before writing to disk
FLUSH_SIZE = 10

app = FastAPI(title="Logger")

_buffer: list = []
_retention_days: int = 7
_last_flush_date: Optional[str] = None  # tracks when we last rotated the log file


class LogEntry(BaseModel):
    username: str
    endpoint: str
    tokens: int
    time: Optional[str] = None


class RetentionUpdate(BaseModel):
    n: int


def _log_file_for(date: datetime) -> Path:
    return LOG_DIR / f"log_{date.strftime('%Y-%m-%d')}.csv"


def _flush(entries: list, date: datetime):
    if not entries:
        return
    log_file = _log_file_for(date)
    write_header = not log_file.exists()
    with open(log_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["time", "username", "endpoint", "tokens"])
        if write_header:
            writer.writeheader()
        writer.writerows(entries)


def _cleanup_old_files(today: datetime):
    cutoff = today - timedelta(days=_retention_days)
    for f in LOG_DIR.glob("log_*.csv"):
        try:
            date_str = f.stem.replace("log_", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date.date() < cutoff.date():
                f.unlink()
        except Exception:
            pass


@app.post("/log")
def add_log(entry: LogEntry):
    global _buffer, _last_flush_date

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    row = {
        "time": entry.time or now.isoformat(),
        "username": entry.username,
        "endpoint": entry.endpoint,
        "tokens": entry.tokens,
    }
    _buffer.append(row)

    # flush when buffer is full
    if len(_buffer) >= FLUSH_SIZE:
        _flush(_buffer, now)
        _buffer = []

        # if the day changed since last flush, clean up old logs
        if _last_flush_date != today_str:
            _cleanup_old_files(now)
        _last_flush_date = today_str

    return {"ok": True}


@app.get("/retention")
def get_retention():
    return {"n": _retention_days}


@app.post("/retention")
def set_retention(body: RetentionUpdate):
    global _retention_days
    if body.n < 1:
        raise HTTPException(status_code=400, detail="n must be at least 1")
    _retention_days = body.n
    # apply immediately so stale files get cleaned up right away
    _cleanup_old_files(datetime.now())
    return {"n": _retention_days}
