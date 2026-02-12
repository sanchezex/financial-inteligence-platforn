"""
Financial Intelligence Platform - Logging Configuration

Centralized logging setup for the application.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import settings


def configure_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
        log_file: Path to log file (optional)
    """
    # Get settings or use defaults
    level = log_level or settings.LOG_LEVEL
    format_str = log_format or settings.LOG_FORMAT
    
    # Convert string to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(format_str)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    root_logger.addHandler(console_handler)
    
    # Create file handler if log_file specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    configure_library_loggers(numeric_level)
    
    # Log startup message
    logging.info(f"Logging configured with level: {level}")


def configure_library_loggers(level: int) -> None:
    """
    Configure logging levels for third-party libraries.
    
    Args:
        level: Minimum logging level
    """
    # Reduce noise from third-party libraries
    library_loggers = {
        'urllib3': logging.WARNING,
        'requests': logging.WARNING,
        'httpx': logging.WARNING,
        'asyncio': logging.WARNING,
        'aiohttp': logging.WARNING,
        'sqlalchemy': logging.WARNING,
        'kafka': logging.WARNING,
        'redis': logging.WARNING,
        'transformers': logging.WARNING,
        'torch': logging.WARNING,
    }
    
    for lib_name, lib_level in library_loggers.items():
        lib_logger = logging.getLogger(lib_name)
        lib_logger.setLevel(lib_level)


class LogManager:
    """
    Manager for creating and managing application loggers.
    """
    
    def __init__(self, name: str):
        """
        Initialize log manager.
        
        Args:
            name: Logger name (usually __name__)
        """
        self.logger = logging.getLogger(name)
        self.name = name
    
    def get_logger(self) -> logging.Logger:
        """
        Get the configured logger instance.
        
        Returns:
            Configured logger instance
        """
        return self.logger
    
    def debug(self, message: str, **kwargs) -> None:
        """
        Log debug message.
        """
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """
        Log info message.
        """
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Log warning message.
        """
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """
        Log error message.
        """
        self.logger.error(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """
        Log critical message.
        """
        self.logger.critical(message, **kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """
        Log performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            **kwargs: Additional context
        """
        self.logger.info(
            f"Performance: {operation} completed in {duration:.3f}s",
            extra={
                "operation": operation,
                "duration_seconds": duration,
                "duration_ms": duration * 1000,
                **kwargs
            }
        )
    
    def log_data_event(self, event_type: str, data_source: str, **kwargs) -> None:
        """
        Log data ingestion/processing events.
        
        Args:
            event_type: Type of event (ingested, processed, failed)
            data_source: Name of the data source
            **kwargs: Additional context
        """
        self.logger.info(
            f"Data Event: {event_type} from {data_source}",
            extra={
                "event_type": event_type,
                "data_source": data_source,
                **kwargs
            }
        )


def get_logger(name: str) -> LogManager:
    """
    Get a LogManager instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        LogManager instance
    """
    return LogManager(name)

