"""Shared test fixtures: lab server + a ready Context."""
from __future__ import annotations

import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lab"))

from argus.config import Config
from argus.httpclient import GuardedClient
from argus.ratelimit import RateLimiter
from argus.scope import ScopeGuard
from argus.session import Session
from argus.tools import Context


@pytest.fixture(scope="session")
def lab_url():
    import vulnapp
    srv = vulnapp.make_server(0)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture()
def ctx(tmp_path, lab_url):
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path)
    scope = ScopeGuard(cfg.target, allow_private=True)
    session = Session(tmp_path, cfg.target, meta={"test": True})
    client = GuardedClient(scope, session, RateLimiter(0),
                           tls_verify=False, max_requests=500)
    c = Context(cfg=cfg, scope=scope, session=session, client=client,
                skills_dir=Path(__file__).parent.parent / "argus" / "skills")
    yield c
    client.close()
