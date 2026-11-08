#!/usr/bin/env python3
"""xss_context.py — locate the reflection context and which metachars survive.

web-xss says 'identify the context first'; nothing in this tree measures it.
This sends one inert canary carrying the meta-character set, finds where it
lands in the response, classifies the surrounding context (html text /
attribute quoted or bare / script block / script string / comment / url),
and reports per-character survival — verbatim, encoded, or stripped. The
context verdict narrows which payload *shape* the skill's references apply;
it is a measurement, not a finding — a reflected, unescaped context is a
candidate until the skill's confirming probe records evidence.

    python3 tools/web/xss_context.py --url 'http://h/s?q=x' --param q
    python3 tools/web/xss_context.py --url URL --body 'q={M}' --method POST
    python3 tools/web/xss_context.py --selftest
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.parse

import httpkit

_MARK = "xzq7"
_CHARSET = "<>'\"&=;()[]`/"
_CANARY = _MARK + _CHARSET + _MARK


def _fire(args, value):
    url, body = args["url"], args.get("body")
    if args.get("param"):
        if args.get("method", "GET") == "GET":
            q = urllib.parse.urlparse(url)
            pairs = urllib.parse.parse_qsl(q.query, keep_blank_values=True)
            pairs = [(k, value if k == args["param"] else v) for k, v in pairs]
            if args["param"] not in [k for k, _ in pairs]:
                pairs.append((args["param"], value))
            url = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(pairs)))
        else:
            enc = urllib.parse.urlencode({args["param"]: value})
            body = enc if not body else body + "&" + enc
    elif body:
        body = body.replace("{M}", urllib.parse.quote_plus(value))
    else:
        url = url.replace("{M}", urllib.parse.quote(value))
    return httpkit.request(url, method=args.get("method", "GET"),
                           headers=args.get("headers"), body=body,
                           timeout=args.get("timeout", 10))


def _survival(body: str) -> dict:
    """Per canary char: verbatim / html-encoded / gone."""
    out = {}
    for ch in _CHARSET:
        variants = {ch, html.escape(ch),
                    f"&#{ord(ch)};", f"&#x{ord(ch):x};",
                    f"%{ord(ch):02x}", f"%{ord(ch):02X}"}
        if ch in body:
            out[ch] = "verbatim"
        elif any(v in body for v in variants if v != ch):
            out[ch] = "encoded"
        else:
            out[ch] = "gone"
    return out


def _context(body: str, pos: int) -> str:
    """Classify the document context around the reflection position."""
    before = body[:pos]
    in_comment = before.rfind("<!--") > before.rfind("-->")
    last_lt, last_gt = before.rfind("<"), before.rfind(">")
    in_tag = last_lt > last_gt
    tag_text = before[last_lt:] if in_tag else ""
    if in_comment:
        return "html-comment"
    if in_tag:
        if re.search(r"=\s*$|=\s*[^\s'\"]*$", tag_text):
            return "attribute (bare)" if "'" not in tag_text and '"' not in tag_text \
                   else "attribute (quoted)"
        return "inside-tag"
    last_script = before.lower().rfind("<script")
    if last_script != -1 and before.lower().rfind("</script") < last_script:
        seg = before[last_script:]
        sq, dq, bt = seg.count("'") % 2, seg.count('"') % 2, seg.count("`") % 2
        if sq or dq or bt:
            return "script-string"
        return "script-code"
    return "html-text"


def probe(args) -> dict:
    r = _fire(args, _CANARY)
    body = r.get("body", "")
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    out = {"url": args["url"], "status": r.get("status"), "canary": _CANARY}
    if r.get("error"):
        out["error"] = r["error"]
        return out
    marks = [m.start() for m in re.finditer(re.escape(_MARK), body)]
    out["mark_hits"] = len(marks)
    if len(marks) < 2:
        out["verdict"] = "not-reflected"
        out["note"] = "canary absent or truncated — no usable reflection here; " \
                      "the falsifier for the class is close by"
        return out
    seg_start, seg_end = marks[0], marks[-1] + len(_MARK)
    segment = body[seg_start:seg_end]
    surv = _survival(segment)
    # locate where the charset sits between the two marks for context read
    ctx_pos = seg_start + len(_MARK)
    out["context"] = _context(body, ctx_pos)
    out["survival"] = surv
    verbatim = [c for c, s in surv.items() if s == "verbatim"]
    encoded = [c for c, s in surv.items() if s == "encoded"]
    out["verbatim"] = "".join(verbatim)
    out["encoded"] = "".join(encoded)
    ctx = out["context"]
    need = {"html-text": "<", "attribute (quoted)": "<>\"'",
            "attribute (bare)": "<>", "script-string": "'\"",
            "script-code": "<>", "html-comment": "-<>", "inside-tag": ">"}.get(ctx, "<>")
    can_close = any(c in verbatim for c in need)
    out["verdict"] = "context-breakable" if can_close else "reflected-sanitised"
    out["candidate_only"] = True
    out["note"] = ("context + verbatim metachars measured; the class's confirming "
                   "probe still owes a rendered-execution excerpt, not this table")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Page(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            v = q.get("q", [""])[0].replace('"', "&quot;")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(f'<html><body>you searched: {v}</body></html>'.encode())

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Page)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/?q=x"
    out = probe({"url": url, "param": "q", "method": "GET", "timeout": 5})
    srv.shutdown()
    assert out["context"] == "html-text", out
    assert "<" in out["verbatim"] and '"' in out["encoded"], out
    assert out["verdict"] == "context-breakable"
    print("xss_context selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--param")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--body", help="POST body; {M} marks the injection slot")
    ap.add_argument("--headers", nargs="*")
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
