"""Kaiten MCP Server (operator) — restricted tools for LLM day-to-day use."""

import logging
import os

from kaiten_mcp.app import create_mcp_server, execute_tool, run_server
from kaiten_mcp.profiles.operator import OPERATOR_TOOL_NAMES
from kaiten_mcp.registry import collect_tools

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

ALL_TOOLS = collect_tools(OPERATOR_TOOL_NAMES)
app = create_mcp_server("kaiten-mcp-operator", ALL_TOOLS)


async def call_tool(name: str, arguments: dict):
    return await execute_tool(name, arguments, ALL_TOOLS)


def main() -> None:
    run_server(app)


if __name__ == "__main__":
    main()
