"""Probes vs the lab app: each check must see its planted bug."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.tools import probes, web


def test_fingerprint_sees_stack(lab_url, ctx):
    out = web.fingerprint(ctx, lab_url)
    assert out["status"] == 200
    assert any("LabVuln" in h for h in out["stack_hints"])
    assert "content-security-policy" in out["missing_security_headers"]
    assert out["robots"]["status"] == 200
    assert "/debug" in out["robots"]["disallow"]


def test_fingerprint_flags_bad_header_values(lab_url, ctx):
    """Headers PRESENT but invalid/self-disabling - the audit miss a
    presence-only check cannot see."""
    out = web.fingerprint(ctx, lab_url + "/bad-headers")
    notes = " ".join(out["header_notes"])
    for token in ("x-frame-options", "x-content-type-options",
                  "strict-transport-security", "referrer-policy",
                  "content-security-policy"):
        assert token in notes, notes
    # and none of them counts as missing - they were sent, just broken
    assert "x-frame-options" not in out["missing_security_headers"]


def test_crawl_maps_surface(lab_url, ctx):
    out = web.crawl(ctx, lab_url, depth=1, max_pages=20)
    assert "/search" in out["endpoints"] or "/item" in out["endpoints"]
    assert any(f["action"].endswith("/search") for f in out["forms"])


def test_js_recon_finds_endpoints_and_secret(lab_url, ctx):
    out = web.js_recon(ctx, lab_url)
    eps = [e["endpoint"] for e in out["endpoints"]]
    assert any("/api/user" in e for e in eps)
    assert out["secret_candidates"]
    # deployed sourcemap is recovered and its sources scanned
    assert out["sourcemaps_found"] == 1
    assert any("/api/admin/export" in e for e in eps), eps
    sm_srcs = {e["source"] for e in out["endpoints"]}
    assert any(".map#" in s for s in sm_srcs)


def test_js_endpoint_regex_generic_clients():
    """Angular http.get / axios instances / superagent .get calls carry
    endpoints the fetch-only pattern missed; plain map.get('key') must
    not become a junk endpoint lead."""
    cases = [
        ("this.http.get('/items')", "/items"),
        ("api.post('/submit', body)", "/submit"),
        ("http.request('/v2/ping')", "/v2/ping"),
        ("axios.delete('/users/1')", "/users/1"),
        ("map.get('key')", None),
        ("dict.post('name')", None),
    ]
    for src, want in cases:
        m = web._JS_ENDPOINT.search(src)
        got = next((g for g in m.groups() if g), None) if m else None
        assert got == want, (src, got)


def test_reflection_probe(lab_url, ctx):
    out = probes.probe_reflection(ctx, lab_url + "/search?q=x", "q")
    assert out["reflected"]
    assert "<" in out["unescaped_chars"]


def test_sqli_probe_error_based(lab_url, ctx):
    out = probes.probe_sqli(ctx, lab_url + "/item?id=1", "id")
    assert "error" in out["verdict"] or "candidate" in out["verdict"]
    assert out["error_markers"] or out["true_false_similarity"] < 0.9


def test_sqli_probe_or_pair(lab_url, ctx):
    # /stock filters with AND visible=1 so both AND arms return the same
    # empty page - only the OR '1'='1 / '1'='2 pair can differentiate
    out = probes.probe_sqli(ctx, lab_url + "/stock?sku=x", "sku")
    assert "OR pair" in out["verdict"], out


def test_sqli_probe_union_cols(lab_url, ctx):
    # items selects 2 columns; ORDER BY 3 is the first failing n
    out = probes.probe_sqli(ctx, lab_url + "/item?id=1", "id", union_cols=6)
    assert out["union"]["columns"] == 2, out["union"]
    out2 = probes.probe_sqli(ctx, lab_url + "/product?id=1", "id",
                             union_cols=6)
    assert out2["union"]["columns"] == 2, out2["union"]
    assert out2["union"]["context"] == "numeric", out2["union"]


def test_time_probe_cmd(lab_url, ctx):
    out = probes.probe_time(ctx, lab_url + "/ping?host=1", "host", delay_s=2)
    assert "cmd" in out["verdict"]


def test_ssti_probe(lab_url, ctx):
    out = probes.probe_ssti(ctx, lab_url + "/hello?name=x", "name")
    assert "ssti candidate" in out["verdict"]


def test_ssti_eval_and_reflect(lab_url, ctx):
    """Engines that render the expr AND echo the raw input (error-page
    style) must still count - expect is a random sum that cannot occur
    naturally."""
    out = probes.probe_ssti(ctx, lab_url + "/hello2?name=x", "name")
    assert "ssti candidate" in out["verdict"], out
    hit = next(r for r in out["results"] if not r.get("negative"))
    assert hit["also_reflected"] is True, hit


def test_lfi_probe(lab_url, ctx):
    out = probes.probe_lfi(ctx, lab_url + "/download?file=x", "file")
    assert "confirmed marker" in out["verdict"]


def test_redirect_probe(lab_url, ctx):
    out = probes.probe_redirect(ctx, lab_url + "/redirect?next=/", "next")
    # client-side redirect via meta-refresh (no Location header)
    out2 = probes.probe_redirect(ctx, lab_url + "/jsredirect?next=/", "next")
    assert "client-side" in out2["verdict"], out2
    assert "open redirect" in out["verdict"]
    # raw-echo redirector also lands javascript: in Location -> DOM XSS
    assert "javascript:" in out["verdict"], out
    assert out["variants"][0].get("javascript_scheme"), out
    out3 = probes.probe_redirect(ctx, lab_url + "/safedirect?next=/", "next")
    assert "protocol-relative" in out3["verdict"], out3


def test_idor_probe(lab_url, ctx):
    out = probes.probe_idor(ctx, lab_url + "/api/user/2")
    assert "idor candidate" in out["verdict"], out


def test_idor_probe_post_body(lab_url, ctx):
    # object id lives inside the JSON body, not the URL
    out = probes.probe_idor(ctx, lab_url + "/api/order", method="POST",
                            data='{"order": 5}')
    assert "idor candidate" in out["verdict"], out


def test_idor_probe_query_id(lab_url, ctx):
    out = probes.probe_idor(ctx, lab_url + "/api/user/2?x=1")
    assert "idor candidate" in out["verdict"] or "neighbors" in out["verdict"], out


def test_ssrf_probe(lab_url, ctx):
    out = probes.probe_ssrf(ctx, lab_url + "/fetch?url=x", "url")
    assert "ssrf" in out["verdict"], out
    hits = [h for h in out["results"] if h["differs"]]
    assert hits, out


def test_xxe_probe(lab_url, ctx):
    out = probes.probe_xxe(ctx, lab_url + "/xml")
    assert "xxe candidate" in out["verdict"], out
    xi = next(r for r in out["results"] if r["name"] == "xinclude-fallback")
    assert xi["marker"], xi


def test_csrf_probe(lab_url, ctx):
    out = probes.probe_csrf(ctx, lab_url + "/login")
    assert "csrf" in out["verdict"], out
    assert out["unprotected"], out
    # JSON API processed via a CORS-simple content type = csrfable
    out2 = probes.probe_csrf(ctx, lab_url + "/api/config",
                             data="theme=light")
    assert "text/plain" in out2["verdict"], out2
    assert out2["content_type_replay"]["processed"]
    # a GET form whose action looks state-changing is a csrf lead even
    # without any POST form - browsers fire cross-origin GETs trivially
    out3 = probes.probe_csrf(ctx, lab_url + "/")
    assert "state-changing" in out3["verdict"], out3
    assert out3["stateful_get_forms"], out3


def test_enum_probe(lab_url, ctx):
    # /login answers "Unknown user" for a bogus name but "Wrong password
    # for admin" for a real one - the differential IS the enumeration
    out = probes.probe_enum(ctx, lab_url + "/login",
                            "username=x&password=x", "username")
    assert "enumeration candidate" in out["verdict"], out
    assert any(t["user"] == "admin" for t in out["results"]), out


def test_lockout_probe(lab_url, ctx):
    body = "username=x&password=x"
    out = probes.probe_lockout(ctx, lab_url + "/login2", body)
    assert "no lockout" in out["verdict"], out
    assert out["attempts"] == 10, out
    out = probes.probe_lockout(ctx, lab_url + "/login3", body)
    assert "throttling observed" in out["verdict"], out
    assert out["attempts"] < 10, out  # broke early on the 429


def test_massassign_probe(lab_url, ctx):
    out = probes.probe_massassign(
        ctx, lab_url + "/api/register",
        data='{"username":"t1","password":"x"}')
    assert "mass-assignment candidate" in out["verdict"], out
    assert "role" in out["accepted_fields"], out


def test_xfh_probe(lab_url, ctx):
    out = probes.probe_xfh(ctx, lab_url + "/reset")
    assert "host-header candidate" in out["verdict"], out
    out = probes.probe_xfh(ctx, lab_url + "/", restricted="/admin")
    assert "acl-bypass candidate" in out["verdict"], out


def test_nosqli_probe(lab_url, ctx):
    out = probes.probe_nosqli(ctx, lab_url + "/api/login",
                              '{"username":"admin","password":"x"}',
                              "password")
    assert "nosqli candidate" in out["verdict"], out
    form = next(h for h in out["results"] if h["op"] == "urlencoded[$ne]")
    assert form["differs"] and form["status"] == 200, out


def test_upload_probe(lab_url, ctx):
    out = probes.probe_upload(ctx, lab_url + "/upload")
    assert "upload candidate" in out["verdict"], out


def test_graphql_introspect(lab_url, ctx):
    from argus.tools import web
    out = web.graphql_introspect(ctx, lab_url + "/graphql")
    assert out["verdict"].startswith("schema introspected"), out
    names = {t["name"] for t in out["types"]}
    assert "User" in names, out
    # the lab answers ?query= too - GET-accepted queries are CSRF-able
    # and the tool must flag the transport
    assert out["get_transport"] is True, out
    assert out["get_request_id"], out


def test_graphql_suggestion_leak(lab_url, ctx):
    """Introspection off but 'did you mean' still enumerates the schema."""
    from argus.tools import web
    out = web.graphql_introspect(ctx, lab_url + "/graphql-strict")
    assert out["suggestion_leak"] is True, out
    assert "suggestions" in out["verdict"], out


def test_race_probe(lab_url, ctx):
    out = probes.probe_race(ctx, lab_url + "/redeem", n=8)
    assert "race candidate" in out["verdict"], out
    assert out["statuses"].get(200, 0) > 1, out
    # serial baseline disambiguates: a repeatable endpoint is not a race
    out2 = probes.probe_race(ctx, lab_url + "/hello", n=6)
    assert "repeatable" in out2["verdict"], out2


def test_deserialize_probe(lab_url, ctx):
    out = probes.probe_deserialize(ctx, lab_url + "/import?data=x", "data")
    assert "deserialization surface" in out["verdict"], out


def test_cache_probe(lab_url, ctx):
    out = probes.probe_cache(ctx, lab_url + "/cached")
    assert "cache-poisoning candidate" in out["verdict"], out
    out = probes.probe_cache(ctx, lab_url + "/profile")
    assert "path confusion" in out["verdict"], out
    assert out["deception"]["similarity"] > 0.9, out


def test_ppoll_probe(lab_url, ctx):
    out = probes.probe_ppoll(ctx, lab_url + "/api/config",
                             lab_url + "/api/config")
    assert "prototype-pollution candidate" in out["verdict"], out
    out = probes.probe_ppoll(ctx, lab_url + "/api/config2",
                             lab_url + "/api/config")
    assert "constructor.prototype" in out["verdict"], out


def test_cors_probe(lab_url, ctx):
    out = probes.probe_cors(ctx, lab_url + "/api/data")
    assert "credentials" in out["verdict"]


def test_jwt_weak_secret(ctx):
    import json as j
    from argus.tools.analysis import jwt_decode
    hdr = {"alg": "HS256", "typ": "JWT"}
    pay = {"sub": "a"}
    import base64, hashlib, hmac
    b = lambda o: base64.urlsafe_b64encode(j.dumps(o).encode()).decode().rstrip("=")
    h, p = b(hdr), b(pay)
    sig = base64.urlsafe_b64encode(
        hmac.new(b"secret123", f"{h}.{p}".encode(), hashlib.sha256).digest()
    ).decode().rstrip("=")
    out = jwt_decode(ctx, f"{h}.{p}.{sig}")
    assert out.get("recovered_secret") == "secret123"


def test_scope_blocks_outside(ctx):
    import pytest
    from argus.scope import ScopeError
    with pytest.raises(ScopeError):
        ctx.client.send("GET", "https://example.org/")


def test_smuggle_probe_desync(lab_url, ctx):
    out = probes.probe_smuggle(ctx, lab_url + "/desync")
    assert "cl.te desync candidate" in out["verdict"]
    assert out["statuses"] == [200, 501]


def test_smuggle_probe_tecl(lab_url, ctx):
    out = probes.probe_smuggle(ctx, lab_url + "/desync-cl")
    assert "te.cl desync candidate" in out["verdict"]
    assert out["statuses"][-1] == 501


def test_smuggle_probe_obf(lab_url, ctx):
    out = probes.probe_smuggle(ctx, lab_url + "/desync-obf")
    assert "obfuscated TE" in out["verdict"]


def test_smuggle_probe_clean(lab_url, ctx):
    out = probes.probe_smuggle(ctx, lab_url + "/desync-none")
    assert "no desync signal" in out["verdict"]


def test_disclosure_probe(lab_url, ctx):
    out = probes.probe_disclosure(ctx, lab_url)
    paths = {h["path"] for h in out["exposed"]}
    assert {"/.git/HEAD", "/.env", "/debug"} <= paths


def test_crlf_probe(lab_url, ctx):
    out = probes.probe_crlf(ctx, lab_url + "/redirect?next=/", "next")
    assert "crlf injection candidate" in out["verdict"]
    assert out["injected_header"] is True


def test_websocket_probe(lab_url, ctx):
    out = probes.probe_websocket(ctx, lab_url + "/ws")
    assert "confirmed" in out["verdict"]
    out2 = probes.probe_websocket(ctx, lab_url + "/")
    assert "no ws" in out2["verdict"]


def test_js_recon_finds_websocket(lab_url, ctx):
    from argus.tools.web import js_recon
    out = js_recon(ctx, lab_url + "/")
    assert any("ws://" in e["endpoint"] for e in out["websocket_endpoints"])


def test_send_raw_preserves_wire_text(lab_url, ctx):
    out = ctx.client.send_raw(
        lab_url + "/desync-none",
        requests=[{"method": "POST",
                   "headers": [["Content-Length", "6"],
                               ["Transfer-Encoding", "chunked"]],
                   "body": b"0\r\n\r\nG"}],
        tool="dbg")
    assert out["sends"][0]["status"] == 200
    entry = ctx.session._transcript[out["sends"][0]["request_id"]]
    text = entry["request"]["request_text"]
    assert "Content-Length: 6" in text
    assert "Transfer-Encoding: chunked" in text  # both headers survive


def test_send_raw_reads_unsolicited(lab_url, ctx):
    out = ctx.client.send_raw(
        lab_url + "/desync-cl",
        requests=[{"method": "POST", "reads": 2,
                   "headers": [["Content-Length", "4"],
                               ["Transfer-Encoding", "chunked"]],
                   "body": b"14\r\nGPOST / HTTP/1.1\r\n\r\n\r\n0\r\n\r\n"}],
        tool="dbg")
    assert [s["status"] for s in out["sends"]] == [200, 501]
    assert out["sends"][1]["solicited"] is False


def test_send_raw_scope_checked(lab_url, ctx):
    import pytest
    with pytest.raises(Exception):
        ctx.client.send_raw(
            "http://169.254.169.254/",
            requests=[{"method": "GET", "headers": [], "body": b""}],
            tool="dbg")


def test_transcript_redacts_operator_secrets(lab_url, tmp_path):
    """A recorded exchange must not persist the operator's live credential
    values - transcripts and rendered reports are shared artifacts. Header
    names stay (audit shows auth was sent); values are redacted."""
    from argus.config import Config
    from argus.scope import ScopeGuard
    from argus.ratelimit import RateLimiter
    from argus.session import Session
    from argus.httpclient import GuardedClient
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path)
    session = Session(tmp_path, lab_url, meta={})
    client = GuardedClient(
        ScopeGuard(lab_url, allow_private=True), session, RateLimiter(0),
        default_headers={"Authorization": "Bearer live-session-tok3n",
                         "Cookie": "sid=sekrit-value"},
        agent="t")
    out = client.send("GET", lab_url + "/", tool="t")
    client.close()
    entry = session._transcript[out["request_id"]]
    wire = entry["request"]["headers"]
    assert wire["authorization"] == "Bearer •••redacted•••"
    assert "sekrit-value" not in str(entry)
    assert "live-session-tok3n" not in str(entry)
    assert wire["cookie"].startswith("sid=")


def test_send_raw_redacts_secrets_keeps_structure(lab_url, tmp_path):
    """send_raw merges operator headers onto the wire; the recorded wire
    text must redact their values while keeping framing evidence intact."""
    from argus.config import Config
    from argus.scope import ScopeGuard
    from argus.ratelimit import RateLimiter
    from argus.session import Session
    from argus.httpclient import GuardedClient
    session = Session(tmp_path, lab_url, meta={})
    client = GuardedClient(
        ScopeGuard(lab_url, allow_private=True), session, RateLimiter(0),
        default_headers={"Authorization": "Bearer live-session-tok3n"})
    out = client.send_raw(
        lab_url + "/desync-none",
        requests=[{"method": "POST",
                   "headers": [["Content-Length", "6"],
                               ["Transfer-Encoding", "chunked"]],
                   "body": b"0\r\n\r\nG"}],
        tool="dbg")
    client.close()
    entry = session._transcript[out["sends"][0]["request_id"]]
    text = entry["request"]["request_text"]
    assert "live-session-tok3n" not in text
    assert "Authorization: •••redacted•••" in text
    assert "Transfer-Encoding: chunked" in text  # evidence untouched


def test_user_agent_header_is_not_a_secret(lab_url, tmp_path):
    """User-Agent is a public banner on every request, not a credential.
    It once fell into the >=8-char default-header sniff and every UA echo
    a target sent back was 'redacted' out of the evidence (e98d8b0)."""
    from argus.scope import ScopeGuard
    from argus.ratelimit import RateLimiter
    from argus.session import Session
    from argus.httpclient import GuardedClient
    session = Session(tmp_path, lab_url, meta={})
    client = GuardedClient(
        ScopeGuard(lab_url, allow_private=True), session, RateLimiter(0),
        agent="t")
    out = client.send("GET", lab_url + "/", tool="t")
    client.close()
    entry = session._transcript[out["request_id"]]
    ua = entry["request"]["headers"].get("user-agent", "")
    assert ua and "redacted" not in ua  # the banner survives the record
    # while a real credential under the same header map is still redacted
    client2 = GuardedClient(
        ScopeGuard(lab_url, allow_private=True), session, RateLimiter(0),
        default_headers={"X-Api-Key": "live-key-12345"}, agent="t")
    out2 = client2.send("GET", lab_url + "/", tool="t")
    client2.close()
    wire2 = session._transcript[out2["request_id"]]["request"]["headers"]
    assert wire2["x-api-key"] == "•••redacted•••"


def test_jwt_decode_malformed_inputs(ctx):
    """Malformed tokens must return an error dict, never raise - the model
    feeds this tool whatever string it finds in a response (57b02e6)."""
    from argus.tools.analysis import jwt_decode
    for bad in ("", "x", "a.b", "!.!.!", "a.b.c.d",
                "bnVsbA.bnVsbA.", 5, None, ["x"]):
        out = jwt_decode(ctx, bad)
        assert isinstance(out, dict)
        assert "error" in out or "issues" in out or "header" in out
    # a valid-JSON non-object segment decodes but is flagged, not trusted
    import base64
    seg = base64.urlsafe_b64encode(b'"x"').decode().rstrip("=")
    out = jwt_decode(ctx, f"{seg}.{seg}.{seg}")
    assert out.get("issues")


def test_lab_survives_garbage_content_length(lab_url):
    """A garbage Content-Length must not kill the lab handler thread -
    the lab is the deterministic fixture every other test stands on
    (5f6e473)."""
    import socket
    from urllib.parse import urlparse
    p = urlparse(lab_url)
    s = socket.create_connection((p.hostname, p.port), timeout=5)
    try:
        s.sendall(b"POST /search HTTP/1.1\r\nHost: x\r\n"
                  b"Content-Length: garbage\r\n\r\n")
        resp = s.recv(4096)
    finally:
        s.close()
    assert b"HTTP/1.1" in resp and b" 5" not in resp.split(b"\r\n")[0]


def test_csrf_samesite_none_is_weak():
    """SameSite=None is as CSRF-weak as absent - browsers send it
    cross-site by design."""
    assert probes._weak_samesite("sess=x; SameSite=None; Secure")
    assert probes._weak_samesite("sess=x; Path=/")
    assert not probes._weak_samesite("sess=x; SameSite=Lax")
    assert not probes._weak_samesite("sess=x; SameSite=Strict")


def test_probe_method_catches_unadvertised_trace(lab_url, ctx):
    """TRACE echo is caught even though the probe now fires whether or
    not Allow advertises it (the lab plants global XST)."""
    out = probes.probe_method(ctx, lab_url + "/")
    assert out["trace_attempt"]["echoes"] is True, out
    assert "cross-site tracing" in out["verdict"], out
