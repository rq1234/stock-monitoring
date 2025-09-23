# 📊 Portfolio Monitoring Dashboard

A full-stack **SPAC Ticker monitoring and anomaly detection** platform.  
It integrates **FastAPI (Python)** backend services with **React + TypeScript (Vite)** frontend to provide:

-  **Stock data visualization** (prices, volume, historical charts)  
-  **Daily anomaly alerts** (Supabase + anomaly detection logic)  
-  **SEC filings** (8-K, S-1, 424B3, etc.) with optional **AI summarization**  
-  **MCP (Modular Command Protocol) tools** for modular backend extensions  

---

## ⚙️ Set up the backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

```
---


## Run Backend Server
```bash
cd..
uvicorn backend.main:app --reload
```
---

## Set up the Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev


Open the app at:
http://localhost:5173

```
---

## Environment Variables
```bash
Backend requires:
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_key>
SEC_API_KEY=<your_sec_api_key>
OPENAI_API_KEY=<your_openai_key>

```
---

##  Features

###  FastAPI Backend
- `/tools/...` endpoints auto-loaded via MCP tool registry  
- Supabase integration for **tickers + anomaly reports**  
- SEC filings fetcher with **LLM summarization** (via OpenAI client)  
- Agents for **lifecycle, risk, reporting, and analysis**  
- Workflow automation (`spac_workflow.py`)  

###  React Frontend
- Interactive dashboard for **monitoring alerts, stock prices, filings**  
- Components: **tickers, anomaly tables, charts, filings list**  
- TypeScript API client (`mcpClient.ts`) to call backend MCP tools  
- Tailwind + shadcn/ui for modern UI styling  

###  Modular MCP Tools
- **alerts.py** → anomaly alerts (markdown)  
- **anomalies.py** → ticker-specific anomaly detection  
- **charts.py** → OHLC + support/resistance  
- **filings.py** → SEC filings with summarization  
- **tickers.py** → list tickers from Supabase  
- **volume.py** → historical volume trends  

###  Services & Scripts
- `alerts_service.py` → background alert service  
- `seed_spac_list.py` → populate SPAC tickers in Supabase  
- Workflow definitions in `workflows/`  

### Overview

#### Intelligent Agents

This project includes four autonomous agents designed to analyze SPAC (Special Purpose Acquisition Company) activity, enforce rules, and provide actionable insights. These agents run as part of the backend (FastAPI + MCP) and are orchestrated by LangChain Graph and the MCP (Modular Command Protocol) agent for modular extensibility.

#### Agents

Analyzer Agent – Evaluates financial and market data for anomalies.
Data Agent – Fetches and validates raw SPAC datasets from Supabase and external APIs.
Lifecycle Agent – Tracks SPAC lifecycle events (IPO, merger, deadlines).
Risk Agent – Assesses compliance and risk factors, ensuring rules are followed.

#### Reporting & Alerts

Reporter Agent – Summarizes findings into daily reports.
Sends Discord alerts for anomalies, risk flags, and rule violations.
Alerts are formatted as Markdown for easy reading.

#### Orchestration

LangChain Graph – Manages agent workflows, allowing outputs from one agent to feed into the next (pipeline execution).
MCP Agent – Acts as the bridge between the agents and the API layer. It can:
Ask clarifying questions if the user request is ambiguous.
Dynamically select tools from the MCP registry (alerts, anomalies, filings, price, volume, etc.).
Expose tools as API endpoints (/tools/...) so they can be invoked directly by the frontend or other services.

#### Advantages
Modularity – Each agent is self-contained and can be extended or swapped independently.
Automation – Data flows automatically from fetch → analyze → report → alert.
Real-time Monitoring – Discord notifications provide instant visibility into risks.
Intelligent Routing – MCP agent ensures the right tool is selected for the job, reducing errors and increasing flexibility.
Scalability – LangChain Graph orchestrates complex multi-step workflows, making it easy to add new rules or monitoring logic.

---

