# MCP (Model Context Protocol) Agents

This directory contains AI agents that integrate with external data sources and tools using the Model Context Protocol (MCP). MCP allows agents to access real-time data, external APIs, and custom tools through a standardized interface.

## 🚀 What is MCP?

Model Context Protocol (MCP) is a standard for connecting AI models to external data sources and tools. It enables agents to:

- Access real-time data from external services
- Interact with databases, APIs, and custom tools
- Maintain context across conversations
- Execute actions in the real world

## 📁 Files in this Directory

| File | Description |
|------|-------------|
| `mcp.py` | Main MCP-enabled agent that can access external tools |
| `stdio.py` | Example MCP server that provides current time information |
| `requirements.txt` | MCP-specific dependencies |

## 🛠️ Available MCP Agents

### Time Agent (`mcp.py`)
A voice agent that can access real-time information through MCP servers.

**Features:**
- Connects to MCP servers via STDIO and HTTP
- Can provide current time and date information
- Extensible to other data sources and tools
- Uses Google Gemini for voice interactions

**Usage:**
```bash
# Run with Docker
./run.sh mcp

# Run directly
python mcp/mcp.py
```

## 🔧 MCP Server Examples

### Current Time Server (`stdio.py`)
A simple MCP server that provides current time information.

**Features:**
- Returns formatted current time and date
- Uses STDIO transport for local communication
- Easy to extend with additional time-related functions

**Usage:**
```bash
# Run the MCP server directly
python mcp/stdio.py
```

## 🏗️ Creating Custom MCP Servers

### 1. Basic MCP Server Structure
```python
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("YourServerName")

@mcp.tool()
def your_function() -> str:
    """Description of what your function does"""
    # Your implementation here
    return "Result"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 2. HTTP MCP Server
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HTTPExample")

@mcp.tool()
def call_external_api() -> str:
    """Call an external API"""
    import requests
    response = requests.get("https://api.example.com/data")
    return response.json()

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
```

## 🔌 Integrating MCP Servers with Agents

### STDIO Integration
```python
from videosdk.agents import MCPServerStdio

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="Your agent instructions",
            mcp_servers=[
                MCPServerStdio(
                    command="python",
                    args=["path/to/your/mcp_server.py"],
                    client_session_timeout_seconds=30
                )
            ]
        )
```

### HTTP Integration
```python
from videosdk.agents import MCPServerHTTP

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="Your agent instructions",
            mcp_servers=[
                MCPServerHTTP(
                    url="https://your-mcp-service.com/api/mcp",
                    client_session_timeout_seconds=30
                )
            ]
        )
```

## 📋 Prerequisites

1. **Install MCP dependencies:**
   ```bash
   pip install fastmcp
   ```

2. **Set up your environment:**
   ```bash
   cp env.sample .env
   # Add your API keys to .env
   ```

3. **Generate a meeting ID:**
   ```bash
   cd pythonSDK
   python main.py
   ```

## 🎯 Use Cases

- **Real-time Data Access**: Stock prices, weather, news
- **External API Integration**: CRM systems, databases, web services
- **Custom Tools**: File operations, system commands, calculations
- **Multi-Service Orchestration**: Combining multiple data sources

## 🔍 Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   - Check the path in your agent configuration
   - Ensure the MCP server file exists and is executable

2. **Connection Timeout**
   - Increase `client_session_timeout_seconds`
   - Check if the MCP server is running correctly

3. **Import Errors**
   - Install required dependencies: `pip install fastmcp`
   - Check Python path and virtual environment

### Debugging Tips

1. **Test MCP Server Independently**
   ```bash
   python mcp/stdio.py
   ```

2. **Check Agent Logs**
   - Look for MCP connection messages
   - Verify server startup and tool registration

3. **Validate Configuration**
   - Ensure meeting ID is set correctly
   - Check API keys in `.env` file

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Library](https://github.com/fastmcp/fastmcp)
- [VideoSDK MCP Integration](https://docs.videosdk.live/ai_agents/mcp)

## 🤝 Contributing

To add new MCP servers or agents:

1. Create your MCP server following the examples above
2. Add any new dependencies to `requirements.txt`
3. Update this README with usage instructions
4. Test thoroughly before submitting

The MCP integration makes your agents more powerful by connecting them to the real world! 