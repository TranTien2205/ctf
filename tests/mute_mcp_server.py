"""An MCP server that starts cleanly and never writes a byte.

A server that fails to start is a different case: `MCPClient._start`
notices and gives up. This one is the case a timeout exists for - the
process is alive, the pipe is open, and nothing ever comes back.
"""
import sys
import time

for _line in sys.stdin:          # pragma: no cover - never returns
    time.sleep(3600)
time.sleep(3600)
