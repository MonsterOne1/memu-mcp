#!/usr/bin/env python3
"""
HTTP API server for memU MCP Server on Render platform

Provides health checks, monitoring endpoints, and management interface
for the Render deployment.
"""

import argparse
import asyncio
import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

from aiohttp import web, web_request
from aiohttp.web import middleware
from aiohttp.web_response import Response
import aiohttp_cors

from .config import Config
from .memu_client import MemuClientWrapper
from .logger import setup_logger


class MemuMCPAPI:
    """HTTP API server for memU MCP Server"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger(config.log_level)
        self.app = web.Application(middlewares=[self.cors_middleware])
        self.memu_client: Optional[MemuClientWrapper] = None
        self.start_time = time.time()
        
        # Setup CORS
        if os.getenv("ENABLE_CORS", "false").lower() == "true":
            self.setup_cors()
        
        # Setup routes
        self.setup_routes()
    
    def setup_cors(self):
        """Setup CORS configuration"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    @middleware
    async def cors_middleware(self, request: web_request.Request, handler):
        """CORS middleware"""
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_get('/', self.root_handler)
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/status', self.status_handler)
        self.app.router.add_get('/metrics', self.metrics_handler)
        self.app.router.add_get('/info', self.info_handler)
        self.app.router.add_post('/test', self.test_handler)
        self.app.router.add_options('/{path:.*}', self.options_handler)
    
    async def root_handler(self, request: web_request.Request) -> Response:
        """Root endpoint"""
        return web.json_response({
            "service": "memU MCP Server API",
            "version": self.config.server_version,
            "status": "running",
            "deployment": "render",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "health": "/health",
                "status": "/status", 
                "metrics": "/metrics",
                "info": "/info",
                "test": "/test"
            }
        })
    
    async def health_handler(self, request: web_request.Request) -> Response:
        """Health check endpoint for Render"""
        try:
            # Basic health check
            uptime = time.time() - self.start_time
            
            health_status = {
                "status": "healthy",
                "uptime_seconds": round(uptime, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "service": "memu-mcp-server-api"
            }
            
            # Test memU client if available
            if self.memu_client:
                try:
                    # Quick connection test (timeout 5s)
                    await asyncio.wait_for(
                        self.test_memu_connection(),
                        timeout=5.0
                    )
                    health_status["memu_connection"] = "ok"
                except asyncio.TimeoutError:
                    health_status["memu_connection"] = "timeout"
                except Exception as e:
                    health_status["memu_connection"] = f"error: {str(e)}"
            else:
                health_status["memu_connection"] = "not_initialized"
            
            return web.json_response(health_status)
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return web.json_response({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=503)
    
    async def status_handler(self, request: web_request.Request) -> Response:
        """Detailed status endpoint"""
        try:
            uptime = time.time() - self.start_time
            
            status = {
                "service": "memU MCP Server",
                "version": self.config.server_version,
                "deployment": "render",
                "uptime_seconds": round(uptime, 2),
                "uptime_human": self.format_uptime(uptime),
                "timestamp": datetime.utcnow().isoformat(),
                "configuration": {
                    "memu_base_url": self.config.memu_base_url,
                    "log_level": self.config.log_level,
                    "max_conversation_length": self.config.max_conversation_length,
                    "api_timeout": self.config.api_timeout,
                    "rate_limit_per_minute": self.config.rate_limit_per_minute
                },
                "environment": {
                    "render_deployment": os.getenv("RENDER_DEPLOYMENT", "false"),
                    "python_version": os.sys.version.split()[0],
                    "platform": os.name
                }
            }
            
            return web.json_response(status)
            
        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return web.json_response({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=500)
    
    async def metrics_handler(self, request: web_request.Request) -> Response:
        """Metrics endpoint for monitoring"""
        try:
            uptime = time.time() - self.start_time
            
            metrics = {
                "uptime_seconds": round(uptime, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "process": {
                    "pid": os.getpid(),
                    "memory_usage_mb": self.get_memory_usage(),
                },
                "system": {
                    "load_average": self.get_load_average(),
                    "cpu_count": os.cpu_count()
                },
                "memu_client": {
                    "initialized": self.memu_client is not None,
                    "base_url": self.config.memu_base_url
                }
            }
            
            return web.json_response(metrics)
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return web.json_response({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=500)
    
    async def info_handler(self, request: web_request.Request) -> Response:
        """Service information endpoint"""
        return web.json_response({
            "name": "memU MCP Server",
            "description": "Model Context Protocol server for memU AI memory framework",
            "version": self.config.server_version,
            "deployment": "render",
            "capabilities": [
                "memorize_conversation",
                "retrieve_memory", 
                "search_memory",
                "manage_memory",
                "get_memory_stats"
            ],
            "protocols": ["MCP", "HTTP"],
            "documentation": "https://github.com/example/memu-mcp-server",
            "health_check": "/health",
            "contact": "support@example.com"
        })
    
    async def test_handler(self, request: web_request.Request) -> Response:
        """Test endpoint for validation"""
        try:
            data = await request.json() if request.content_type == 'application/json' else {}
            
            test_result = {
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
                "echo": data,
                "server_info": {
                    "version": self.config.server_version,
                    "uptime": round(time.time() - self.start_time, 2)
                }
            }
            
            # Test memU connection if requested
            if data.get("test_memu_connection"):
                if self.memu_client:
                    try:
                        await self.test_memu_connection()
                        test_result["memu_test"] = "success"
                    except Exception as e:
                        test_result["memu_test"] = f"failed: {str(e)}"
                else:
                    test_result["memu_test"] = "client_not_initialized"
            
            return web.json_response(test_result)
            
        except Exception as e:
            self.logger.error(f"Test handler failed: {e}")
            return web.json_response({
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, status=500)
    
    async def options_handler(self, request: web_request.Request) -> Response:
        """Handle OPTIONS requests for CORS"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            }
        )
    
    async def test_memu_connection(self) -> bool:
        """Test memU client connection"""
        if not self.memu_client:
            raise ConnectionError("memU client not initialized")
        
        # This would be implemented based on memU's actual health check API
        # For now, we'll use a placeholder
        return True
    
    def format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in human readable format"""
        uptime = int(uptime_seconds)
        days = uptime // 86400
        hours = (uptime % 86400) // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return round(process.memory_info().rss / 1024 / 1024, 2)
        except ImportError:
            return 0.0
    
    def get_load_average(self) -> Optional[float]:
        """Get system load average"""
        try:
            return round(os.getloadavg()[0], 2)
        except (AttributeError, OSError):
            return None
    
    async def initialize_memu_client(self):
        """Initialize memU client for health checks"""
        try:
            self.memu_client = MemuClientWrapper(self.config)
            await self.memu_client.initialize()
            self.logger.info("memU client initialized for API health checks")
        except Exception as e:
            self.logger.warning(f"Failed to initialize memU client for health checks: {e}")
    
    async def startup(self):
        """Startup tasks"""
        self.logger.info(f"Starting memU MCP API server v{self.config.server_version}")
        await self.initialize_memu_client()
    
    async def cleanup(self):
        """Cleanup tasks"""
        if self.memu_client:
            await self.memu_client.close()
        self.logger.info("memU MCP API server stopped")
    
    async def run(self, host: str = "0.0.0.0", port: int = 10000):
        """Run the HTTP API server"""
        await self.startup()
        
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            self.logger.info(f"memU MCP API server running on http://{host}:{port}")
            
            # Keep server running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            self.logger.error(f"API server error: {e}")
            raise
        finally:
            await self.cleanup()


def main():
    """Main function to start the API server"""
    parser = argparse.ArgumentParser(description="memU MCP Server API")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", 10000)),
        help="Port to bind to"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default=None
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.from_file(args.config) if args.config else Config()
    
    # Create and run API server
    api_server = MemuMCPAPI(config)
    
    try:
        asyncio.run(api_server.run(args.host, args.port))
    except KeyboardInterrupt:
        print("\nShutting down API server...")
    except Exception as e:
        print(f"API server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()