# backend/main.py
import importlib
import pkgutil
import json
from fastapi import FastAPI, APIRouter, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.mcp_server import mcp
import backend.mcp_server.tools as tools_pkg
from backend.mcp_clients.openai_client import run_agent


# -----------------------------
# Models
# -----------------------------
class AgentQuery(BaseModel):
    query: str


# -----------------------------
# FastAPI Setup
# -----------------------------
app = FastAPI(title="MCP Agent API", version="2.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-load all MCP tools dynamically
for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
    importlib.import_module(f"{tools_pkg.__name__}.{module_name}")

router = APIRouter()


# -----------------------------
# Generic Tool Endpoint
# -----------------------------
@router.post("/tools/{tool_name}")
async def run_tool(tool_name: str, payload: dict = Body(...)):
    """Generic wrapper for any MCP tool."""
    data = payload.get("args", payload) if payload else {}
    tool = mcp.tools.get(tool_name)

    if not tool:
        return {"error": f"Tool '{tool_name}' not found"}

    try:
        return tool(**data) if data else tool()
    except Exception as e:
        return {"error": str(e)}


app.include_router(router)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "📈 MCP Agent backend is live",
        "endpoints": ["/tools/{tool_name}", "/mcp/agent"],
    }


# -----------------------------
# Helper: Detect ticker
# -----------------------------
async def extract_ticker(user_query: str) -> str | None:
    """Try to extract a valid ticker from query, fallback to LLM reasoning."""
    words = user_query.split()
    candidates = [w.upper() for w in words if len(w) <= 5 and w.isalpha()]

    if candidates:
        return candidates[-1]

    # 🧠 Fallback to LLM reasoning
    prompt = f"""
    Extract the stock ticker symbol (like AAPL, TSLA, etc.) from this query: '{user_query}'.
    If none exists, reply 'None' only.
    """
    result = await run_agent(prompt, structured=False)
    if isinstance(result, str) and result.strip().upper() != "NONE":
        return result.strip().upper()

    return None


# -----------------------------
# Helper: Summarize results
# -----------------------------
async def summarize_result(result: dict, context: str) -> str:
    """Use LLM to summarize structured tool output into readable text."""
    prompt = f"""
    You are a financial assistant. Summarize the following {context} data
    into 2–3 sentences that are clear and informative for an investor.
    If numeric data is given, highlight the key insights.

    Data:
    {json.dumps(result, indent=2)}
    """
    summary = await run_agent(prompt, structured=False)
    return summary


# -----------------------------
# MCP AGENT ENDPOINT
# -----------------------------
@app.post("/mcp/agent")
async def mcp_agent(query: AgentQuery):
    """Reasoning agent for MCP demo."""
    user_query = query.query.lower().strip()
    ticker = await extract_ticker(user_query)

    # 1️⃣ Stock Price Queries
    if any(word in user_query for word in ["price", "stock", "value", "worth"]):
        if ticker:
            tool = mcp.tools.get("get_stock_price")
            res = tool(ticker=ticker, period="1mo", interval="1d")
            if "error" not in res:
                summary = await summarize_result(res, "stock price")
                return {"answer": summary, "data": res}
            return {"answer": res}
        return {"answer": "⚠️ Could not detect a ticker symbol."}

    # 2️⃣ Volume Queries
    if "volume" in user_query:
        if ticker:
            tool = mcp.tools.get("get_volume_history")
            res = tool(ticker=ticker, days=30)
            summary = await summarize_result(res, "trading volume")
            return {"answer": summary, "data": res}
        return {"answer": "⚠️ Please specify a ticker for volume analysis."}

    # 3️⃣ Filings Queries
    if any(word in user_query for word in ["filing", "10-k", "8-k", "report"]):
        if ticker:
            tool = mcp.tools.get("get_filings")
            res = tool(ticker=ticker, form_types=["8-K"], limit=3, summarize=True)
            return {"answer": res}
        return {"answer": "⚠️ Please provide a ticker to fetch filings."}

    # 4️⃣ List Available Tickers
    if "list" in user_query:
        tool = mcp.tools.get("list_tickers")
        return {"answer": tool()}

    # 5️⃣ Anomaly Detection
    if any(word in user_query for word in ["anomaly", "spike", "unusual"]):
        if ticker:
            tool = mcp.tools.get("detect_anomalies")
            res = tool(ticker=ticker)
            summary = await summarize_result(res, "anomaly detection")
            return {"answer": summary, "data": res}
        return {"answer": "⚠️ Please provide a ticker for anomaly checking."}

    # 6️⃣ Fallback → Let LLM interpret any other financial question
    try:
        result = await run_agent(query.query, structured=False)
        return {"answer": result}
    except Exception as e:
        return {"answer": f"⚠️ MCP LLM fallback failed: {str(e)}"}





