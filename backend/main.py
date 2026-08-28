from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.algorithms.distance_matrix import (
    haversine_distance,
    compute_distance_matrix,
    estimate_eta_and_cost
)
from backend.algorithms.tsp_solver import optimize_delivery_route
from backend.algorithms.dijkstra import build_graph_from_matrix, find_shortest_path
from backend.geo_utils import geocode_address, reverse_geocode

app = FastAPI(
    title="BigBasket Delivery Route Optimization Engine",
    description="High-performance backend API for BB Express dispatch, route optimization, and TSP solving.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Schemas ---

class LatLng(BaseModel):
    latitude: float = Field(..., json_schema_extra={"example": 12.9352})
    longitude: float = Field(..., json_schema_extra={"example": 77.6245})


class DistanceRequest(BaseModel):
    point_a: LatLng
    point_b: LatLng


class DistanceMatrixRequest(BaseModel):
    points: List[LatLng]


class OrderItem(BaseModel):
    id: Optional[Any] = 1
    customer_name: Optional[str] = "Customer"
    address: Optional[str] = ""
    latitude: float
    longitude: float
    items_count: Optional[int] = 1
    grocery_items: Optional[List[str]] = []
    priority: Optional[str] = "NORMAL"
    time_slot: Optional[str] = "Standard"


class DepotItem(BaseModel):
    name: str = "BigBasket Dark Store"
    latitude: float
    longitude: float
    address: Optional[str] = ""


class QuickOptimizeRequest(BaseModel):
    depot: DepotItem
    orders: List[OrderItem]
    use_2opt: bool = True
    avg_speed_kmh: float = 22.0
    fuel_cost_per_km_inr: float = 5.0
    service_time_per_stop_min: float = 4.0


class GeocodeRequest(BaseModel):
    address: str
    city: Optional[str] = "Bengaluru"


class DijkstraRequest(BaseModel):
    points: List[LatLng]
    source_index: int = 0
    target_index: int = 1


# --- API Endpoints ---

@app.get("/")
def root():
    return {
        "service": "BigBasket RoutePulse API",
        "phase": "Phase 1 - Backend Core & Optimization Algorithms",
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/ping")
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "bb-route-optimizer", "version": "1.0.0"}


@app.post("/api/distance/haversine")
def calculate_distance(payload: DistanceRequest):
    dist = haversine_distance(
        (payload.point_a.latitude, payload.point_a.longitude),
        (payload.point_b.latitude, payload.point_b.longitude)
    )
    return {"distance_km": dist}


@app.post("/api/distance/matrix")
def get_distance_matrix(payload: DistanceMatrixRequest):
    coords = [(p.latitude, p.longitude) for p in payload.points]
    matrix = compute_distance_matrix(coords)
    return {"matrix": matrix, "size": len(coords)}


@app.post("/api/optimize/quick")
def quick_optimize_route(payload: QuickOptimizeRequest):
    depot_dict = payload.depot.model_dump()
    orders_list = [o.model_dump() for o in payload.orders]
    
    result = optimize_delivery_route(
        depot=depot_dict,
        orders=orders_list,
        use_2opt=payload.use_2opt,
        avg_speed_kmh=payload.avg_speed_kmh,
        service_time_per_stop_min=payload.service_time_per_stop_min,
        fuel_cost_per_km_inr=payload.fuel_cost_per_km_inr
    )
    return result


@app.post("/api/geocode")
def geocode(payload: GeocodeRequest):
    lat, lon = geocode_address(payload.address, default_city=payload.city)
    return {
        "address": payload.address,
        "latitude": lat,
        "longitude": lon,
        "city": payload.city
    }


@app.post("/api/dijkstra/shortest-path")
def dijkstra_path(payload: DijkstraRequest):
    if len(payload.points) < 2:
        raise HTTPException(status_code=400, detail="At least 2 points are required.")
    
    coords = [(p.latitude, p.longitude) for p in payload.points]
    matrix = compute_distance_matrix(coords)
    G = build_graph_from_matrix(matrix)
    
    res = find_shortest_path(G, payload.source_index, payload.target_index)
    return res


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
