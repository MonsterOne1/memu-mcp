"""Logging configuration for memU MCP Server"""

import logging
import os
import sys
from typing import Optional

import structlog
from rich.console import Console
from rich.logging import RichHandler


def setup_logger(log_level: str = "INFO") -> structlog.stdlib.BoundLogger:
    """Setup structured logging with rich formatting"""
    
    # Check if running in Render environment
    is_render = os.getenv("RENDER_DEPLOYMENT", "false").lower() == "true"
    
    if is_render:
        # Render environment - use simple logging to stderr
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            stream=sys.stderr,  # Use stderr to avoid interfering with stdio protocol
            force=True
        )
        
        # Configure structlog for Render (JSON output to stderr)
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    else:
        # Local development - use rich formatting
        console = Console(stderr=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(
                    console=console,
                    show_time=True,
                    show_level=True,
                    show_path=False,
                    markup=True,
                    rich_tracebacks=True,
                )
            ]
        )
        
        # Configure structlog for development
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer() if not is_render else structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    return structlog.get_logger("memu_mcp_server")


class MemuLogger:
    """Custom logger wrapper for memU MCP Server"""
    
    def __init__(self, logger: structlog.stdlib.BoundLogger):
        self.logger = logger
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.logger.critical(message, **kwargs)
    
    def log_tool_call(self, tool_name: str, arguments: dict, success: bool = True):
        """Log tool call with structured data"""
        self.logger.info(
            "Tool call",
            tool_name=tool_name,
            arguments=arguments,
            success=success
        )
    
    def log_memu_api_call(self, method: str, response_time: float, success: bool = True):
        """Log memU API call"""
        self.logger.info(
            "memU API call",
            method=method,
            response_time_ms=round(response_time * 1000, 2),
            success=success
        )