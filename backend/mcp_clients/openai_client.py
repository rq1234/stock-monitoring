import os
import traceback
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def run_agent(user_query: str, structured: bool = False) -> str:
    """
    Run the MCP agent with the given user query and return the response.
    - If structured=True, the agent will try to return JSON instead of free text.
    """

    SYSTEM_PROMPT = """
You are MCP Agent — a finance-focused AI assistant with access to the following tools:

🛠️ Tools you can use:
- get_stock_price(ticker, period, interval): Fetches stock prices and computes support/resistance
- get_volume_history(ticker, days): Returns recent trading volumes
- get_filings(ticker): Summarizes recent SEC filings (8-K, 10-K)
- detect_anomalies(ticker): Detects unusual trading behavior or volume spikes

💡 Your goals:
1. Understand whether the user wants **data**, **analysis**, or both.
2. If data → use the correct MCP tool.
3. If analysis → explain using reasoning grounded in financial logic.
4. If both → fetch data first, then analyze it clearly and concisely.
5. Always provide context (e.g., what metrics mean, or why the data matters).
6. Avoid hallucinating — if a ticker or data is unavailable, say so.

🎯 Output rules:
- Be concise but insightful.
- When `structured=True`, return valid JSON with keys like "type", "content", "ticker", etc.
"""

    # Start the MCP server (the one managing your data tools)
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "backend.mcp_server.mcp_server"],  # start your MCP server as a subprocess
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 🔧 Load MCP tools dynamically
                tools = await load_mcp_tools(session)
                if not tools:
                    return {"type": "error", "content": "⚠️ No tools were loaded. Check your MCP server."}

                # 🔧 Initialize OpenAI LLM
                llm = ChatOpenAI(
                    model="gpt-4.1-mini",
                    temperature=0,
                    openai_api_key=OPENAI_API_KEY,
                )

                # 🔧 Create a ReAct-style agent (LLM + tools)
                agent = create_react_agent(llm, tools)

                # ✅ Construct conversation context (include system prompt)
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_query}
                ]

                if structured:
                    messages.append({
                        "role": "system",
                        "content": (
                            "Return ONLY valid JSON. Use one of the formats below:\n"
                            '{"type": "text", "content": "..."} OR '
                            '{"type": "chart", "ticker": "...", "data": [...]} OR '
                            '{"type": "filings", "ticker": "...", "filings": [...]} OR '
                            '{"type": "anomalies", "ticker": "...", "anomalies": [...]}'
                        )
                    })

                # 🔧 Run the agent
                try:
                    result = await agent.ainvoke({"messages": messages})
                except Exception as inner_e:
                    print("💥 Agent crashed inside ainvoke:", inner_e)
                    traceback.print_exc()
                    return {"type": "error", "content": f"⚠️ MCP agent error (ainvoke): {str(inner_e)}"}

                # ✅ Validate and return
                if not result or "messages" not in result:
                    return {"type": "error", "content": "⚠️ MCP agent returned an unexpected result."}

                return result["messages"][-1].content

    except Exception as outer_e:
        print("💥 MCP client failed:", outer_e)
        traceback.print_exc()
        return {"type": "error", "content": f"⚠️ MCP agent error: {str(outer_e)}"}

