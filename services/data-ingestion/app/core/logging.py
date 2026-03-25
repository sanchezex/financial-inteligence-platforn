"""
Data Ingestion Service - Logging (Symlink to backend logging)
"""

from backend.app.core.logging import configure_logging, get_logger, LogManager

__all__ = ['configure_logging', 'get_logger', 'LogManager']

