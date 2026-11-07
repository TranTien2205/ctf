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


def test_reflection_probe(lab_url, ctx):
    out = probes.probe_reflection(ctx, lab_url + "/search?q=x", "q")
    assert out["reflected"]
    assert "<" in out["unescaped_chars"]


def test_sqli_probe_error_based(lab_url, ctx):
    out = probes.probe_sqli(ctx, lab_url + "/item?id=1", "id")
    assert "error" in out["verdict"] or "candidate" in out["verdict"]
    assert out["error_markers"] or out["true_false_similarity"] < 0.9


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
