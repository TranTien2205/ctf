"""The argus operator console: a stdlib HTTP server over the session dir.

`server.py` is the wire (routing, limits, security headers), `api.py` is the
data (runs, findings, reports, the prompt gate). `dashboard.html` beside them
is the page; it is read at request time and the server degrades to a plain
notice if it is absent.

    from argus.web import make_server, serve

Nothing here imports a third-party package, and nothing here runs a scan: a
run is performed by the `runner` callable handed to `make_server`, so the web
layer can never report that an agent ran when none did.
"""
from __future__ import annotations

from .api import (MAX_BODY, MODES, RUN_STATES, RunRegistry, TooManyRuns,
                  credential_source_present, findings_rows, health,
                  preview_prompt, reports_rows, scan_runs)
from .server import make_server, serve

__all__ = [
    "MAX_BODY",
    "MODES",
    "RUN_STATES",
    "RunRegistry",
    "TooManyRuns",
    "credential_source_present",
    "findings_rows",
    "health",
    "make_server",
    "preview_prompt",
    "reports_rows",
    "scan_runs",
    "serve",
]
