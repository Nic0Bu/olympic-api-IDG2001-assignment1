"""Startup script — waits for postgres, creates tables, loads dataset if empty."""

import time
from pathlib import Path
from sqlalchemy.exc import OperationalError

print("Starting up...")

# Postgres might not be ready immediately even with depends_on
for attempt in range(30):
    try:
        from app.database import engine, SessionLocal, Base
        from app.models import AthleteEvent
        Base.metadata.create_all(bind=engine)
        print("Database connection OK.")
        break
    except OperationalError:
        print(f"Waiting for database... ({attempt + 1}/30)")
        time.sleep(2)
else:
    print("Could not connect to the database after 30 attempts, giving up.")
    raise SystemExit(1)

db = SessionLocal()
try:
    count = db.query(AthleteEvent).count()
    if count == 0:
        csv_path = Path("data/athlete_events.csv")
        if csv_path.exists():
            print("DB is empty, loading dataset (this takes a minute or two)...")
            from load_data import load_data
            load_data(csv_path)
        else:
            print("No CSV found at data/athlete_events.csv — skipping data load.")
    else:
        print(f"DB already has {count} rows, skipping load.")
finally:
    db.close()

print("Startup complete.")
