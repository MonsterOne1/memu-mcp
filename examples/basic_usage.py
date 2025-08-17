#!/usr/bin/env python3
"""
Basic usage examples for memU MCP Server tools

This script demonstrates how to use the memU MCP Server tools
programmatically (useful for testing and integration examples).
"""

import asyncio
import json
from pathlib import Path
import sys

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memu_mcp_server.config import Config
from memu_mcp_server.memu_client import MemuClientWrapper
from memu_mcp_server.tools import MemoryTools
from memu_mcp_server.logger import setup_logger


async def main():
    """Run basic usage examples"""
    
    print("=== memU MCP Server - Basic Usage Examples ===\n")
    
    # Load configuration
    try:
        config = Config()
        print(f"✓ Configuration loaded")
        print(f"  Server: {config.server_name} v{config.server_version}")
        print(f"  memU API: {config.memu_base_url}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        print("Please set MEMU_API_KEY environment variable")
        return
    
    # Setup logger
    logger = setup_logger(config.log_level)
    print(f"✓ Logger initialized (level: {config.log_level})")
    
    # Initialize memU client
    memu_client = MemuClientWrapper(config)
    try:
        await memu_client.initialize()
        print("✓ memU client initialized")
    except Exception as e:
        print(f"✗ memU client error: {e}")
        return
    
    # Initialize tools
    tools = MemoryTools(memu_client, logger)
    print("✓ Memory tools initialized\n")
    
    # Example 1: Memorize a conversation
    print("=== Example 1: Memorizing a Conversation ===")
    try:
        conversation = """
        User: What's the capital of France?
        Assistant: The capital of France is Paris. It's also the most populous city in France and serves as the country's political, economic, and cultural center.
        User: Tell me more about Paris.
        Assistant: Paris is known for its iconic landmarks like the Eiffel Tower, Notre-Dame Cathedral, and the Louvre Museum. It's often called the "City of Light" and is famous for its art, fashion, cuisine, and romantic atmosphere.
        """
        
        result = await tools.memorize_conversation({
            "conversation": conversation.strip(),
            "user_id": "example_user",
            "user_name": "Example User",
            "agent_id": "demo_assistant",
            "agent_name": "Demo Assistant"
        })
        
        print("✓ Conversation memorized successfully")
        print(f"  Memory ID: {result.get('memory_id', 'N/A')}")
        print(f"  Tokens processed: {result.get('tokens_processed', 'N/A')}")
        print(f"  Processing time: {result.get('processing_time', 'N/A')}s")
        
    except Exception as e:
        print(f"✗ Failed to memorize conversation: {e}")
    
    print()
    
    # Example 2: Retrieve memories
    print("=== Example 2: Retrieving Memories ===")
    try:
        result = await tools.retrieve_memory({
            "query": "capital of France",
            "user_id": "example_user",
            "limit": 5
        })
        
        print("✓ Memories retrieved successfully")
        print(f"  Total found: {result.get('total_found', 0)}")
        memories = result.get('memories', [])
        
        for i, memory in enumerate(memories[:3]):  # Show first 3
            print(f"  Memory {i+1}:")
            print(f"    ID: {memory.get('id', 'N/A')}")
            print(f"    Relevance: {memory.get('relevance_score', 'N/A')}")
            print(f"    Content: {memory.get('content', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"✗ Failed to retrieve memories: {e}")
    
    print()
    
    # Example 3: Search memories
    print("=== Example 3: Searching Memories ===")
    try:
        result = await tools.search_memory({
            "search_query": "Paris landmarks",
            "user_id": "example_user",
            "filters": {
                "agent_id": "demo_assistant"
            },
            "limit": 3
        })
        
        print("✓ Memory search completed")
        print(f"  Total results: {result.get('total_results', 0)}")
        results = result.get('results', [])
        
        for i, memory in enumerate(results):
            print(f"  Result {i+1}:")
            print(f"    ID: {memory.get('id', 'N/A')}")
            print(f"    Similarity: {memory.get('similarity_score', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Failed to search memories: {e}")
    
    print()
    
    # Example 4: Get memory statistics
    print("=== Example 4: Memory Statistics ===")
    try:
        result = await tools.get_memory_stats({
            "user_id": "example_user",
            "include_details": True
        })
        
        print("✓ Memory statistics retrieved")
        print(f"  Total memories: {result.get('total_memories', 0)}")
        print(f"  Total conversations: {result.get('total_conversations', 0)}")
        print(f"  Memory size: {result.get('memory_size_mb', 0)} MB")
        
        details = result.get('details', {})
        if details:
            print("  Memory breakdown:")
            for agent_id, count in details.get('memories_by_agent', {}).items():
                print(f"    {agent_id}: {count} memories")
        
    except Exception as e:
        print(f"✗ Failed to get memory statistics: {e}")
    
    print()
    
    # Example 5: Memory management (update/delete)
    print("=== Example 5: Memory Management ===")
    try:
        # This is a demonstration - in practice you'd use real memory IDs
        result = await tools.manage_memory({
            "action": "update",
            "memory_id": "demo_memory_001",
            "new_content": "Updated memory content with additional information",
            "user_id": "example_user"
        })
        
        print("✓ Memory update demonstration completed")
        print(f"  Message: {result.get('message', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Memory management failed: {e}")
    
    print()
    
    # Cleanup
    await memu_client.close()
    print("✓ Client connection closed")
    print("\n=== Examples completed successfully ===")


if __name__ == "__main__":
    asyncio.run(main())