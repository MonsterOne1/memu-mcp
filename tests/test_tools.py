"""Tests for memory tools"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from memu_mcp_server.tools import MemoryTools
from memu_mcp_server.memu_client import MemuClientWrapper
from memu_mcp_server.logger import MemuLogger


class TestMemoryTools:
    """Test memory tools functionality"""
    
    @pytest.fixture
    def mock_memu_client(self):
        """Create a mock memU client"""
        client = AsyncMock(spec=MemuClientWrapper)
        return client
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger"""
        logger = MagicMock(spec=MemuLogger)
        return logger
    
    @pytest.fixture
    def memory_tools(self, mock_memu_client, mock_logger):
        """Create memory tools instance with mocked dependencies"""
        return MemoryTools(mock_memu_client, mock_logger)
    
    @pytest.mark.asyncio
    async def test_memorize_conversation_success(self, memory_tools, mock_memu_client):
        """Test successful conversation memorization"""
        # Setup mock response
        mock_response = {
            "success": True,
            "message": "Conversation memorized successfully",
            "memory_id": "mem_001",
            "tokens_processed": 50,
            "processing_time": 0.234
        }
        mock_memu_client.memorize_conversation.return_value = mock_response
        
        # Test arguments
        arguments = {
            "conversation": "User: Hello! Assistant: Hi there!",
            "user_id": "test_user",
            "user_name": "Test User",
            "agent_id": "test_agent",
            "agent_name": "Test Agent"
        }
        
        # Call the tool
        result = await memory_tools.memorize_conversation(arguments)
        
        # Verify the call
        mock_memu_client.memorize_conversation.assert_called_once_with(
            conversation="User: Hello! Assistant: Hi there!",
            user_id="test_user",
            user_name="Test User",
            agent_id="test_agent",
            agent_name="Test Agent"
        )
        
        # Verify the result
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_memorize_conversation_missing_conversation(self, memory_tools):
        """Test memorize_conversation with missing conversation parameter"""
        arguments = {
            "user_id": "test_user"
        }
        
        with pytest.raises(ValueError, match="conversation is required"):
            await memory_tools.memorize_conversation(arguments)
    
    @pytest.mark.asyncio
    async def test_memorize_conversation_too_long(self, memory_tools):
        """Test memorize_conversation with conversation that's too long"""
        arguments = {
            "conversation": "x" * 100001,  # Exceed 100k character limit
            "user_id": "test_user"
        }
        
        with pytest.raises(ValueError, match="Conversation too long"):
            await memory_tools.memorize_conversation(arguments)
    
    @pytest.mark.asyncio
    async def test_memorize_conversation_defaults(self, memory_tools, mock_memu_client):
        """Test memorize_conversation with default values"""
        mock_response = {"success": True}
        mock_memu_client.memorize_conversation.return_value = mock_response
        
        arguments = {
            "conversation": "Test conversation"
        }
        
        await memory_tools.memorize_conversation(arguments)
        
        # Verify default values were used
        mock_memu_client.memorize_conversation.assert_called_once_with(
            conversation="Test conversation",
            user_id="default_user",
            user_name="User",
            agent_id="default_agent",
            agent_name="Assistant"
        )
    
    @pytest.mark.asyncio
    async def test_retrieve_memory_success(self, memory_tools, mock_memu_client):
        """Test successful memory retrieval"""
        mock_response = {
            "success": True,
            "memories": [
                {
                    "id": "mem_001",
                    "content": "Test memory",
                    "relevance_score": 0.85
                }
            ],
            "total_found": 1
        }
        mock_memu_client.retrieve_memory.return_value = mock_response
        
        arguments = {
            "query": "test query",
            "user_id": "test_user",
            "limit": 5
        }
        
        result = await memory_tools.retrieve_memory(arguments)
        
        mock_memu_client.retrieve_memory.assert_called_once_with(
            query="test query",
            user_id="test_user",
            limit=5
        )
        
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_retrieve_memory_missing_query(self, memory_tools):
        """Test retrieve_memory with missing query parameter"""
        arguments = {
            "user_id": "test_user"
        }
        
        with pytest.raises(ValueError, match="query is required"):
            await memory_tools.retrieve_memory(arguments)
    
    @pytest.mark.asyncio
    async def test_retrieve_memory_invalid_limit(self, memory_tools):
        """Test retrieve_memory with invalid limit values"""
        # Test with limit too low
        arguments = {
            "query": "test",
            "limit": 0
        }
        
        with pytest.raises(ValueError, match="limit must be an integer between 1 and 50"):
            await memory_tools.retrieve_memory(arguments)
        
        # Test with limit too high
        arguments = {
            "query": "test",
            "limit": 51
        }
        
        with pytest.raises(ValueError, match="limit must be an integer between 1 and 50"):
            await memory_tools.retrieve_memory(arguments)
        
        # Test with non-integer limit
        arguments = {
            "query": "test",
            "limit": "invalid"
        }
        
        with pytest.raises(ValueError, match="limit must be an integer between 1 and 50"):
            await memory_tools.retrieve_memory(arguments)
    
    @pytest.mark.asyncio
    async def test_search_memory_success(self, memory_tools, mock_memu_client):
        """Test successful memory search"""
        mock_response = {
            "success": True,
            "results": [
                {
                    "id": "mem_001",
                    "content": "Search result",
                    "similarity_score": 0.92
                }
            ]
        }
        mock_memu_client.search_memory.return_value = mock_response
        
        arguments = {
            "search_query": "search test",
            "user_id": "test_user",
            "filters": {"agent_id": "test_agent"},
            "limit": 3
        }
        
        result = await memory_tools.search_memory(arguments)
        
        mock_memu_client.search_memory.assert_called_once_with(
            search_query="search test",
            user_id="test_user",
            filters={"agent_id": "test_agent"},
            limit=3
        )
        
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_search_memory_missing_query(self, memory_tools):
        """Test search_memory with missing search_query parameter"""
        arguments = {
            "user_id": "test_user"
        }
        
        with pytest.raises(ValueError, match="search_query is required"):
            await memory_tools.search_memory(arguments)
    
    @pytest.mark.asyncio
    async def test_manage_memory_update_success(self, memory_tools, mock_memu_client):
        """Test successful memory update"""
        mock_response = {
            "success": True,
            "message": "Memory updated successfully"
        }
        mock_memu_client.update_memory.return_value = mock_response
        
        arguments = {
            "action": "update",
            "memory_id": "mem_001",
            "new_content": "Updated content",
            "user_id": "test_user"
        }
        
        result = await memory_tools.manage_memory(arguments)
        
        mock_memu_client.update_memory.assert_called_once_with(
            memory_id="mem_001",
            new_content="Updated content",
            user_id="test_user"
        )
        
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_manage_memory_delete_success(self, memory_tools, mock_memu_client):
        """Test successful memory deletion"""
        mock_response = {
            "success": True,
            "message": "Memory deleted successfully"
        }
        mock_memu_client.delete_memory.return_value = mock_response
        
        arguments = {
            "action": "delete",
            "memory_id": "mem_001",
            "user_id": "test_user"
        }
        
        result = await memory_tools.manage_memory(arguments)
        
        mock_memu_client.delete_memory.assert_called_once_with(
            memory_id="mem_001",
            user_id="test_user"
        )
        
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_manage_memory_invalid_action(self, memory_tools):
        """Test manage_memory with invalid action"""
        arguments = {
            "action": "invalid_action",
            "memory_id": "mem_001"
        }
        
        with pytest.raises(ValueError, match="action must be 'update' or 'delete'"):
            await memory_tools.manage_memory(arguments)
    
    @pytest.mark.asyncio
    async def test_manage_memory_missing_memory_id(self, memory_tools):
        """Test manage_memory with missing memory_id"""
        arguments = {
            "action": "update"
        }
        
        with pytest.raises(ValueError, match="memory_id is required"):
            await memory_tools.manage_memory(arguments)
    
    @pytest.mark.asyncio
    async def test_manage_memory_update_missing_content(self, memory_tools):
        """Test manage_memory update without new_content"""
        arguments = {
            "action": "update",
            "memory_id": "mem_001"
        }
        
        with pytest.raises(ValueError, match="new_content is required for update action"):
            await memory_tools.manage_memory(arguments)
    
    @pytest.mark.asyncio
    async def test_get_memory_stats_success(self, memory_tools, mock_memu_client):
        """Test successful memory statistics retrieval"""
        mock_response = {
            "success": True,
            "total_memories": 42,
            "total_conversations": 15,
            "memory_size_mb": 1.2
        }
        mock_memu_client.get_memory_stats.return_value = mock_response
        
        arguments = {
            "user_id": "test_user",
            "include_details": True
        }
        
        result = await memory_tools.get_memory_stats(arguments)
        
        mock_memu_client.get_memory_stats.assert_called_once_with(
            user_id="test_user",
            include_details=True
        )
        
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_get_memory_stats_invalid_include_details(self, memory_tools):
        """Test get_memory_stats with invalid include_details value"""
        arguments = {
            "include_details": "invalid"
        }
        
        with pytest.raises(ValueError, match="include_details must be a boolean"):
            await memory_tools.get_memory_stats(arguments)