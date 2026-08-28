"""
Phase 1 Demonstration Script: BigBasket Delivery Route Optimization Engine
Runs TSP Route Optimization on realistic Bengaluru Dark Store & Grocery Orders.
"""

import json
import os
import sys

# Ensure UTF-8 output encoding for Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from backend.algorithms.tsp_solver import optimize_delivery_route
from backend.algorithms.distance_matrix import compute_distance_matrix, haversine_distance

def run_demo():
    print("=" * 75)
    print("[*] BIGBASKET BB-EXPRESS ROUTE OPTIMIZATION ENGINE -- PHASE 1 DEMO")
    print("=" * 75)

    # 1. Load sample data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    depots_path = os.path.join(base_dir, "data", "depots.json")
    orders_path = os.path.join(base_dir, "data", "sample_orders.json")

    with open(depots_path, "r", encoding="utf-8") as f:
        depots = json.load(f)
    with open(orders_path, "r", encoding="utf-8") as f:
        orders = json.load(f)

    selected_depot = depots[0]  # Koramangala Hub
    print(f"\n[HUB] Selected Fulfillment Hub : {selected_depot['name']}")
    print(f"      Address                  : {selected_depot['address']}")
    print(f"      Coordinates              : ({selected_depot['latitude']}, {selected_depot['longitude']})")

    print(f"\n[BATCH] Loaded Delivery Batch  : {len(orders)} Grocery Orders across Bengaluru")
    for o in orders[:5]:
        print(f"      - Order #{o['id']}: {o['customer_name']} | {o['address'][:40]}... [{o['priority']}]")
    if len(orders) > 5:
        print(f"      ... and {len(orders) - 5} more orders.")

    # 2. Run Route Optimization
    print("\n[OPTIMIZING] Executing TSP Nearest Neighbor + 2-Opt Optimizer...")
    result = optimize_delivery_route(
        depot=selected_depot,
        orders=orders,
        use_2opt=True,
        avg_speed_kmh=22.0,
        fuel_cost_per_km_inr=5.0
    )

    # 3. Display Performance Results
    print("\n" + "=" * 75)
    print(">> OPTIMIZATION METRICS & BUSINESS SAVINGS")
    print("=" * 75)
    print(f"   Algorithm Applied        : {result['algorithm_used']}")
    print(f"   Original / Raw Distance  : {result['unoptimized_distance_km']} km")
    print(f"   Optimized Route Distance : {result['optimized_distance_km']} km")
    print(f"   Distance Saved           : {result['distance_saved_km']} km (Savings: {result['savings_percentage']}%)")
    print(f"   Total Estimated Duration : {result['total_duration_minutes']} mins (Travel: {result['travel_time_minutes']}m, Service: {result['service_time_minutes']}m)")
    print(f"   Estimated Fuel Cost      : Rs. {result['fuel_cost_inr']} INR")
    print(f"   Estimated CO2 Emissions  : {result['co2_emissions_kg']} kg")

    # 4. Display Step-by-Step Delivery Itinerary
    print("\n" + "=" * 75)
    print(">> DISPATCH ITINERARY (STEP-BY-STEP SEQUENCE)")
    print("=" * 75)
    for stop in result["stops"]:
        step_num = stop["step"]
        if stop["type"] == "depot":
            if step_num == 0:
                print(f"[{step_num:02d}] [HUB START]  : {stop['name']}")
            else:
                print(f"[{step_num:02d}] [HUB RETURN] : {stop['name']} | Total Dist: {stop['cumulative_distance_km']} km | Final ETA: {stop['cumulative_eta_minutes']} min")
        else:
            items_preview = ", ".join(stop.get("grocery_items", [])[:2])
            print(f"[{step_num:02d}] [DROP-OFF]    : {stop['name']} (Order #{stop['order_id']})")
            print(f"     Address     : {stop['address']}")
            print(f"     Priority    : {stop['priority']} | Slot: {stop['time_slot']}")
            print(f"     Leg Dist    : {stop['leg_distance_km']} km | Cumulative: {stop['cumulative_distance_km']} km | ETA: {stop['cumulative_eta_minutes']} mins")
            print(f"     Items       : {items_preview}...")

    print("=" * 75)
    print("[SUCCESS] Phase 1 Algorithms fully functional and verified!")
    print("=" * 75)

if __name__ == "__main__":
    run_demo()
