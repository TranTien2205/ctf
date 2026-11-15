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


def test_excluded_path_bypass_attempts_denied():
    """httpx decodes %XX and resolves .. before the wire, so exclusions
    must be checked on the normalized path too."""
    g = ScopeGuard("https://target.example", exclude_paths=["/admin"],
                   allow_private=False)
    for u in ("https://target.example/%61dmin",
              "https://target.example/%2561dmin",   # double-encoded
              "https://target.example/x/../admin",
              "https://target.example/x/./../admin",
              "https://target.example/ADMIN/../admin",
              "https://target.example/x/%2e%2e/admin"):
        with pytest.raises(ScopeError, match="excluded"):
            g.check(u)
    # normalization must not over-block siblings
    g.check("https://target.example/x/../administer")
    g.check("https://target.example/%61dminister")


def test_excluded_path_iis_bypass_denied():
    """IIS-class targets fold case and treat \\ as a separator - the
    exclusion must match the same way or the guard is cosmetic."""
    g = ScopeGuard("https://target.example", exclude_paths=["/admin"],
                   allow_private=False)
    for u in ("https://target.example/ADMIN",
              "https://target.example/Admin/Panel",
              "https://target.example/x%5c..%5cadmin",
              "https://target.example/x\\..\\admin"):
        with pytest.raises(ScopeError, match="excluded"):
            g.check(u)
    g.check("https://target.example/administrator")  # no over-block


def test_one_slash_too_many_is_not_a_different_path():
    """Three bypasses, one rule: normpath preserves exactly two slashes.

    `posixpath.normpath` is POSIX-faithful about a path beginning with
    exactly two slashes being implementation-defined, so it leaves
    `//admin` alone while collapsing `///admin` to `/admin`. The guard was
    therefore refusing MORE slashes than it allowed, which is the shape of
    a normalization that disagrees with itself rather than one that is
    missing.

    All three forms are inside the threat model the two tests above
    already state. `//admin` goes on the wire as-is and nginx and Apache
    merge duplicate slashes by default. `/%2fadmin` is sent raw by httpx -
    `raw_path=b'/%2fadmin'` - so the target does the decoding and lands in
    the same place. `/\\admin` is the IIS separator the fold above exists
    for, and the fold produced `//admin`, which the same rule then spared.
    """
    g = ScopeGuard("https://target.example", exclude_paths=["/admin"],
                   allow_private=False)
    for u in ("https://target.example//admin",
              "https://target.example//ADMIN",
              "https://target.example/%2fadmin",
              "https://target.example/%2Fadmin",
              "https://target.example/\\admin",
              "https://target.example/%5cadmin",
              "https://target.example//admin/panel",
              "https://target.example/x/..//admin"):
        with pytest.raises(ScopeError, match="excluded"):
            g.check(u)
    # collapsing separators must not swallow a sibling, and over-blocking
    # here would be a silent loss of coverage rather than a loud one
    for u in ("https://target.example//administrator",
              "https://target.example//admin-tools",
              "https://target.example/x/admin",
              "https://target.example//public"):
        g.check(u)


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


def test_trailing_dot_fqdn_matches():
    """'t.example.' is the same DNS name as 't.example' (root marker) -
    normalizing avoids a false denial on self-links, without opening
    suffix-confusion (evil-t.example. still denied)."""
    g = ScopeGuard("http://t.example", allow_private=True)
    g._private_cache["t.example."] = False   # skip DNS in the unit check
    g.check("http://t.example./")
    assert g.host_allowed("T.EXAMPLE.")
    assert not g.host_allowed("evil-t.example.")
    assert not g.host_allowed(".")


def test_ipv6_only_private_host_denied(monkeypatch):
    """A hostname resolving ONLY via AAAA to ::1 must not read as public -
    gethostbyname raised for v6-only answers, so the old check failed open."""
    import socket
    def fake_gai(host, port, *a, **k):
        return [(socket.AF_INET6, socket.SOCK_STREAM, 6, "",
                 ("::1", 0, 0, 0))]
    monkeypatch.setattr(socket, "getaddrinfo", fake_gai)
    from argus.scope import _is_private_host
    assert _is_private_host("v6loop.example")


def test_mixed_records_denied_when_any_private(monkeypatch):
    """A host answering public+private together must not pass on the
    strength of the public record alone - the connector may pick either."""
    import socket
    def fake_gai(host, port, *a, **k):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.9", 0))]
    monkeypatch.setattr(socket, "getaddrinfo", fake_gai)
    from argus.scope import _is_private_host
    assert _is_private_host("mixed.example")


