#!/usr/bin/env python3
"""
Example MCP client for testing memU MCP Server

This demonstrates how to connect to and use the memU MCP Server
from a client application.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Example MCP client usage"""
    
    print("=== memU MCP Server Client Example ===\n")
    
    # Server command - adjust path as needed
    server_script = Path(__file__).parent.parent / "src" / "memu_mcp_server" / "main.py"
    
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env={
            "MEMU_API_KEY": "your_api_key_here",  # Replace with actual API key
            "LOG_LEVEL": "INFO"
        }
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                # Initialize the session
                await session.initialize()
                print("✓ Connected to memU MCP Server")
                
                # List available tools
                tools = await session.list_tools()
                print(f"✓ Available tools: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                print()
                
                # Example 1: Memorize a conversation
                print("=== Memorizing Conversation ===")
                try:
                    result = await session.call_tool("memorize_conversation", {
                        "conversation": "User: Hello! Assistant: Hi there! How can I help you today?",
                        "user_id": "client_test_user",
                        "user_name": "Test User",
                        "agent_id": "test_assistant",
                        "agent_name": "Test Assistant"
                    })
                    
                    print("✓ Conversation memorized")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            response_data = json.loads(content.text)
                            print(f"  Memory ID: {response_data.get('memory_id', 'N/A')}")
                            print(f"  Processing time: {response_data.get('processing_time', 'N/A')}s")
                    
                except Exception as e:
                    print(f"✗ Failed to memorize conversation: {e}")
                
                print()
                
                # Example 2: Retrieve memories
                print("=== Retrieving Memories ===")
                try:
                    result = await session.call_tool("retrieve_memory", {
                        "query": "greeting conversation",
                        "user_id": "client_test_user",
                        "limit": 5
                    })
                    
                    print("✓ Memories retrieved")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            response_data = json.loads(content.text)
                            memories = response_data.get('memories', [])
                            print(f"  Found {len(memories)} memories")
                    
                except Exception as e:
                    print(f"✗ Failed to retrieve memories: {e}")
                
                print()
                
                # Example 3: Get memory statistics
                print("=== Memory Statistics ===")
                try:
                    result = await session.call_tool("get_memory_stats", {
                        "user_id": "client_test_user",
                        "include_details": True
                    })
                    
                    print("✓ Statistics retrieved")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            response_data = json.loads(content.text)
                            print(f"  Total memories: {response_data.get('total_memories', 0)}")
                            print(f"  Total conversations: {response_data.get('total_conversations', 0)}")
                    
                except Exception as e:
                    print(f"✗ Failed to get statistics: {e}")
                
                print()
                
                # Example 4: Search memories
                print("=== Searching Memories ===")
                try:
                    result = await session.call_tool("search_memory", {
                        "search_query": "hello greeting",
                        "user_id": "client_test_user",
                        "limit": 3
                    })
                    
                    print("✓ Search completed")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            response_data = json.loads(content.text)
                            results = response_data.get('results', [])
                            print(f"  Found {len(results)} matching memories")
                    
                except Exception as e:
                    print(f"✗ Search failed: {e}")
                
                print()
                print("=== Client example completed ===")
    
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("Make sure:")
        print("  1. MEMU_API_KEY is set correctly")
        print("  2. memU service is accessible")
        print("  3. Server dependencies are installed")


if __name__ == "__main__":
    # Check if mcp is installed
    try:
        import mcp
    except ImportError:
        print("Error: MCP client library not found")
        print("Install with: pip install mcp")
        sys.exit(1)
    
    asyncio.run(main())