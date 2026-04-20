"""Script to load the Olympic dataset CSV into the SQLite database.

Download athlete_events.csv from Kaggle and place it in the data/ folder,
then run:

    python load_data.py

Dataset: kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results
Expected columns:
    ID,Name,Sex,Age,Height,Weight,Team,NOC,Games,Year,Season,City,Sport,Event,Medal
"""

import csv
import sys
from pathlib import Path
from typing import Optional
from app.database import engine, SessionLocal, Base
from app.models import AthleteEvent

Base.metadata.create_all(bind=engine)

CSV_PATH = Path("data/athlete_events.csv")
BATCH_SIZE = 1000


def parse_float(value: object) -> Optional[float]:
    """Return a float for the value, or None if it is empty or non-numeric."""
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return None


def parse_int(value: object) -> Optional[int]:
    """Return an int for the value, or None if it is empty or non-numeric."""
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return None


def load_data(csv_path: Path = CSV_PATH) -> int:
    """Load athlete events from a CSV file into the database.

    Inserts rows in batches for efficiency.
    Returns the total number of rows inserted.
    """
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.")
        print(
            "Download athlete_events.csv from Kaggle and place it in data/"
        )
        sys.exit(1)

    db = SessionLocal()
    count = 0
    batch: list = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                event = AthleteEvent(
                    athlete_id=parse_int(row.get("ID")),
                    name=row.get("Name", ""),
                    sex=row.get("Sex") or None,
                    age=parse_float(row.get("Age")),
                    height=parse_float(row.get("Height")),
                    weight=parse_float(row.get("Weight")),
                    team=row.get("Team") or None,
                    noc=row.get("NOC") or None,
                    games=row.get("Games") or None,
                    year=parse_int(row.get("Year")),
                    season=row.get("Season") or None,
                    city=row.get("City") or None,
                    sport=row.get("Sport") or None,
                    event=row.get("Event") or None,
                    medal=row.get("Medal") or None,
                )
                batch.append(event)
                count += 1
                if len(batch) >= BATCH_SIZE:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    print(f"  Inserted {count} rows...", end="\r")
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
        print(f"\nDone. Inserted {count} rows total.")
        return count
    finally:
        db.close()


if __name__ == "__main__":
    print(f"Loading data from {CSV_PATH} ...")
    load_data()
