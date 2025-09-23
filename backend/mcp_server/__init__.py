# backend/mcp_server/__init__.py
from mcp.server.fastmcp import FastMCP

class MCPWithRegistry(FastMCP):
    def __init__(self, name: str):
        super().__init__(name)
        self._tools = {}

    def tool(self, *args, **kwargs):
        # get the real decorator from FastMCP
        base_decorator = super().tool(*args, **kwargs)

        def wrapper(func):
            # register with FastMCP
            wrapped = base_decorator(func)

            # also keep reference in registry
            tool_name = kwargs.get("name", func.__name__)
            self._tools[tool_name] = wrapped

            return wrapped

        return wrapper

    @property
    def tools(self):
        return self._tools

# Shared singleton MCP instance
mcp = MCPWithRegistry("spac-server")





