#!/usr/bin/env python3
"""An MCP server that answers initialize, then emits one hostile frame
followed by a legitimate reply - the shape that killed the reader thread."""
import json, sys
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except Exception:
        continue
    rid = msg.get("id")
    if msg.get("method") == "initialize":
        sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":rid,"result":
            {"protocolVersion":"2024-11-05","capabilities":{},
             "serverInfo":{"name":"hostile","version":"1"}}}) + "\n")
        sys.stdout.flush()
    elif rid is not None:
        sys.stdout.write("[" * 100000 + "]" * 100000 + "\n")
        sys.stdout.write(json.dumps({"jsonrpc":"2.0","id":rid,
            "result":{"tools":[]}}) + "\n")
        sys.stdout.flush()
