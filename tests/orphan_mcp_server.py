"""A minimal MCP server that spawns a grandchild, for the orphan test.

Real MCP servers spawn things: a fetch server starts a browser, a scanner
server shells out. This one spawns a sleeper that touches a marker file a
moment after start, so a test can ask whether closing the client killed
the TREE or only the process it could see.

Kept beside `fake_mcp_server.py` and `hostile_mcp_server.py` rather than
inlined, because an MCP client only keeps a process alive if the handshake
succeeds - `MCPClient` kills and forgets a server whose `initialize` fails,
so a stub that does not answer leaves nothing to close and the test would
pass against the defect.
"""
import json
import os
import subprocess
import sys

MARKER = os.environ.get("ORPHAN_MARKER", "")

# the grandchild: sleeps past the test's own wait, then records that it
# was still alive by touching the marker
if MARKER:
    subprocess.Popen(
        [sys.executable, "-c",
         "import time, sys, pathlib\n"
         "time.sleep(2)\n"
         f"pathlib.Path({MARKER!r}).write_text('alive')\n"
         "time.sleep(30)\n"])


def _send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except ValueError:
        continue
    mid = msg.get("id")
    method = msg.get("method")
    if method == "initialize":
        _send({"jsonrpc": "2.0", "id": mid,
               "result": {"protocolVersion": "2024-11-05",
                          "serverInfo": {"name": "orphan", "version": "1"},
                          "capabilities": {}}})
    elif method == "tools/list":
        _send({"jsonrpc": "2.0", "id": mid, "result": {"tools": []}})
    elif mid is not None:
        _send({"jsonrpc": "2.0", "id": mid, "result": {"content": []}})
