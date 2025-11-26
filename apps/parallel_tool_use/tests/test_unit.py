"""Unit tests for App 01: Parallel Tool Use."""
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock environment dependencies before app import."""
    # Remove app from sys.modules to ensure clean import with mocks
    if 'apps.parallel_tool_use.app' in sys.modules:
        del sys.modules['apps.parallel_tool_use.app']
        
    with patch('shared.config.load_config') as mock_config_load, \
         patch('shared.llm.LLMFactory.create') as mock_llm_create:
        
        # Setup mock config
        config = MagicMock()
        config.sentry_dsn = None
        config.environment = "test"
        config.version = "0.1.0-test"
        config.api_host = "0.0.0.0"
        config.api_port = 8000
        config.tavily_api_key = "test-key"
        mock_config_load.return_value = config
        
        # Setup mock LLM
        llm = MagicMock()
        llm.bind_tools = MagicMock(return_value=llm)
        mock_llm_create.return_value = llm
        
        yield


def test_health_endpoint():
    """Test health endpoint returns 200 and correct format."""
    from apps.parallel_tool_use.app import app as fastapi_app
    
    client = TestClient(fastapi_app)
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "app" in data
    assert "version" in data
    assert data["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint returns API information."""
    from apps.parallel_tool_use.app import app as fastapi_app
    
    client = TestClient(fastapi_app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "endpoints" in data


@patch('apps.parallel_tool_use.app.agent_app')
def test_run_endpoint_success(mock_agent_app):
    """Test run endpoint with successful agent execution."""
    from apps.parallel_tool_use.app import app as fastapi_app
    from langchain_core.messages import AIMessage
    
    # Mock agent response
    mock_state = {
        "messages": [AIMessage(content="Test response")],
        "performance_log": ["[AGENT] LLM call took 0.5 seconds."]
    }
    mock_agent_app.stream.return_value = iter([mock_state])
    
    client = TestClient(fastapi_app)
    response = client.post(
        "/run",
        json={"query": "Test query"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "performance_log" in data
    assert "total_time" in data
    assert data["result"] == "Test response"


@patch('apps.parallel_tool_use.app.agent_app')
def test_run_endpoint_error(mock_agent_app):
    """Test run endpoint handles errors gracefully."""
    from apps.parallel_tool_use.app import app as fastapi_app
    
    # Mock agent error
    mock_agent_app.stream.side_effect = Exception("Test error")
    
    client = TestClient(fastapi_app)
    response = client.post(
        "/run",
        json={"query": "Test query"}
    )
    
    assert response.status_code == 500


def test_get_stock_price_tool():
    """Test stock price tool with mocked yfinance."""
    from apps.parallel_tool_use.app import get_stock_price
    
    with patch('apps.parallel_tool_use.app.yf.Ticker') as mock_ticker:
        mock_info = {'regularMarketPrice': 150.00}
        mock_ticker.return_value.info = mock_info
        
        result = get_stock_price.invoke({"symbol": "AAPL"})
        assert result == 150.00


def test_get_recent_company_news_tool():
    """Test company news tool with mocked Tavily."""
    from apps.parallel_tool_use.app import get_recent_company_news
    
    with patch('apps.parallel_tool_use.app.TavilySearchResults') as mock_tavily:
        mock_search = MagicMock()
        mock_search.invoke.return_value = [{"title": "Test News", "url": "http://example.com"}]
        mock_tavily.return_value = mock_search
        
        result = get_recent_company_news.invoke({"company_name": "Apple"})
        assert isinstance(result, list)
        assert len(result) > 0
