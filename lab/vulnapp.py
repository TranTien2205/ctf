#!/usr/bin/env python3
"""Compat shim - the lab moved into the package so `argus demo` works
from an installed wheel. `python lab/vulnapp.py [port]` and
`import vulnapp` (tests/selftest keep lab/ on sys.path) still work."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# `import *` skips every name starting with an underscore, so a test reaching
# for `vulnapp._lab_exec` or `vulnapp._injected_commands` got an
# AttributeError against a shim that claims `import vulnapp` still works.
# Copy the whole namespace instead: the shim is either transparent or it is a
# trap for the next person who believes its docstring.
from argus.lab import vulnapp as _real  # noqa: E402

globals().update({k: v for k, v in vars(_real).items()
                  if k not in ("__name__", "__file__", "__loader__",
                               "__spec__", "__package__", "__doc__",
                               "__builtins__")})
make_server = _real.make_server

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    srv = make_server(port)
    print(f"lab vulnerable app on http://127.0.0.1:{srv.server_address[1]}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
