"""
Ingestion module.

- Reads files from wx_data/
- Converts -9999 to None, tenths to float units
- Avoids duplicate inserts by checking unique constraint
- Returns a summary dict for programmatic use (helpful in tests)
"""

import os
import logging
from datetime import datetime
from .database import db
from .models import WeatherRecord

logger = logging.getLogger(__name__)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

def _to_float_tenths(value):
    """Convert string numeric tenths to float; return None for -9999 or invalid."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v == -9999:
        return None
    return v / 10.0

def ingest_weather_data(folder_path="wx_data", commit_every=1000):
    """
    Ingest all files from folder_path.

    Returns:
        dict: {processed: int, inserted: int, elapsed_seconds: float}
    """
    start = datetime.utcnow()
    processed = 0
    inserted = 0

    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Data folder not found: {folder_path}")

    # Iterate sorted so results are deterministic
    for fname in sorted(os.listdir(folder_path)):
        if fname.startswith("."):
            continue
        station_id = os.path.splitext(fname)[0]
        fpath = os.path.join(folder_path, fname)
        with open(fpath, "r", encoding="utf-8") as fh:
            for line in fh:
                processed += 1
                parts = line.strip().split("\t")
                if len(parts) < 4:
                    logger.debug("Skipping malformed line: %r", line)
                    continue
                date_str, tmax_s, tmin_s, prcp_s = parts[:4]

                max_temp = _to_float_tenths(tmax_s)
                min_temp = _to_float_tenths(tmin_s)
                prcp_mm = _to_float_tenths(prcp_s)

                # Check if exists
                exists = WeatherRecord.query.filter_by(
                    station_id=station_id, date=date_str
                ).first()
                if exists:
                    continue

                rec = WeatherRecord(
                    station_id=station_id,
                    date=date_str,
                    max_temp=max_temp,
                    min_temp=min_temp,
                    precipitation=prcp_mm
                )
                db.session.add(rec)
                inserted += 1

                # Flush/commit in batches if dataset is large (not necessary for tests)
                if inserted % commit_every == 0:
                    db.session.commit()

    db.session.commit()
    end = datetime.utcnow()
    elapsed = (end - start).total_seconds()
    logger.info("Ingestion complete: processed=%d inserted=%d elapsed=%.2f s",
                processed, inserted, elapsed)
    return {"processed": processed, "inserted": inserted, "elapsed_seconds": elapsed}

