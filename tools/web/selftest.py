#!/usr/bin/env python3
"""Offline self-test for tools/web/: every primitive against a local mock target.

No network, no challenge instance, no optional dependency required — it starts a
loopback HTTP server that imitates the five shapes these tools exist for (a file
read, a record-id oracle, a bulk oracle, a sloppy sanitizer, a PDF renderer),
runs each CLI against it, and asserts on the JSON each one printed.

    python3 tools/web/selftest.py           # JSON verdict, exit 0 on PASS
    python3 tools/web/selftest.py --verbose # include each tool's own output
"""
import argparse
import html as html_mod
import json
import os
import re
import subprocess
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import httpkit  # noqa: E402

ORDERS = {str(n): {"id": n, "owner": "u%d" % (n % 3), "total": 10 * n}
          for n in (1, 2, 3, 7, 11, 42)}
ORDERS["42"]["note"] = "SELFTEST{idor_reached_another_owner}"

FILES = {
    "/proc/self/mountinfo":
        "28 24 0:25 / /proc rw,nosuid - proc proc rw\n"
        "31 24 8:1 /srv/chal/flag.txt /flag ro,relatime - ext4 /dev/sda1 ro\n",
    "/etc/hostname": "selftest-container\n",
    "/proc/self/environ": "PATH=/usr/bin\x00SESSION_SECRET=s3cr3t\x00",
    "/srv/chal/flag.txt": "SELFTEST{read_loop_followed_mountinfo}\n",
}


def _pdf(text):
    content = ("BT /F1 14 Tf 40 700 Td (%s) Tj ET" % text).encode()
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offs = bytearray(b"%PDF-1.4\n"), []
    for index, obj in enumerate(objs, 1):
        offs.append(len(out))
        out += b"%d 0 obj\n" % index + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offs:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" \
           % (len(objs) + 1, xref)
    return bytes(out)


