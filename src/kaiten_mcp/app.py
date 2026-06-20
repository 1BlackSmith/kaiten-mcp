"""Shared MCP application factory and tool dispatch."""

import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

from kaiten_mcp.client import KaitenApiError, KaitenClient
from kaiten_mcp.tools.compact import strip_base64

load_dotenv()

logger = logging.getLogger(__name__)

COMPACT_JSON_THRESHOLD = 10_000
FILE_OUTPUT_THRESHOLD = 200_000

_client: KaitenClient | None = None


def get_client() -> KaitenClient:
    global _client
    if _client is None:
        _client = KaitenClient()
    return _client


async def execute_tool(name: str, arguments: dict, tools: dict[str, dict]) -> CallToolResult:
    """Run a tool handler and format the MCP response."""
    try:
        if name not in tools:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
        handler = tools[name]["handler"]
        client = get_client()
        result = await handler(client, arguments)

        if isinstance(result, (dict, list)):
            result, stripped = strip_base64(result)
            text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
            if len(text) > COMPACT_JSON_THRESHOLD:
                text = json.dumps(result, ensure_ascii=False, separators=(",", ":"), default=str)
            output_dir = os.environ.get("KAITEN_MCP_OUTPUT_DIR")
            if len(text) > FILE_OUTPUT_THRESHOLD and output_dir:
                os.makedirs(output_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(output_dir, f"{name}_{ts}.json")
                with open(file_path, "w", encoding="utf-8") as f:  # noqa: ASYNC230
                    f.write(text)
                count = len(result) if isinstance(result, list) else 1
                sample = result[:3] if isinstance(result, list) else result
                summary = json.dumps(
                    {
                        "saved_to": file_path,
                        "total_items": count,
                        "size_bytes": len(text),
                        "sample": sample,
                        "tip": "Read the saved file to process data. Use 'fields' parameter to reduce response size.",
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                    default=str,
                )
                text = summary
            if stripped:
                text += (
                    f"\n\n[Omitted {stripped} base64-encoded field(s). "
                    "Data available via Kaiten web UI.]"
                )
        else:
            text = str(result) if result is not None else "OK"
        return CallToolResult(content=[TextContent(type="text", text=text)])
    except KaitenApiError as e:
        return CallToolResult(
            content=[
                TextContent(type="text", text=f"Kaiten API Error {e.status_code}: {e.message}")
            ],
            isError=True,
        )
    except Exception as e:
        logger.exception("Unhandled error in call_tool")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")],
            isError=True,
        )


async def list_tools_for(tools: dict[str, dict]) -> list[Tool]:
    """Return MCP Tool descriptors for a registry (for tests and tooling)."""
    return [
        Tool(
            name=name,
            description=defn["description"],
            inputSchema=defn["inputSchema"],
        )
        for name, defn in tools.items()
    ]


def create_mcp_server(server_name: str, tools: dict[str, dict]) -> Server:
    """Build an MCP Server bound to a fixed tool registry."""
    app = Server(server_name)

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        return await list_tools_for(tools)

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> CallToolResult:
        return await execute_tool(name, arguments, tools)

    return app


def run_server(app: Server) -> None:
    import asyncio

    async def _run() -> None:
        try:
            async with stdio_server() as (read_stream, write_stream):
                await app.run(read_stream, write_stream, app.create_initialization_options())
        finally:
            global _client
            if _client is not None:
                await _client.close()
                _client = None

    asyncio.run(_run())
