# backend/main.py
import importlib
import pkgutil
from fastapi import FastAPI, APIRouter, Request, Body
from fastapi.middleware.cors import CORSMiddleware

from backend.mcp_server import mcp
import backend.mcp_server.tools as tools_pkg

# Initialize FastAPI app
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:3000"] if frontend only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-load all modules in backend/mcp_server/tools
for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
    importlib.import_module(f"{tools_pkg.__name__}.{module_name}")

# Router for tools
router = APIRouter()

@router.post("/tools/{tool_name}")
async def run_tool(tool_name: str, payload: dict = Body(...)):
    # frontend sends { "args": {...} }
    data = payload.get("args", payload) if payload else {}

    tool = mcp.tools.get(tool_name)
    if not tool:
        return {"error": f"Tool '{tool_name}' not found"}

    try:
        return tool(**data) if data else tool()
    except Exception as e:
        return {"error": str(e)}


# Register router with app
app.include_router(router)

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "SPAC Tracker backend is live 🚀",
        "endpoints": ["/tools/{tool_name}"]
    }


