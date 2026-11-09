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


def test_deserialize_shares_the_rce_requirement():
    assert proof.spec_for("deserialize").required == proof.spec_for("rce").required
    assert proof.grade("deserialization", "uid=33(www-data) gid=33(www-data)",
                       [RCE_PROOF]).grade == "proven"


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
    assert proof.grade("lfi", "not found", [miss]).grade == "unproven"


def test_ssti_distinguishes_evaluation_from_an_echo():
    done = ex("r12", "http://t.local/hello?name=%7B%7B7*7%7D%7D", "Hello 49")
    echo = ex("r13", "http://t.local/hello?name=%7B%7B7*7%7D%7D", "Hello {{7*7}}")
    assert proof.grade("ssti", "Hello 49", [done]).grade == "proven"
    assert proof.grade("ssti", "Hello {{7*7}}", [echo]).grade == "unproven"


def test_idor_needs_two_subjects_and_a_difference():
    mine = ex("r14", "http://t.local/api/user/1", '{"id":1,"username":"me"}')
    theirs = ex("r15", "http://t.local/api/user/2", '{"id":2,"username":"admin"}')
    assert proof.grade("idor", '"username":"admin"', [theirs]).grade == "unproven"
    assert proof.grade("idor", '"username":"admin"',
                       [mine, theirs]).grade == "proven"
    # the boilerplate case: the quoted bytes are in both responses, so the
    # difference is the page and not the identity - the floor check fails and
    # nothing above unproven is available
    assert proof.grade("idor", '"username"', [mine, theirs]).grade == "unproven"


def test_jwt_needs_the_rejected_control():
    forged = ex("r16", "http://t.local/api/me", '{"role":"admin"}', 200,
                req_headers={"authorization": "Bearer forged"})
    bad = ex("r17", "http://t.local/api/me", "invalid signature", 401,
             req_headers={"authorization": "Bearer wrong"})
    assert proof.grade("jwt", '{"role":"admin"}', [forged]).grade == "candidate"
    assert proof.grade("jwt", '{"role":"admin"}', [forged, bad]).grade == "proven"


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
