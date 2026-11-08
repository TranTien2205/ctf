#!/usr/bin/env python3
"""ssti_probe.py — template-engine marker matrix. Stdlib only (httpkit).

The web-ssti skill's whole first phase is "render an arithmetic marker, read
which engine evaluated it". Nothing else in this tree fires that matrix. This
sends each marker into one named parameter and records, per marker: status,
whether the arithmetic result replaced the literal marker (evaluated), the
literal marker survived (reflected, no eval — itself an XSS-shaped signal),
or nothing came back. The engine hint it emits is a CANDIDATE — confirmation
still needs the class's own confirming probe and verbatim evidence.

    python3 tools/web/ssti_probe.py --url URL --param name
    python3 tools/web/ssti_probe.py --url URL --body 'name={M}&go=1'
    python3 tools/web/ssti_probe.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse

import httpkit

# (marker, evaluated-result, engine hint). Order matters: braces first because
# the {{7*'7'}} discriminator only means anything next to a {{7*7}} hit.
_MARKERS = [
    ("{{7*7}}",   "49",      "braces (jinja2/twig/nunjucks/tornado)"),
    ("{{7*'7'}}", "7777777", "jinja2/nunjucks (python string-repeat)"),
    ("${7*7}",    "49",      "dollar-brace (freemarker/thymeleaf/mako/EL)"),
    ("<%= 7*7 %>","49",      "erb/ejs/jsp style"),
    ("#{7*7}",    "49",      "hash-brace (pug/jade/ruby-interp)"),
    ("{7*7}",     "49",      "bare braces (smarty/velocity)"),
    ("*{7*7}",    "49",      "asterisk-brace (thymeleaf inline)"),
]


def _fire(base_args, value) -> dict:
    url = base_args["url"]
    body = base_args.get("body")
    if base_args.get("param"):
        if base_args.get("method", "GET") == "GET":
            q = urllib.parse.urlparse(url)
            pairs = urllib.parse.parse_qsl(q.query)
            pairs = [(k, value if k == base_args["param"] else v) for k, v in pairs]
            if base_args["param"] not in [k for k, _ in pairs]:
                pairs.append((base_args["param"], value))
            url = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(pairs)))
        else:
            enc = urllib.parse.urlencode({base_args["param"]: value})
            body = enc if not body else body + "&" + enc
    elif body:
        body = body.replace("{M}", urllib.parse.quote_plus(value) if base_args.get("urlencode") else value)
    else:
        url = url.replace("{M}", urllib.parse.quote(value))
    return httpkit.request(url, method=base_args.get("method", "GET"),
                           headers=base_args.get("headers"), body=body,
                           timeout=base_args.get("timeout", 10))


def probe(base_args) -> dict:
    results = []
    for marker, want, hint in _MARKERS:
        r = _fire(base_args, marker)
        body = r.get("body", "")
        if isinstance(body, bytes):
            body = body.decode("utf-8", "replace")
        rec = {"marker": marker, "status": r.get("status"), "bytes": len(body)}
        if r.get("error"):
            rec["verdict"] = "transport-error"
            rec["detail"] = r["error"]
        elif want in body and marker not in body:
            rec["verdict"] = "evaluated"
            rec["engine_hint"] = hint
            i = body.find(want)
            rec["excerpt"] = body[max(0, i - 40): i + len(want) + 40]
        elif marker in body:
            rec["verdict"] = "reflected-literal"
        else:
            rec["verdict"] = "gone"
        results.append(rec)
    evaluated = [r for r in results if r["verdict"] == "evaluated"]
    hints = list(dict.fromkeys(r.get("engine_hint") for r in evaluated))
    out = {"url": base_args["url"], "param": base_args.get("param"), "results": results}
    if evaluated:
        # jinja2 vs twig: {{7*'7'}} → 7777777 is python-family; twig gives 49
        py = any(r["marker"] == "{{7*'7'}}" and r["verdict"] == "evaluated" for r in results)
        braces = any(r["marker"] == "{{7*7}}" and r["verdict"] == "evaluated" for r in results)
        if py:
            out["engine_candidate"] = "jinja2-or-nunjucks (python string-repeat confirmed)"
        elif braces:
            out["engine_candidate"] = "braces engine, not python-string-repeat (twig or other)"
        else:
            out["engine_candidate"] = hints[0]
        out["candidate_only"] = True
    else:
        lit = [r for r in results if r["verdict"] == "reflected-literal"]
        out["engine_candidate"] = None
        out["note"] = (f"{len(lit)} marker(s) reflected literally — template evaluation not "
                       "observed; reflected input is a different signal") if lit else \
                      "no marker evaluated or reflected"
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Jinja(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            name = q.get("name", [""])[0]
            rendered = name.replace("{{7*7}}", "49").replace("{{7*'7'}}", "7777777")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f"hello {rendered}".encode())

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Jinja)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    out = probe({"url": url, "param": "name", "method": "GET", "timeout": 5})
    srv.shutdown()
    assert out["engine_candidate"].startswith("jinja2"), out
    ev = {r["marker"]: r["verdict"] for r in out["results"]}
    assert ev["{{7*7}}"] == "evaluated" and ev["{{7*'7'}}"] == "evaluated"
    assert ev["<%= 7*7 %>"] in ("reflected-literal", "gone")  # jinja doesn't eat erb marks
    print("ssti_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="target URL ({M} placeholder allowed in path/query)")
    ap.add_argument("--param", help="parameter name to carry the marker")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--body", help="POST body; use {M} where the marker goes")
    ap.add_argument("--urlencode", action="store_true", help="quote_plus the marker inside --body")
    ap.add_argument("--headers", nargs="*", help="'K: v' pairs")
    ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not (args.param or args.body or "{M}" in args.url):
        ap.print_help()
        return 2
    out = probe(vars(args) | {"headers": httpkit.parse_headers(args.headers)})
    httpkit.jprint(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
