"""Tool implementations for memU MCP Server"""

import json
from typing import Any, Dict, Optional

from .memu_client import MemuClientWrapper
from .logger import MemuLogger


class MemoryTools:
    """Implementation of memory-related tools for MCP server"""
    
    def __init__(self, memu_client: MemuClientWrapper, logger: MemuLogger):
        self.memu_client = memu_client
        self.logger = logger
        
        # Set logger for memu client
        self.memu_client.set_logger(logger)
    
    async def memorize_conversation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Store a conversation in memory"""
        try:
            # Extract and validate arguments
            conversation = arguments.get("conversation")
            if not conversation:
                raise ValueError("conversation is required")
            
            user_id = arguments.get("user_id", "default_user")
            user_name = arguments.get("user_name", "User")
            agent_id = arguments.get("agent_id", "default_agent")
            agent_name = arguments.get("agent_name", "Assistant")
            
            # Validate conversation length
            if len(conversation) > 100000:  # 100k character limit
                raise ValueError("Conversation too long (max 100,000 characters)")
            
            self.logger.log_tool_call("memorize_conversation", arguments)
            
            # Call memU client
            result = await self.memu_client.memorize_conversation(
                conversation=conversation,
                user_id=user_id,
                user_name=user_name,
                agent_id=agent_id,
                agent_name=agent_name
            )
            
            self.logger.info(f"Successfully memorized conversation for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in memorize_conversation: {e}")
            self.logger.log_tool_call("memorize_conversation", arguments, success=False)
            raise
    
    async def retrieve_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant memories based on query"""
        try:
            # Extract and validate arguments
            query = arguments.get("query")
            if not query:
                raise ValueError("query is required")
            
            user_id = arguments.get("user_id", "default_user")
            limit = arguments.get("limit", 10)
            
            # Validate limit
            if not isinstance(limit, int) or limit < 1 or limit > 50:
                raise ValueError("limit must be an integer between 1 and 50")
            
            self.logger.log_tool_call("retrieve_memory", arguments)
            
            # Call memU client
            result = await self.memu_client.retrieve_memory(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            self.logger.info(f"Retrieved {len(result.get('memories', []))} memories for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in retrieve_memory: {e}")
            self.logger.log_tool_call("retrieve_memory", arguments, success=False)
            raise
    
    async def search_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search memories using semantic similarity"""
        try:
            # Extract and validate arguments
            search_query = arguments.get("search_query")
            if not search_query:
                raise ValueError("search_query is required")
            
            user_id = arguments.get("user_id", "default_user")
            filters = arguments.get("filters", {})
            limit = arguments.get("limit", 10)
            
            # Validate limit
            if not isinstance(limit, int) or limit < 1 or limit > 50:
                raise ValueError("limit must be an integer between 1 and 50")
            
            # Validate filters
            if filters and not isinstance(filters, dict):
                raise ValueError("filters must be a dictionary")
            
            self.logger.log_tool_call("search_memory", arguments)
            
            # Call memU client
            result = await self.memu_client.search_memory(
                search_query=search_query,
                user_id=user_id,
                filters=filters,
                limit=limit
            )
            
            self.logger.info(f"Found {len(result.get('results', []))} memories for search query")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in search_memory: {e}")
            self.logger.log_tool_call("search_memory", arguments, success=False)
            raise
    
    async def manage_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Update or delete specific memories"""
        try:
            # Extract and validate arguments
            action = arguments.get("action")
            if action not in ["update", "delete"]:
                raise ValueError("action must be 'update' or 'delete'")
            
            memory_id = arguments.get("memory_id")
            if not memory_id:
                raise ValueError("memory_id is required")
            
            user_id = arguments.get("user_id", "default_user")
            
            self.logger.log_tool_call("manage_memory", arguments)
            
            # Handle different actions
            if action == "update":
                new_content = arguments.get("new_content")
                if not new_content:
                    raise ValueError("new_content is required for update action")
                
                result = await self.memu_client.update_memory(
                    memory_id=memory_id,
                    new_content=new_content,
                    user_id=user_id
                )
                
            elif action == "delete":
                result = await self.memu_client.delete_memory(
                    memory_id=memory_id,
                    user_id=user_id
                )
            
            self.logger.info(f"Successfully {action}d memory {memory_id} for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in manage_memory: {e}")
            self.logger.log_tool_call("manage_memory", arguments, success=False)
            raise
    
    async def get_memory_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        try:
            # Extract and validate arguments
            user_id = arguments.get("user_id", "default_user")
            include_details = arguments.get("include_details", False)
            
            # Validate include_details
            if not isinstance(include_details, bool):
                raise ValueError("include_details must be a boolean")
            
            self.logger.log_tool_call("get_memory_stats", arguments)
            
            # Call memU client
            result = await self.memu_client.get_memory_stats(
                user_id=user_id,
                include_details=include_details
            )
            
            self.logger.info(f"Retrieved memory stats for user {user_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in get_memory_stats: {e}")
            self.logger.log_tool_call("get_memory_stats", arguments, success=False)
            raise
    
    def _format_result(self, result: Dict[str, Any]) -> str:
        """Format result as JSON string for MCP response"""
        try:
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception:
            return str(result)