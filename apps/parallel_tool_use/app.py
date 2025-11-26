"""App 01: Parallel Tool Use - Production FastAPI Application

This application demonstrates parallel tool execution using LangGraph with real-world APIs.
Extracted from 01_parallel_tool_use.ipynb for production deployment.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, TypedDict, Annotated
import time
import operator

from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import yfinance as yf

from shared.config import load_config
from shared.llm import LLMFactory
from shared.observability import init_sentry, HealthCheck

# Load configuration
config = load_config()

# Initialize Sentry
init_sentry(
    dsn=config.sentry_dsn,
    environment=config.sentry_environment or config.environment,
    release=config.version,
    traces_sample_rate=config.sentry_traces_sample_rate,
)

# Initialize FastAPI
app = FastAPI(
    title="App 01: Parallel Tool Use",
    description="Production-ready agent with parallel tool execution",
    version=config.version,
)

# Initialize health check
health_check = HealthCheck(app_name="parallel-tool-use", version=config.version)


# Define Tools
@tool
def get_stock_price(symbol: str) -> float:
    """Get the current stock price for a given stock symbol using Yahoo Finance."""
    print(f"--- [Tool Call] Executing get_stock_price for symbol: {symbol} ---")
    ticker = yf.Ticker(symbol)
    price = ticker.info.get('regularMarketPrice', ticker.info.get('currentPrice'))
    if price is None:
        return f"Could not find price for symbol {symbol}"
    return price


@tool
def get_recent_company_news(company_name: str) -> list:
    """Get recent news articles and summaries for a given company name using the Tavily search engine."""
    print(f"--- [Tool Call] Executing get_recent_company_news for: {company_name} ---")
    tavily_search = TavilySearchResults(
        max_results=5,
        api_key=config.tavily_api_key
    )
    query = f"latest news about {company_name}"
    return tavily_search.invoke(query)


# Agent State
class AgentState(TypedDict):
    """State schema for the agent graph."""
    messages: Annotated[List[BaseMessage], operator.add]
    performance_log: Annotated[List[str], operator.add]


# Create LLM
llm = LLMFactory.create(config=config)

# Create tools list
tools = [get_stock_price, get_recent_company_news]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(tools)

# Create tool node
tool_node = ToolNode(tools)


# Define Graph Nodes
def call_model(state: AgentState):
    """The agent node: calls the LLM, measures performance, and logs the result."""
    print("--- AGENT: Invoking LLM --- ")
    start_time = time.time()
    
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    log_entry = f"[AGENT] LLM call took {execution_time:.2f} seconds."
    print(log_entry)
    
    return {
        "messages": [response],
        "performance_log": [log_entry]
    }


def should_continue(state: AgentState) -> str:
    """Determine whether to continue to tools or end."""
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END


# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

# Compile the graph
agent_app = workflow.compile()


# API Models
class QueryRequest(BaseModel):
    """Request model for agent queries."""
    query: str
    stream: Optional[bool] = False


class QueryResponse(BaseModel):
    """Response model for agent queries."""
    result: str
    performance_log: List[str]
    total_time: float


# API Endpoints
@app.get("/health")
async def health():
    """Health check endpoint for monitoring."""
    return health_check.get_health_status()


@app.post("/run", response_model=QueryResponse)
async def run_agent(request: QueryRequest) -> QueryResponse:
    """
    Execute the agent with the given query.
    
    Args:
        request: QueryRequest containing the user's query
        
    Returns:
        QueryResponse with the agent's result and performance metrics
    """
    try:
        start_time = time.time()
        
        # Prepare inputs
        inputs = {
            "messages": [HumanMessage(content=request.query)],
            "performance_log": []
        }
        
        # Execute agent
        final_state = None
        for output in agent_app.stream(inputs, stream_mode="values"):
            final_state = output
        
        # Extract result
        if final_state and 'messages' in final_state:
            last_msg = final_state['messages'][-1]
            result = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        else:
            result = "No response generated"
        
        total_time = time.time() - start_time
        
        return QueryResponse(
            result=result,
            performance_log=final_state.get('performance_log', []) if final_state else [],
            total_time=total_time
        )
    
    except Exception as e:
        print(f"Error executing agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "App 01: Parallel Tool Use",
        "version": config.version,
        "description": "Production-ready agent with parallel tool execution",
        "endpoints": {
            "health": "/health",
            "run": "/run (POST)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level="info"
    )
