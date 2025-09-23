# backend/agents/tools.py
from langchain.agents import tool
from backend.agents.data_agent import fetch_and_store_daily_data
from backend.agents.analyzer_agent import run_analyzer
from backend.agents.lifecycle_agent import run_lifecycle
from backend.agents.risk_agent import run_risk
from backend.agents.reporter_agent import run_reporter

@tool
def data_tool(_input: str) -> str:
    """Fetch and store OHLCV + metadata for SPAC tickers"""
    fetch_and_store_daily_data()
    return "Data fetched"

@tool
def analyzer_tool(_input: str) -> str:
    """Run anomaly detection checks on SPAC data"""
    run_analyzer()
    return "Analyzer complete"

@tool
def lifecycle_tool(_input: str) -> str:
    """Check IPO milestones (e.g. 15, 30, 60 trading days)"""
    run_lifecycle()
    return "Lifecycle check complete"

@tool
def risk_tool(_input: str) -> str:
    """Flag SPACs with higher regulatory risk (e.g. Chinese SPACs)"""
    run_risk()
    return "Risk analysis complete"

@tool
def reporter_tool(_input: str) -> str:
    """Compile anomalies, lifecycle, and risk alerts into a Markdown report and send via Discord"""
    run_reporter()
    return "Report sent"

