# backend/mcp_server/tools/alerts.py
from backend.mcp_server import mcp
from backend.agents.reporter_agent import build_markdown_from_anomalies, normalize_anomaly
from backend.db.supabase_client import supabase
from datetime import date

@mcp.tool()
def get_alerts_markdown(start_date: str = None) -> dict:
    """
    Fetch and render anomalies for a specific day.
    Only returns entries with exact trade_date = start_date.
    """
    today = date.today().isoformat()
    target_date = start_date or today

    print(f"📅 Fetching anomalies for {target_date}")

    response = (
        supabase.table("anomaly_reports")
        .select("ticker, trade_date, anomaly_type, description")
        .eq("trade_date", target_date)  # ✅ match exact date
        .execute()
    )

    anomalies = [normalize_anomaly(a) for a in (response.data or [])]
    print(f"✅ Found {len(anomalies)} anomalies for {target_date}")

    md = build_markdown_from_anomalies(anomalies)

    return {
        "date": target_date,
        "count": len(anomalies),
        "markdown": md
    }



