from langchain.mcp.adapter import MCPAdapter
from .config import settings

MCP_URL = settings.MCP_URL

async def load_tools(client):
    async with MCPAdapter(client) as adapter:
        tools = await adapter.list_tools()

    return tools
