"""Sentry initialization and error tracking utilities."""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from typing import Optional


def init_sentry(
    dsn: Optional[str] = None,
    environment: str = "local",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    enable_fastapi: bool = True,
) -> None:
    """
    Initialize Sentry for error tracking.
    
    Args:
        dsn: Sentry DSN (if None, Sentry will not be initialized)
        environment: Deployment environment (local, staging, production)
        release: Release version
        traces_sample_rate: Percentage of transactions to sample (0.0 to 1.0)
        enable_fastapi: Whether to enable FastAPI integration
    """
    if not dsn:
        print("⚠️  Sentry DSN not provided. Sentry will not be initialized.")
        return
    
    integrations = []
    if enable_fastapi:
        integrations.append(FastApiIntegration())
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        traces_sample_rate=traces_sample_rate,
        integrations=integrations,
        # Send PII data (personally identifiable information) to Sentry
        send_default_pii=False,
        # Attach stack traces to all messages
        attach_stacktrace=True,
    )
    
    print(f"✅ Sentry initialized for environment: {environment}")


def capture_exception(exception: Exception, **kwargs) -> None:
    """
    Capture an exception and send to Sentry.
    
    Args:
        exception: The exception to capture
        **kwargs: Additional context to attach to the event
    """
    sentry_sdk.capture_exception(exception, **kwargs)


def capture_message(message: str, level: str = "info", **kwargs) -> None:
    """
    Capture a message and send to Sentry.
    
    Args:
        message: The message to capture
        level: Message level (debug, info, warning, error, fatal)
        **kwargs: Additional context to attach to the event
    """
    sentry_sdk.capture_message(message, level=level, **kwargs)


__all__ = ["init_sentry", "capture_exception", "capture_message"]
