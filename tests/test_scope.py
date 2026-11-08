"""ScopeGuard: the boundary every request passes."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.config import Config
from argus.httpclient import GuardedClient, RequestBudgetExhausted
from argus.ratelimit import RateLimiter
from argus.scope import ScopeError, ScopeGuard
from argus.session import Session


def test_framing_headers_dropped_from_config(tmp_path):
    """A Burp-copied header file always carries Host:/Content-Length: -
    honoring them would desync the wire from the scoped URL (scope check
    says host A, wire says host B) and break request framing."""
    import argparse
    from argus.config import load_config
    args = argparse.Namespace(
        api_key="k", auth_token=None, header_file=None,
        header=["Host: evil.example", "Cookie: s=1",
                "Content-Length: 9", "X-Custom: v"],
        scope=[], exclude=[], target="http://127.0.0.1:1", model=None,
        max_turns=1, max_requests=1, max_time=1, rate=0, goal="",
        operator="", proxy="", llm_max_tokens=1, mcp_config=None,
        resume=None, allow_private=True, tls_verify=False,
        no_external=False, quiet=True, session_dir=str(tmp_path),
        tools="")
    cfg = load_config(args)
    hdrs = cfg.resolved_headers()
    assert "Host" not in hdrs and "Content-Length" not in hdrs
    assert hdrs["Cookie"] == "s=1" and hdrs["X-Custom"] == "v"


def test_in_scope_host_ok():
    g = ScopeGuard("https://target.example/app", allow_private=False)
    g.check("https://target.example/login?next=/x")


def test_out_of_scope_host_denied():
    g = ScopeGuard("https://target.example", allow_private=False)
    with pytest.raises(ScopeError):
        g.check("https://evil.example/")


def test_subdomain_allowed_by_default():
    g = ScopeGuard("https://target.example", allow_private=False)
    g.check("https://api.target.example/")


def test_scheme_restricted():
    g = ScopeGuard("https://target.example")
    for bad in ("file:///etc/passwd", "gopher://x/", "ftp://target.example/"):
        with pytest.raises(ScopeError):
            g.check(bad)


def test_extra_hosts():
    g = ScopeGuard("https://a.example", extra_hosts=["b.example"],
                   allow_private=False)
    g.check("https://b.example/api")


def test_excluded_path_denied():
    g = ScopeGuard("https://target.example", exclude_paths=["/logout", "/admin"],
                   allow_private=False)
    with pytest.raises(ScopeError):
        g.check("https://target.example/logout")
    with pytest.raises(ScopeError):
        g.check("https://target.example/admin/reset")
    g.check("https://target.example/administer")  # prefix boundary


def test_private_refused_by_default():
    g = ScopeGuard("https://target.example", extra_hosts=["internal.example"],
                   allow_private=False)
    g._private_cache["internal.example"] = True
    with pytest.raises(ScopeError):
        g.check("http://internal.example/")


def test_private_target_autoallows():
    g = ScopeGuard("http://127.0.0.1:8777")
    assert g.allow_private
    g.check("http://127.0.0.1:8777/")


def test_redirect_follow_stays_in_scope(ctx, lab_url):
    """follow_redirects must scope-check every hop - a 302 to a foreign
    host is refused, and the blocked hop lands in the transcript."""
    out = ctx.client.send("GET", lab_url + "/redirect?next=/item?id=1",
                          follow_redirects=True)
    assert out["status"] == 200                    # in-scope hop followed

    with pytest.raises(ScopeError):
        ctx.client.send("GET",
                        lab_url + "/redirect?next=http://evil.example/x",
                        follow_redirects=True)
    last = ctx.session._transcript[f"r{ctx.session._seq}"]
    assert last["response"].get("blocked_redirect") is True
    assert "evil.example" in last["response"].get("blocked_to", "")


def test_curl_arg_guards(ctx):
    """curl flags that read local files, redirect the connection, inject
    options, or write outside cwd are refused."""
    from argus.tools.analysis import _curl_arg_check
    c = lambda toks: _curl_arg_check(ctx, toks)
    # local file exfiltration to the target or into the transcript
    assert c(["-d", "@/etc/passwd", "http://x/"])
    assert c(["-d@/etc/passwd", "http://x/"])
    assert c(["-F", "f=@cfg", "http://x/"])
    assert c(["-Ff=<cfg", "http://x/"])
    assert c(["--form", "f=@cfg", "http://x/"])
    assert c(["--data-urlencode", "n@/etc/passwd", "http://x/"])
    assert c(["-T", "secret", "http://x/"])
    assert c(["-Tsecret", "http://x/"])
    assert c(["--upload-file", "s", "http://x/"])
    assert c(["-b", "cookiejar", "http://x/"])
    assert c(["-bjar", "http://x/"])
    assert c(["-w", "@/etc/passwd", "http://x/"])
    # option injection re-enables everything above
    assert c(["-K", "cfg", "http://x/"])
    assert c(["--config=cfg", "http://x/"])
    # connection redirection while URL stays in-scope
    assert c(["--resolve", "x:80:1.2.3.4", "http://x/"])
    assert c(["--connect-to", "::1.2.3.4:", "http://x/"])
    assert c(["-x", "http://proxy:8080", "http://x/"])
    assert c(["--proxy", "p:8080", "http://x/"])
    assert c(["--socks5", "1.2.3.4", "http://x/"])
    assert c(["--unix-socket", "/tmp/s", "http://x/"])
    # bundled short flags: '-sK cfg' is -s + -K, '-sd@x' is -d @x
    assert c(["-sK", "cfg", "http://x/"])
    assert c(["-sd@x", "http://x/"])
    assert c(["-sT", "secret", "http://x/"])
    assert c(["-sx", "http://proxy:8080", "http://x/"])
    # file writes confined to a plain filename
    assert c(["-o", "../evil", "http://x/"])
    assert c(["-oC:/tmp/x", "http://x/"])
    assert c(["--output=/abs/x", "http://x/"])
    assert c(["--dump-header", "/tmp/h", "http://x/"])
    assert c(["-c", "../jar", "http://x/"])
    # harmless flags pass through
    assert c(["-f", "http://x/"]) is None
    assert c(["-sS", "-o", "out.txt", "http://x/"]) is None
    assert c(["-d", "a=b@c.d", "http://x/"]) is None
    assert c(["-d", "a=b", "http://x/"]) is None
    assert c(["-F", "f=me@x", "http://x/"]) is None
    assert c(["-b", "session=abc", "http://x/"]) is None
    assert c(["-H", "A: b", "http://x/"]) is None
    assert c(["-w", "%{http_code}", "http://x/"]) is None


def test_nmap_arg_guards(ctx, tmp_path):
    """nmap -iL files are scope-checked; local script paths, random
    targets, and out-of-cwd output are refused."""
    from argus.tools.analysis import _nmap_arg_check
    n = lambda toks: _nmap_arg_check(ctx, toks)
    f = tmp_path / "targets.txt"
    f.write_text("127.0.0.1\nevil.example\n")
    assert n(["-iL", str(f)])
    f.write_text("# comment\n127.0.0.1\n")
    assert n(["-iL", str(f)]) is None
    assert n(["-iL", str(tmp_path / "nope.txt")])
    assert n(["-iR", "100"])
    assert n(["--script", "./evil.nse", "127.0.0.1"])
    assert n(["--script", str(tmp_path / "x.nse"), "127.0.0.1"])
    assert n(["-oX", "/tmp/out.xml", "127.0.0.1"])
    assert n(["--resume", "prev.xml"])
    assert n(["--proxies", "http://p:8080", "127.0.0.1"])
    assert n(["-sV", "--script", "vuln", "127.0.0.1"]) is None
    assert n(["-oN", "scan.txt", "127.0.0.1"]) is None


def test_sqlmap_arg_guards(ctx, tmp_path):
    """sqlmap --eval executes Python locally; -r request files carry
    hosts inside; -d connects to arbitrary DBMS hosts."""
    from argus.tools.analysis import _sqlmap_arg_check
    s = lambda toks: _sqlmap_arg_check(ctx, toks)
    assert s(["-u", "http://x/?a=1", "--eval", "import os"])
    assert s(["-u", "http://x/", "-d", "mysql://u:p@db/"])
    assert s(["-u", "http://x/", "--tamper", "../evil.py"])
    assert s(["-u", "http://x/", "-c", "cfg.ini"])
    assert s(["-u", "http://x/", "--proxy", "http://p:8080"])
    req = tmp_path / "req.txt"
    req.write_text("GET / HTTP/1.1\nHost: evil.example\n\n")
    assert s(["-r", str(req)])
    req.write_text("GET / HTTP/1.1\nHost: 127.0.0.1\n\n")
    assert s(["-r", str(req)]) is None
    assert s(["-u", "http://x/?a=1", "--batch", "--level=3"]) is None
    assert s(["-u", "http://x/", "--tamper", "between,randomcase"]) is None


def test_ffuf_arg_guards(ctx, tmp_path):
    """ffuf -w wordlists must live in resources/wordlists or cwd - an
    arbitrary file is exfiltrated line by line as payloads."""
    from argus.tools.analysis import _ffuf_arg_check
    f = lambda toks: _ffuf_arg_check(ctx, toks)
    assert f(["-w", "/etc/passwd:FUZZ", "-u", "http://x/FUZZ"])
    assert f(["-w", str(tmp_path / "wl.txt"), "-u", "http://x/FUZZ"])
    assert f(["-x", "http://proxy:8080", "-u", "http://x/FUZZ"])
    assert f(["-of", "/tmp/out.json", "-u", "http://x/FUZZ"])
    repo_wl = (Path(__file__).resolve().parent.parent
               / "argus" / "resources" / "wordlists" / "dirs-small.txt")
    assert f(["-w", f"{repo_wl}:FUZZ", "-u", "http://x/FUZZ"]) is None
    assert f(["-u", "http://x/FUZZ", "-mc", "200"]) is None


def test_send_timeout_never_infinite(ctx):
    """send(timeout=None) must NOT pass timeout=None to httpx - that
    builds Timeout(None), an infinite wait overriding the 15s default."""
    import httpx
    calls = []

    class _Resp:
        status_code = 200
        headers = httpx.Headers()
        content = b""
        encoding = "utf-8"
        url = "http://127.0.0.1/"

    orig = ctx.client._client.request

    def spy(method, url, **kw):
        calls.append(kw)
        return _Resp()

    ctx.client._client.request = spy
    try:
        ctx.client.send("GET", "http://127.0.0.1/")
        ctx.client.send("GET", "http://127.0.0.1/", timeout=3.0)
    finally:
        ctx.client._client.request = orig
    assert "timeout" not in calls[0]
    assert calls[1]["timeout"] == 3.0


def test_transcript_records_wire_headers(lab_url, tmp_path):
    """Recorded request headers must reflect the wire - client default
    headers (e.g. --header Authorization) and jar cookies included. Secret
    VALUES are redacted (the audit shows auth was sent, not the token)."""
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path)
    scope = ScopeGuard(cfg.target, allow_private=True)
    session = Session(tmp_path, cfg.target, meta={})
    client = GuardedClient(scope, session, RateLimiter(0),
                           default_headers={"Authorization": "Bearer t3st"},
                           tls_verify=False)
    out = client.send("GET", lab_url + "/")
    entry = session.get_exchange(out["request_id"])
    hdrs = {k.lower(): v for k, v in entry["request"]["headers"].items()}
    assert hdrs.get("authorization") == "Bearer •••redacted•••"
    assert hdrs.get("host", "").startswith("127.0.0.1")


def test_redirect_hops_count_against_budget(lab_url, tmp_path):
    """Each followed redirect is a real wire request and must consume the
    request budget - otherwise a redirect loop multiplies the cap by 8."""
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path)
    scope = ScopeGuard(cfg.target, allow_private=True)
    session = Session(tmp_path, cfg.target, meta={})
    client = GuardedClient(scope, session, RateLimiter(0),
                           tls_verify=False, max_requests=2)
    out = client.send("GET", lab_url + "/redirect?next=/item?id=1",
                      follow_redirects=True)
    assert out["status"] == 200
    assert client.sent == 2                     # 1 initial + 1 hop
    with pytest.raises(RequestBudgetExhausted):
        client.send("GET", lab_url + "/")


def test_proxy_routes_traffic(lab_url, tmp_path):
    """--proxy must actually route target traffic through the proxy -
    the operator's inspection point (Burp/ZAP) depends on it."""
    import threading
    import urllib.request
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    hits = []

    class _ForwardProxy(BaseHTTPRequestHandler):
        def do_GET(self):
            hits.append(self.path)
            data = urllib.request.urlopen(self.path, timeout=5).read()
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a):
            pass

    proxy = ThreadingHTTPServer(("127.0.0.1", 0), _ForwardProxy)
    threading.Thread(target=proxy.serve_forever, daemon=True).start()
    try:
        cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path)
        scope = ScopeGuard(cfg.target, allow_private=True)
        session = Session(tmp_path, cfg.target, meta={})
        client = GuardedClient(scope, session, RateLimiter(0),
                               proxy=f"http://127.0.0.1:{proxy.server_address[1]}")
        out = client.send("GET", lab_url + "/")
        assert out["status"] == 200
        assert hits and hits[0].startswith("http://127.0.0.1:")
    finally:
        proxy.shutdown()


def test_nuclei_arg_guards(ctx, tmp_path):
    """nuclei -l target files are scope-checked; a hand-made template
    file and code templates are refused; built-in template names pass."""
    from argus.tools.analysis import _nuclei_arg_check
    n = lambda toks: _nuclei_arg_check(ctx, toks)
    tl = tmp_path / "targets.txt"
    tl.write_text("http://evil.example/\n")
    assert n(["-l", str(tl)])
    tl.write_text("http://127.0.0.1/\n")
    assert n(["-l", str(tl)]) is None
    tpl = tmp_path / "evil.yaml"
    tpl.write_text("id: x\n")
    assert n(["-t", str(tpl), "-u", "http://x/"])
    assert n(["-code", "-u", "http://x/"])
    assert n(["-p", "http://proxy:8080", "-u", "http://x/"])
    assert n(["-o", "../res.txt", "-u", "http://x/"])
    assert n(["-u", "http://x/", "-t", "cves/"]) is None
