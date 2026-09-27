"""
Delay Propagation Graph Engine — RailFlow AI

CORE DIFFERENTIATOR:
Models delay as a network propagation problem using NetworkX.
Nodes = Trains (train_id) and Track Sections (section_id)
Edges = Shared section occupancy, headway buffer, and platform precedence dependencies.
Computes the cascading ripple effect when one train experiences additional delay.
"""
import networkx as nx
from typing import Dict, Any, List, Tuple


def build_propagation_graph(train_observations: List[Dict[str, Any]]) -> nx.DiGraph:
    """
    Constructs a directed NetworkX graph representing train dependency on track sections.
    """
    G = nx.DiGraph()

    section_train_map: Dict[str, List[Dict[str, Any]]] = {}

    for obs in train_observations:
        t_id = str(obs["train_id"])
        s_id = str(obs.get("section_id", "SEC_DEFAULT"))

        # Add Train node
        G.add_node(
            t_id,
            node_type="train",
            train_name=obs.get("train_name", f"Train {t_id}"),
            current_delay=float(obs.get("delay_minutes", 0.0)),
            section_id=s_id,
            speed_kmh=float(obs.get("speed_kmh", 50.0))
        )

        # Add Section node if not exists
        if not G.has_node(s_id):
            G.add_node(
                s_id,
                node_type="section",
                congestion_score=float(obs.get("congestion_score", 0.4)),
                section_type=obs.get("section_type", "trunk")
            )

        # Edge from train to section (occupies section)
        G.add_edge(t_id, s_id, edge_type="occupies")

        if s_id not in section_train_map:
            section_train_map[s_id] = []
        section_train_map[s_id].append(obs)

    # Build sequence & precedence edges between trains sharing the same section
    for s_id, trains in section_train_map.items():
        # Sort trains by scheduled order or current distance
        sorted_trains = sorted(trains, key=lambda x: x.get("distance_covered_km", 0.0), reverse=True)
        for i in range(len(sorted_trains) - 1):
            ahead_t = str(sorted_trains[i]["train_id"])
            behind_t = str(sorted_trains[i + 1]["train_id"])

            # Edge from leading train to trailing train (trailing train depends on leading train headway)
            # Headway clearance factor (e.g. 0.65 cascade transfer ratio)
            G.add_edge(
                ahead_t,
                behind_t,
                edge_type="headway_dependency",
                transfer_ratio=0.65,
                section_id=s_id
            )

    return G


def simulate_cascade(
    G: nx.DiGraph,
    primary_train_id: str,
    additional_delay_min: float
) -> List[Dict[str, Any]]:
    """
    Simulates cascading delay propagation downstream from primary_train_id.
    Returns list of affected downstream trains and their calculated added cascade delay.
    """
    if primary_train_id not in G:
        return []

    cascaded_effects = []
    visited = set()

    # Queue of (current_node, propagated_extra_delay)
    queue = [(primary_train_id, additional_delay_min)]
    visited.add(primary_train_id)

    while queue:
        curr_train, extra_delay = queue.pop(0)

        # Explore outgoing dependency edges
        for neighbor in G.successors(curr_train):
            edge_data = G.get_edge_data(curr_train, neighbor)
            if edge_data and edge_data.get("edge_type") == "headway_dependency":
                transfer_ratio = edge_data.get("transfer_ratio", 0.60)
                # Cascaded delay dampens naturally with distance/headway buffer
                transferred_delay = round(extra_delay * transfer_ratio, 2)

                if transferred_delay >= 1.0 and neighbor not in visited:
                    visited.add(neighbor)
                    orig_delay = G.nodes[neighbor].get("current_delay", 0.0)
                    t_name = G.nodes[neighbor].get("train_name", f"Train {neighbor}")

                    cascaded_effects.append({
                        "train_id": neighbor,
                        "train_name": t_name,
                        "original_delay_min": orig_delay,
                        "additional_cascade_delay_min": transferred_delay,
                        "new_projected_delay_min": round(orig_delay + transferred_delay, 2),
                        "dependency_reason": f"Headway block dependency behind Train {curr_train}"
                    })

                    queue.append((neighbor, transferred_delay))

    return cascaded_effects
