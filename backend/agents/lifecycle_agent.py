# backend/agents/lifecycle_agent.py
from backend.db.supabase_client import supabase
from datetime import date
from typing import List, Dict


def check_milestones(ticker: str, ipo_date: date) -> List[str]:
    """
    Given ticker + IPO date, return milestone alerts if any apply.
    """
    days_since_ipo = (date.today() - ipo_date).days
    alerts = []

    if 12 <= days_since_ipo <= 20:
        alerts.append(f"{days_since_ipo} days since IPO (near 15-day milestone)")
    elif 30 <= days_since_ipo <= 43:
        alerts.append(f"{days_since_ipo} days since IPO (near 1-month milestone)")
    elif 55 <= days_since_ipo <= 68:
        alerts.append(f"{days_since_ipo} days since IPO (near 3-month milestone)")

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
            "trade_date": today,  # ✅ force today's date
            "anomaly_type": anomaly_type,
            "description": alert["description"],
        }).execute()
        return True

    return False


def run_lifecycle_agent(state: Dict = None) -> Dict:
    """
    Lifecycle agent: check IPO milestones for tickers in state["tickers"],
    or all SPACs if not provided. Deduplicates alerts by (ticker, type, desc)
    *for today only*. Updates and returns state.
    """
    if state is None:
        state = {}

    tickers = state.get("tickers")
    if not tickers:
        rows = supabase.table("spac_list").select("ticker, ipo_date").execute().data
        tickers = [row["ticker"] for row in rows] if rows else []

    # Pull IPO dates for selected tickers
    spac_rows = (
        supabase.table("spac_list")
        .select("ticker, ipo_date")
        .in_("ticker", tickers)
        .execute()
        .data
    )

    today = date.today().isoformat()
    new_alerts: List[Dict] = []

    for row in spac_rows:
        ticker = row["ticker"]
        ipo_date = row.get("ipo_date")

        if not ipo_date:
            continue
        if isinstance(ipo_date, str):
            try:
                ipo_date = date.fromisoformat(ipo_date)
            except ValueError:
                continue  # skip malformed dates

        alerts = check_milestones(ticker, ipo_date)

        for desc in alerts:
            alert = {
                "ticker": ticker,
                "anomaly_type": "Lifecycle",
                "description": desc,
            }

            if insert_alert_if_new(alert, "Lifecycle"):
                print(f"📌 {ticker} ({today}) [Lifecycle] {desc}")
                new_alerts.append({**alert, "trade_date": today})
            else:
                print(f"⏩ Skipped duplicate for {ticker} ({today}): {desc}")

    # --- Update workflow state ---
    state.update({
        "tickers": tickers,
        "anomalies": state.get("anomalies", []) + new_alerts
    })

    print(f"\n✅ Lifecycle agent finished with {len(new_alerts)} new milestone alerts today.")
    return state


if __name__ == "__main__":
    print("🚀 Running Lifecycle Agent...")
    final_state = run_lifecycle_agent()
    print(f"✅ Completed — {len(final_state.get('anomalies', []))} total anomalies in state")