def test_all_public_records_allowed(monkeypatch):
    import socket
    def fake_gai(host, port, *a, **k):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0)),
                (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 0))]
    monkeypatch.setattr(socket, "getaddrinfo", fake_gai)
    from argus.scope import _is_private_host
    assert not _is_private_host("public.example")


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


def test_external_args_scope_scan(ctx):
    """The bare-arg scan must see targets that aren't URLs: hostnames, IPs,
    and IPv6 literals - `nmap ::1` must not slip past split(':')."""
    from argus.tools.analysis import _args_scope_check
    import pytest
    from argus.scope import ScopeError
    ok = lambda a: _args_scope_check(ctx, a)
    with pytest.raises(ScopeError):
        ok("-sV evil.example")           # bare hostname
    with pytest.raises(ScopeError):
        ok("-sV ::1")                    # IPv6 literal (was: empty split)
    with pytest.raises(ScopeError):
        ok("-sV [fe80::1]")              # bracketed IPv6
    with pytest.raises(ScopeError):
        ok("-u http://evil.example/")    # plain URL
    ok("-sV 127.0.0.1")                  # in-scope IP
    ok("-sV 127.0.0.1:8080")             # in-scope host:port
    ok("-p 80,443")                      # port list - not a host
    ok("--top-ports 5000")               # port arg - not a host


def test_the_arg_scan_is_as_wide_as_the_tool_it_guards(ctx):
    """Whatever curl will dial, this scan has to hand to the guard.

    `ScopeGuard.check` is not the defect in either case below - asked, it
    refuses all of these. The defect is that it was never asked, because
    the code deciding WHAT to ask about was narrower than the binary that
    receives the argument string.

    1. `_URL_RE` was case-sensitive while the token loop's "already
       handled above" skip was `(?i)`, so `HTTP://` was handled by neither.
    2. An `os.sep in tok` skip exempted every token containing a
       separator, and `host:port/path` is a URL curl accepts with no
       scheme. Measured with curl 8.x: `HTTP://127.0.0.1:1/`,
       `HTTPS://127.0.0.1:1/` and `127.0.0.1:1/path` all reach
       `(7) Failed to connect`, which is curl reporting that it parsed the
       argument and dialled it.

    The second half of this test is the half that matters: a scan tightened
    until it refuses ordinary tool arguments gets switched off by whoever
    hits it next.
    """
    from argus.tools.analysis import _args_scope_check
    import pytest
    from argus.scope import ScopeError

    for hostile in ("http://evil.example/x",      # the covered form
                    "HTTP://evil.example/x",      # case-sensitive finder
                    "HTTPS://evil.example/x",
                    "HtTp://evil.example/x",
                    "evil.example/path",          # scheme-less, with a path
                    "evil.example:8080/path",     # ...and a port
                    "EVIL.example/x"):
        with pytest.raises(ScopeError):
            _args_scope_check(ctx, hostile)

    # ...and every one of these is an argument a real run sends.
    for benign in ("-w /usr/share/wordlists/common.txt",
                   "-w wordlists/common.txt",
                   "-iL targets.txt",
                   "-oN /tmp/out.txt",
                   "-p 80,443",
                   "--top-ports 5000",
                   "-u http://127.0.0.1/FUZZ",
                   "-H 'User-Agent: argus/1.0'",
                   "--data-urlencode q=1"):
        _args_scope_check(ctx, benign)


def test_external_args_scope_scan_host_spellings(ctx):
    """Single-label and non-canonical IP spellings are targets too:
    'nmap localhost' scans the agent host, and nmap parses 127.1 /
    2130706433 even where this machine's resolver does not. Private
    spellings are denied against a public scope."""
    from argus.tools.analysis import _args_scope_check
    from argus.scope import ScopeGuard, ScopeError
    import pytest, types
    c = types.SimpleNamespace(scope=ScopeGuard("http://public.example"))
    for a in ("-sV localhost", "-sV 127.1", "-sV 2130706433",
              "-sV 0x7f000001", "-sV ::ffff:127.0.0.1"):
        with pytest.raises(ScopeError):
            _args_scope_check(c, a)
    _args_scope_check(c, "-p 80,443")   # ports are not hosts
    _args_scope_check(c, "--top-ports 5000")


