"""Drive argus's probes + proof gate against the THIRD-PARTY targets.

Not an autonomous assessment: the endpoints are named here, which is the
job an LLM would do. What this measures is narrower and still worth having -
whether the probe plane and the evidence gate work on applications this
project did not write, which is the objection a self-written lab invites.
"""
import pathlib
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

BIND = sys.argv[1] if len(sys.argv) > 1 else "192.168.223.221"
DVWA_COOKIE = sys.argv[2] if len(sys.argv) > 2 else ""
BWAPP_COOKIE = sys.argv[3] if len(sys.argv) > 3 else ""

CASES = [
    # (label, base url, cookie, probe callable, class)
    ("DVWA  SQLi",
     f"http://{BIND}:8081", DVWA_COOKIE,
     lambda ctx, b: probes.probe_sqli(
         ctx, b + "/vulnerabilities/sqli/?id=1&Submit=Submit", "id",
         extract_table="users", extract_columns="user,password"),
     "sqli"),
    ("DVWA  reflected XSS",
     f"http://{BIND}:8081", DVWA_COOKIE,
     lambda ctx, b: probes.probe_reflection(
         ctx, b + "/vulnerabilities/xss_r/?name=x", "name"),
     "xss"),
    # POST, because both of these endpoints are POST-only: driving them with
    # GET returned "no signal", which looked like the probe failing and was
    # the harness asking the wrong way round.
    ("DVWA  command injection",
     f"http://{BIND}:8081", DVWA_COOKIE,
     lambda ctx, b: probes.probe_cmdi(
         ctx, b + "/vulnerabilities/exec/", "ip", method="POST",
         data="ip=127.0.0.1&Submit=Submit"),
     "rce"),
    ("bWAPP SQLi (GET/search)",
     f"http://{BIND}:8080", BWAPP_COOKIE,
     lambda ctx, b: probes.probe_sqli(
         ctx, b + "/sqli_1.php?title=x&action=search", "title",
         extract_table="users", extract_columns="login,password"),
     "sqli"),
    ("bWAPP OS command injection",
     f"http://{BIND}:8080", BWAPP_COOKIE,
     lambda ctx, b: probes.probe_cmdi(
         ctx, b + "/commandi.php", "target", method="POST",
         data="target=www.nsa.gov&form=submit"),
     "rce"),
    ("Juice Shop SQLi (login)",
     f"http://{BIND}:3000", "",
     lambda ctx, b: probes.probe_sqli(
         ctx, b + "/rest/products/search?q=x", "q",
         extract_table="Users", extract_columns="email,password"),
     "sqli"),
]

_ORDER = {"proven": 3, "candidate": 2, "unproven": 1, "refused": 0}
print(f"{'target / class':32s} {'probe verdict':46s} grade")
print("-" * 92)
for label, base, cookie, call, klass in CASES:
    tmp = pathlib.Path(tempfile.mkdtemp())
    cfg = Config(target=base, allow_private=True, session_dir=tmp)
    scope = ScopeGuard(cfg.target, allow_private=True)
    sess = Session(tmp, cfg.target, meta={"bench": label})
    headers = {"Cookie": cookie} if cookie else None
    cl = GuardedClient(scope, sess, RateLimiter(0), tls_verify=False,
                       max_requests=200, default_headers=headers)
    ctx = Context(cfg=cfg, scope=scope, session=sess, client=cl,
                  skills_dir=pathlib.Path("/home/kali/ctf/argus/skills"))
    try:
        out = call(ctx, base)
    except Exception as exc:
        print(f"{label:32s} RAISED {type(exc).__name__}: {str(exc)[:38]}")
        cl.close()
        continue
    ex = [e for e in sess._transcript.values()
          if isinstance(e.get("response"), dict)]
    best = ("unproven", ["no evidence"])
    for e in ex:
        body = proof.resp_body(e)
        quotes = [l.strip() for l in body.splitlines()
                  if 6 <= len(l.strip()) <= 300]
        for q in quotes[:40]:
            v = proof.grade(klass, q, ex)
            if _ORDER.get(v.grade, 0) > _ORDER.get(best[0], 0):
                best = (v.grade, v.missing)
            if best[0] == "proven":
                break
        if best[0] == "proven":
            break
    verdict = str(out.get("verdict") or out.get("error") or "-")[:44]
    print(f"{label:32s} {verdict:46s} {best[0].upper()}")
    if best[0] != "proven":
        print(f"{'':32s} missing: {str(best[1])[:50]}")
    cl.close()