class Mock(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _send(self, code, body, ctype="text/plain"):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/read":
            path = (query.get("file") or [""])[0]
            if path in FILES:
                return self._send(200, json.dumps({"content": FILES[path]}),
                                  "application/json")
            return self._send(404, json.dumps({"error": "no such file"}),
                              "application/json")
        if parsed.path.startswith("/order/"):
            oid = parsed.path.rsplit("/", 1)[-1]
            if oid in ORDERS:
                return self._send(200, json.dumps(ORDERS[oid]), "application/json")
            return self._send(404, json.dumps({"error": "order not found"}),
                              "application/json")
        if parsed.path == "/echo":                 # strips '<script' ONCE, then unescapes
            value = (query.get("q") or [""])[0]
            return self._send(200, "<div id=out>%s</div>"
                              % html_mod.unescape(value.replace("<script", "")),
                              "text/html")
        if parsed.path == "/render":
            return self._send(200, _pdf((query.get("name") or ["anon"])[0]),
                              "application/pdf")
        if parsed.path == "/ssti":
            value = (query.get("q") or [""])[0]
            return self._send(200, "<p>result: %s</p>"
                              % ("49" if value == "{{7*7}}" else value), "text/html")
        return self._send(404, "no route")

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8", "replace")
        if urllib.parse.urlparse(self.path).path == "/orders":
            try:
                ids = [str(i) for i in json.loads(raw).get("ids", [])]
            except ValueError:
                return self._send(400, "bad json")
            missing = [i for i in ids if i not in ORDERS]
            return self._send(200, json.dumps(
                {"found": [ORDERS[i] for i in ids if i in ORDERS],
                 "message": "not found: " + ", ".join(missing)}), "application/json")
        return self._send(404, "no route")


def run(argv):
    proc = subprocess.run([sys.executable] + argv, capture_output=True, text=True,
                          cwd=HERE)
    try:
        return json.loads(proc.stdout), proc
    except ValueError:
        return {"_unparsed_stdout": proc.stdout[:800],
                "_stderr": proc.stderr[:400]}, proc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    server = HTTPServer(("127.0.0.1", args.port), Mock)
    base = "http://127.0.0.1:%d" % server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    cases = []

    def case(name, argv_list, check):
        out, proc = run(argv_list)
        try:
            ok, detail = check(out)
        except Exception as exc:
            ok, detail = False, "%s: %s" % (type(exc).__name__, exc)
        entry = {"case": name, "pass": bool(ok), "detail": detail,
                 "exit": proc.returncode}
        if args.verbose or not ok:
            entry["output"] = out
        cases.append(entry)

    try:
        # 1. pdf_text: the flag is inside a PDF the target rendered
        case("pdf_text: live PDF over HTTP",
             ["pdf_text.py", base + "/render?name=SELFTEST%7Bpdf_ok%7D", "--compact"],
             lambda o: ("SELFTEST{pdf_ok}" in (o.get("text") or ""),
                        "extractor=%s chars=%s" % (o.get("extractor") or o.get("engine_used"),
                                                   o.get("chars"))))

        # 2. sanitizer_fuzz: the grammar must find the entity bypass of /echo
        case("sanitizer_fuzz: finds the entity bypass on a live endpoint",
             ["sanitizer_fuzz.py", "--url", base + "/echo?q={payload}",
              "--forbidden", "<script", "--urlencode", "--families",
              "raw,entity,splice", "--max-cases", "60", "--compact"],
             lambda o: (o["hits"] > 0,
                        "%d hits of %d cases run" % (o["hits"], o["total_cases"])))

        # 3. sanitizer_fuzz: a correct escaper must give a clean, countable 0-of-N
        case("sanitizer_fuzz: 0-of-N negative is recordable",
             ["sanitizer_fuzz.py", "--callable", "html:escape",
              "--forbidden", "<", "--compact"],
             lambda o: (o["hits"] == 0 and o["total_cases"] > 500
                        and o.get("verdict") == "clean",
                        "0 of %d cases produced a hit" % o["total_cases"]))

        # 4. read_loop: mountinfo names a bind mount, the loop follows it to the flag
        case("read_loop: mountinfo -> bind mount -> flag",
             ["read_loop.py", "--url", base + "/read?file={path}",
              "--profile", "container", "--extract", r'"content":\s*"(.*)"\s*}',
              "--extract-paths", "--compact"],
             lambda o: (any("SELFTEST{read_loop_followed_mountinfo}" in
                            str(r.get("findings", {}).get("flag_shape", ""))
                            for r in o["results"]),
                        o["verdict_line"]))

        # 5. id_sweep single: baseline separates the six real ids from 44 misses
        case("id_sweep: single-request oracle",
             ["id_sweep.py", "--url", base + "/order/{id}", "--range", "1-50",
              "--compact"],
             lambda o: (o["hits"] == 6 and
                        "SELFTEST{idor_reached_another_owner}" in
                        json.dumps(o["outcome"]["flag_shapes"]),
                        o["verdict_line"]))

        # 6. id_sweep bulk: same answer, 4 requests instead of 200
        case("id_sweep: bulk oracle names the misses",
             ["id_sweep.py", "--url", base + "/orders", "--method", "POST",
              "--header", "Content-Type: application/json",
              "--body", '{"ids":[{ids}]}', "--range", "1-200", "--bulk", "50",
              "--miss-regex", "not found: ([0-9, ]+)", "--compact"],
             lambda o: (sorted(o["outcome"]["hits"], key=int) ==
                        ["1", "2", "3", "7", "11", "42"] and o["requests_sent"] == 4,
                        "%s in %d requests" % (o["verdict_line"], o["requests_sent"])))

        # 7. http_probe: the gate command it prints must quote a real substring
        case("http_probe: post-probe argv quotes verbatim evidence",
             ["http_probe.py", "--url", base + "/ssti?q=%7B%7B7*7%7D%7D",
              "--challenge", "selftest-not-written", "--class", "web-ssti",
              "--evidence-regex", "result: 49", "--on-match", "confirms",
              "--evidence-kind", "class", "--compact"],
             lambda o: (o["verdict"] == "confirms" and
                        o["evidence"]["is_verbatim_substring"] and
                        "--verdict confirms" in o["post_probe_command"],
                        o["evidence"]["excerpt"]))

        # 8. http_probe: a dead connection can never be proposed as a confirm
        case("http_probe: transport failure downgrades to inconclusive",
             ["http_probe.py", "--url", "http://127.0.0.1:9/dead",
              "--challenge", "selftest-not-written", "--class", "web-ssti",
              "--evidence-regex", ".", "--on-match", "confirms",
              "--on-miss", "confirms", "--evidence-kind", "class",
              "--timeout", "3", "--compact"],
             lambda o: (o["verdict"] == "inconclusive" and
                        o["evidence"]["kind"] == "transport",
                        "; ".join(o["verdict_downgrades"])))
    finally:
        server.shutdown()

    failures = [c for c in cases if not c["pass"]]
    report = {"mode": "tools-web-selftest", "target": base,
              "total": len(cases), "failures": len(failures),
              "verdict": "PASS" if not failures else "FAIL", "cases": cases}
    httpkit.jprint(report, args.compact)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
