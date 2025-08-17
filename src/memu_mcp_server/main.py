#!/usr/bin/env python3
"""
Main entry point for memU MCP Server
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from .server import MemuMCPServer
from .config import Config
from .logger import setup_logger


def main():
    """Main function to start the memU MCP server"""
    parser = argparse.ArgumentParser(description="memU MCP Server")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level"
    )
    parser.add_argument(
        "--render-mode",
        action="store_true",
        help="Enable Render deployment mode"
    )
    
    args = parser.parse_args()
    
    # Set Render environment flag if specified
    if args.render_mode:
        os.environ["RENDER_DEPLOYMENT"] = "true"
    
    # Load configuration
    config = Config.from_file(args.config) if args.config else Config()
    config.log_level = args.log_level
    
    # Setup logger early for better error reporting
    logger = setup_logger(config.log_level)
    
    # Check if running in Render environment
    is_render = os.getenv("RENDER_DEPLOYMENT", "false").lower() == "true"
    
    if is_render:
        logger.info("Starting memU MCP Server in Render deployment mode")
        
        # Validate required environment variables for Render
        required_vars = ["MEMU_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            sys.exit(1)
        
        # Set additional Render-specific configuration
        config.server_name = os.getenv("MCP_SERVER_NAME", "memu-mcp-server-render")
        
        logger.info(f"Render configuration loaded: server={config.server_name}")
    else:
        logger.info("Starting memU MCP Server in local development mode")
    
    # Create and run server
    server = MemuMCPServer(config)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        if is_render:
            logger.info("Received shutdown signal, stopping server...")
        else:
            print("\nShutting down memU MCP Server...")
        sys.exit(0)
    except Exception as e:
        if is_render:
            logger.error(f"Server error: {e}")
        else:
            print(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()