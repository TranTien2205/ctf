"""One consistent measurement pass over every target, with the final gate.

Writes a table meant to be quoted in the evaluation chapter. Endpoints are
named by the operator for the third-party apps - that is the job an LLM
would do - so this measures the probe plane and the evidence gate, not
autonomous assessment.
"""
import json
import pathlib
import re
import sys
import tempfile

sys.path.insert(0, "/home/kali/ctf")
from argus import proof
from argus.config import Config
from argus.httpclient import GuardedClient
from argus.ratelimit import RateLimiter
from argus.scope import ScopeGuard
from argus.session import Session
from argus.tools import Context, probes

BIND = sys.argv[1]
DVWA_C, BWAPP_C = sys.argv[2], sys.argv[3]
TOK = re.compile(r"[A-Za-z0-9_.@$()=/:-]{6,200}")

CASES = [
    ("argus-lab", f"http://{BIND}:8777", "", "sqli", "SQLi /item",
     lambda c, b: probes.probe_sqli(c, b + "/item?id=1", "id",
                                    extract_table="users",
                                    extract_columns="username,password")),
    ("argus-lab", f"http://{BIND}:8777", "", "rce", "cmdi /ping",
     lambda c, b: probes.probe_cmdi(c, b + "/ping?host=127.0.0.1", "host")),
    ("DVWA", f"http://{BIND}:8081", DVWA_C, "sqli", "SQLi /vulnerabilities/sqli",
     lambda c, b: probes.probe_sqli(
         c, b + "/vulnerabilities/sqli/?id=1&Submit=Submit", "id",
         extract_table="users", extract_columns="user,password")),
    ("DVWA", f"http://{BIND}:8081", DVWA_C, "rce", "cmdi /vulnerabilities/exec",
     lambda c, b: probes.probe_cmdi(c, b + "/vulnerabilities/exec/", "ip",
                                    method="POST",
                                    data="ip=127.0.0.1&Submit=Submit")),
    ("DVWA", f"http://{BIND}:8081", DVWA_C, "xss", "reflected XSS /xss_r",
     lambda c, b: probes.probe_reflection(
         c, b + "/vulnerabilities/xss_r/?name=x", "name")),
    ("bWAPP", f"http://{BIND}:8080", BWAPP_C, "sqli", "SQLi /sqli_1.php",
     lambda c, b: probes.probe_sqli(c, b + "/sqli_1.php?title=x&action=search",
                                    "title", extract_table="users",
                                    extract_columns="login,password")),
    ("bWAPP", f"http://{BIND}:8080", BWAPP_C, "rce", "cmdi /commandi.php",
     lambda c, b: probes.probe_cmdi(c, b + "/commandi.php", "target",
                                    method="POST",
                                    data="target=www.nsa.gov&form=submit")),
    ("Juice Shop", f"http://{BIND}:3000", "", "sqli", "SQLi /rest/products/search",
     lambda c, b: probes.probe_sqli(c, b + "/rest/products/search?q=x", "q",
                                    extract_table="Users",
                                    extract_columns="email,password")),
]
_ORD = {"proven": 3, "candidate": 2, "unproven": 1, "refused": 0}
rows = []
for app, base, cookie, klass, label, call in CASES:
    tmp = pathlib.Path(tempfile.mkdtemp())
    cfg = Config(target=base, allow_private=True, session_dir=tmp)
    scope = ScopeGuard(cfg.target, allow_private=True)
    sess = Session(tmp, cfg.target, meta={"m": label})
    cl = GuardedClient(scope, sess, RateLimiter(0), tls_verify=False,
                       max_requests=300,
                       default_headers={"Cookie": cookie} if cookie else None)
    ctx = Context(cfg=cfg, scope=scope, session=sess, client=cl,
                  skills_dir=pathlib.Path("/home/kali/ctf/argus/skills"))
    try:
        out = call(ctx, base)
        err = ""
    except Exception as exc:
        out, err = {}, f"{type(exc).__name__}"
    ex = [e for e in sess._transcript.values()
          if isinstance(e.get("response"), dict)]
    best, quote = ("unproven", []), ""
    for e in ex:
        body = proof.resp_body(e)
        cands = [t for t in dict.fromkeys(TOK.findall(body))]
        cands += [x.strip() for x in re.split(r"<br\s*/?>|\n", body)
                  if 6 <= len(x.strip()) <= 300]
        for q in cands:
            v = proof.grade(klass, q, ex)
            if _ORD.get(v.grade, 0) > _ORD.get(best[0], 0):
                best, quote = (v.grade, v.missing), q
            if best[0] == "proven":
                break
        if best[0] == "proven":
            break
    ceiling = proof.spec_for(klass).ceiling or "proven"
    rows.append({"app": app, "class": klass, "label": label,
                 "requests": len(ex), "grade": best[0], "ceiling": ceiling,
                 "at_ceiling": _ORD[best[0]] >= _ORD[ceiling],
                 "quote": quote[:60], "missing": best[1],
                 "verdict": str(out.get("verdict") or err or "-")[:70]})
    cl.close()

print(f"{'app':11s} {'class':5s} {'reqs':>4s} {'grade':10s} {'ceil':10s} ok  quote")
print("-" * 104)
for r in rows:
    print(f"{r['app']:11s} {r['class']:5s} {r['requests']:4d} {r['grade']:10s} "
          f"{r['ceiling']:10s} {'Y' if r['at_ceiling'] else 'n'}   {r['quote'][:40]!r}")
print()
tot = len(rows)
at = sum(1 for r in rows if r["at_ceiling"])
print(f"{at}/{tot} cases reached the class ceiling; "
      f"{sum(r['requests'] for r in rows)} requests total")
pathlib.Path(sys.argv[4]).write_text(json.dumps(rows, indent=2), encoding="utf-8")
