# backend/mcp_server/mcp_server.py
import sys, traceback
from backend.mcp_server import mcp  # shared MCP instance

# Import all tools so their @mcp.tool() decorators register
import backend.mcp_server.tools.volume
import backend.mcp_server.tools.price
import backend.mcp_server.tools.sec_filings
import backend.mcp_server.tools.anomalies
import backend.mcp_server.tools.charts
import backend.mcp_server.tools.tickers

if __name__ == "__main__":
    print("🚀 Starting MCP server (stdio transport)...", file=sys.stderr, flush=True)
    try:
        # stdio transport for LLM integrations
        mcp.run(transport="stdio")
    except Exception as e:
        print("💥 MCP server crashed:", e, file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)










