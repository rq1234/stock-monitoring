# backend/agents/reporter_agent.py
import os
import requests
from datetime import date
from backend.db.supabase_client import supabase

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
REPORTS_DIR = "reports"


def save_markdown_report(content: str, filename: str) -> str:
    """Save Markdown content locally and return the file path."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📄 Markdown report saved to {path}")
    return path


def send_to_discord(filepath: str, summary: str, message: str = "📊 Daily SPAC Report"):
    """Send the Markdown file to Discord via webhook with a summary message."""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ No Discord webhook configured")
        return

    try:
        with open(filepath, "rb") as f:
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                data={"content": f"{message}\n{summary}"},
                files={"file": (os.path.basename(filepath), f, "text/markdown")},
            )
        if response.status_code in (200, 204):
            print("✅ Report sent to Discord")
        else:
            print(f"❌ Discord webhook error: {response.status_code} {response.text}")
    except Exception as e:
        print(f"❌ Failed to send Discord message: {e}")


def normalize_anomaly(a: dict) -> dict:
    """Ensure anomaly dict has all required keys."""
    return {
        "ticker": a.get("ticker", "UNKNOWN"),
        "trade_date": a.get("trade_date", date.today().isoformat()),
        "anomaly_type": a.get("anomaly_type", "Unknown"),
        "description": a.get("description", "No description"),
    }


def build_markdown_from_anomalies(anomalies: list) -> str:
    """Build a Markdown report with deduplicated, merged Volume sections."""
    if not anomalies:
        return "# 📊 Daily SPAC Alerts\n\n✅ No anomalies today."

    # Normalize anomalies
    grouped = {}
    ticker_categories = {}
    for a in anomalies:
        ticker = a["ticker"]
        anomaly_type = a["anomaly_type"]

        grouped.setdefault(anomaly_type, []).append(a)
        ticker_categories.setdefault(ticker, set()).add(anomaly_type)

    content = "# 📊 Daily SPAC Alerts\n\n"

    # ---- Priority Section: Multi-category tickers ----
    priority = [t for t, cats in ticker_categories.items() if len(cats) > 1]
    if priority:
        content += "## ⚠️ Priority: Multi-Category Tickers\n\n"
        for ticker in sorted(priority):
            cats = ", ".join(sorted(ticker_categories[ticker]))
            ticker_anomalies = [a for a in anomalies if a["ticker"] == ticker]
            content += f"- [**{ticker}**]({ticker}) → in categories: *{cats}*\n"
            for a in sorted(ticker_anomalies, key=lambda x: x["anomaly_type"]):
                content += f"  - ({a['trade_date']}) [{a['anomaly_type']}] {a['description']}\n"
            content += "\n"

    # ---- Organize Volume Alerts (deduped + merged per ticker) ----
    if "Volume" in grouped:
        merged = {}
        for a in grouped["Volume"]:
            ticker = a["ticker"]
            desc = a["description"]

            # Normalize duplicate ANNA-type messages
            desc = desc.replace(f"{ticker} ($", f"{ticker} ($").replace(f"{ticker} had", f"{ticker} had")

            if ticker not in merged:
                merged[ticker] = {
                    "trade_date": a["trade_date"],
                    "lows": [],
                    "spikes": [],
                    "zeros": []
                }

            if "very low volume" in desc:
                merged[ticker]["lows"].append(desc)
            elif "zero volume" in desc or "(0)" in desc:
                merged[ticker]["zeros"].append(desc)
            else:
                merged[ticker]["spikes"].append(desc)

        content += "## 🔹 Volume Alerts\n\n"

        # Very Low Volume
        low_tickers = {t: d for t, d in merged.items() if d["lows"]}
        if low_tickers:
            content += "### 🔻 Very Low Volume (Price ≥ $0.20)\n\n"
            for ticker, data in sorted(low_tickers.items()):
                # Dedup reasons
                reasons = list(set(data["lows"]))
                content += f"- [**{ticker}**]({ticker}) ({data['trade_date']}) → {'; '.join(reasons)}\n"

            content += "\n"

        # Volume Spikes
        spike_tickers = {t: d for t, d in merged.items() if d["spikes"]}
        if spike_tickers:
            content += "### 🚀 Volume Spikes\n\n"
            for ticker, data in sorted(spike_tickers.items()):
                reasons = list(set(data["spikes"]))
                content += f"- [**{ticker}**]({ticker}) ({data['trade_date']}) → {'; '.join(reasons)}\n"
            content += "\n"

        # Zero Volume
        zero_tickers = {t: d for t, d in merged.items() if d["zeros"]}
        if zero_tickers:
            content += "### ⚠️ Suspicious Zero-Volume\n\n"
            for ticker, data in sorted(zero_tickers.items()):
                reasons = list(set(data["zeros"]))
                content += f"- [**{ticker}**]({ticker}) ({data['trade_date']}) → {'; '.join(reasons)}\n"
            content += "\n"

        grouped.pop("Volume")

    # ---- Remaining Categories ----
    for category, alerts in grouped.items():
        content += f"## 🔹 {category} Alerts\n\n"
        for a in sorted(alerts, key=lambda x: x["ticker"]):
            content += f"- [**{a['ticker']}**]({a['ticker']}) ({a['trade_date']}) → {a['description']}\n"
        content += "\n"

    return content



def run_reporter_agent(state: dict = None, target_date: str | None = None) -> dict:
    """Reporter agent entrypoint."""
    target_date = target_date or date.today().isoformat()

    response = (
        supabase.table("anomaly_reports")
        .select("ticker, trade_date, anomaly_type, description")
        .eq("trade_date", target_date)
        .execute()
    )
    anomalies = [normalize_anomaly(a) for a in (response.data or [])]

    if state is not None:
        state["anomalies"] = anomalies

    # Build + save report
    content = build_markdown_from_anomalies(anomalies)
    filename = f"spac_alerts_{target_date}.md"
    path = save_markdown_report(content, filename)

    anomaly_count = len(anomalies)
    summary = "✅ No anomalies today." if anomaly_count == 0 else f"⚡ {anomaly_count} anomalies detected today."

    # Send to Discord
    send_to_discord(path, summary, f"📊 SPAC Anomaly Report for {target_date}")

    # Log reporting event
    supabase.table("alerts_log").upsert({
        "alert_date": target_date,
        "alert_channel": "discord"
    }).execute()

    print("✅ Reporter agent finished.")

    if state is not None:
        return state
    return {"status": "done", "file": path, "anomalies": anomaly_count}


if __name__ == "__main__":
    run_reporter_agent()













