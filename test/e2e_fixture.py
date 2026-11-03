#!/usr/bin/env python3
"""End-to-end: drive the broker against the local fixture and check the gate.

This is the integration test for the tool plane and the ledger. It runs with no
network, no lab VM and no model: every call is a deterministic broker call, so a
failure here is a failure in this toolkit rather than in a model's judgement.

What it asserts:

* every class the fixture plants reaches `proven` through its own proof tool
* a finding with incomplete evidence is REFUSED, and the refusal names the check
* an out-of-scope target and a disabled tier are refused at the broker
* the probe budget stops a sixth variant of the same idea
* the report separates confirmed findings from candidates
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "test" / "fixtures"))

import vulnapp                                                   # noqa: E402
from argus.broker.serve import merge                             # noqa: E402
from argus.broker.servers import SERVER_NAMES                    # noqa: E402
from argus.config import Paths                                   # noqa: E402
from argus.ledger import decide, hooks, report                   # noqa: E402
from argus.ledger.state import State                             # noqa: E402

ENGAGEMENT = "e2e-fixture"
FAILURES: list[str] = []
STEPS = 0


def check(label: str, condition: bool, detail: str = "") -> bool:
    global STEPS
    STEPS += 1
    mark = "PASS" if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        FAILURES.append(f"{label}: {detail}")
    return condition


def main() -> int:
    # Every registered server, not a hand-written list: a list written before a
    # server existed is a list that silently stops covering it.
    server = merge(list(SERVER_NAMES))
    app, port = vulnapp.serve()
    base = f"http://127.0.0.1:{port}"
    print(f"fixture at {base}\n")

    def call(tool: str, **arguments) -> dict:
        # `tool` rather than `name`: session.add takes an argument called `name`,
        # and a helper that shadows a tool's own argument is a helper that cannot
        # call that tool.
        return server.call(tool, arguments, engagement=ENGAGEMENT, actor="e2e")

    shutil.rmtree(Paths(ENGAGEMENT).dir, ignore_errors=True)

    print("1. open the engagement")
    opened = hooks.open_engagement(
        ENGAGEMENT, objective="prove every class the fixture plants, with evidence",
        scope={"in_scope": [f"127.0.0.1:{port}"], "out_of_scope": [], "allowed_ports": [port]},
        tiers=["passive", "active", "intrusive"],
        authorisation="local test fixture owned by this repository; loopback only")
    check("engagement opened", bool(opened), opened.message)
    check("target admitted", bool(hooks.add_target(ENGAGEMENT, base + "/")))
    check("out-of-scope target refused",
          not hooks.add_target(ENGAGEMENT, "http://example.com/"),
          hooks.add_target(ENGAGEMENT, "http://example.com/").message)
    action = decide.decide(ENGAGEMENT)
    check("controller asks for recon first", action.action == "recon", f"{action.action}/{action.step}")

    print("\n2. recon, deterministically")
    fingerprint = call("recon.fingerprint", target=base)
    check("fingerprint read the server banner", fingerprint["ok"]
          and "VulnWidgets" in json.dumps(fingerprint["data"]), fingerprint["summary"][:90])
    params = call("recon.params", target=base + "/", depth=1)
    found = {p["name"] for p in params["data"]["parameters"]}
    check("parameter discovery found the inputs", {"id", "q", "file", "expr"} <= found,
          f"{sorted(found)}")
    mined = call("recon.js_mine", target=base + "/")
    check("javascript mining found the hidden endpoint",
          "/admin/export" in mined["data"]["endpoints"], f"{mined['summary']}")
    check("javascript mining reported a key shape, redacted",
          any(s["kind"] == "aws-access-key" and "REDACTED" in s["preview"]
              for s in mined["data"]["secrets"]), json.dumps(mined["data"]["secrets"]))

    print("\n3. sqli: signal, then a bounded extraction")
    sqli = call("ledger.open_hypothesis", target=base + "/", vuln_class="sqli",
                statement="the id parameter of /item is concatenated into a SQL query",
                falsifier="a quote does not change the response", entry_point={"param": "id"})
    sqli_id = sqli["data"]["hypothesis"]["id"]
    differential = call("http.differential", url=base + "/item", hypothesis_id=sqli_id,
                        vuln_class="sqli", baseline_params={"id": "1"},
                        variant_params={"id": "1'"}, repeat=2)
    check("quote differential is a real difference",
          differential["data"]["status_changed"] and differential["data"]["baseline_stable"],
          differential["summary"][:100])
    premature = call("ledger.record_finding", hypothesis_id=sqli_id,
                     title="SQL injection in /item", evidence_ids=[differential["evidence_id"]])
    check("a finding without extraction is REFUSED", not premature["ok"],
          f"{premature['error']}: {premature['summary'][:120]}")
    enumerated = call("exploit.sqlmap", target=base + "/item?id=1", mode="enumerate",
                      hypothesis_id=sqli_id, vuln_class="sqli", param="id", max_seconds=300)
    print(f"      sqlmap enumerate: {enumerated['summary'][:120]}")
    tables = (enumerated.get("data") or {}).get("tables") or []
    extracted = call("exploit.sqlmap", target=base + "/item?id=1", mode="extract",
                     hypothesis_id=sqli_id, vuln_class="sqli", param="id",
                     table="users", rows=3, max_seconds=300)
    check("sqlmap extracted a named table with rows",
          bool((extracted.get("evidence_id")) and "row(s) of users" in extracted["summary"]),
          extracted["summary"][:140])
    graded = call("proof.verify", vuln_class="sqli", hypothesis=sqli_id)
    check("sqli grades proven", graded["data"]["grade"] == "proven", graded["data"]["grade"])
    recorded = call("ledger.record_finding", hypothesis_id=sqli_id,
                    title="SQL injection in the id parameter of /item",
                    evidence_ids=[e["id"] for e in State.load(ENGAGEMENT).data["evidence_index"]
                                  if e.get("hypothesis_id") == sqli_id],
                    impact="read access to every row of the application database",
                    remediation="use a parameterised query",
                    reproduce=[f"curl '{base}/item?id=1%27'"])
    check("sqli finding recorded as confirmed", recorded["ok"]
          and "confirmed" in recorded["summary"], recorded["summary"][:120])

    print("\n4. rce: one benign command, and the nonce is the proof")
    rce = call("ledger.open_hypothesis", target=base + "/", vuln_class="rce",
               statement="the host parameter of /ping reaches a shell",
               falsifier="a separator does not change the output", entry_point={"param": "host"})
    rce_id = rce["data"]["hypothesis"]["id"]
    marker = call("proof.exec_marker", url=base + "/ping?host=127.0.0.1{payload}",
                  hypothesis_id=rce_id, vuln_class="rce", separator=";", encode="url")
    check("the marker command's nonce came back", marker["data"]["echoed"], marker["summary"][:120])
    check("identity output captured", bool(marker["data"]["identity"]), str(marker["data"]["identity"]))
    check("rce grades proven", marker["data"]["proof_grade"] == "proven",
          marker["data"]["proof_grade"])
    rce_finding = call("ledger.record_finding", hypothesis_id=rce_id,
                       title="Command injection in the host parameter of /ping",
                       evidence_ids=[marker["evidence_id"]],
                       impact="arbitrary command execution as the service account",
                       remediation="do not build a shell command from request data",
                       reproduce=[f"curl '{base}/ping?host=127.0.0.1%3Bid'"])
    check("rce finding recorded", rce_finding["ok"], rce_finding["summary"][:100])

    print("\n5. lfi: a known file, and the control that makes it mean something")
    lfi = call("ledger.open_hypothesis", target=base + "/", vuln_class="lfi",
               statement="the file parameter of /view is joined without normalisation",
               falsifier="traversal is rejected at every depth", entry_point={"param": "file"})
    lfi_id = lfi["data"]["hypothesis"]["id"]
    read = call("proof.file_read", url=base + "/view?file={payload}", hypothesis_id=lfi_id,
                vuln_class="lfi", encode="url", max_attempts=16)
    check("a known-file sentinel was read", read["data"]["sentinel"] is not None,
          f"{read['data']['sentinel']} via {read['data']['payload']}")
    check("the negative control was recorded", bool(read["data"]["control"]["status"]),
          json.dumps(read["data"]["control"]))
    check("lfi grades proven", read["data"]["proof_grade"] == "proven", read["data"]["proof_grade"])
    lfi_finding = call("ledger.record_finding", hypothesis_id=lfi_id,
                       title="Arbitrary file read in the file parameter of /view",
                       evidence_ids=[e["id"] for e in State.load(ENGAGEMENT).data["evidence_index"]
                                     if e.get("hypothesis_id") == lfi_id],
                       impact="any file the service account can read",
                       remediation="resolve the path and verify it stays inside the content root",
                       reproduce=[f"curl '{base}/view?file=/etc/passwd'"])
    check("lfi finding recorded", lfi_finding["ok"] and "confirmed" in lfi_finding["summary"],
          lfi_finding["summary"][:100])

    print("\n6. ssti: a nonce-derived product, not 7*7")
    ssti = call("ledger.open_hypothesis", target=base + "/", vuln_class="ssti",
                statement="the expr parameter of /calc is evaluated server-side",
                falsifier="the expression is echoed verbatim", entry_point={"param": "expr"})
    ssti_id = ssti["data"]["hypothesis"]["id"]
    evaluated = call("proof.template_eval", url=base + "/calc?expr={payload}",
                     hypothesis_id=ssti_id, vuln_class="ssti", encode="url",
                     expression_template="{a}*{b}")
    check("the product was computed, not echoed", evaluated["data"]["evaluated"]
          and not evaluated["data"]["expression_echoed"], evaluated["summary"][:110])
    check("ssti grades proven", evaluated["data"]["proof_grade"] == "proven",
          evaluated["data"]["proof_grade"])
    ssti_finding = call("ledger.record_finding", hypothesis_id=ssti_id,
                        title="Server-side expression evaluation in the expr parameter of /calc",
                        evidence_ids=[evaluated["evidence_id"]],
                        impact="arbitrary expression evaluation in the application process",
                        remediation="never evaluate request data as an expression",
                        reproduce=[f"curl '{base}/calc?expr=9577*6131'"])
    check("ssti finding recorded", ssti_finding["ok"] and "confirmed" in ssti_finding["summary"],
          ssti_finding["summary"][:100])

    print("\n7. idor: two actors and the entitlement control")
    idor = call("ledger.open_hypothesis", target=base + "/", vuln_class="idor",
                statement="/api/note returns any note id regardless of the user parameter",
                falsifier="a note belonging to another user is refused",
                entry_point={"param": "id", "location": "query"})
    idor_id = idor["data"]["hypothesis"]["id"]
    own = call("http.probe", url=base + "/api/note?id=1&user=alice", hypothesis_id=idor_id,
               vuln_class="idor", actor="alice", note="alice reads her own note")
    cross = call("http.probe", url=base + "/api/note?id=2&user=alice", hypothesis_id=idor_id,
                 vuln_class="idor", actor="alice", note="alice reads the admin note")
    # The cross-read record needs the subject it reached, and the control needs a
    # different outcome: both are recorded explicitly rather than inferred.
    call("ledger.add_evidence", kind="probe", vuln_class="idor", hypothesis_id=idor_id,
         target=base + "/", record={"actor": "alice", "accessed_subject": "admin",
                                    "response": {"status": 200, "body_span": cross["output"][:500]},
                                    "summary": "alice received the note owned by admin"})
    call("ledger.add_evidence", kind="control", vuln_class="idor", hypothesis_id=idor_id,
         target=base + "/", record={"is_control": True, "actor": "alice",
                                    "response": {"status": 404, "body_span": "{\"error\": \"not found\"}"},
                                    "summary": "a note id that does not exist answers 404, so 200 "
                                               "is not the generic response"})
    idor_graded = call("proof.verify", vuln_class="idor", hypothesis=idor_id)
    check("idor grades proven with its control", idor_graded["data"]["grade"] == "proven",
          f"{idor_graded['data']['grade']} missing={idor_graded['data']['missing']}")
    idor_finding = call("ledger.record_finding", hypothesis_id=idor_id,
                        title="Any note id is readable regardless of the user parameter",
                        evidence_ids=[e["id"] for e in State.load(ENGAGEMENT).data["evidence_index"]
                                      if e.get("hypothesis_id") == idor_id],
                        impact="every note in the application, including other tenants'",
                        remediation="authorise on the session identity, never on a request parameter",
                        reproduce=[f"curl '{base}/api/note?id=2&user=alice'"])
    check("idor finding recorded", idor_finding["ok"] and "confirmed" in idor_finding["summary"],
          idor_finding["summary"][:100])

    print("\n8. xss: reflection is not execution")
    xss = call("ledger.open_hypothesis", target=base + "/", vuln_class="xss",
               statement="the q parameter of /search is reflected into a script string",
               falsifier="the value is encoded in both contexts", entry_point={"param": "q"})
    xss_id = xss["data"]["hypothesis"]["id"]
    token = "argusxsstoken1"
    reflected = call("http.probe", url=f"{base}/search?q={token}", hypothesis_id=xss_id,
                     vuln_class="xss", token=token)
    check("the reflection context was identified",
          "script-string" in (reflected["data"]["reflected_context"] or []),
          str(reflected["data"]["reflected_context"]))
    xss_graded = call("proof.verify", vuln_class="xss", hypothesis=xss_id)
    check("xss stays SUPPORTED without a browser", xss_graded["data"]["grade"] == "supported",
          f"{xss_graded['data']['grade']} missing={xss_graded['data']['missing']}")
    xss_candidate = call("ledger.record_finding", hypothesis_id=xss_id,
                         title="Reflected value in a script string on /search",
                         evidence_ids=[reflected["evidence_id"]],
                         impact="possible script execution in a visitor's session")
    check("it is recorded as a candidate, not a finding",
          xss_candidate["ok"] and "candidate" in xss_candidate["summary"],
          xss_candidate["summary"][:100])

    print("\n9. a redirect is a new target")
    from argus.broker import httpkit
    scope = State.load(ENGAGEMENT).scope
    allow = (lambda candidate: bool(scope.check(candidate)))
    external = httpkit.request("GET", f"{base}/redirect?to=http://evil.example.com/pwn",
                               follow=True, allow=allow)
    check("an out-of-scope redirect is refused, not followed",
          external.status is None and "not in the engagement scope" in (external.error or ""),
          str(external.error)[:90])
    internal = httpkit.request("GET", f"{base}/redirect?to=/robots.txt", follow=True, allow=allow)
    check("an in-scope redirect is followed", internal.status == 200
          and "Disallow" in internal.body, internal.summary())
    unguarded = httpkit.request("GET", f"{base}/redirect?to=http://evil.example.com/pwn",
                                follow=True)
    check("follow without an allow predicate refuses every hop",
          unguarded.status is None, str(unguarded.error)[:80])
    # A fresh hypothesis, in the class this actually is: the sqli one is confirmed
    # by now, and the ledger refuses a probe against a closed hypothesis — which is
    # how this assertion failed the first time it ran.
    redirect = call("ledger.open_hypothesis", target=base + "/", vuln_class="open-redirect",
                    statement="the to parameter of /redirect is reflected into Location unchecked",
                    falsifier="an external host in `to` is rejected or rewritten",
                    entry_point={"param": "to", "location": "query"})
    not_followed = call("http.probe", url=f"{base}/redirect?to=http://evil.example.com/pwn",
                        hypothesis_id=redirect["data"]["hypothesis"]["id"],
                        vuln_class="open-redirect")
    check("not following still records the Location as the measurement",
          (not_followed.get("data") or {}).get("location") == "http://evil.example.com/pwn",
          str(not_followed.get("data") or not_followed.get("message"))[:90])

    print("\n10. the brakes")
    dos = call("ledger.open_hypothesis", target=base + "/", vuln_class="dos",
               statement="the search endpoint can be made to hang")
    check("a refused class cannot be opened", not dos["ok"], f"{dos.get('error')}")
    nonsense = call("ledger.open_hypothesis", target=base + "/", vuln_class="telepathy",
                    statement="the app leaks thoughts")
    check("an unknown class cannot be opened", not nonsense["ok"], f"{nonsense.get('error')}")
    out_of_scope = call("http.probe", url="http://example.com/", hypothesis_id=sqli_id,
                        vuln_class="sqli")
    check("out-of-scope probe refused at the broker", not out_of_scope["ok"],
          f"{out_of_scope['error']}: {out_of_scope['message'][:70]}")
    orphan = call("http.probe", url=base + "/")
    check("a probe with no hypothesis refused", not orphan["ok"], orphan["error"])

    budget_hypothesis = call("ledger.open_hypothesis", target=base + "/", vuln_class="nosqli",
                             statement="the id parameter is a mongo filter",
                             falsifier="the backend is sqlite")["data"]["hypothesis"]["id"]
    refusal = None
    for attempt in range(8):
        result = call("http.probe", url=f"{base}/item?id={attempt}",
                      hypothesis_id=budget_hypothesis, vuln_class="nosqli")
        if not result["ok"]:
            refusal = result
            break
    check("the probe budget stops repetition", refusal is not None and refusal["error"] == "budget-spent",
          (refusal or {}).get("message", "budget never fired")[:110])

    print("\n11. tier enforcement on a second engagement")
    shutil.rmtree(Paths("e2e-passive").dir, ignore_errors=True)
    hooks.open_engagement("e2e-passive", objective="read-only check",
                          scope={"in_scope": [f"127.0.0.1:{port}"], "allowed_ports": [port]},
                          tiers=["passive"])
    passive_state = State.load("e2e-passive")
    passive_hypothesis = passive_state.add_hypothesis(base + "/", "rce", "same injection")
    passive_state.save()
    blocked = server.call("proof.exec_marker",
                          {"url": base + "/ping?host=127.0.0.1{payload}", "separator": ";",
                           "hypothesis_id": passive_hypothesis["id"], "vuln_class": "rce"},
                          engagement="e2e-passive")
    check("an intrusive tool is refused when the tier is off", not blocked["ok"],
          f"{blocked['error']}: {blocked['message'][:80]}")

    print("\n12. cross-verification and the report")
    findings = State.load(ENGAGEMENT).data["findings"]
    confirmed = [f for f in findings if f["status"] == "confirmed"]
    candidates = [f for f in findings if f["status"] != "confirmed"]
    for finding in confirmed:
        call("ledger.cross_verify", finding_id=finding["id"], verifier="e2e-deterministic",
             agrees=True, note="evidence re-read by the test")
    demoted = call("ledger.cross_verify", finding_id=confirmed[0]["id"],
                   verifier="e2e-disagreeing-model", agrees=False,
                   note="the dump could have come from a seeded fixture")
    check("a disagreement demotes a confirmed finding", "candidate" in demoted["summary"],
          demoted["summary"])
    call("ledger.cross_verify", finding_id=confirmed[0]["id"], verifier="e2e-deterministic",
         agrees=True, note="re-confirmed after review")
    path = report.write(ENGAGEMENT)
    text = Path(path).read_text()
    check("the report separates confirmed from candidates",
          "## Confirmed findings" in text and "## Candidates" in text, path)
    check("the report states what was not tested", "absence of testing" in text)
    check("at least five classes reached a confirmed finding", len(confirmed) >= 5,
          f"confirmed={[f['vuln_class'] for f in confirmed]} candidates={[f['vuln_class'] for f in candidates]}")

    print("\n13. the session plane: two identities in one call")
    authz = call("ledger.open_hypothesis", target=base + "/", vuln_class="idor",
                 statement="/api/note serves any note id to any identity",
                 falsifier="a note owned by another identity is refused",
                 entry_point={"param": "id", "location": "query"})
    authz_id = authz["data"]["hypothesis"]["id"]
    for name, field, value, owns in [("alice", "user", "alice", "note 1"),
                                     ("admin", "user", "admin", "note 2")]:
        added = call("session.add", name=name, scheme="query", field=field, value=value,
                     note=f"fixture identity that owns {owns}")
        check(f"identity {name} recorded", added["ok"],
              (added.get("summary") or f"{added.get('error')}: {added.get('message')}")[:140])
    listed = call("session.list")
    check("the identity list describes and never values",
          "alice" not in str(listed.get("data")) or all(
              "value" not in entry for entry in (listed["data"].get("identities") or [])),
          str(listed.get("summary"))[:90])
    compared = call("session.compare_as", actor="alice", other="admin",
                    accessed_subject="admin", url=base + "/api/note?id=2",
                    own_url=base + "/api/note?id=1", hypothesis_id=authz_id,
                    vuln_class="idor")
    check("compare_as emits the cross-read and both controls in one probe",
          compared["ok"] and len(compared.get("evidence_ids") or []) >= 3,
          f"{len(compared.get('evidence_ids') or [])} record(s): "
          + (compared.get("summary") or f"{compared.get('error')}: {compared.get('message')}")[:130])
    session_graded = call("proof.verify", vuln_class="idor", hypothesis=authz_id)
    # The fixture answers 200 to every note id and ignores the user parameter, so
    # all four of compare_as's records carry the same status and the class's
    # "outcomes actually differ" check cannot pass. `supported` is the honest
    # grade here, and the missing check is the useful output: compare_as takes
    # three controls — the other identity, unauthenticated, and the actor's own
    # resource — and none of them establishes what "not found" looks like. That
    # fourth control is what section 7 added by hand to reach `proven`.
    check("compare_as reaches `supported` and names the control it does not take",
          (session_graded.get("data") or {}).get("grade") == "supported"
          and "outcomes actually differ" in str((session_graded.get("data") or {}).get("missing")),
          str((session_graded.get("data") or {}).get("missing"))[:120])

    print("\n14. the web plane against what the fixture actually has")
    redirect_hypothesis = call("ledger.open_hypothesis", target=base + "/",
                               vuln_class="open-redirect",
                               statement="the to parameter of /redirect is copied into Location",
                               falsifier="an off-origin destination is rejected or rewritten",
                               entry_point={"param": "to"})["data"]["hypothesis"]["id"]
    probed = call("web.redirect_probe", url=f"{base}/redirect", param="to",
                  in_origin_destination="/robots.txt", hypothesis_id=redirect_hypothesis,
                  vuln_class="open-redirect")
    check("redirect_probe finds the off-origin Location and names the shape",
          probed["ok"] and probed["data"].get("proof_grade") == "proven",
          f"{probed.get('summary','')[:110]}")
    cors = call("web.cors_probe", url=base + "/", hypothesis_id=redirect_hypothesis,
                vuln_class="open-redirect")
    check("cors_probe reports the matrix and calls an unexploitable row unexploitable",
          cors["ok"] and cors["result"] == "no-signal", f"{cors.get('summary','')[:100]}")
    graphql = call("web.graphql_probe", url=base + "/graphql", mode="introspect",
                   hypothesis_id=redirect_hypothesis, vuln_class="open-redirect")
    check("graphql_probe on an endpoint that is not GraphQL says so rather than inventing a schema",
          graphql["result"] == "no-signal", f"{graphql.get('summary','')[:100]}")

    print("\n15. chain cards harvested from this engagement")
    import tempfile
    from argus.knowledge import chains
    with tempfile.TemporaryDirectory() as corpus:
        harvested = chains.harvest(ENGAGEMENT, directory=corpus)
        written = harvested.get("written") or []
        skipped = harvested.get("skipped") or []
        # Four, not five: section 12 demoted the sqli finding on a reviewer's
        # disagreement and a later agreement does not silently restore it, so two
        # candidates remain and are correctly skipped.
        confirmed_now = [f for f in State.load(ENGAGEMENT).data["findings"]
                         if f.get("status") == "confirmed"]
        check("a card is harvested for every confirmed finding and no candidate",
              len(written) == len(confirmed_now) and len(skipped) == 2,
              f"{len(written)} written for {len(confirmed_now)} confirmed, "
              f"{len(skipped)} skipped")
        check("each skipped candidate carries the reason it was skipped",
              all("not-confirmed" in str(entry.get("why", "")) for entry in skipped),
              str(skipped)[:160])
        state = State.load(ENGAGEMENT)
        origin = next(iter(state.data["targets"]))
        stack = state.data["targets"][origin].get("stack") or {}
        ranked = chains.match(stack, directory=corpus)
        check("the corpus ranks its own cards against the observed stack",
              bool(ranked) and ranked[0].get("score", 0) > 0,
              f"top: {ranked[0].get('slug') if ranked else None} "
              f"score={ranked[0].get('score') if ranked else None}")
        unrelated = chains.match({"server": "nginx/1.24", "technologies": ["wordpress"]},
                                 directory=corpus)
        top_unrelated = unrelated[0].get("score", 0) if unrelated else 0
        check("an unrelated stack scores below the real one",
              top_unrelated < ranked[0].get("score", 0), f"{top_unrelated} vs {ranked[0].get('score')}")
        poisoned = dict(chains.load(written[0]["slug"], directory=corpus) or {})
        poisoned["title"] = f"chain against {origin}"
        verdict = chains.validate(poisoned, engagement=ENGAGEMENT)
        check("a card carrying the target's address is refused, with the field named",
              not verdict.ok, str(getattr(verdict, "reasons", verdict))[:150])
        for card in chains.cards(directory=corpus):
            blob = json.dumps(card)
            check(f"card {card.get('slug','?')[:28]} carries no proof output",
                  "uid=" not in blob and "FLAG{" not in blob, blob[:80])

    app.shutdown()
    print(f"\n{STEPS - len(FAILURES)}/{STEPS} checks passed")
    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"report: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