def test_nmap_arg_guards(ctx, tmp_path):
    """nmap -iL files are scope-checked; local script paths, random
    targets, and out-of-cwd output are refused."""
    from argus.tools.analysis import _nmap_arg_check
    n = lambda toks: _nmap_arg_check(ctx, toks)
    f = tmp_path / "targets.txt"
    f.write_text("127.0.0.1\nevil.example\n")
    assert n(["-iL", str(f)])
    # IPv6 literals inside a target file must not slip past split(':')
    f.write_text("127.0.0.1\n::1\n")
    assert n(["-iL", str(f)])
    f.write_text("[fe80::1]\n")
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

        # httpx's signature is `iter_bytes(chunk_size=None)`, and a
        # fake with a MANDATORY argument is unfaithful to the thing
        # it stands in for: `_fetch_capped` passes no size now, so
        # it can come back to its deadline per arriving piece, and
        # these two fakes raised TypeError on a change the real
        # client accepts.
        def iter_bytes(self, chunk_size=None):
            return iter(())

    orig = ctx.client._client.stream

    class _StreamCtx:
        def __enter__(self):
            return _Resp()

        def __exit__(self, *a):
            return False

    def spy(method, url, **kw):
        calls.append(kw)
        return _StreamCtx()

    ctx.client._client.stream = spy
    try:
        ctx.client.send("GET", "http://127.0.0.1/")
        ctx.client.send("GET", "http://127.0.0.1/", timeout=3.0)
    finally:
        ctx.client._client.stream = orig
    assert "timeout" not in calls[0]
    assert calls[1]["timeout"] == 3.0


def test_response_body_read_is_bounded(ctx):
    """A response larger than BODY_CAP must cap the stored body AND flag
    truncated - the stream is abandoned instead of buffering it whole."""
    import httpx
    from argus.httpclient import BODY_CAP

    class _BigResp:
        status_code = 200
        headers = httpx.Headers({"content-type": "text/plain"})
        encoding = "utf-8"
        url = "http://127.0.0.1/"

        # httpx's signature is `iter_bytes(chunk_size=None)`, and a
        # fake with a MANDATORY argument is unfaithful to the thing
        # it stands in for: `_fetch_capped` passes no size now, so
        # it can come back to its deadline per arriving piece, and
        # these two fakes raised TypeError on a change the real
        # client accepts.
        def iter_bytes(self, chunk_size=None):
            # three 128KB chunks = 384KB > 200KB cap
            for _ in range(3):
                yield b"A" * 131072

    class _Ctx:
        def __enter__(self):
            return _BigResp()

        def __exit__(self, *a):
            return False

    orig = ctx.client._client.stream
    ctx.client._client.stream = lambda *a, **k: _Ctx()
    try:
        out = ctx.client.send("GET", "http://127.0.0.1/")
    finally:
        ctx.client._client.stream = orig
    assert out["body_truncated_at"] == BODY_CAP
    assert len(out["body"]) <= BODY_CAP
    # persisted transcript body is bounded too
    entry = ctx.session._transcript[out["request_id"]]
    assert entry["response"]["truncated"] is True
    assert len(entry["response"]["body"]) <= BODY_CAP


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


def test_multicast_is_private_and_a_public_address_still_passes():
    """The boundary refused RFC1918 and loopback and allowed multicast.

    Measured against a PUBLIC target with `allow_private` off: `localhost`
    and `10.0.0.1` were refused, `224.0.0.1` and `239.255.255.250` - the
    SSDP group, a local-network address - were allowed. The host still had
    to be in scope, so this was never an allowlist bypass; it was a
    disagreement about what counts as private inside a module whose job is
    to refuse before any bytes are sent.

    The second half of this test is the half that keeps the fix honest: a
    real public address must still pass, or the repair is just a stricter
    gate.
    """
    guard = ScopeGuard("http://example.com/",
                       extra_hosts=["10.0.0.1", "224.0.0.1",
                                    "239.255.255.250", "93.184.216.34"],
                       allow_private=False)
    assert guard.allow_private is False
    guard.check("http://example.com/x")
    guard.check("http://93.184.216.34/x")
    for host in ("10.0.0.1", "224.0.0.1", "239.255.255.250"):
        with pytest.raises(ScopeError):
            guard.check(f"http://{host}/x")


def test_ipv4_mapped_ipv6_was_not_the_gap():
    """Checked rather than assumed - the obvious guess was wrong.

    `::ffff:127.0.0.1` looks like a classic way past a loopback check, and
    `ipaddress` already resolves the mapped forms: it reports loopback for
    that and link-local for `::ffff:169.254.169.254`. Asserting it keeps a
    future reader from "fixing" what is not broken, and catches a stdlib
    change if one ever lands.
    """
    import ipaddress

    from argus.scope import _ip_private

    for text in ("::ffff:127.0.0.1", "::ffff:10.0.0.1",
                 "::ffff:169.254.169.254", "64:ff9b::7f00:1",
                 "::1", "fc00::1", "fe80::1"):
        assert _ip_private(ipaddress.ip_address(text)), text
    for text in ("8.8.8.8", "93.184.216.34", "2606:4700::1111"):
        assert not _ip_private(ipaddress.ip_address(text)), text


