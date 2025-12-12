import pytest
from app.ingestion import ingest_weather_data
from app.models import WeatherRecord
from app.database import db

def test_ingest_and_duplicates(app, tmp_wx_folder):
    with app.app_context():
        summary = ingest_weather_data(folder_path=tmp_wx_folder)
        # three lines => 3 processed; inserted 3
        assert summary["processed"] == 3
        assert summary["inserted"] == 3

        # Run ingestion again - duplicates should be skipped
        summary2 = ingest_weather_data(folder_path=tmp_wx_folder)
        assert summary2["inserted"] == 0

        # Verify DB rows
        records = WeatherRecord.query.all()
        assert len(records) == 3

        # Check a sample record values (converted)
        r = WeatherRecord.query.filter_by(station_id="STATION_TEST", date="19850101").first()
        assert r.max_temp == pytest.approx(21.5)
        assert r.min_temp == pytest.approx(10.5)
        assert r.precipitation == pytest.approx(0.5)

