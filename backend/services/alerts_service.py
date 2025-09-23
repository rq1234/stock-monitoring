from datetime import date
from backend.db.supabase_client import supabase
from backend.agents.reporter_agent import normalize_anomaly

def fetch_alerts(start_date: str = None, end_date: str = None, ticker: str = None):
    """Fetch anomalies from Supabase within a date range (optionally by ticker)."""
    today = date.today().isoformat()
    start_date = start_date or today
    end_date = end_date or today

    query = (
        supabase.table("anomaly_reports")
        .select("ticker, trade_date, anomaly_type, description")
        .gte("trade_date", start_date)
        .lte("trade_date", end_date)
        .order("trade_date", desc=True)
    )

    if ticker:
        query = query.eq("ticker", ticker.upper())

    response = query.execute()
    anomalies = [normalize_anomaly(a) for a in (response.data or [])]

    return {
        "date": today,
        "start_date": start_date,
        "end_date": end_date,
        "count": len(anomalies),
        "ticker": ticker.upper() if ticker else None,
        "anomalies": anomalies
    }
