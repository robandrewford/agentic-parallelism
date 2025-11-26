"""Setup script for installing shared modules as an editable package."""
from setuptools import setup, find_packages

setup(
    name="agentic-parallelism-shared",
    version="0.1.0",
    description="Shared modules for agentic parallelism applications",
    author="Robert Ford",
    packages=find_packages(where="shared"),
    package_dir={"": "shared"},
    python_requires=">=3.11",
    install_requires=[
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "langchain>=0.1.0",
        "langgraph>=0.1.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "sentry-sdk>=1.30.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "ruff>=0.1.0",
        ],
    },
)
