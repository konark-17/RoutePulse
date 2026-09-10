# 🛒 Route Optimization Engine

A high-performance Delivery Route Optimization System engineered for large-scale grocery logistics (inspired by BigBasket / BB Daily operations).

---

## 📌 Phase 1: Core Algorithms & REST Engine (Completed)

Phase 1 establishes the mathematical optimization core, graph routing, geocoding pipeline, and FastAPI backend:

1. **Haversine Distance Engine** (`backend/algorithms/distance_matrix.py`):
   - Computes great-circle distances across GPS coordinates in kilometers with Earth curvature compensation ($R = 6371.0088\text{ km}$).
   - Builds $N \times N$ pairwise symmetric distance matrices in $O(N^2)$ time.
   - Calculates real-world ETA (with traffic speed heuristics and customer drop-off service times), fuel cost in INR, and carbon footprint ($CO_2$).

2. **Nearest Neighbor TSP Heuristic** (`backend/algorithms/tsp_solver.py`):
   - Greedy Traveling Salesperson tour generator that begins at the Dark Store / Fulfillment Hub and iteratively selects the closest unvisited drop-off location.

3. **2-Opt Local Search Improvement** (`backend/algorithms/tsp_solver.py`):
   - Iterative sub-route reversal that detects and eliminates edge crossings / path tangles, delivering an additional 5%–15% route reduction.

4. **NetworkX Dijkstra Routing** (`backend/algorithms/dijkstra.py`):
   - Graph-based single-source and all-pairs shortest path calculations.

5. **Geocoding & Cache Layer** (`backend/geo_utils.py`):
   - OpenStreetMap Nominatim integration with rate limiting and pre-seeded cached coordinates for prominent Bengaluru delivery hubs.

6. **FastAPI REST API** (`backend/main.py`):
   - High-throughput asynchronous endpoints for distance calculation, route optimization, geocoding, and shortest path graph queries.

---

## 📂 Project Structure

```
BigBasket/
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application & API endpoints
│   ├── geo_utils.py                # Geocoding & caching engine
│   └── algorithms/
│       ├── __init__.py
│       ├── distance_matrix.py      # Haversine formula & ETA estimation
│       ├── tsp_solver.py           # Nearest Neighbor + 2-Opt TSP solver
│       └── dijkstra.py             # NetworkX shortest path graph algorithms
├── data/
│   ├── depots.json                 # BigBasket Fulfillment Hubs in Bengaluru
│   └── sample_orders.json          # Realistic BigBasket grocery delivery orders
├── tests/
│   ├── __init__.py
│   ├── test_phase1.py              # Algorithm unit tests
│   └── test_api_phase1.py          # FastAPI endpoint integration tests
├── pytest.ini                      # Test runner configuration
├── requirements.txt                # Python dependencies
├── run_phase1_demo.py              # Interactive CLI demonstration
└── README.md
```


## 📊 Sample Optimization Output (Phase 1 Demo)

```
===========================================================================
>> OPTIMIZATION METRICS & BUSINESS SAVINGS
===========================================================================
   Algorithm Applied        : Nearest Neighbor Heuristic
   Original / Raw Distance  : 30.43 km
   Optimized Route Distance : 22.83 km
   Distance Saved           : 7.6 km (Savings: 25.0%)
   Total Estimated Duration : 102.3 mins (Travel: 62.3m, Service: 40.0m)
   Estimated Fuel Cost      : Rs. 114.13 INR
   Estimated CO2 Emissions  : 2.168 kg
```

