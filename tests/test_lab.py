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


def test_time_probe_cmd(lab_url, ctx):
    out = probes.probe_time(ctx, lab_url + "/ping?host=1", "host", delay_s=2)
    assert "cmd" in out["verdict"]


def test_ssti_probe(lab_url, ctx):
    out = probes.probe_ssti(ctx, lab_url + "/hello?name=x", "name")
    assert "ssti candidate" in out["verdict"]


def test_lfi_probe(lab_url, ctx):
    out = probes.probe_lfi(ctx, lab_url + "/download?file=x", "file")
    assert "confirmed marker" in out["verdict"]


def test_redirect_probe(lab_url, ctx):
    out = probes.probe_redirect(ctx, lab_url + "/redirect?next=/", "next")
    # client-side redirect via meta-refresh (no Location header)
    out2 = probes.probe_redirect(ctx, lab_url + "/jsredirect?next=/", "next")
    assert "client-side" in out2["verdict"], out2
    assert out["verdict"] == "open redirect"


def test_idor_probe(lab_url, ctx):
    out = probes.probe_idor(ctx, lab_url + "/api/user/2")
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


def test_xfh_probe(lab_url, ctx):
    out = probes.probe_xfh(ctx, lab_url + "/reset")
    assert "host-header candidate" in out["verdict"], out


def test_nosqli_probe(lab_url, ctx):
    out = probes.probe_nosqli(ctx, lab_url + "/api/login",
                              '{"username":"admin","password":"x"}',
                              "password")
    assert "nosqli candidate" in out["verdict"], out


def test_upload_probe(lab_url, ctx):
    out = probes.probe_upload(ctx, lab_url + "/upload")
    assert "upload candidate" in out["verdict"], out


def test_graphql_introspect(lab_url, ctx):
    from argus.tools import web
    out = web.graphql_introspect(ctx, lab_url + "/graphql")
    assert out["verdict"] == "schema introspected", out
    names = {t["name"] for t in out["types"]}
    assert "User" in names, out


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


def test_ppoll_probe(lab_url, ctx):
    out = probes.probe_ppoll(ctx, lab_url + "/api/config",
                             lab_url + "/api/config")
    assert "prototype-pollution candidate" in out["verdict"], out


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
