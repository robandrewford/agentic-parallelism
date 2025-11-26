"""Configuration management for agentic parallelism applications."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class BaseConfig(BaseSettings):
    """Base configuration class with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    environment: str = Field(default="local", description="Deployment environment: local, staging, production")
    version: str = Field(default="0.1.0", description="Application version")
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", description="LLM provider: openai, anthropic, azure, huggingface")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    huggingface_token: Optional[str] = Field(default=None, description="Hugging Face token")
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(default=True, description="Enable LangSmith tracing")
    langchain_api_key: Optional[str] = Field(default=None, description="LangSmith API key")
    langchain_project: str = Field(default="agentic-parallelism", description="LangSmith project name")
    
    # Sentry Configuration
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    sentry_environment: Optional[str] = Field(default=None, description="Sentry environment (defaults to environment)")
    sentry_traces_sample_rate: float = Field(default=0.1, description="Sentry traces sample rate")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    
    # Tool API Keys
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily API key for search")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set sentry_environment to environment if not explicitly set
        if self.sentry_environment is None:
            self.sentry_environment = self.environment


def load_config() -> BaseConfig:
    """Load configuration from environment variables and .env file."""
    return BaseConfig()


__all__ = ["BaseConfig", "load_config"]
