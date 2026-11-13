#!/usr/bin/env python3
"""Compat shim - the lab moved into the package so `argus demo` works
from an installed wheel. `python lab/vulnapp.py [port]` and
`import vulnapp` (tests/selftest keep lab/ on sys.path) still work."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.lab.vulnapp import *  # noqa: F401,F403,E402
from argus.lab.vulnapp import make_server  # noqa: F401,E402

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    srv = make_server(port)
    print(f"lab vulnerable app on http://127.0.0.1:{srv.server_address[1]}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
