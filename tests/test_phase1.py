import math
import pytest
from backend.algorithms.distance_matrix import (
    haversine_distance, 
    compute_distance_matrix, 
    estimate_eta_and_cost
)
from backend.algorithms.tsp_solver import (
    solve_tsp_nearest_neighbor, 
    solve_tsp_2opt, 
    optimize_delivery_route
)
from backend.algorithms.dijkstra import build_graph_from_matrix, find_shortest_path
from backend.geo_utils import geocode_address

# Benchmark coordinates in Bengaluru
KORAMANGALA = (12.9352, 77.6245)
INDIRANAGAR = (12.9784, 77.6408)
HSR_LAYOUT = (12.9121, 77.6446)
WHITEFIELD = (12.9698, 77.7499)
BTM_LAYOUT = (12.9166, 77.6101)


def test_haversine_distance():
    # Distance between Koramangala and Indiranagar is roughly 5.0 - 5.5 km
    dist = haversine_distance(KORAMANGALA, INDIRANAGAR)
    assert 4.8 <= dist <= 5.8
    # Distance to self must be 0
    assert haversine_distance(KORAMANGALA, KORAMANGALA) == 0.0


def test_distance_matrix():
    coords = [KORAMANGALA, INDIRANAGAR, HSR_LAYOUT, WHITEFIELD]
    matrix = compute_distance_matrix(coords)
    
    assert len(matrix) == 4
    assert len(matrix[0]) == 4
    
    # Test symmetry & diagonal zeros
    for i in range(4):
        assert matrix[i][i] == 0.0
        for j in range(4):
            assert matrix[i][j] == matrix[j][i]
            assert matrix[i][j] >= 0.0


def test_nearest_neighbor_tsp():
    coords = [KORAMANGALA, INDIRANAGAR, HSR_LAYOUT, WHITEFIELD, BTM_LAYOUT]
    matrix = compute_distance_matrix(coords)
    tour, total_dist = solve_tsp_nearest_neighbor(matrix, start_node=0)
    
    # Must start at 0, visit all 5 unique nodes, and return to 0 (length 6)
    assert len(tour) == 6
    assert tour[0] == 0
    assert tour[-1] == 0
    assert set(tour) == {0, 1, 2, 3, 4}
    assert total_dist > 0.0


def test_tsp_2opt_optimizer():
    coords = [KORAMANGALA, INDIRANAGAR, HSR_LAYOUT, WHITEFIELD, BTM_LAYOUT]
    matrix = compute_distance_matrix(coords)
    
    nn_tour, nn_dist = solve_tsp_nearest_neighbor(matrix, start_node=0)
    opt_tour, opt_dist = solve_tsp_2opt(nn_tour, matrix)
    
    # 2-Opt must not increase the tour length
    assert opt_dist <= nn_dist + 1e-5
    assert set(opt_tour) == {0, 1, 2, 3, 4}
    assert opt_tour[0] == 0
    assert opt_tour[-1] == 0


def test_optimize_delivery_route_high_level():
    depot = {
        "name": "BB Dark Store Koramangala",
        "latitude": KORAMANGALA[0],
        "longitude": KORAMANGALA[1]
    }
    sample_orders = [
        {"id": 101, "customer_name": "Aarav", "latitude": INDIRANAGAR[0], "longitude": INDIRANAGAR[1]},
        {"id": 102, "customer_name": "Priya", "latitude": HSR_LAYOUT[0], "longitude": HSR_LAYOUT[1]},
        {"id": 103, "customer_name": "Rohan", "latitude": BTM_LAYOUT[0], "longitude": BTM_LAYOUT[1]}
    ]
    
    result = optimize_delivery_route(depot, sample_orders, use_2opt=True)
    
    assert "optimized_distance_km" in result
    assert "unoptimized_distance_km" in result
    assert "stops" in result
    assert len(result["stops"]) == 5  # Depot start + 3 orders + Depot return
    assert result["ordered_order_ids"] == [o["order_id"] for o in result["stops"] if o["type"] == "order"]
    assert result["total_duration_minutes"] > 0
    assert result["fuel_cost_inr"] > 0


def test_dijkstra_shortest_path():
    coords = [KORAMANGALA, INDIRANAGAR, HSR_LAYOUT]
    matrix = compute_distance_matrix(coords)
    G = build_graph_from_matrix(matrix)
    
    path_res = find_shortest_path(G, source=0, target=1)
    assert path_res["found"] is True
    assert path_res["source"] == 0
    assert path_res["target"] == 1
    assert path_res["distance_km"] > 0


def test_geocoding_cache():
    coords = geocode_address("koramangala 4th block")
    assert abs(coords[0] - 12.9344) < 0.01
    assert abs(coords[1] - 77.6289) < 0.01
