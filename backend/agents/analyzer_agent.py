# backend/agents/analyzer_agent.py
import yfinance as yf
from backend.db.supabase_client import supabase
from datetime import date
from typing import Dict, List


def analyze_ticker(ticker: str) -> List[Dict]:
    """
    Analyze a single ticker for volume anomalies.
    Combines multiple triggers into one description per type
    so no duplicates like "ANNA ($4.36)" vs "ANNA had very low volume".
    """
    stock = yf.Ticker(ticker)
    info = stock.info or {}

    # Yahoo averages
    avg10 = info.get("averageDailyVolume10Day")
    avg90 = info.get("averageDailyVolume3Month")

    # Latest stored OHLCV from Supabase
    rows = (
        supabase.table("spac_data")
        .select("trade_date, volume, close")
        .eq("ticker", ticker)
        .order("trade_date", desc=True)
        .limit(6)  # today + last 5 days
        .execute()
        .data
    )
    if not rows:
        return []

    today_row = rows[0]
    today_vol = today_row["volume"]
    today_price = today_row.get("close", 0)

    # Compute local average from last 5 days (excluding today if possible)
    past_vols = [r["volume"] for r in rows[1:]] if len(rows) > 1 else []
    local_avg = sum(past_vols) / len(past_vols) if past_vols else None

    alerts: List[Dict] = []

    # ---- Rule 1: Very low volume (price ≥ $0.20) ----
    if today_price >= 0.20 and today_vol < 10_000:
        alerts.append({
            "ticker": ticker,
            "anomaly_type": "Volume",
            #  always include price consistently
            "description": f"{ticker} (${today_price:.2f}) had very low volume ({today_vol:,})"
        })

    # ---- Rule 2: Volume spikes (combine reasons into one alert) ----
    spike_reasons = []
    if avg10 and today_vol > 3 * avg10:
        spike_reasons.append(f">3× Yahoo 10-day avg ({avg10:,.0f})")
    if avg90 and today_vol > 3 * avg90:
        spike_reasons.append(f">3× Yahoo 90-day avg ({avg90:,.0f})")
    if local_avg and today_vol > 3 * local_avg:
        spike_reasons.append(f">3× local 5-day avg ({local_avg:,.0f})")

    if spike_reasons:
        alerts.append({
            "ticker": ticker,
            "anomaly_type": "Volume",
            "description": f"{ticker} volume {today_vol:,} is " + "; ".join(spike_reasons)
        })

    return alerts


def insert_alert_if_new(alert: Dict, anomaly_type: str) -> bool:
    """Insert anomaly into Supabase if not already logged *today*."""
    today = date.today().isoformat()

    exists = (
        supabase.table("anomaly_reports")
        .select("id")
        .eq("ticker", alert["ticker"])
        .eq("trade_date", today)
        .eq("anomaly_type", anomaly_type)
        .eq("description", alert["description"])
        .execute()
        .data
    )

    if not exists:
        supabase.table("anomaly_reports").insert({
            "ticker": alert["ticker"],
            "trade_date": today,
            "anomaly_type": anomaly_type,
            "description": alert["description"],
        }).execute()
        return True

    return False


def run_analyzer_agent(state: Dict = None) -> Dict:
    """Run anomaly detection across tickers, ensuring no duplicates."""
    if state is None:
        state = {}

    tickers = state.get("tickers")
    if not tickers:
        rows = supabase.table("spac_list").select("ticker").execute().data
        tickers = [row["ticker"] for row in rows] if rows else []

    results: List[Dict] = []
    today = date.today().isoformat()

    for ticker in tickers:
        alerts = analyze_ticker(ticker)
        for alert in alerts:
            if insert_alert_if_new(alert, "Volume"):
                print(f"⚡ {alert['ticker']} ({today}) [Volume] {alert['description']}")
                results.append({**alert, "trade_date": today})
            else:
                print(f"⏩ Skipped duplicate for {alert['ticker']} ({today}): {alert['description']}")

    state.update({
        "tickers": tickers,
        "anomalies": state.get("anomalies", []) + results
    })

    print(f"\n Analyzer agent finished with {len(results)} new volume alerts.")
    return state


if __name__ == "__main__":
    print("🚀 Running Analyzer Agent...")
    final_state = run_analyzer_agent()
    print(f"Completed — {len(final_state.get('anomalies', []))} alerts found")











