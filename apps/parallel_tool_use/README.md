# App 01: Parallel Tool Use

Production-ready FastAPI application demonstrating parallel tool execution using LangGraph with real-world APIs.

## 📋 Overview

This application showcases:
- **Parallel Tool Execution**: Using LangGraph to coordinate multiple API calls
- **Real-World Integration**: Stock prices (yfinance) and news search (Tavily)
- **Production-Ready**: FastAPI with health checks, Sentry integration, and containerization
- **SOLO-Aligned**: Follows the SOLO automation architecture with Azure Container Apps deployment

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   # From repository root
   pip install -e .
   pip install -r apps/parallel_tool_use/requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp apps/parallel_tool_use/.env.example apps/parallel_tool_use/.env
   # Edit .env with your API keys
   ```

3. **Run the Application**:
   ```bash
   cd apps/parallel_tool_use
   python app.py
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn apps.parallel_tool_use.app:app --reload
   ```

4. **Access the API**:
   - **API Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health
   - **Root**: http://localhost:8000/

### Docker Development

1. **Build and Run with Docker Compose**:
   ```bash
   cd infrastructure
   docker-compose up app-01
   ```

2. **Access the API**: http://localhost:8001

### Testing

```bash
# Unit tests
pytest apps/parallel_tool_use/tests/test_unit.py -v

# E2E tests (requires API keys)
export APP_URL=http://localhost:8000
pytest apps/parallel_tool_use/tests/test_e2e.py -v -m e2e

# With coverage
pytest apps/parallel_tool_use/tests/ --cov --cov-report=html
```

## 📦 API Endpoints

### POST /run
Execute the agent with a natural language query.

**Request**:
```json
{
  "query": "What is the current stock price of NVIDIA (NVDA) and what is the latest news?"
}
```

**Response**:
```json
{
  "result": "The current stock price of NVIDIA (NVDA) is $177.82. Recent news includes...",
  "performance_log": [
    "[AGENT] LLM call took 2.34 seconds.",
    "[TOOLS] Executed 2 tools in 1.56 seconds."
  ],
  "total_time": 4.12
}
```

### GET /health
Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "app": "parallel-tool-use",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "timestamp": "2025-11-25T23:15:00Z"
}
```

## 🔧 Configuration

Configuration is managed through environment variables. See `.env.example` for all options.

**Key Variables**:
- `LLM_PROVIDER`: Choose from `openai`, `anthropic`, `azure`, or `huggingface`
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
- `TAVILY_API_KEY`: Tavily API key for news search
- `SENTRY_DSN`: Sentry DSN for error tracking
- `LANGCHAIN_API_KEY`: LangSmith API key for tracing

## 🏗️ Architecture

```
┌─────────────┐
│   FastAPI   │
│  /run, /health│
└──────┬──────┘
       │
       v
┌─────────────┐
│  LangGraph  │
│   Agent     │
└──────┬──────┘
       │
       ├────────────┬────────────┐
       v            v            v
┌──────────┐ ┌──────────┐ ┌──────────┐
│   LLM    │ │  Stock   │ │   News   │
│ Provider │ │  Price   │ │  Search  │
└──────────┘ └──────────┘ └──────────┘
```

## 🚢 Deployment

### Azure Container Apps (Recommended)

1. **Build and Push Image**:
   ```bash
   docker build -t app-01:latest -f apps/parallel_tool_use/Dockerfile .
   docker tag app-01:latest ${ACR_NAME}.azurecr.io/parallel_tool_use:latest
   docker push ${ACR_NAME}.azurecr.io/parallel_tool_use:latest
   ```

2. **Deploy**:
   ```bash
   ./infrastructure/scripts/deploy-staging.sh
   ```

### Via GitHub Actions

Deployment is automated via GitHub Actions:
- **Staging**: Automatic on merge to `main`
- **Production**: Automatic on version tags (`v*.*.*`)

See `.github/workflows/cd-staging.yml` and `.github/workflows/cd-production.yml`.

## 📊 Monitoring

- **Health Checks**: Automated via GitHub Actions every 15 minutes
- **Sentry**: Error tracking and performance monitoring
- **LangSmith**: LLM call tracing and debugging

## 🧪 Development

### Adding New Tools

1. Define the tool with `@tool` decorator:
   ```python
   @tool
   def my_new_tool(param: str) -> str:
       """Description for the LLM."""
       return "result"
   ```

2. Add to tools list:
   ```python
   tools = [get_stock_price, get_recent_company_news, my_new_tool]
   ```

3. Write tests:
   ```python
   def test_my_new_tool():
       result = my_new_tool.invoke({"param": "test"})
       assert result == "expected"
   ```

### Code Quality

```bash
# Linting
ruff check apps/parallel_tool_use/

# Format
ruff format apps/parallel_tool_use/
```

## 📚 Related Documentation

- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Azure Container Apps**: https://learn.microsoft.com/en-us/azure/container-apps/

## 📝 License

See root repository LICENSE file.
