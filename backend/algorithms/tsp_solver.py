from typing import List, Dict, Any, Tuple
from .distance_matrix import compute_distance_matrix, haversine_distance, estimate_eta_and_cost

def calculate_tour_distance(tour: List[int], distance_matrix: List[List[float]]) -> float:
    """Calculate the total path distance for an ordered sequence of node indices."""
    total = 0.0
    for i in range(len(tour) - 1):
        total += distance_matrix[tour[i]][tour[i + 1]]
    return round(total, 3)


def solve_tsp_nearest_neighbor(distance_matrix: List[List[float]], start_node: int = 0) -> Tuple[List[int], float]:
    """
    Nearest Neighbor greedy algorithm for TSP.
    Time complexity: O(N^2)
    
    1. Start at depot (start_node = 0)
    2. Repeatedly visit closest unvisited customer
    3. Return to depot
    """
    n = len(distance_matrix)
    if n <= 1:
        return [0, 0], 0.0
    
    visited = [False] * n
    visited[start_node] = True
    tour = [start_node]
    current = start_node

    for _ in range(n - 1):
        nearest_node = None
        min_dist = float("inf")
        for candidate in range(n):
            if not visited[candidate] and distance_matrix[current][candidate] < min_dist:
                min_dist = distance_matrix[current][candidate]
                nearest_node = candidate
        
        if nearest_node is not None:
            visited[nearest_node] = True
            tour.append(nearest_node)
            current = nearest_node

    # Complete the cycle back to depot
    tour.append(start_node)
    total_dist = calculate_tour_distance(tour, distance_matrix)
    return tour, total_dist


def solve_tsp_2opt(tour: List[int], distance_matrix: List[List[float]], max_iterations: int = 500) -> Tuple[List[int], float]:
    """
    2-Opt local search improvement on an existing TSP tour.
    Removes edge crossings by reversing sub-segments of the tour.
    """
    best_tour = list(tour)
    best_distance = calculate_tour_distance(best_tour, distance_matrix)
    improved = True
    iteration = 0
    n = len(best_tour)

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        # Don't modify the start depot (index 0) and end depot (index -1)
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                # Calculate current cost
                current_cost = (
                    distance_matrix[best_tour[i - 1]][best_tour[i]] +
                    distance_matrix[best_tour[j]][best_tour[j + 1]]
                )
                
                # Calculate new cost after reversing segment between i and j
                new_cost = (
                    distance_matrix[best_tour[i - 1]][best_tour[j]] +
                    distance_matrix[best_tour[i]][best_tour[j + 1]]
                )
                
                if new_cost < current_cost - 1e-6:
                    # 2-opt swap: reverse segment [i...j]
                    best_tour[i:j + 1] = reversed(best_tour[i:j + 1])
                    best_distance = calculate_tour_distance(best_tour, distance_matrix)
                    improved = True
                    break
            if improved:
                break

    return best_tour, best_distance


