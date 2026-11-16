"""Produce a SEALED, verifiable session per third-party target.

Same probes as probe_thirdparty.py, but the findings go through the real
`record_finding` tool - so the evidence gate decides the grade and the
session ends up hash-chained, reportable and re-verifiable with
`argus verify`. The endpoints are named here, which is the job an LLM would
do; everything after the naming is the system's own.
"""
import json
import pathlib
import sys

sys.path.insert(0, "/home/kali/ctf")
from argus import proof
from argus.config import Config
from argus.httpclient import GuardedClient
from argus.ratelimit import RateLimiter
from argus.report.markdown import render_report
from argus.scope import ScopeGuard
from argus.session import Session
from argus.tools import Context, probes, registry

BIND, OUTROOT = sys.argv[1], pathlib.Path(sys.argv[2])
DVWA_COOKIE, BWAPP_COOKIE = sys.argv[3], sys.argv[4]

TARGETS = {
    "dvwa": (f"http://{BIND}:8081", DVWA_COOKIE, [
        ("sqli", "critical", "SQL injection in /vulnerabilities/sqli id parameter",
         "SQL injection via the `id` parameter: the DBMS names itself in the "
         "error channel and a bounded UNION read returns rows from `users`.",
         "Use parameterised queries; never concatenate request values into SQL.",
         lambda ctx, b: probes.probe_sqli(
             ctx, b + "/vulnerabilities/sqli/?id=1&Submit=Submit", "id",
             extract_table="users", extract_columns="user,password")),
        ("rce", "critical", "OS command injection in /vulnerabilities/exec ip parameter",
         "The `ip` field reaches a shell: `id` output came back with this "
         "probe's own nonce, proving execution rather than reflection.",
         "Never pass request values to a shell; use argv and an allowlist.",
         lambda ctx, b: probes.probe_cmdi(
             ctx, b + "/vulnerabilities/exec/", "ip", method="POST",
             data="ip=127.0.0.1&Submit=Submit")),
    ]),
    "bwapp": (f"http://{BIND}:8080", BWAPP_COOKIE, [
        ("sqli", "critical", "SQL injection in sqli_1.php title parameter",
         "SQL injection via the `title` parameter: the engine names itself "
         "and a bounded UNION read returns rows from `users`.",
         "Use parameterised queries.",
         lambda ctx, b: probes.probe_sqli(
             ctx, b + "/sqli_1.php?title=x&action=search", "title",
             extract_table="users", extract_columns="login,password")),
        ("rce", "critical", "OS command injection in commandi.php target parameter",
         "The `target` field reaches a shell: `id` output came back with "
         "this probe's own nonce.",
         "Never pass request values to a shell.",
         lambda ctx, b: probes.probe_cmdi(
             ctx, b + "/commandi.php", "target", method="POST",
             data="target=www.nsa.gov&form=submit")),
    ]),
}

_TOK = __import__("re").compile(r"[A-Za-z0-9_.@$()=/-]{6,200}")

for name, (base, cookie, cases) in TARGETS.items():
    outdir = OUTROOT / name
    cfg = Config(target=base, allow_private=True, session_dir=outdir,
                 model="probe-driver", max_requests=400, rate_rps=0)
    scope = ScopeGuard(cfg.target, allow_private=True)
    sess = Session(outdir, cfg.target,
                   meta={"model": "probe-driver", "target_app": name,
                         "note": "endpoints named by the operator; probes, "
                                 "grading and report by argus"})
    cl = GuardedClient(scope, sess, RateLimiter(0), tls_verify=False,
                       max_requests=400,
                       default_headers={"Cookie": cookie} if cookie else None)
    ctx = Context(cfg=cfg, scope=scope, session=sess, client=cl,
                  skills_dir=pathlib.Path("/home/kali/ctf/argus/skills"))
    print(f"\n########## {name} ({base}) ##########")
    for klass, sev, title, desc, fix, call in cases:
        before = [e["id"] for e in sess._transcript.values()
                  if isinstance(e.get("response"), dict)]
        out = call(ctx, base)
        ex = [e for e in sess._transcript.values()
              if isinstance(e.get("response"), dict) and e["id"] not in before]
        print(f"  {klass:5s} probe: {str(out.get('verdict'))[:66]}")
        # the best honest quote this evidence supports, then let the GATE decide
        best, ids, quote = "unproven", [], ""
        for e in ex:
            body = proof.resp_body(e)
            # Split on <br> as well as newlines: DVWA renders a whole dump
            # inside ONE <pre> line, so a line filter alone offered a
            # 5000-character candidate and never the rows. Tokens first,
            # because a tester quotes one distinctive value, and no cap -
            # the earlier cap of 80 cut the candidate list before the
            # password hash that actually proves the read.
            import re as _re
            parts = _re.split(r"<br\s*/?>|\n", body)
            cands = [t for t in dict.fromkeys(_TOK.findall(body))]
            cands += [x.strip() for x in parts if 6 <= len(x.strip()) <= 300]
            for q in cands:
                v = proof.grade(klass, q, ex)
                if v.grade == "proven":
                    best, ids, quote = "proven", [x["id"] for x in ex], q
                    break
            if best == "proven":
                break
        if not quote:
            print(f"  {klass:5s} -> no quote reached proven; not recorded")
            continue
        res = registry.dispatch(ctx, "record_finding", {
            "title": title, "severity": sev, "category": klass, "url": base,
            "evidence_ids": ids, "evidence_excerpt": quote,
            "description": desc, "remediation": fix})
        r = res.get("result") or res
        print(f"  {klass:5s} -> recorded {r.get('recorded')} grade={r.get('grade')}")
    render_report(sess, cfg, summary="Probe-driven run: the operator named the endpoints; the probes, the evidence gate and this report are the system's own.")
    digest = sess.seal_artifacts()
    cl.close()
    print(f"  session: {outdir}  (sealed {str(digest)[:16]}...)")
