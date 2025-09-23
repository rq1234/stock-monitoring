# backend/workflows/spac_workflow.py
import logging
from datetime import date
from typing import List, Dict, Any
from langgraph.graph import StateGraph, END, START

from backend.agents.data_agent import fetch_and_store_daily_data
from backend.agents.analyzer_agent import run_analyzer_agent
from backend.agents.lifecycle_agent import run_lifecycle_agent
from backend.agents.risk_agent import run_risk_agent
from backend.agents.reporter_agent import run_reporter_agent

# ---- Configure Logging ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ---- Define Workflow State ----
class State(dict):
    tickers: List[str]
    anomalies: List[Dict[str, Any]]

# ---- LangGraph Workflow ----
workflow = StateGraph(State)

# Data Agent Node
def data_node(state: State) -> State:
    logging.info("📥 Running Data Agent...")
    tickers_state = fetch_and_store_daily_data()
    state["tickers"] = tickers_state.get("tickers", [])
    logging.info(f"✅ Data Agent finished: {len(state['tickers'])} tickers updated")
    return state

# Analyzer Node
def analyzer_node(state: State) -> State:
    logging.info("🔍 Running Analyzer Agent...")
    state = run_analyzer_agent(state)
    logging.info(f"✅ Analyzer finished: {len(state.get('anomalies', []))} anomalies found so far")
    return state

# Lifecycle Node
def lifecycle_node(state: State) -> State:
    logging.info("📆 Running Lifecycle Agent...")
    state = run_lifecycle_agent(state)
    logging.info(f"✅ Lifecycle finished: {len(state.get('anomalies', []))} anomalies found so far")
    return state

# Risk Node
def risk_node(state: State) -> State:
    logging.info("⚠️ Running Risk Agent...")
    state = run_risk_agent(state)
    logging.info(f"✅ Risk finished: {len(state.get('anomalies', []))} anomalies found so far")
    return state

# Reporter Node
def reporter_node(state: State) -> State:
    logging.info("📝 Running Reporter Agent...")
    state = run_reporter_agent(state)  # ✅ always queries Supabase for today's anomalies
    logging.info("✅ Reporter finished: Report saved, sent to Discord, and logged")
    return state

# ---- Register Nodes ----
workflow.add_node("data", data_node)
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("lifecycle", lifecycle_node)
workflow.add_node("risk", risk_node)
workflow.add_node("reporter", reporter_node)

# ---- Define Edges ----
workflow.add_edge(START, "data")
workflow.add_edge("data", "analyzer")
workflow.add_edge("analyzer", "lifecycle")
workflow.add_edge("lifecycle", "risk")
workflow.add_edge("risk", "reporter")
workflow.add_edge("reporter", END)

# ---- Compile App ----
app = workflow.compile()




