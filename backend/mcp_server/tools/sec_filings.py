# backend/mcp_server/tools/sec_filings.py
import requests
import os
import json
from backend.mcp_server import mcp
from backend.lib.openai_client import client

# 🔑 SEC-API.io Key & Bases
SEC_API_KEY = os.getenv("SEC_API_KEY")
SEC_API_BASE = os.getenv("SEC_API_BASE", "https://api.sec-api.io")  # auto switch
SEC_DOWNLOAD_BASE = "https://archive.sec-api.io"
SEC_PDF_BASE = "https://api.sec-api.io/filing-reader"

CACHE_FILE = "filings_cache.json"


# --- Cache Helpers ---
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


# --- LLM Summarizer ---
def summarize_filing(text: str, form_type: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Extract key facts clearly and concisely."},
                {"role": "user", "content": (
                    f"Summarize the important details from this SEC filing (Form {form_type}). "
                    f"Focus on financials, executive/board changes, offerings, clinical or product news, "
                    f"and risks if relevant:\n\n{text}"
                )}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ LLM summarization failed: {e}"


# --- Helper: SEC Query ---
def query_sec_api(payload: dict) -> requests.Response:
    """
    Handles free vs paid SEC-API query styles.
    """
    if SEC_API_BASE.endswith("/query"):
        # Paid plan → use Authorization header
        url = SEC_API_BASE
        headers = {"Authorization": SEC_API_KEY, "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json=payload)
    else:
        # Free plan → use ?token query param
        url = f"{SEC_API_BASE}?token={SEC_API_KEY}"
        resp = requests.post(url, json=payload)

    # Debug info
    print("=== [DEBUG] SEC Query ===")
    print("URL:", url)
    print("Status:", resp.status_code)
    print("Payload:", json.dumps(payload))
    print("Response snippet:", resp.text[:400])
    print("=========================")

    return resp


# --- MCP Tool: Fetch + Summarize Filings ---
@mcp.tool()
def get_filings(
    ticker: str,
    form_types: list[str] = ["8-K"],
    limit: int = 3,
    summarize: bool = False,
    pdf: bool = False
) -> dict:
    """
    Fetch the most recent SEC filings for a given stock ticker.
    Supports 8-K, S-1, 424B3, 4, etc.
    Uses SEC-API Query + Download API (+ optional PDF).
    """
    if not SEC_API_KEY:
        return {"error": "Missing SEC_API_KEY in environment"}

    form_types = [ft.upper() for ft in form_types]
    cache = load_cache()
    cache_key = f"{ticker}_{'_'.join(form_types)}_{limit}_{summarize}_{pdf}"

    # ✅ Serve from cache
    if cache_key in cache:
        print(f"[CACHE HIT] {cache_key}")
        return cache[cache_key]

    # --- Build Query ---
    query_str = f"ticker:{ticker.upper()} AND formType:({' OR '.join([f'\"{ft}\"' for ft in form_types])})"
    payload = {
        "query": {"query_string": {"query": query_str}},
        "from": 0,
        "size": limit,
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    resp = query_sec_api(payload)
    if resp.status_code != 200:
        return {"error": f"SEC-API query failed {resp.status_code}", "body": resp.text[:200]}

    data = resp.json()
    filings = []

    for f in data.get("filings", []):
        print("=== [DEBUG] Filing metadata ===")
        print(json.dumps(f, indent=2)[:800])
        print("===============================")

        accession = f.get("accessionNo", "")
        cik = f.get("cik", "").lstrip("0")
        form_type = f.get("formType")
        date = f.get("filedAt", "")[:10]
        link = f.get("linkToFilingDetails")

        filing = {
            "date": date,
            "accession": accession,
            "formType": form_type,
            "url": link
        }

        # --- Fetch full filing text via Download API ---
        doc_files = f.get("documentFormatFiles", [])
        if doc_files:
            doc_url = doc_files[0].get("documentUrl", "")
            if "sec.gov/Archives" in doc_url:
                print("[DEBUG] Attempting Download URL:", doc_url)
            try:
                path = doc_url.split("/data/")[-1]
                download_url = f"{SEC_DOWNLOAD_BASE}/{path}?token={SEC_API_KEY}"
                print("[DEBUG] Archive URL:", download_url)

                filing_text = requests.get(download_url).text
                print("[DEBUG] Filing text length:", len(filing_text))

                if summarize:
                    filing["summary"] = summarize_filing(filing_text[:10000], form_type)

                if pdf:
                    pdf_url = (
                        f"{SEC_PDF_BASE}?token={SEC_API_KEY}&url={doc_url.replace('/ix?doc=', '')}"
                    )
                    print("[DEBUG] PDF URL:", pdf_url)
                    filing["pdf_url"] = pdf_url
            except Exception as e:
                print("[ERROR] Filing text fetch failed:", e)
                filing["summary"] = f"⚠️ Failed to fetch filing text: {e}"

        filings.append(filing)

    output = {"ticker": ticker.upper(), "filings": filings}
    cache[cache_key] = output
    save_cache(cache)

    return output









