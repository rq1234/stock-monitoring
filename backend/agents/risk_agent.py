# backend/agents/risk_agent.py
from backend.db.supabase_client import supabase
from datetime import date
from typing import Dict, List


def check_risks(ticker: str, country: str, exchange: str) -> List[str]:
    """
    Apply risk rules to a SPAC given its metadata.
    Returns a list of alert descriptions.
    """
    alerts = []

    # Rule 1: Chinese SPACs
    if country and "China" in country:
        alerts.append(f"{ticker} is a Chinese SPAC (Country={country})")

    # Rule 2: OTC or Pink sheet exchanges
    if exchange and ("OTC" in exchange or "Pink" in exchange):
        alerts.append(f"{ticker} trades on a risky exchange ({exchange})")

    return alerts


def insert_alert_if_new(alert: Dict, anomaly_type: str) -> bool:
    """
    Insert anomaly into Supabase if not already logged *today*.
    Always enforces today's trade_date.
    Returns True if inserted, False if duplicate.
    """
    today = date.today().isoformat()

    exists = (
        supabase.table("anomaly_reports")
        .select("id")
        .eq("ticker", alert["ticker"])
        .eq("trade_date", today)   # ✅ only today
        .eq("anomaly_type", anomaly_type)
        .eq("description", alert["description"])
        .execute()
        .data
    )

    if not exists:
        supabase.table("anomaly_reports").insert({
            "ticker": alert["ticker"],
            "trade_date": today,  # ✅ force today
            "anomaly_type": anomaly_type,
            "description": alert["description"],
        }).execute()
        return True

    return False


def run_risk_agent(state: Dict = None) -> Dict:
    """
    Risk agent: check SPACs against risk rules.
    Deduplicates anomalies by (ticker, type, desc) *for today only*.
    Updates and returns state.
    """
    if state is None:
        state = {}

    rows = supabase.table("spac_list").select("ticker, country, exchange").execute().data
    if not rows:
        print("⚠️ No tickers found in spac_list")
        return state

    tickers = [row["ticker"] for row in rows if "ticker" in row]
    today = date.today().isoformat()
    new_alerts: List[Dict] = []

    for row in rows:
        ticker = row.get("ticker")
        if not ticker:
            continue

        country = row.get("country", "Unknown")
        exchange = row.get("exchange", "Unknown")

        alerts = check_risks(ticker, country, exchange)

        for desc in alerts:
            alert = {
                "ticker": ticker,
                "anomaly_type": "Risk",
                "description": desc,
            }

            if insert_alert_if_new(alert, "Risk"):
                print(f"📌 {ticker} ({today}) [Risk] {desc}")
                new_alerts.append({**alert, "trade_date": today})
            else:
                print(f"⏩ Skipped duplicate for {ticker} ({today}): {desc}")

    # --- Update workflow state ---
    state.update({
        "tickers": tickers,
        "anomalies": state.get("anomalies", []) + new_alerts
    })

    print(f"\n✅ Risk agent finished with {len(new_alerts)} new risk alerts today.")
    return state


if __name__ == "__main__":
    print("🚀 Running Risk Agent...")
    final_state = run_risk_agent()
    print(f"✅ Completed — {len(final_state.get('anomalies', []))} total anomalies in state")





