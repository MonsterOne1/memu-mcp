# memU MCP Server

A Model Context Protocol (MCP) server that provides access to memU AI memory framework capabilities.

## Overview

This MCP server wraps the memU AI memory framework, enabling AI applications to use advanced memory management features through the standardized MCP protocol.

## Features

- **Memory Storage**: Store and organize conversation memories
- **Smart Retrieval**: Retrieve relevant memories using semantic search
- **Memory Management**: Update, delete, and organize memory data
- **Statistics**: Get insights into memory usage and performance
- **Multi-user Support**: Handle multiple users and AI agents

## Quick Start

### Prerequisites

- Python 3.8+
- memU API key (get one at https://app.memu.so/api-key/)

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd memu-mcp-server

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export MEMU_API_KEY="your-memu-api-key"

# Run the server
python -m memu_mcp_server.main
```

### Render Deployment

```bash
# Deploy to Render (using Blueprint)
1. Connect your GitHub repository to Render
2. Render will automatically detect render.yaml
3. Set MEMU_API_KEY as a secret in Render dashboard
4. Deploy!

# Or use the Render CLI
render deploy
```

### Usage Examples

```bash
# Local development
python -m memu_mcp_server.main --log-level DEBUG

# Render mode (for testing locally)
python -m memu_mcp_server.main --render-mode

# With custom configuration
python -m memu_mcp_server.main --config config/server.json

# API server (for health checks)
python -m memu_mcp_server.api --host 0.0.0.0 --port 8080
```

## Configuration

- **Local Development**: See `config/example.json` for configuration options
- **Render Deployment**: See [Render Deployment Guide](docs/RENDER_DEPLOYMENT.md)
- **Environment Variables**: See [Environment Variables Guide](docs/ENVIRONMENT_VARIABLES.md)

## Available Tools

- `memorize_conversation`: Store conversation memories
- `retrieve_memory`: Retrieve relevant memories
- `search_memory`: Search memories by query
- `manage_memory`: Update or delete memories
- `get_memory_stats`: Get memory statistics

## Documentation

- [API Reference](docs/API.md) - Detailed API documentation
- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [Render Deployment](docs/RENDER_DEPLOYMENT.md) - Deploy to Render platform
- [Environment Variables](docs/ENVIRONMENT_VARIABLES.md) - Configuration reference

## Deployment Options

### Local Development
```bash
python -m memu_mcp_server.main
```

### Docker
```bash
docker-compose up memu-mcp-server
```

### Render (Cloud)
Use the included `render.yaml` Blueprint for one-click deployment to Render.

### Claude Desktop Integration
Add to your Claude Desktop configuration:
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

## Health Monitoring

When deployed with the Web Service component, monitoring endpoints are available:

- `GET /health` - Health check
- `GET /status` - Detailed status
- `GET /metrics` - Performance metrics
- `GET /info` - Service information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Check the `docs/` directory
- Email: support@example.com

## License

MIT License