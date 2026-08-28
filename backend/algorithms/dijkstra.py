import networkx as nx
from typing import List, Tuple, Dict, Any, Optional

def build_graph_from_matrix(distance_matrix: List[List[float]], labels: Optional[List[str]] = None) -> nx.Graph:
    """
    Build a NetworkX undirected weighted graph from a 2D distance matrix.
    """
    G = nx.Graph()
    n = len(distance_matrix)
    
    # Add nodes with optional labels
    for i in range(n):
        label = labels[i] if labels and i < len(labels) else f"Node_{i}"
        G.add_node(i, label=label)

    # Add weighted edges between all pairs
    for i in range(n):
        for j in range(i + 1, n):
            weight = distance_matrix[i][j]
            G.add_edge(i, j, weight=weight)

    return G


def find_shortest_path(
    G: nx.Graph, 
    source: int, 
    target: int
) -> Dict[str, Any]:
    """
    Find shortest path and distance between source and target using Dijkstra's algorithm.
    """
    try:
        path = nx.dijkstra_path(G, source=source, target=target, weight="weight")
        length = nx.dijkstra_path_length(G, source=source, target=target, weight="weight")
        return {
            "source": source,
            "target": target,
            "path": path,
            "distance_km": round(length, 3),
            "found": True
        }
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        return {
            "source": source,
            "target": target,
            "path": [],
            "distance_km": 0.0,
            "found": False,
            "error": str(e)
        }


def all_pairs_shortest_paths(G: nx.Graph) -> Dict[int, Dict[int, float]]:
    """
    Compute all-pairs shortest path lengths using Dijkstra.
    """
    lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))
    return lengths
