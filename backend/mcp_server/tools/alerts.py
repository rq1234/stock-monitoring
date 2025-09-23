# backend/mcp_server/tools/alerts.py
from backend.mcp_server import mcp
from backend.agents.reporter_agent import build_markdown_from_anomalies, normalize_anomaly
from backend.db.supabase_client import supabase
from datetime import date

@mcp.tool()
def get_alerts_markdown(start_date: str = None) -> dict:
    today = date.today().isoformat()
    start_date = start_date or today
    

    response = (
        supabase.table("anomaly_reports")
        .select("ticker, trade_date, anomaly_type, description")
        .gte("trade_date", start_date)
        .execute()
    )
    anomalies = [normalize_anomaly(a) for a in (response.data or [])]
    md = build_markdown_from_anomalies(anomalies)

    return {"date": today, "count": len(anomalies), "markdown": md}
