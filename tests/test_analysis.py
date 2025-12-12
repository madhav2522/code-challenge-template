from app.ingestion import ingest_weather_data
from app.analysis import compute_yearly_stats
from app.models import WeatherStats
import pytest

def test_compute_yearly_stats(app, tmp_wx_folder):
    with app.app_context():
        ingest_summary = ingest_weather_data(folder_path=tmp_wx_folder)
        assert ingest_summary["inserted"] == 3

        stats_summary = compute_yearly_stats()
        # We have single station STATION_TEST and year 1985 -> 1 group
        assert stats_summary["inserted"] == 1

        stat = WeatherStats.query.filter_by(station_id="STATION_TEST", year=1985).first()
        assert stat is not None
        # avg_max: (21.5 + 20.0) / 2  -> 20.75 (one missing)
        assert pytest.approx(stat.avg_max_temp, rel=1e-3) == 20.75
        # avg_min: (10.5 + 9.5) / 2 -> 10.0 (one missing)
        assert pytest.approx(stat.avg_min_temp, rel=1e-3) == 10.0
        # total precip mm: 0.5 + 0.0 + 1.0 = 1.5 mm -> in cm = 0.15
        assert pytest.approx(stat.total_precip_cm, rel=1e-3) == 0.15

