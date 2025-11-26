"""Health check utilities for monitoring application status."""
from typing import Dict, Any, Optional
from datetime import datetime


class HealthCheck:
    """Health check utility for monitoring application status."""
    
    def __init__(self, app_name: str, version: str):
        """Initialize health check with app name and version."""
        self.app_name = app_name
        self.version = version
        self.start_time = datetime.utcnow()
    
    def get_health_status(
        self,
        include_dependencies: bool = False,
        dependencies: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Get the health status of the application.
        
        Args:
            include_dependencies: Whether to include dependency checks
            dependencies: Dictionary of dependency names and their health status
            
        Returns:
            Dictionary containing health status information
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        status = {
            "status": "healthy",
            "app": self.app_name,
            "version": self.version,
            "uptime_seconds": uptime,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if include_dependencies and dependencies:
            status["dependencies"] = dependencies
            # Set overall status to unhealthy if any dependency is down
            if not all(dependencies.values()):
                status["status"] = "unhealthy"
        
        return status
    
    @staticmethod
    def check_dependency(check_func: callable, dependency_name: str) -> bool:
        """
        Check if a dependency is healthy.
        
        Args:
            check_func: Function that returns True if dependency is healthy
            dependency_name: Name of the dependency
            
        Returns:
            True if dependency is healthy, False otherwise
        """
        try:
            return check_func()
        except Exception as e:
            print(f"⚠️  Dependency check failed for {dependency_name}: {e}")
            return False


__all__ = ["HealthCheck"]
