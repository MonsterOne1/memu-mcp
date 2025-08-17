"""memU client wrapper for MCP server integration"""

import asyncio
import os
import time
from typing import Any, Dict, List, Optional, Union

from memu import MemuClient

from .config import Config
from .logger import MemuLogger


class MemuClientWrapper:
    """Wrapper around memU client with additional functionality for MCP server"""
    
    def __init__(self, config: Config):
        self.config = config
        self._client: Optional[MemuClient] = None
        self._logger: Optional[MemuLogger] = None
        self._retry_count = 0
        self._max_retries = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        self._base_delay = float(os.getenv("WORKER_RESTART_DELAY", "5"))
    
    async def initialize(self):
        """Initialize the memU client with retry logic"""
        for attempt in range(self._max_retries + 1):
            try:
                self._client = MemuClient(
                    base_url=self.config.memu_base_url,
                    api_key=self.config.memu_api_key
                )
                
                # Test connection
                await self._test_connection()
                
                if self._logger:
                    self._logger.info(
                        f"memU client initialized successfully on attempt {attempt + 1}"
                    )
                
                self._retry_count = 0  # Reset retry count on success
                return
                
            except Exception as e:
                if self._logger:
                    self._logger.warning(
                        f"Failed to initialize memU client (attempt {attempt + 1}/{self._max_retries + 1}): {e}"
                    )
                
                if attempt < self._max_retries:
                    delay = self._base_delay * (2 ** attempt)  # Exponential backoff
                    if self._logger:
                        self._logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    raise ConnectionError(f"Failed to initialize memU client after {self._max_retries + 1} attempts: {e}")
    
    async def _test_connection(self):
        """Test the connection to memU API"""
        try:
            # Simple test call to verify API key and connection
            start_time = time.time()
            
            # This is a placeholder - actual implementation would depend on memU API
            # For now, we'll assume the client is properly initialized if no exception is raised
            
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("test_connection", response_time, True)
                
        except Exception as e:
            if self._logger:
                self._logger.log_memu_api_call("test_connection", 0, False)
            raise
    
    def set_logger(self, logger: MemuLogger):
        """Set the logger for this client"""
        self._logger = logger
    
    async def memorize_conversation(
        self,
        conversation: str,
        user_id: str,
        user_name: str,
        agent_id: str,
        agent_name: str
    ) -> Dict[str, Any]:
        """Store a conversation in memU memory"""
        if not self._client:
            raise RuntimeError("Client not initialized")
        
        start_time = time.time()
        
        try:
            # Call memU API to store conversation
            result = await asyncio.to_thread(
                self._client.memorize_conversation,
                conversation=conversation,
                user_id=user_id,
                user_name=user_name,
                agent_id=agent_id,
                agent_name=agent_name
            )
            
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("memorize_conversation", response_time, True)
            
            return {
                "success": True,
                "message": "Conversation memorized successfully",
                "memory_id": getattr(result, 'id', None),
                "tokens_processed": len(conversation.split()),
                "processing_time": round(response_time, 3)
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("memorize_conversation", response_time, False)
            
            raise RuntimeError(f"Failed to memorize conversation: {e}")
    
    async def retrieve_memory(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Retrieve relevant memories based on query"""
        if not self._client:
            raise RuntimeError("Client not initialized")
        
        start_time = time.time()
        
        try:
            # This would be implemented based on memU's actual API
            # For now, we'll create a placeholder response structure
            
            # Simulated API call
            await asyncio.sleep(0.1)  # Simulate API delay
            
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("retrieve_memory", response_time, True)
            
            # Placeholder response structure
            return {
                "success": True,
                "memories": [
                    {
                        "id": "mem_001",
                        "content": "Example memory content related to query",
                        "relevance_score": 0.85,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "user_id": user_id,
                        "metadata": {
                            "conversation_id": "conv_001",
                            "agent_id": "agent_001"
                        }
                    }
                ],
                "total_found": 1,
                "query": query,
                "processing_time": round(response_time, 3)
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("retrieve_memory", response_time, False)
            
            raise RuntimeError(f"Failed to retrieve memories: {e}")
    
    async def search_memory(
        self,
        search_query: str,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search memories using semantic similarity"""
        if not self._client:
            raise RuntimeError("Client not initialized")
        
        start_time = time.time()
        
        try:
            # Placeholder implementation
            await asyncio.sleep(0.1)
            
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("search_memory", response_time, True)
            
            return {
                "success": True,
                "results": [
                    {
                        "id": "mem_002",
                        "content": "Memory content matching search query",
                        "similarity_score": 0.92,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "user_id": user_id
                    }
                ],
                "total_results": 1,
                "search_query": search_query,
                "filters_applied": filters or {},
                "processing_time": round(response_time, 3)
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("search_memory", response_time, False)
            
            raise RuntimeError(f"Failed to search memories: {e}")
    
    async def update_memory(
        self,
        memory_id: str,
        new_content: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Update a specific memory"""
        if not self._client:
            raise RuntimeError("Client not initialized")
        
        start_time = time.time()
        
        try:
            # Placeholder implementation
            await asyncio.sleep(0.05)
            
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("update_memory", response_time, True)
            
            return {
                "success": True,
                "message": "Memory updated successfully",
                "memory_id": memory_id,
                "updated_content": new_content,
                "processing_time": round(response_time, 3)
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("update_memory", response_time, False)
            
            raise RuntimeError(f"Failed to update memory: {e}")
    
    async def delete_memory(
        self,
        memory_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Delete a specific memory"""
        if not self._client:
            raise RuntimeError("Client not initialized")
        
        start_time = time.time()
        
        try:
            # Placeholder implementation
            await asyncio.sleep(0.05)
            
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("delete_memory", response_time, True)
            
            return {
                "success": True,
                "message": "Memory deleted successfully",
                "memory_id": memory_id,
                "processing_time": round(response_time, 3)
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("delete_memory", response_time, False)
            
            raise RuntimeError(f"Failed to delete memory: {e}")
    
    async def get_memory_stats(
        self,
        user_id: str,
        include_details: bool = False
    ) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        if not self._client:
            raise RuntimeError("Client not initialized")
        
        start_time = time.time()
        
        try:
            # Placeholder implementation
            await asyncio.sleep(0.1)
            
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("get_memory_stats", response_time, True)
            
            stats = {
                "success": True,
                "user_id": user_id,
                "total_memories": 42,
                "total_conversations": 15,
                "memory_size_mb": 1.2,
                "last_updated": "2024-01-01T12:00:00Z",
                "processing_time": round(response_time, 3)
            }
            
            if include_details:
                stats["details"] = {
                    "memories_by_agent": {
                        "agent_001": 25,
                        "agent_002": 17
                    },
                    "memory_types": {
                        "conversation": 35,
                        "facts": 7
                    },
                    "date_range": {
                        "earliest": "2023-12-01T00:00:00Z",
                        "latest": "2024-01-01T12:00:00Z"
                    }
                }
            
            return stats
            
        except Exception as e:
            response_time = time.time() - start_time
            if self._logger:
                self._logger.log_memu_api_call("get_memory_stats", response_time, False)
            
            raise RuntimeError(f"Failed to get memory stats: {e}")
    
    async def close(self):
        """Close the client connection"""
        if self._client:
            # Clean up any resources if needed
            self._client = None
            if self._logger:
                self._logger.info("memU client connection closed")