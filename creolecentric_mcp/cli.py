"""Console entrypoint: `creolecentric-mcp`."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from . import __version__
from .proxy import run_proxy


_DEFAULT_URL = "https://creolecentric.com/mcp/"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="creolecentric-mcp",
        description=(
            "Stdio MCP proxy for the CreoleCentric remote MCP server. "
            "Lets stdio-only MCP clients (Claude Desktop, etc.) talk to "
            "https://creolecentric.com/mcp/ over the local process."
        ),
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("CREOLECENTRIC_MCP_URL", _DEFAULT_URL),
        help=(
            "Remote MCP Streamable HTTP endpoint "
            f"(env: CREOLECENTRIC_MCP_URL, default: {_DEFAULT_URL})"
        ),
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("CREOLECENTRIC_API_KEY"),
        help=(
            "CreoleCentric API key in `cc_<keyid>_<secret>` form "
            "(env: CREOLECENTRIC_API_KEY). Generate one at "
            "https://creolecentric.com/api-keys."
        ),
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Log proxy activity to stderr.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"creolecentric-mcp {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.api_key:
        print(
            "creolecentric-mcp: missing API key. Set CREOLECENTRIC_API_KEY "
            "or pass --api-key. Generate a key at "
            "https://creolecentric.com/api-keys.",
            file=sys.stderr,
        )
        return 2

    if args.verbose:
        # MCP servers must keep stdout clean for JSON-RPC frames; log to stderr.
        logging.basicConfig(
            level=logging.INFO,
            stream=sys.stderr,
            format="%(asctime)s creolecentric-mcp %(levelname)s %(message)s",
        )

    try:
        asyncio.run(run_proxy(args.url, args.api_key))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"creolecentric-mcp: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
