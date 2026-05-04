"""Stdio → Streamable HTTP proxy for the CreoleCentric MCP server.

Speaks MCP over stdio (so any MCP client that only supports stdio — including
some embedded Claude Desktop configurations — can talk to it) and forwards
every `tools/list` and `tools/call` to the remote `/mcp/` Streamable HTTP
endpoint. The remote does the real work; this module is a thin transport
adapter.
"""
from __future__ import annotations

import logging
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
import mcp.types as types


logger = logging.getLogger("creolecentric_mcp")


async def run_proxy(remote_url: str, api_key: str) -> None:
    """Run the stdio proxy. Blocks until the stdio peer closes the connection."""
    headers = {"Authorization": f"Bearer {api_key}"}

    async with streamablehttp_client(remote_url, headers=headers) as (
        read_stream,
        write_stream,
        _get_session_id,
    ):
        async with ClientSession(read_stream, write_stream) as remote:
            init_result = await remote.initialize()
            remote_name = getattr(init_result.serverInfo, "name", "creolecentric")
            remote_version = getattr(init_result.serverInfo, "version", "")
            instructions = getattr(init_result, "instructions", None)

            server = Server(
                name=f"{remote_name}-stdio-proxy",
                version=remote_version or "0.0.0",
                instructions=instructions,
            )

            @server.list_tools()
            async def list_tools() -> list[types.Tool]:
                result = await remote.list_tools()
                return list(result.tools)

            @server.call_tool()
            async def call_tool(name: str, arguments: dict[str, Any]):
                result = await remote.call_tool(name, arguments)
                # Mirror isError so MCP-spec tool errors propagate verbatim.
                if getattr(result, "isError", False):
                    text = ""
                    for block in result.content:
                        if isinstance(block, types.TextContent):
                            text = block.text
                            break
                    raise RuntimeError(text or f"Remote tool '{name}' returned an error")
                # Forward both content blocks and structuredContent so the
                # local server doesn't trip outputSchema validation when the
                # forwarded Tool spec declares one.
                structured = getattr(result, "structuredContent", None)
                content = list(result.content)
                if structured is not None:
                    return content, structured
                return content

            async with stdio_server() as (stdin_stream, stdout_stream):
                await server.run(
                    stdin_stream,
                    stdout_stream,
                    server.create_initialization_options(),
                )
