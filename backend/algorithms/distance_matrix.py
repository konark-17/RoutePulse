import math
from typing import List, Tuple, Dict, Any

EARTH_RADIUS_KM = 6371.0088

def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees: lat, lon).
    Returns distance in kilometers.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    
    # Clamp 'a' to avoid math domain errors due to floating point inaccuracies
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance_km = EARTH_RADIUS_KM * c
    return round(distance_km, 3)


def compute_distance_matrix(coordinates: List[Tuple[float, float]]) -> List[List[float]]:
    """
    Build an N x N symmetric distance matrix for a list of (lat, lon) tuples.
    Index 0 is typically the Depot/Warehouse.
    """
    n = len(coordinates)
    matrix = [[0.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            dist = haversine_distance(coordinates[i], coordinates[j])
            matrix[i][j] = dist
            matrix[j][i] = dist

    return matrix


def estimate_eta_and_cost(
    distance_km: float,
    num_stops: int,
    avg_speed_kmh: float = 22.0,
    service_time_per_stop_min: float = 4.0,
    fuel_cost_per_km_inr: float = 5.0,
    co2_per_km_grams: float = 95.0
) -> Dict[str, Any]:
    """
    Estimate delivery travel duration (in minutes), fuel cost (in INR),
    and carbon footprint for a given route distance and number of delivery stops.
    """
    if avg_speed_kmh <= 0:
        avg_speed_kmh = 22.0

    travel_time_minutes = (distance_km / avg_speed_kmh) * 60.0
    total_service_time_minutes = num_stops * service_time_per_stop_min
    total_duration_minutes = round(travel_time_minutes + total_service_time_minutes, 1)

    total_fuel_cost = round(distance_km * fuel_cost_per_km_inr, 2)
    total_co2_kg = round((distance_km * co2_per_km_grams) / 1000.0, 3)

    return {
        "travel_time_minutes": round(travel_time_minutes, 1),
        "service_time_minutes": round(total_service_time_minutes, 1),
        "total_duration_minutes": total_duration_minutes,
        "fuel_cost_inr": total_fuel_cost,
        "co2_emissions_kg": total_co2_kg
    }
