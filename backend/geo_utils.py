import time
import requests
from typing import Tuple, Optional, Dict

# In-memory geocode cache to avoid unnecessary network requests and rate limits
GEOCODE_CACHE: Dict[str, Tuple[float, float]] = {
    # Pre-seeded common Bengaluru locations for instant resolution & offline demo reliability
    "koramangala": (12.9352, 77.6245),
    "koramangala 4th block": (12.9344, 77.6289),
    "koramangala 5th block": (12.9351, 77.6186),
    "indiranagar": (12.9784, 77.6408),
    "indiranagar 100 feet road": (12.9719, 77.6412),
    "hsr layout": (12.9121, 77.6446),
    "hsr layout sector 1": (12.9121, 77.6446),
    "hsr layout sector 7": (12.9081, 77.6322),
    "btm layout": (12.9166, 77.6101),
    "btm 1st stage": (12.9218, 77.6146),
    "btm 2nd stage": (12.9128, 77.6092),
    "whitefield": (12.9698, 77.7499),
    "bellandur": (12.9260, 77.6833),
    "domlur": (12.9610, 77.6387),
    "ejipura": (12.9432, 77.6280),
    "sarjapur road": (12.9135, 77.6782),
    "jayanagar": (12.9308, 77.5838),
    "jp nagar": (12.9063, 77.5857),
    "mg road": (12.9756, 77.6066),
    "electronic city": (12.8399, 77.6770),
    "marathahalli": (12.9591, 77.6974),
    "hebbal": (13.0358, 77.5970),
    "malleshwaram": (13.0031, 77.5643),
    "rajajinagar": (12.9982, 77.5530),
    "old airport road": (12.9592, 77.6540),
    "madivala": (12.9220, 77.6200),
}

NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
REVERSE_BASE_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "BigBasket-Delivery-Optimizer/1.0 (academic-project)"}

_last_request_time = 0.0

def _rate_limit():
    """Ensure at least 1.0 second between Nominatim API calls per usage policy."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)
    _last_request_time = time.time()


def geocode_address(address: str, default_city: str = "Bengaluru") -> Tuple[float, float]:
    """
    Convert an address or landmark string to (latitude, longitude).
    Checks cache first, then calls OpenStreetMap Nominatim API.
    If not found, returns nearest matched area or default central Bengaluru coords.
    """
    cleaned = address.strip().lower()

    # 1. Direct cache lookup
    for key, coords in GEOCODE_CACHE.items():
        if key in cleaned:
            return coords

    # 2. OpenStreetMap Nominatim request
    query = f"{address}, {default_city}, India"
    params = {
        "q": query,
        "format": "json",
        "limit": 1
    }

    try:
        _rate_limit()
        resp = requests.get(NOMINATIM_BASE_URL, params=params, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                GEOCODE_CACHE[cleaned] = (lat, lon)
                return (lat, lon)
    except Exception as e:
        print(f"[Geocode Warning] Failed to geocode '{address}': {e}")

    # Fallback to default Bengaluru city center
    return (12.9716, 77.5946)


def reverse_geocode(lat: float, lon: float) -> str:
    """
    Convert (latitude, longitude) coordinates to a human-readable address.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json"
    }

    try:
        _rate_limit()
        resp = requests.get(REVERSE_BASE_URL, params=params, headers=HEADERS, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("display_name", f"{lat:.4f}, {lon:.4f}")
    except Exception as e:
        print(f"[Reverse Geocode Warning] Failed for ({lat}, {lon}): {e}")

    return f"Location ({lat:.4f}, {lon:.4f})"
