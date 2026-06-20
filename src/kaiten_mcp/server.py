"""Kaiten MCP Server (full) — exposes all Kaiten API tools."""

import logging
import os

from kaiten_mcp.app import (
    COMPACT_JSON_THRESHOLD,
    FILE_OUTPUT_THRESHOLD,
    create_mcp_server,
    execute_tool,
    get_client,
    list_tools_for,
    run_server,
)
from kaiten_mcp.registry import TOOL_MODULES, collect_tools

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

ALL_TOOLS = collect_tools()
app = create_mcp_server("kaiten-mcp", ALL_TOOLS)


async def call_tool(name: str, arguments: dict):
    return await execute_tool(name, arguments, ALL_TOOLS)


async def list_tools():
    return await list_tools_for(ALL_TOOLS)


def main() -> None:
    run_server(app)


if __name__ == "__main__":
    main()
