#!/usr/bin/env python3
"""upload_probe.py — upload canary files, then classify what the server did.

The web-file-upload workflow is mechanical: a canary per candidate type,
upload, fetch back, and read whether the server stored it raw, executed it,
or mangled it. Nothing in this tree produced the files or graded the
fetch-back. `gen` writes a deterministic canary set (each carries UPMARK so
the verdict is greppable verbatim); `verify` fetches a named upload and
classifies executed / served-raw / blocked / gone — a candidate verdict,
because content-type and status decide which bypass the skill tries next.

    python3 tools/web/upload_probe.py gen --dir up/ [--mark UPMARK]
    python3 tools/web/upload_probe.py verify --url http://h/up/m.gif --expect-source '<?php'
    python3 tools/web/upload_probe.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import httpkit                          # noqa: E402

_PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQ"
    "AAAABJRU5ErkJggg==")
_GIF_1PX = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01" \
           b"\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"

_MARK = "UPMARK"


def canaries(mark: str) -> dict:
    """filename -> bytes. Each carries `mark` so the verdict greps verbatim."""
    php = f"<?php echo '{mark}-PHP-EXEC'; ?>".encode()
    return {
        "c_php_plain.php": php,
        "c_php_in_gif.gif": _GIF_1PX + php,
        "c_php_in_png.png": _PNG_1PX + php,
        "c_php_phtml.phtml": php,
        "c_php_caps.PhP": php,
        "c_svg.svg": (f"<svg xmlns='http://www.w3.org/2000/svg'>"
                      f"<script>/*{mark}-SVG*/</script><text>{mark}</text></svg>").encode(),
        "c_html.html": f"<html><body>{mark}-HTML</body></html>".encode(),
        "c_htaccess": b"AddType application/x-httpd-php .jpg\n",
        "c_txt.txt": f"{mark}-TXT".encode(),
    }


def cmd_gen(args) -> int:
    os.makedirs(args.dir, exist_ok=True)
    manifest = []
    for name, data in canaries(args.mark).items():
        p = os.path.join(args.dir, name)
        with open(p, "wb") as fh:
            fh.write(data)
        manifest.append({"file": p, "bytes": len(data),
                         "question": "served-raw / executed / rejected?"})
    print(json.dumps({"mark": args.mark, "files": manifest}, indent=1))
    return 0


def verify(args) -> dict:
    url = args["url"]
    r = httpkit.request(url, timeout=args.get("timeout", 10))
    body = r.get("body", "")
    if isinstance(body, bytes):
        body_text = body.decode("utf-8", "replace")
    else:
        body_text = body
    ct = (r.get("headers") or {}).get("content-type",
         (r.get("headers") or {}).get("Content-Type", ""))
    out = {"url": url, "status": r.get("status"), "content_type": ct,
           "bytes": len(body)}
    if r.get("error"):
        out["verdict"] = "transport-error"
        out["error"] = r["error"]
        return out
    mark = args.get("expect_source")
    if r.get("status") in (404, 403):
        out["verdict"] = "blocked-or-absent"
    elif mark and mark in body_text:
        out["verdict"] = "served-raw"
        i = body_text.find(mark)
        out["excerpt"] = body_text[max(0, i - 30): i + len(mark) + 30]
    elif mark and mark not in body_text and len(body_text) < 200 and body_text.strip():
        out["verdict"] = "executed-or-transformed"
        out["excerpt"] = body_text[:200]
        out["note"] = ("source marker absent but output present — the marker "
                       "was interpreted, not stored")
    elif not body_text.strip():
        out["verdict"] = "empty-response"
    else:
        out["verdict"] = "transformed-unrelated"
    out["candidate_only"] = True
    return out


def _selftest() -> int:
    import threading, tempfile
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    mark = "UPMARKT3ST"
    files = canaries(mark)
    php_raw = files["c_php_plain.php"].decode()

    class Up(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.endswith(".php"):
                # server executes php: source marker gone, output marker present
                self.send_response(200)
                self.end_headers()
                self.wfile.write(f"{mark}-PHP-EXEC".encode())
            elif self.path.endswith(".gif"):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(files["c_php_in_gif.gif"])
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Up)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    v_exec = verify({"url": base + "/x.php", "expect_source": "<?php", "timeout": 5})
    v_raw = verify({"url": base + "/x.gif", "expect_source": "<?php", "timeout": 5})
    srv.shutdown()
    assert v_exec["verdict"] == "executed-or-transformed", v_exec
    assert v_raw["verdict"] == "served-raw" and "<?php" in v_raw["excerpt"], v_raw
    with tempfile.TemporaryDirectory() as td:
        import argparse as ap
        ns = ap.Namespace(dir=td, mark=mark)
        assert cmd_gen(ns) == 0
        assert os.path.getsize(os.path.join(td, "c_php_plain.php")) > 10
    print("upload_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    g = sub.add_parser("gen")
    g.add_argument("--dir", required=True)
    g.add_argument("--mark", default=_MARK)
    g.set_defaults(fn=cmd_gen)
    v = sub.add_parser("verify")
    v.add_argument("--url", required=True)
    v.add_argument("--expect-source", help="verbatim source marker to look for (e.g. '<?php')")
    v.add_argument("--timeout", type=float, default=10)
    v.set_defaults(fn=lambda a: httpkit.jprint(verify(vars(a))) or 0)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if getattr(args, "fn", None):
        return args.fn(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
