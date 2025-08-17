"""
memU MCP Server

A Model Context Protocol (MCP) server for memU AI memory framework.
Provides standardized memory management capabilities for AI applications.
"""

__version__ = "0.1.0"
__author__ = "memU MCP Server Team"
__email__ = "support@example.com"

from .server import MemuMCPServer
from .config import Config

__all__ = ["MemuMCPServer", "Config"]