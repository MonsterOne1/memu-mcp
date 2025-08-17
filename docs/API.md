# memU MCP Server API Documentation

This document describes the tools and interfaces provided by the memU MCP Server.

## Overview

The memU MCP Server provides 5 main tools for memory management:

- `memorize_conversation`: Store conversations in memory
- `retrieve_memory`: Retrieve relevant memories
- `search_memory`: Search memories semantically
- `manage_memory`: Update or delete memories
- `get_memory_stats`: Get memory statistics

## Tools Reference

### memorize_conversation

Store a conversation in memU memory for future reference.

**Parameters:**
- `conversation` (string, required): The conversation text to memorize
- `user_id` (string, optional): Unique identifier for the user (default: "default_user")
- `user_name` (string, optional): Display name for the user (default: "User")
- `agent_id` (string, optional): Unique identifier for the AI agent (default: "default_agent")
- `agent_name` (string, optional): Display name for the AI agent (default: "Assistant")

**Response:**
```json
{
  "success": true,
  "message": "Conversation memorized successfully",
  "memory_id": "mem_001",
  "tokens_processed": 150,
  "processing_time": 0.234
}
```

**Example:**
```json
{
  "conversation": "User: What's the weather like? Assistant: I don't have access to current weather data.",
  "user_id": "user123",
  "user_name": "John Doe",
  "agent_id": "assistant1",
  "agent_name": "Weather Assistant"
}
```

### retrieve_memory

Retrieve relevant memories based on a query.

**Parameters:**
- `query` (string, required): Query to search for relevant memories
- `user_id` (string, optional): User ID to search memories for (default: "default_user")
- `limit` (integer, optional): Maximum number of memories to retrieve (default: 10, max: 50)

**Response:**
```json
{
  "success": true,
  "memories": [
    {
      "id": "mem_001",
      "content": "Example memory content",
      "relevance_score": 0.85,
      "timestamp": "2024-01-01T12:00:00Z",
      "user_id": "user123",
      "metadata": {
        "conversation_id": "conv_001",
        "agent_id": "agent_001"
      }
    }
  ],
  "total_found": 1,
  "query": "weather information",
  "processing_time": 0.156
}
```

### search_memory

Search memories using semantic similarity.

**Parameters:**
- `search_query` (string, required): Text to search for in memories
- `user_id` (string, optional): User ID to search memories for (default: "default_user")
- `filters` (object, optional): Additional filters for search
  - `date_from` (string): Start date filter (ISO format)
  - `date_to` (string): End date filter (ISO format)
  - `agent_id` (string): Filter by agent ID
- `limit` (integer, optional): Maximum number of results (default: 10, max: 50)

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "mem_002",
      "content": "Memory content matching search query",
      "similarity_score": 0.92,
      "timestamp": "2024-01-01T12:00:00Z",
      "user_id": "user123"
    }
  ],
  "total_results": 1,
  "search_query": "weather forecast",
  "filters_applied": {},
  "processing_time": 0.089
}
```

### manage_memory

Update or delete specific memories.

**Parameters:**
- `action` (string, required): Action to perform ("update" or "delete")
- `memory_id` (string, required): ID of the memory to manage
- `new_content` (string, required for update): New content for update action
- `user_id` (string, optional): User ID who owns the memory (default: "default_user")

**Response for Update:**
```json
{
  "success": true,
  "message": "Memory updated successfully",
  "memory_id": "mem_001",
  "updated_content": "New content here",
  "processing_time": 0.045
}
```

**Response for Delete:**
```json
{
  "success": true,
  "message": "Memory deleted successfully",
  "memory_id": "mem_001",
  "processing_time": 0.032
}
```

### get_memory_stats

Get statistics about stored memories.

**Parameters:**
- `user_id` (string, optional): User ID to get stats for (default: "default_user")
- `include_details` (boolean, optional): Include detailed breakdown (default: false)

**Response:**
```json
{
  "success": true,
  "user_id": "user123",
  "total_memories": 42,
  "total_conversations": 15,
  "memory_size_mb": 1.2,
  "last_updated": "2024-01-01T12:00:00Z",
  "processing_time": 0.067,
  "details": {
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
}
```

## Error Handling

All tools return error responses in the following format when an error occurs:

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ValidationError|ConnectionError|InternalError",
  "processing_time": 0.012
}
```

## Rate Limits

- 60 requests per minute per user
- 1000 requests per hour per user
- Memory storage limited to 100,000 characters per conversation

## Authentication

The server requires a valid memU API key configured via environment variables or configuration file.