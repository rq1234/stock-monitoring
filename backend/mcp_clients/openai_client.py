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

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "backend.mcp_server.mcp_server"],  # start your MCP server as subprocess
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 🔧 Load MCP tools
                tools = await load_mcp_tools(session)
                if not tools:
                    return {"type": "error", "content": "⚠️ No tools were loaded. Check your MCP server."}

                # 🔧 Initialize LLM
                llm = ChatOpenAI(
                    model="gpt-4.1-mini",
                    temperature=0,
                    openai_api_key=OPENAI_API_KEY,
                )

                # 🔧 Create agent
                agent = create_react_agent(llm, tools)

                # ✅ Build messages
                messages = [{"role": "user", "content": user_query}]
                if structured:
                    messages.append({
                        "role": "system",
                        "content": (
                            "Respond ONLY in valid JSON. "
                            "Use one of these formats: "
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

                # ✅ Validate response
                if not result or "messages" not in result:
                    return {"type": "error", "content": "⚠️ MCP agent returned an unexpected result."}

                return result["messages"][-1].content

    except Exception as outer_e:
        print("💥 MCP client failed:", outer_e)
        traceback.print_exc()
        return {"type": "error", "content": f"⚠️ MCP agent error: {str(outer_e)}"}
