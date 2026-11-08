#!/usr/bin/env python3
"""graphql_probe.py — introspection + field-suggestion enumeration.

web-graphql's first probe is one introspection query; when it is
disabled, one deliberately-unknown field whose error leaks suggestions.
This runs both: `introspect` sends the bounded __schema query and
summarizes types/queries/mutations; `suggest` fires one unknown field
and parses every 'did you mean' hint; `map` loops the suggestion oracle
over a seed list, bounded to --max fields, recovering the schema shape
without introspection. Everything is a CANDIDATE — a recovered field
name is a measurement, not an authorization result.

    python3 tools/web/graphql_probe.py introspect --url http://h/graphql
    python3 tools/web/graphql_probe.py suggest --url http://h/graphql --field nope
    python3 tools/web/graphql_probe.py map --url http://h/graphql --seed user,me,node
    python3 tools/web/graphql_probe.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import sys

import httpkit

_INTRO = {"query": "{__schema{queryType{name}mutationType{name}"
                  "subscriptionType{name}types{name kind}}}"}
_SUGGEST_RX = re.compile(r"[Dd]id you mean ([^?]+)\?")


def _send(args, query):
    hdrs = dict(args.get("headers") or {})
    hdrs.setdefault("Content-Type", "application/json")
    r = httpkit.request(args["url"], method="POST", headers=hdrs,
                        body=json.dumps({"query": query}),
                        timeout=args.get("timeout", 15))
    body = r.get("body", "")
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    try:
        return r.get("status"), json.loads(body)
    except Exception:
        return r.get("status"), {"_raw": body[:300]}


def introspect(args) -> dict:
    status, doc = _send(args, _INTRO["query"])
    out = {"url": args["url"], "status": status}
    schema = (((doc or {}).get("data") or {}).get("__schema"))
    if not schema:
        errs = (doc or {}).get("errors") or []
        out["introspection"] = "disabled-or-error"
        out["errors"] = [e.get("message", "")[:200] for e in errs][:3]
        out["note"] = "fall back to suggest/map — suggestion oracle"
        return out
    types = schema.get("types") or []
    out["introspection"] = "enabled"
    out["query_type"] = (schema.get("queryType") or {}).get("name")
    out["mutation_type"] = (schema.get("mutationType") or {}).get("name")
    out["subscription_type"] = (schema.get("subscriptionType") or {}).get("name")
    out["type_count"] = len(types)
    interesting = [t["name"] for t in types
                   if t.get("kind") == "OBJECT" and not t["name"].startswith("__")]
    out["object_types"] = interesting[:50]
    return out


def _hints(doc):
    hints = set()
    for e in (doc or {}).get("errors") or []:
        m = _SUGGEST_RX.search(e.get("message", ""))
        if m:
            seg = m.group(1)
            quoted = re.findall(r'"([^"]+)"', seg)
            if quoted:
                hints.update(quoted)
            else:
                for part in re.split(r",| or ", seg):
                    p = part.strip()
                    if p:
                        hints.add(p)
    return hints


def suggest(args) -> dict:
    _, doc = _send(args, "{%s}" % args["field"])
    hints = sorted(_hints(doc))
    return {"field_sent": args["field"], "suggestions": hints,
            "errors": [(e.get("message") or "")[:200]
                       for e in (doc or {}).get("errors") or []][:3],
            "candidate_only": True}


def map_fields(args) -> dict:
    seen, queue = set(args.get("seed") or []), list(args.get("seed") or [])
    recovered = {}
    limit = args.get("max", 40)
    while queue and len(recovered) < limit:
        field = queue.pop(0)
        _, doc = _send(args, "{%s}" % field)
        hints = _hints(doc)
        ok = not (doc or {}).get("errors") or \
            all("did you mean" in (e.get("message") or "").lower()
                for e in doc["errors"])
        recovered[field] = {"accepted": bool(ok and (doc or {}).get("data")),
                            "suggestions": sorted(hints)}
        for h in hints:
            if h not in seen:
                seen.add(h)
                queue.append(h)
    return {"queried": len(recovered), "recovered": recovered,
            "candidate_only": True}


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Gql(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            q = json.loads(self.rfile.read(n).decode())["query"]
            if "__schema" in q:
                doc = {"data": {"__schema": {
                    "queryType": {"name": "Query"}, "mutationType": None,
                    "subscriptionType": None,
                    "types": [{"name": "Query", "kind": "OBJECT"},
                              {"name": "User", "kind": "OBJECT"}]}}}
            elif "nope" in q:
                doc = {"errors": [{"message":
                    'Cannot query field "nope" on type "Query". '
                    'Did you mean "users" or "me"?'}]}
            else:
                doc = {"data": {}}
            self.send_response(200)
            body = json.dumps(doc).encode()
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Gql)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/graphql"
    out = introspect({"url": url, "headers": {}, "timeout": 10})
    assert out["introspection"] == "enabled" and "User" in out["object_types"], out
    s = suggest({"url": url, "field": "nope", "headers": {}, "timeout": 10})
    assert "users" in s["suggestions"], s
    srv.shutdown()
    print("graphql_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("introspect", "suggest", "map"):
        p = sub.add_parser(name)
        p.add_argument("--url", required=True)
        p.add_argument("--headers", nargs="*")
        p.add_argument("--timeout", type=float, default=15)
        if name == "suggest":
            p.add_argument("--field", required=True)
        if name == "map":
            p.add_argument("--seed", required=True,
                           help="comma-separated starting field names")
            p.add_argument("--max", type=int, default=40)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.cmd:
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    if args.cmd == "map":
        a["seed"] = [s.strip() for s in args.seed.split(",") if s.strip()]
        out = map_fields(a)
    elif args.cmd == "suggest":
        out = suggest(a)
    else:
        out = introspect(a)
    httpkit.jprint(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
