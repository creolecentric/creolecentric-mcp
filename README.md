# creolecentric-mcp

Stdio MCP proxy for the [CreoleCentric](https://creolecentric.com) remote MCP server.

CreoleCentric exposes its developer API as MCP tools at
`https://creolecentric.com/mcp/` over the Streamable HTTP transport. Most
modern MCP clients (Claude Desktop, Claude Code, Cursor) can talk to that
URL directly. This package is for the **stdio-only** clients — it spawns
locally, speaks stdio MCP, and forwards every request to the remote server.

## Install

```bash
pip install creolecentric-mcp
```

## Use

```bash
export CREOLECENTRIC_API_KEY=cc_<keyid>_<secret>
creolecentric-mcp        # speaks MCP on stdio; quit with Ctrl-D
```

Generate an API key at <https://creolecentric.com/api-keys>.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or the equivalent on your platform:

```json
{
  "mcpServers": {
    "creolecentric": {
      "command": "creolecentric-mcp",
      "env": {
        "CREOLECENTRIC_API_KEY": "cc_<keyid>_<secret>"
      }
    }
  }
}
```

Restart Claude Desktop. The 24 CreoleCentric tools (TTS, translation,
dictionary lookup, STT, account/credits) appear in the tool picker.

## Pointing at a different server

```bash
creolecentric-mcp --url https://staging.creolecentric.com/mcp/ --api-key cc_...
# or via env
CREOLECENTRIC_MCP_URL=https://staging.creolecentric.com/mcp/ creolecentric-mcp
```

## What it does

```
Claude Desktop  ──stdio MCP──>  creolecentric-mcp  ──Streamable HTTP MCP──>  https://creolecentric.com/mcp/
```

Each `tools/list` and `tools/call` from the local stdio peer is forwarded
to the remote server with your API key in the `Authorization` header. All
auth, scope checks, rate-limits, and credit deduction happen on the server
side — this binary is a thin transport adapter and stores nothing.

## Why not just use the remote URL directly?

If your MCP client supports remote (HTTP / Streamable HTTP) servers, you
should use `https://creolecentric.com/mcp/` directly with an
`Authorization: Bearer cc_...` header — no shim required. See the
[setup page](https://creolecentric.com/developer/mcp).

This package exists for clients that haven't shipped remote-MCP support yet.
