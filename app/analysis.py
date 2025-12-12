"""
Compute yearly aggregation and store results in WeatherStats.

- Year extracted as first 4 chars of the YYYYMMDD date string
- Averages ignore NULLs in DB
- Precip mm -> cm conversion (divide by 10)
- Skips existing station-year rows
"""

from sqlalchemy.sql import func
from .database import db
from .models import WeatherRecord, WeatherStats
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
    logger.addHandler(ch)
logger.setLevel(logging.INFO)

def compute_yearly_stats():
    # group by station + year (year is substr(date,1,4))
    year_expr = func.substr(WeatherRecord.date, 1, 4).label("year")
    q = db.session.query(
        WeatherRecord.station_id.label("station_id"),
        year_expr,
        func.avg(WeatherRecord.max_temp).label("avg_max"),
        func.avg(WeatherRecord.min_temp).label("avg_min"),
        func.sum(WeatherRecord.precipitation).label("sum_precip_mm")
    ).group_by(WeatherRecord.station_id, year_expr)

    results = q.all()
    inserted = 0
    for row in results:
        station_id = row.station_id
        year = int(row.year)
        avg_max = float(row.avg_max) if row.avg_max is not None else None
        avg_min = float(row.avg_min) if row.avg_min is not None else None
        sum_precip_mm = float(row.sum_precip_mm) if row.sum_precip_mm is not None else None
        total_precip_cm = (sum_precip_mm / 10.0) if sum_precip_mm is not None else None

        # skip if exists
        if WeatherStats.query.filter_by(station_id=station_id, year=year).first():
            continue

        stat = WeatherStats(
            station_id=station_id,
            year=year,
            avg_max_temp=avg_max,
            avg_min_temp=avg_min,
            total_precip_cm=total_precip_cm
        )
        db.session.add(stat)
        inserted += 1

    db.session.commit()
    logger.info("Yearly stats computation complete. Inserted=%d groups", inserted)
    return {"inserted": inserted, "groups": len(results)}

