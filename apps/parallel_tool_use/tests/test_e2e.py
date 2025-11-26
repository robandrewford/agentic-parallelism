"""End-to-end tests for App 01: Parallel Tool Use."""
import pytest
import requests
import os


@pytest.mark.e2e
def test_health_endpoint():
    """Critical: Health check must work for uptime monitoring."""
    base_url = os.getenv("APP_URL", "http://localhost:8000")
    
    response = requests.get(f"{base_url}/health", timeout=10)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "app" in data


@pytest.mark.e2e
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY to be set"
)
def test_agent_execution_with_real_apis():
    """Critical: Agent can execute with real LLM and tools."""
    base_url = os.getenv("APP_URL", "http://localhost:8000")
    
    # This uses real APIs - run sparingly!
    response = requests.post(
        f"{base_url}/run",
        json={"query": "What is NVDA stock price?"},
        timeout=60  # Allow time for LLM inference
    )
    
    assert response.status_code == 200
    
    data = response.json()
    assert "result" in data
    assert "performance_log" in data
    assert "total_time" in data
    assert len(data["result"]) > 0
    assert data["total_time"] > 0


@pytest.mark.e2e
def test_root_endpoint():
    """Test root endpoint returns API information."""
    base_url = os.getenv("APP_URL", "http://localhost:8000")
    
    response = requests.get(f"{base_url}/", timeout=10)
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "endpoints" in data


@pytest.mark.e2e
def test_invalid_request():
    """Test API handles invalid requests gracefully."""
    base_url = os.getenv("APP_URL", "http://localhost:8000")
    
    # Empty query
    response = requests.post(
        f"{base_url}/run",
        json={},
        timeout=10
    )
    assert response.status_code in [400, 422]  # Validation error


if __name__ == "__main__":
    # Run E2E tests
    pytest.main([__file__, "-v", "-m", "e2e"])
