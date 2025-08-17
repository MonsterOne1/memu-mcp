# Setup Guide for memU MCP Server

This guide will help you set up and configure the memU MCP Server.

## Prerequisites

- Python 3.8 or higher
- memU API key (sign up at https://app.memu.so/)
- Git (for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd memu-mcp-server
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install in Development Mode (Optional)

```bash
pip install -e .
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your settings:

```env
# Required
MEMU_API_KEY=your_memu_api_key_here

# Optional (defaults shown)
MEMU_BASE_URL=https://api.memu.so
MCP_SERVER_NAME=memu-mcp-server
MCP_SERVER_VERSION=0.1.0
LOG_LEVEL=INFO
DEFAULT_USER_ID=default_user
DEFAULT_AGENT_ID=default_agent
MAX_CONVERSATION_LENGTH=8000
MEMORY_RETENTION_DAYS=30
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
ALLOWED_ORIGINS=*
API_TIMEOUT=30
```

### Configuration File (Alternative)

You can also use a JSON configuration file:

```bash
cp config/example.json config/local.json
```

Edit `config/local.json` with your settings.

### Getting a memU API Key

1. Go to https://app.memu.so/
2. Sign up for an account
3. Navigate to API Keys section
4. Generate a new API key
5. Copy the key to your configuration

## Running the Server

### Basic Usage

```bash
python -m memu_mcp_server.main
```

### With Custom Configuration

```bash
python -m memu_mcp_server.main --config config/local.json
```

### With Custom Log Level

```bash
python -m memu_mcp_server.main --log-level DEBUG
```

### As Installed Package

If you installed with `pip install -e .`:

```bash
memu-mcp-server
```

## MCP Client Integration

### Claude Desktop Integration

Add the server to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "memu-memory": {
      "command": "python",
      "args": ["-m", "memu_mcp_server.main"],
      "env": {
        "MEMU_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Other MCP Clients

The server implements the standard MCP protocol and should work with any compliant client.

## Verification

### Test the Installation

```bash
# Run with debug logging to see detailed output
python -m memu_mcp_server.main --log-level DEBUG
```

### Check Tool Availability

When connected to an MCP client, you should see these tools available:
- memorize_conversation
- retrieve_memory
- search_memory
- manage_memory
- get_memory_stats

## Troubleshooting

### Common Issues

1. **"MEMU_API_KEY not found"**
   - Ensure your API key is set in `.env` or configuration file
   - Check that the file is in the correct location

2. **"Connection failed"**
   - Verify your API key is valid
   - Check network connectivity
   - Ensure memU service is accessible

3. **"Module not found"**
   - Make sure you've activated the virtual environment
   - Install dependencies with `pip install -r requirements.txt`

### Debug Mode

Run with debug logging for detailed information:

```bash
python -m memu_mcp_server.main --log-level DEBUG
```

### Log Files

Logs are output to stderr and can be redirected:

```bash
python -m memu_mcp_server.main 2> server.log
```

## Security Considerations

- Keep your memU API key secure
- Don't commit API keys to version control
- Use environment variables or secure configuration management
- Consider network security when deploying

## Performance Tuning

### Memory Usage

- Adjust `MAX_CONVERSATION_LENGTH` based on your needs
- Monitor memory usage with longer conversations

### Rate Limiting

- Adjust rate limits based on your memU plan
- Monitor API usage to avoid hitting limits

### Logging

- Use `INFO` level for production
- Use `DEBUG` only for development

## Next Steps

- Read the [API Documentation](API.md) for detailed tool usage
- Check out [examples](../examples/) for integration samples
- Review [troubleshooting](TROUBLESHOOTING.md) for common issues