##  Project Structure
```bash
backend/
 ├── agents/              # AI agents (analytics, reporting, lifecycle)
 ├── db/                  # Supabase repos + client
 ├── lib/                 # Shared utilities (OpenAI client, etc.)
 ├── mcp_clients/         # MCP client agents (OpenAI + demo)
 ├── mcp_server/          # MCP FastAPI server + tools
 │   ├── tools/           #  MCP Tools (exposed as /tools/<name>)
 │   │   ├── alerts.py        # Daily anomaly alerts (Markdown output)
 │   │   ├── anomalies.py     # Anomaly normalization / detection
 │   │   ├── charts.py        # Generate price/volume chart data
 │   │   ├── price.py         # Fetch current stock price
 │   │   ├── sec_filings.py   # SEC filings fetch + summarize (8-K, S-1, etc.)
 │   │   ├── sec_utils.py     # SEC helper functions
 │   │   ├── tickers.py       # List available tickers from Supabase
 │   │   └── volume.py        # Volume history from Supabase
 │   ├── http_server.py   # FastAPI router → turns MCP tools into API routes
 │   ├── mcp_core.py      # MCP registry logic
 │   └── mcp_server.py    # MCP server bootstrap
 ├── routers/             # API routers (custom endpoints)
 ├── scripts/             # One-off scripts (e.g., seed SPAC data)
 ├── services/            # Background services (alerts, etc.)
 ├── workflows/           # Workflow orchestration (SPAC workflow engine)
 ├── main.py              # FastAPI entrypoint (loads tools + starts app)
 └── requirements.txt     # Backend dependencies

frontend/
 ├── src/
 │   ├── components/      
 │   │   ├── layout/      # Global app layout
 │   │   │   ├── Navbar.tsx   # Top navigation bar (branding, links, actions)
 │   │   │   └── Sidebar.tsx  # Sidebar navigation (routes to dashboard, agents, etc.)
 │   │   │
 │   │   └── ui/          # Dashboard UI widgets
 │   │       ├── AnomalyTable.tsx   # Displays anomalies from MCP alerts
 │   │       ├── DashboardCard.tsx  # Reusable card container for sections
 │   │       ├── ErrorBoundary.tsx  # Catch & display frontend errors
 │   │       ├── FilingsList.tsx    # Shows SEC filings (with summaries/PDF links)
 │   │       ├── StockChartCard.tsx # Price + indicator charts
 │   │       ├── TickerSelector.tsx # Dropdown to select ticker (via MCP tickers tool)
 │   │       └── VolumeChart.tsx    # Historical volume chart
 │   │
 │   ├── lib/             # Frontend helpers + API clients
 │   │   ├── mcpClient.ts # Wrapper for calling backend MCP tools (fetch → JSON)
 │   │   └── utils.ts     # Misc frontend utilities
 │   │
 │   ├── pages/           # High-level app pages
 │   │   ├── Dashboard.tsx  # Portfolio monitoring dashboard (charts + alerts)
 │   │   └── AgentPage.tsx  # Experimental agent interactions
 │   │
 │   ├── App.tsx          # Root React app shell
 │   ├── main.tsx         # Vite entrypoint
 │   ├── App.css          # Global styles
 │   └── index.css        # Tailwind / base CSS
 │
 ├── public/              # Static assets (icons, logos, etc.)
 ├── package.json         # Frontend dependencies
 └── vite.config.ts       # Vite config

```
## ⚙️ Architecture
```bash
- **Frontend (Vercel)**  
  The React frontend is deployed on Vercel. Any pushes to the `main` branch under the `/frontend` folder trigger an automatic redeploy.  
  URL: `https://<your-frontend>.vercel.app`

- **Backend (Render)**  
  The FastAPI backend lives in `/backend` and is hosted on Render.  
  Render automatically redeploys whenever commits are pushed to the GitHub repo’s `main` branch (if linked).  
  URL: `https://spac-tracker.onrender.com`

- **Database (Supabase)**  
  Supabase stores ticker lists, anomaly reports, and SEC filings.  
  Credentials are stored in `.env` and passed into Render and Vercel as environment variables.

- **Cron Jobs (GitHub Actions)**  
  A GitHub workflow (`.github/workflows/cron.yml`) runs daily on a schedule.  
  It triggers backend tasks such as refreshing ticker data and anomaly detection.

```  
