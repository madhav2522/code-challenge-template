import pytest
from app.ingestion import ingest_weather_data
from app.analysis import compute_yearly_stats

def test_weather_route(client, app, tmp_wx_folder):
    # ingest data into app's DB
    with app.app_context():
        ingest_weather_data(folder_path=tmp_wx_folder)
    # call API
    resp = client.get("/api/weather")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

def test_stats_route(client, app, tmp_wx_folder):
    with app.app_context():
        ingest_weather_data(folder_path=tmp_wx_folder)
        compute_yearly_stats()
    resp = client.get("/api/weather/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["station_id"] == "STATION_TEST"
    assert item["year"] == 1985