def test_a_bundled_poc_does_not_follow_the_target_off_scope():
    """`run_exploit` checks the argv; the PoC then chose its own host.

    The scripts under `argus/resources/exploits/` run as subprocesses with
    no ScopeGuard, no rate limiter and no transcript, and
    `urllib.request.urlopen` follows up to ten redirects by default,
    re-attaching the original headers to each new host. So an in-scope
    target answering `302 -> http://other/` moved the PoC onto a host the
    guard refuses, with its forged credential attached, while the recorded
    `exploit_run` event still named the in-scope argument and carried no
    trace of the host that produced the bytes.

    Measured before the fix: the second server received
    `Authorization: Bearer <forged>` and the PoC exited 0, printing the
    body as proof.
    """
    import http.server
    import socketserver
    import subprocess
    import sys
    import threading
    from pathlib import Path

    seen = {}

    class _Final(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen["auth"] = self.headers.get("Authorization")
            body = b'{"user":"admin","role":"admin"}'
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass

    final = socketserver.TCPServer(("127.0.0.1", 0), _Final)
    fport = final.server_address[1]

    class _Redirect(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{fport}/api/me")
            self.end_headers()

        def log_message(self, *a):
            pass

    redirect = socketserver.TCPServer(("127.0.0.1", 0), _Redirect)
    rport = redirect.server_address[1]
    threading.Thread(target=final.serve_forever, daemon=True).start()
    threading.Thread(target=redirect.serve_forever, daemon=True).start()
    try:
        poc = (Path(__file__).resolve().parent.parent / "argus" / "resources"
               / "exploits" / "lab-jwt-forge" / "exploit.py")
        out = subprocess.run([sys.executable, str(poc),
                              f"http://127.0.0.1:{rport}"],
                             capture_output=True, text=True, timeout=60)
    finally:
        final.shutdown()
        redirect.shutdown()

    assert seen.get("auth") is None, (
        "the forged credential followed the target's redirect to a host "
        "the scope guard never saw")
    assert out.returncode != 0, out.stdout
    assert "not following a redirect" in out.stdout, out.stdout
    assert str(fport) in out.stdout, (
        "the PoC must name the host it refused to follow: " + out.stdout)


def test_an_exclusion_that_excludes_nothing_is_refused_not_discarded():
    """`--exclude /` was stored, reported, and enforced against nothing.

    `ScopeGuard` keeps `p.rstrip("/")` and its enforcement loop skips a
    falsy prefix, so `/` and `//` became `""`. The entry excluded nothing
    while `exclude_paths` stayed truthy as `['']`, `describe()` printed
    "excluded paths: " with an empty value, and the operator's original `/`
    survived into meta.json for the report to print as an enforced
    restriction. Every other malformed value in `load_config` raises; this
    one was silent, and silently not enforcing a no-go area is the worst
    direction for this flag to fail in.
    """
    import argparse
    import tempfile

    import pytest

    from argus.config import load_config
    from argus.scope import ScopeGuard

    def _args(exclude):
        return argparse.Namespace(
            api_key="k", auth_token=None, header_file=None, header=[],
            scope=[], exclude=list(exclude), target="http://127.0.0.1:1",
            model=None, max_turns=1, max_requests=1, max_time=1, rate=0,
            goal="", operator="", proxy="", llm_max_tokens=1,
            mcp_config=None, resume=None, allow_private=True,
            tls_verify=False, no_external=False, quiet=True,
            session_dir=tempfile.mkdtemp(), tools="")

    for bad in ("/", "//", "///"):
        with pytest.raises(SystemExit, match="exclude"):
            load_config(_args([bad]))
    # a real path is still accepted, and still normalised
    cfg = load_config(_args(["admin/", "/logout"]))
    assert cfg.exclude_paths == ["/admin/", "/logout"], cfg.exclude_paths

    # and a guard built directly - tests, cli.py, the team plane - drops an
    # entry it cannot match rather than reporting one it is not enforcing
    g = ScopeGuard("http://t.test", allow_private=True,
                   exclude_paths=["/", "//", "/admin"])
    assert g.exclude_paths == ["/admin"], g.exclude_paths
    assert "excluded paths: /admin" in g.describe(), g.describe()
