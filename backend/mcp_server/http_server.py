# backend/mcp_server/http_server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.mcp_server import mcp
import traceback
from backend.mcp_clients import demo_agent





# ✅ Import all tools so they register
import backend.mcp_server.tools.price
import backend.mcp_server.tools.volume
import backend.mcp_server.tools.tickers
import backend.mcp_server.tools.anomalies
import backend.mcp_server.tools.sec_filings
import backend.mcp_server.tools.charts
import backend.mcp_server.tools.alerts


app = FastAPI(title="MCP HTTP API")

# 🔑 Allow frontend (localhost:5173) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ToolRequest(BaseModel):
    args: dict = {}


@app.post("/tools/{tool_name}")
async def run_tool(tool_name: str, req: ToolRequest):
    """
    Run an MCP tool by name.
    All exceptions are caught and returned as JSON instead of FastAPI's {"detail": ...}.
    """
    try:
        tool = mcp.tools.get(tool_name)
        if not tool:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(mcp.tools.keys()),
            }

        result = tool(**req.args)
        return result

    except Exception as e:
        # Print full traceback to backend logs
        traceback.print_exc()

        # Return structured JSON to frontend
        return {
            "error": str(e),
            "type": e.__class__.__name__,
            "traceback": traceback.format_exc().splitlines()[-5:],  # last 5 lines for context
        }


# 👇 Debug: print registered tools on startup
print("✅ Registered tools:", list(mcp.tools.keys()), flush=True)

app.include_router(demo_agent.router, prefix="/mcp", tags=["MCP Agent"])






