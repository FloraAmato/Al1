"""
Test API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_dispute(client: TestClient):
    """Test creating a dispute."""
    dispute_data = {
        "name": "Test Dispute",
        "resolution_method": "ratings",
        "bounds_percentage": 0.25,
        "rating_weight": 1.1,
        "agents": [
            {
                "email": "agent1@example.com",
                "name": "Agent 1",
                "share_of_entitlement": 0.5,
            },
            {
                "email": "agent2@example.com",
                "name": "Agent 2",
                "share_of_entitlement": 0.5,
            },
        ],
        "goods": [
            {
                "name": "House",
                "estimated_value": 100000,
                "indivisible": True,
            },
            {
                "name": "Car",
                "estimated_value": 20000,
                "indivisible": True,
            },
        ],
    }

    response = client.post("/api/v1/disputes/", json=dispute_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dispute"
    assert len(data["agents"]) == 2
    assert len(data["goods"]) == 2
