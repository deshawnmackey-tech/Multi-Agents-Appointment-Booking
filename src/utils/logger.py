"""
Logging configuration and utilities.
"""
import logging
import sys
from typing import Optional

from src.config import get_settings

settings = get_settings()


def setup_logger(
    name: str,
    level: Optional[str] = None,
    format_type: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure a logger.
    
    Args:
        name: Logger name
        level: Optional log level override
        format_type: Optional format type override (json or text)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))
    
    # Set format
    fmt_type = format_type or settings.log_format
    
    if fmt_type == "json":
        # JSON format for production
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s",'
            '"message":"%(message)s","module":"%(module)s","function":"%(funcName)s",'
            '"line":%(lineno)d}'
        )
    else:
        # Text format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
            '[%(module)s:%(funcName)s:%(lineno)d]'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return setup_logger(name)


# Create default application logger
app_logger = get_logger("app")

# Made with Bob