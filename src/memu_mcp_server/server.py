"""Main MCP server implementation for memU"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence

from mcp import server
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetPromptRequest,
    GetPromptResult,
    GetResourceRequest,
    GetResourceResult,
    ListPromptsRequest,
    ListPromptsResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Prompt,
    Resource,
    TextContent,
    Tool,
    INTERNAL_ERROR,
    INVALID_PARAMS,
)

from .config import Config
from .memu_client import MemuClientWrapper
from .tools import MemoryTools
from .logger import setup_logger


class MemuMCPServer:
    """MCP Server for memU AI memory framework"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = setup_logger(config.log_level)
        self.mcp_server = Server("memu-mcp-server")
        self.memu_client = MemuClientWrapper(config)
        self.memory_tools = MemoryTools(self.memu_client, self.logger)
        
        # Setup MCP server handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server request handlers"""
        
        @self.mcp_server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="memorize_conversation",
                    description="Store a conversation in memory for future reference",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "conversation": {
                                "type": "string",
                                "description": "The conversation text to memorize"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "Unique identifier for the user",
                                "default": self.config.default_user_id
                            },
                            "user_name": {
                                "type": "string",
                                "description": "Display name for the user"
                            },
                            "agent_id": {
                                "type": "string",
                                "description": "Unique identifier for the AI agent",
                                "default": self.config.default_agent_id
                            },
                            "agent_name": {
                                "type": "string",
                                "description": "Display name for the AI agent"
                            }
                        },
                        "required": ["conversation"]
                    }
                ),
                Tool(
                    name="retrieve_memory",
                    description="Retrieve relevant memories based on context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Query to search for relevant memories"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID to search memories for",
                                "default": self.config.default_user_id
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of memories to retrieve",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="search_memory",
                    description="Search memories using semantic similarity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "Text to search for in memories"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID to search memories for",
                                "default": self.config.default_user_id
                            },
                            "filters": {
                                "type": "object",
                                "description": "Additional filters for search",
                                "properties": {
                                    "date_from": {"type": "string", "format": "date"},
                                    "date_to": {"type": "string", "format": "date"},
                                    "agent_id": {"type": "string"}
                                }
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["search_query"]
                    }
                ),
                Tool(
                    name="manage_memory",
                    description="Update or delete specific memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["update", "delete"],
                                "description": "Action to perform on the memory"
                            },
                            "memory_id": {
                                "type": "string",
                                "description": "ID of the memory to manage"
                            },
                            "new_content": {
                                "type": "string",
                                "description": "New content for update action"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID who owns the memory",
                                "default": self.config.default_user_id
                            }
                        },
                        "required": ["action", "memory_id"]
                    }
                ),
                Tool(
                    name="get_memory_stats",
                    description="Get statistics about stored memories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "User ID to get stats for",
                                "default": self.config.default_user_id
                            },
                            "include_details": {
                                "type": "boolean",
                                "description": "Include detailed breakdown",
                                "default": False
                            }
                        }
                    }
                )
            ]
        
        @self.mcp_server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                self.logger.info(f"Calling tool: {name} with arguments: {arguments}")
                
                if name == "memorize_conversation":
                    result = await self.memory_tools.memorize_conversation(arguments)
                elif name == "retrieve_memory":
                    result = await self.memory_tools.retrieve_memory(arguments)
                elif name == "search_memory":
                    result = await self.memory_tools.search_memory(arguments)
                elif name == "manage_memory":
                    result = await self.memory_tools.manage_memory(arguments)
                elif name == "get_memory_stats":
                    result = await self.memory_tools.get_memory_stats(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return CallToolResult(
                    content=[TextContent(type="text", text=str(result))]
                )
            
            except ValueError as e:
                self.logger.error(f"Invalid parameters for tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
            except Exception as e:
                self.logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Internal error: {str(e)}")],
                    isError=True
                )
    
    async def run(self):
        """Run the MCP server"""
        try:
            self.config.validate_required_fields()
            self.logger.info(f"Starting memU MCP Server v{self.config.server_version}")
            
            # Initialize memU client connection
            await self.memu_client.initialize()
            
            # Run the MCP server
            async with self.mcp_server.stdio_server() as (read_stream, write_stream):
                await self.mcp_server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config.server_name,
                        server_version=self.config.server_version,
                        capabilities=server.ServerCapabilities(
                            tools={}
                        )
                    )
                )
                
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise
        finally:
            await self.memu_client.close()