def optimize_delivery_route(
    depot: Dict[str, Any],
    orders: List[Dict[str, Any]],
    use_2opt: bool = True,
    avg_speed_kmh: float = 22.0,
    service_time_per_stop_min: float = 4.0,
    fuel_cost_per_km_inr: float = 5.0
) -> Dict[str, Any]:
    """
    High-level route optimizer for BigBasket delivery dispatch.
    
    Accepts:
      - depot: dict containing {"name": str, "latitude": float, "longitude": float}
      - orders: list of order dicts containing at least {"id": int/str, "customer_name": str, "latitude": float, "longitude": float}
    
    Returns structured result with:
      - Unoptimized vs Optimized stats & savings %
      - Step-by-step ordered itinerary with cumulative distance & ETA
      - Full waypoint coordinate path for map rendering
    """
    if not orders:
        return {
            "depot": depot,
            "stops": [],
            "ordered_order_ids": [],
            "unoptimized_distance_km": 0.0,
            "optimized_distance_km": 0.0,
            "distance_saved_km": 0.0,
            "savings_percentage": 0.0,
            "total_duration_minutes": 0.0,
            "fuel_cost_inr": 0.0,
            "co2_emissions_kg": 0.0,
            "algorithm_used": "None (No orders)"
        }

    # Index 0 is Depot; Indices 1..N are Orders
    locations = [{"type": "depot", **depot}] + [{"type": "order", **o} for o in orders]
    coordinates = [(loc["latitude"], loc["longitude"]) for loc in locations]
    
    dist_matrix = compute_distance_matrix(coordinates)

    # Calculate baseline unoptimized distance (orders processed in raw input sequence)
    unoptimized_tour = [0] + list(range(1, len(locations))) + [0]
    unoptimized_dist = calculate_tour_distance(unoptimized_tour, dist_matrix)

    # 1. Nearest Neighbor TSP
    nn_tour, nn_dist = solve_tsp_nearest_neighbor(dist_matrix, start_node=0)
    
    final_tour = nn_tour
    final_dist = nn_dist
    algo_name = "Nearest Neighbor Heuristic"

    # 2. Optional 2-Opt Optimization
    if use_2opt and len(orders) > 2:
        opt_tour, opt_dist = solve_tsp_2opt(nn_tour, dist_matrix)
        if opt_dist < final_dist:
            final_tour = opt_tour
            final_dist = opt_dist
            algo_name = "Nearest Neighbor + 2-Opt Optimizer"

    # Compute step-by-step stops with cumulative distance and ETA
    stops = []
    cumulative_dist = 0.0
    cumulative_time_min = 0.0

    for step_idx in range(len(final_tour)):
        node_idx = final_tour[step_idx]
        loc = locations[node_idx]

        leg_dist = 0.0
        if step_idx > 0:
            prev_node = final_tour[step_idx - 1]
            leg_dist = dist_matrix[prev_node][node_idx]
            cumulative_dist += leg_dist
            leg_travel_time = (leg_dist / avg_speed_kmh) * 60.0
            cumulative_time_min += leg_travel_time

        # If it's a customer stop, add service handling time
        if loc["type"] == "order":
            cumulative_time_min += service_time_per_stop_min

        stop_info = {
            "step": step_idx,
            "type": loc["type"],
            "name": loc.get("name") or loc.get("customer_name", "Unknown"),
            "address": loc.get("address", ""),
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "order_id": loc.get("id"),
            "items_count": loc.get("items_count", 1),
            "grocery_items": loc.get("grocery_items", []),
            "priority": loc.get("priority", "NORMAL"),
            "time_slot": loc.get("time_slot", "Standard"),
            "leg_distance_km": round(leg_dist, 2),
            "cumulative_distance_km": round(cumulative_dist, 2),
            "cumulative_eta_minutes": round(cumulative_time_min, 1)
        }
        stops.append(stop_info)

    # Cost and emission estimations
    cost_metrics = estimate_eta_and_cost(
        distance_km=final_dist,
        num_stops=len(orders),
        avg_speed_kmh=avg_speed_kmh,
        service_time_per_stop_min=service_time_per_stop_min,
        fuel_cost_per_km_inr=fuel_cost_per_km_inr
    )

    saved_km = max(0.0, round(unoptimized_dist - final_dist, 2))
    savings_pct = round((saved_km / unoptimized_dist * 100.0), 1) if unoptimized_dist > 0 else 0.0

    # Ordered list of order IDs (excluding depot stops)
    ordered_order_ids = [
        locations[idx]["id"] for idx in final_tour if locations[idx]["type"] == "order"
    ]

    return {
        "depot": depot,
        "stops": stops,
        "ordered_order_ids": ordered_order_ids,
        "total_stops": len(orders),
        "unoptimized_distance_km": round(unoptimized_dist, 2),
        "optimized_distance_km": round(final_dist, 2),
        "distance_saved_km": saved_km,
        "savings_percentage": savings_pct,
        "total_duration_minutes": cost_metrics["total_duration_minutes"],
        "travel_time_minutes": cost_metrics["travel_time_minutes"],
        "service_time_minutes": cost_metrics["service_time_minutes"],
        "fuel_cost_inr": cost_metrics["fuel_cost_inr"],
        "co2_emissions_kg": cost_metrics["co2_emissions_kg"],
        "algorithm_used": algo_name
    }
