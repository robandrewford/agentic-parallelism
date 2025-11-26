"""Configuration for App 01: Parallel Tool Use."""
from shared.config import BaseConfig


class App01Config(BaseConfig):
    """App-specific configuration extending base config."""
    
    # App-specific settings can be added here if needed
    pass


def load_app_config() -> App01Config:
    """Load App 01 configuration."""
    return App01Config()
