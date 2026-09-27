"""
Unit Tests — Root-Cause Delay Explainer & Smart Alternative Route Engine
Tests find_direct_alternative(), find_chained_alternative(), root_cause_delay(), and constants.
"""
import pytest
import networkx as nx

from app.pipeline.alternatives import (
    root_cause_delay,
    find_direct_alternative,
    find_chained_alternative,
    evaluate_train_alternatives,
    DIRECT_IMPROVEMENT_THRESHOLD_MIN,
    MIN_CONNECTION_BUFFER_MIN,
    DELAY_TRIGGER_THRESHOLD_MIN,
)


def test_constants():
    assert DIRECT_IMPROVEMENT_THRESHOLD_MIN == 15
    assert MIN_CONNECTION_BUFFER_MIN == 20
    assert DELAY_TRIGGER_THRESHOLD_MIN == 30


def test_root_cause_delay_conflict():
    G = nx.DiGraph()
    G.add_node("12002", node_type="train")
    G.add_node("12951", node_type="train")
    G.add_edge("12002", "12951", edge_type="headway_dependency", overlap=True, section_id="SEC_NDLS_CNB")

    reason, reason_type, blocking_id = root_cause_delay(G, "12951")
    assert reason_type == "conflict"
    assert blocking_id == "12002"
    assert "12002" in reason


def test_root_cause_delay_operational():
    G = nx.DiGraph()
    G.add_node("12951", node_type="train")
    reason, reason_type, blocking_id = root_cause_delay(G, "12951")
    assert reason_type == "operational"
    assert blocking_id is None
    assert len(reason) > 5


def test_find_direct_alternative_independent():
    # Direct search for 12951 (delayed 45 mins)
    direct = find_direct_alternative("12951", "NDLS", "MMCT", orig_predicted_delay_min=45.0)
    assert direct is not None
    assert "train_id" in direct
    assert "predicted_arrival" in direct
    assert direct["train_id"] != "12951"


def test_find_chained_alternative_independent():
    # Chained search for 12424 (delayed 50 mins)
    chained = find_chained_alternative("12424", "NDLS", "DBRG", orig_predicted_delay_min=50.0)
    if chained is not None:
        assert "leg_1" in chained
        assert "leg_2" in chained
        assert "total_journey_time_minutes" in chained
        assert chained["leg_1"]["train_id"] is not None
        assert chained["leg_2"]["train_id"] is not None


def test_evaluate_train_alternatives_no_delay_trigger():
    # Train 12002 has 5m delay (< 30m trigger)
    res = evaluate_train_alternatives("12002")
    assert res["has_alternative"] is False
    assert res["alternative_type"] is None
    assert res["direct"] is None
    assert res["chained"] is None
