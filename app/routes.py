"""
API routes for /api/weather and /api/weather/stats
Includes pagination and filtering.
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from .models import WeatherRecord, WeatherStats
from .database import db

api = Blueprint("api", __name__)

DEFAULT_PER_PAGE = 50
MAX_PER_PAGE = 500

def paginate_query(query, page, per_page):
    if page < 1:
        page = 1
    per_page = max(1, min(per_page, MAX_PER_PAGE))
    total = query.count()
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    return items, total

@api.route("/weather", methods=["GET"])
def get_weather():
    """
    GET /api/weather
    Query params:
      - station: station_id filter
      - date: YYYYMMDD filter
      - page, per_page: pagination
    """
    station = request.args.get("station")
    date = request.args.get("date")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))

    q = WeatherRecord.query.order_by(WeatherRecord.station_id, WeatherRecord.date)
    if station:
        q = q.filter_by(station_id=station)
    if date:
        q = q.filter_by(date=date)

    items, total = paginate_query(q, page, per_page)
    results = [{
        "station_id": i.station_id,
        "date": i.date,
        "max_temp": i.max_temp,
        "min_temp": i.min_temp,
        "precipitation_mm": i.precipitation
    } for i in items]

    return jsonify({"page": page, "per_page": per_page, "total": total, "items": results})

@api.route("/weather/stats", methods=["GET"])
def get_stats():
    """
    GET /api/weather/stats
    Query params:
      - station: station_id filter
      - year: YYYY filter
      - page, per_page: pagination
    """
    station = request.args.get("station")
    year = request.args.get("year")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", DEFAULT_PER_PAGE))

    q = WeatherStats.query.order_by(WeatherStats.station_id, WeatherStats.year)
    if station:
        q = q.filter_by(station_id=station)
    if year:
        try:
            q = q.filter_by(year=int(year))
        except ValueError:
            return jsonify({"error": "Invalid year parameter"}), 400

    items, total = paginate_query(q, page, per_page)
    results = [{
        "station_id": i.station_id,
        "year": i.year,
        "avg_max_temp": i.avg_max_temp,
        "avg_min_temp": i.avg_min_temp,
        "total_precip_cm": i.total_precip_cm
    } for i in items]

    return jsonify({"page": page, "per_page": per_page, "total": total, "items": results})

