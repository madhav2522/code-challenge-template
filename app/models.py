"""
ORM models: WeatherRecord and WeatherStats.
"""

from .database import db

class WeatherRecord(db.Model):
    __tablename__ = "weather_records"

    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(64), nullable=False, index=True)
    date = db.Column(db.String(8), nullable=False, index=True)  # YYYYMMDD
    max_temp = db.Column(db.Float, nullable=True)  # degrees C
    min_temp = db.Column(db.Float, nullable=True)  # degrees C
    precipitation = db.Column(db.Float, nullable=True)  # mm

    __table_args__ = (
        db.UniqueConstraint("station_id", "date", name="uq_station_date"),
    )

class WeatherStats(db.Model):
    __tablename__ = "weather_stats"

    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(64), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    avg_max_temp = db.Column(db.Float, nullable=True)
    avg_min_temp = db.Column(db.Float, nullable=True)
    total_precip_cm = db.Column(db.Float, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("station_id", "year", name="uq_station_year"),
    )

