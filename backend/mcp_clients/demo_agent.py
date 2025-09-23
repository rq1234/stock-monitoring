import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.mcp_clients.openai_client import run_agent

# ✅ FastAPI router
router = APIRouter()

class AgentRequest(BaseModel):
    query: str
    structured: bool = False  # optional flag to request JSON output

@router.post("/agent")
async def ask_agent(payload: AgentRequest):
    """
    Frontend → /mcp/agent
    Example body:
    {
        "query": "show me last 10 days of DSY volume",
        "structured": true
    }

    Response:
    {
        "answer": "...or structured JSON..."
    }
    """
    try:
        answer = await run_agent(payload.query, structured=payload.structured)

        # 🔧 Handle error dicts
        if isinstance(answer, dict) and answer.get("type") == "error":
            raise HTTPException(status_code=500, detail=answer["content"])

        # 🔧 Try parsing JSON if structured
        if payload.structured and isinstance(answer, str):
            try:
                parsed = json.loads(answer)
                return {"answer": parsed}
            except Exception:
                # Fall back to raw string if not valid JSON
                return {"answer": answer}

        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"⚠️ MCP agent error: {str(e)}")




# 🚀 API endpoint
@router.post("/agent")
async def ask_agent(payload: AgentRequest):
    """
    Frontend → /mcp/agent
    Body: { "query": "Tell me about DSY", "structured": false }
    Response: { "answer": ... }
    """
    answer = await run_agent(payload.query, structured=payload.structured)

    if isinstance(answer, dict) and answer.get("type") == "error":
        raise HTTPException(status_code=500, detail=answer["content"])

    return {"answer": answer}









    





