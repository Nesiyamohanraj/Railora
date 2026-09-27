"""
API Endpoint Tests — RailFlow AI
Tests all FastAPI REST endpoints using httpx AsyncClient and ASGITransport.
"""
import pytest
import httpx

from main import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def async_client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.anyio
async def test_root_endpoint(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Online"


@pytest.mark.anyio
async def test_predict_endpoint(async_client):
    payload = {
        "train_id": "12951",
        "current_station": "NDLS",
        "current_delay_minutes": 15.0
    }
    response = await async_client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify passenger response fields
    assert "train_name" in data
    assert "train_number" in data
    assert "predicted_eta_range" in data
    assert "current_status" in data
    assert "delay_reason" in data
    assert "current_position" in data
    assert "next_station" in data
    assert "previous_station" in data
    assert "historical_reliability_score" in data
    assert "confidence_trend" in data
    assert "alternative_trains" in data

    # Verify operator-only debug fields are EXCLUDED
    assert "baseline_delay" not in data
    assert "raw_shap_matrix" not in data
    assert "graph_nodes" not in data


@pytest.mark.anyio
async def test_sample_trains_endpoint(async_client):
    response = await async_client.get("/sample_trains")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 1


@pytest.mark.anyio
async def test_live_train_endpoint(async_client):
    response = await async_client.get("/train/12951/live")
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "12951"
    assert "predicted_eta_range" in data


@pytest.mark.anyio
async def test_propagation_endpoint(async_client):
    response = await async_client.get("/propagation/SEC_NDLS_CNB")
    assert response.status_code == 200
    data = response.json()
    assert data["section_id"] == "SEC_NDLS_CNB"
    assert "cascaded_delays" in data
    assert "graph_summary" in data


@pytest.mark.anyio
async def test_whatif_endpoint(async_client):
    payload = {
        "train_id": "12951",
        "additional_delay_minutes": 15.0,
        "section_id": "SEC_NDLS_CNB"
    }
    response = await async_client.post("/whatif", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_train_id"] == "12951"
    assert data["applied_additional_delay_min"] == 15.0
    assert "affected_trains" in data


@pytest.mark.anyio
async def test_network_health_endpoint(async_client):
    response = await async_client.get("/network/health")
    assert response.status_code == 200
    data = response.json()
    assert "total_active_trains" in data
    assert "top_congested_sections" in data


@pytest.mark.anyio
async def test_alternatives_endpoint(async_client):
    response = await async_client.get("/alternatives/12951")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "has_alternative" in data
    assert "reason_type" in data
    assert "delay_minutes" in data
