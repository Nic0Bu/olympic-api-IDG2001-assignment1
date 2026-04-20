"""Startup script run before the web server on Render.

Creates database tables and loads the dataset if the DB is empty.
Safe to run multiple times — skips loading if data already exists.
"""

from pathlib import Path
from app.database import engine, SessionLocal, Base
from app.models import AthleteEvent

print("Running startup checks...")
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    count = db.query(AthleteEvent).count()
    if count == 0:
        csv_path = Path("data/athlete_events.csv")
        if csv_path.exists():
            print("Database is empty — loading dataset (this may take a minute)...")
            from load_data import load_data
            load_data(csv_path)
        else:
            print("Warning: data/athlete_events.csv not found, skipping data load.")
    else:
        print(f"Database already has {count} rows — skipping data load.")
finally:
    db.close()

print("Startup complete.")
