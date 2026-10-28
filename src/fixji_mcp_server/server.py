from fastmcp import FastMCP
from .tools import register_all_mcps
from .config import settings

mcp = FastMCP()

register_all_mcps(mcp=mcp)

def main():
    mcp.run(transport = 'streamable-http', host = settings.MCP_HOST, port = settings.MCP_PORT)

if __name__ == "__main__":
    main()