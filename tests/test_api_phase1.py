from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoints():
    r1 = client.get("/")
    assert r1.status_code == 200
    assert r1.json()["status"] == "online"

    r2 = client.get("/ping")
    assert r2.status_code == 200
    assert r2.json()["status"] == "healthy"


def test_api_distance_haversine():
    payload = {
        "point_a": {"latitude": 12.9352, "longitude": 77.6245},
        "point_b": {"latitude": 12.9784, "longitude": 77.6408}
    }
    resp = client.post("/api/distance/haversine", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "distance_km" in data
    assert 4.8 <= data["distance_km"] <= 5.8


def test_api_optimize_quick():
    payload = {
        "depot": {
            "name": "BB Dark Store Koramangala",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "address": "Koramangala 4th Block"
        },
        "orders": [
            {
                "id": 1,
                "customer_name": "Aarav",
                "latitude": 12.9344,
                "longitude": 77.6289,
                "address": "Koramangala",
                "items_count": 3
            },
            {
                "id": 2,
                "customer_name": "Priya",
                "latitude": 12.9218,
                "longitude": 77.6146,
                "address": "BTM Layout",
                "items_count": 2
            }
        ],
        "use_2opt": True,
        "avg_speed_kmh": 22.0,
        "fuel_cost_per_km_inr": 5.0
    }
    resp = client.post("/api/optimize/quick", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "optimized_distance_km" in data
    assert "stops" in data
    assert len(data["stops"]) == 4  # Start Hub + 2 Orders + Return Hub
    assert data["total_duration_minutes"] > 0


def test_api_geocode():
    payload = {"address": "koramangala", "city": "Bengaluru"}
    resp = client.post("/api/geocode", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["latitude"] > 0
    assert data["longitude"] > 0


def test_api_dijkstra_path():
    payload = {
        "points": [
            {"latitude": 12.9352, "longitude": 77.6245},
            {"latitude": 12.9784, "longitude": 77.6408},
            {"latitude": 12.9121, "longitude": 77.6446}
        ],
        "source_index": 0,
        "target_index": 1
    }
    resp = client.post("/api/dijkstra/shortest-path", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert data["distance_km"] > 0
