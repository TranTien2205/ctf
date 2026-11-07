"""Fake MCP server for tests: newline-delimited JSON-RPC over stdio."""
import json
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        msg = json.loads(line)
    except ValueError:
        continue
    rid = msg.get("id")
    if rid is None:
        continue  # notification, no response
    method = msg.get("method")
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05",
                  "capabilities": {"tools": {}},
                  "serverInfo": {"name": "fake", "version": "0"}}
    elif method == "tools/list":
        result = {"tools": [{"name": "echo", "description": "echo args back"},
                            {"name": "fail", "description": "returns isError"}]}
    elif method == "tools/call":
        params = msg.get("params") or {}
        if params.get("name") == "fail":
            result = {"isError": True,
                      "content": [{"type": "text", "text": "tool broke"}]}
        else:
            result = {"content": [{"type": "text", "text":
                                   "echo:" + json.dumps(params.get("arguments") or {},
                                                        sort_keys=True)}]}
    else:
        resp = {"jsonrpc": "2.0", "id": rid,
                "error": {"code": -32601, "message": f"unknown {method}"}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()
        continue
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": rid,
                                 "result": result}) + "\n")
    sys.stdout.flush()
