"""Serve the tool plane over MCP stdio.

    python3 -m argus.broker.serve all --engagement acme-dmz
    python3 -m argus.broker.serve recon exploit proof

`all` merges every server into one endpoint, which is what an MCP client wants:
one entry in its configuration, 29 namespaced tools, one engagement binding.
Individual servers exist for the case where a client should only see part of the
surface — a read-only reviewer, for instance, gets `ledger knowledge`.
"""
from __future__ import annotations

import argparse
import sys

from .mcp import Server, serve_stdio
from .servers import SERVER_NAMES, load


def merge(names: list[str]) -> Server:
    merged = Server("all", "argus tool plane: recon, fuzz, scan, exploit, proof, ledger, knowledge")
    for name in names:
        server = load(name)
        for tool_name, spec in server.tools.items():
            if tool_name in merged.tools:
                raise ValueError(f"tool name collision on {tool_name}")
            merged.tools[tool_name] = spec
    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="argus-broker", description=__doc__.splitlines()[0])
    parser.add_argument("servers", nargs="*", default=["all"],
                        help=f"server names ({', '.join(SERVER_NAMES)}) or 'all'")
    parser.add_argument("--engagement", default=None,
                        help="bind every call to this engagement (else ARGUS_ENGAGEMENT)")
    parser.add_argument("--list", action="store_true", help="print the tool table and exit")
    args = parser.parse_args(argv)

    names = list(SERVER_NAMES) if (not args.servers or "all" in args.servers) else args.servers
    unknown = [name for name in names if name not in SERVER_NAMES]
    if unknown:
        parser.error(f"unknown server(s): {unknown}; known: {', '.join(SERVER_NAMES)}")
    server = merge(names)

    if args.list:
        for spec in server.tools.values():
            print(f"{spec.name:26} {spec.tier:10} {'target' if spec.touches_target else 'local':7} "
                  f"{(spec.proves or '-'):18} {spec.description.splitlines()[0][:70]}")
        print(f"\n{len(server.tools)} tools from {len(names)} server(s)")
        return 0
    return serve_stdio(server, engagement=args.engagement)


if __name__ == "__main__":
    sys.exit(main())
