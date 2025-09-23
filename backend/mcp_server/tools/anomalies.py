from backend.mcp_server import mcp
from backend.db.supabase_client import supabase
from datetime import date
from typing import Optional

@mcp.tool()
def detect_anomalies(ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
    """
    Fetch anomalies for a given ticker from Supabase.
    
    Args:
        ticker (str): Stock/SPAC ticker symbol.
        start_date (str, optional): Start date in YYYY-MM-DD format. Defaults to today.
        end_date (str, optional): End date in YYYY-MM-DD format. Defaults to today.
    
    Returns:
        dict: A dictionary with anomalies for the ticker.
    """
    today = date.today().isoformat()

    # Default to today's date if not provided
    start_date = start_date or today
    end_date = end_date or today

    rows = (
        supabase.table("anomaly_reports")
        .select("trade_date, anomaly_type, description")
        .eq("ticker", ticker.upper())
        .gte("trade_date", start_date)
        .lte("trade_date", end_date)
        .order("trade_date", desc=True)
        .execute()
        .data
    )

    return {
        "ticker": ticker.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "anomalies": rows or []
    }

