#!/usr/bin/env python3
"""ECB byte-at-a-time oracle attack: recover a server-appended secret.

crypto-triage names this shape "repeating 16-byte ciphertext blocks" —
an oracle that computes ECB(secret_prefix || attacker_input || secret)
or ECB(attacker_input || secret). Given only ciphertext access through
a URL template, this tool (1) proves the codebook shape, (2) measures
block size and any fixed prefix pad, then (3) recovers the appended
secret one byte at a time by dictionary matching.

  python3 tools/ecb_oracle.py --url 'http://t/e?d={PT}' shape --bs 16
  python3 tools/ecb_oracle.py --url 'http://t/e?d={PT}' crack --bs 16
  python3 tools/ecb_oracle.py --selftest

{PT} in the URL is replaced by the hex of our chosen plaintext; {PTB}
by standard base64. The response is expected to be hex ciphertext
(--hex), base64, or raw bytes. Bounded by --max-requests: byte-at-a-time
costs ~256 requests per recovered byte, so the budget is mandatory.

Falsifier first: run `shape`; if it reports no repeated block under
repeated input, this is not ECB (or input does not reach the cipher)
and `crack` output is meaningless. Random-prefix variants (cryptopals
#14 shape) need a per-request random offset — this tool requires the
prefix to be constant; see ../ctf-crypto/modern-ciphers-2.md.
"""
import argparse, base64, json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import quote

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "web"))
import httpkit  # noqa: E402

ALPHA = bytes(range(32, 127)) + b"\n\r\t{}_" + bytes(range(256))


def make_oracle(url_t, mode):
    def ask(pt):
        u = url_t.replace("{PT}", pt.hex()).replace(
            "{PTB}", quote(base64.b64encode(pt).decode()))
        r = httpkit.request(u, timeout=15)
        if not r["ok"]:
            raise RuntimeError("oracle request failed: %s" % r["error"])
        body = r["body"].strip()
        if mode == "hex":
            return bytes.fromhex(body)
        if mode == "b64":
            return base64.b64decode(body)
        return r["body_bytes"]
    return ask


def shape(oracle, bs):
    """Prove ECB-ness: feed 4 blocks of a repeating byte; a pair of equal
    ciphertext blocks = codebook. Also locate the prefix pad by scanning
    how many leading bytes must precede the repeats for them to align."""
    rep = bytes(4 * bs)
    probe = oracle(rep)
    seen = {}
    for i in range(0, len(probe) - bs, bs):
        blk = probe[i:i + bs]
        if blk in seen:
            return {"ecb": True, "block_size": bs,
                    "first_repeat_block": seen[blk],
                    "ct_blocks": len(probe) // bs,
                    "note": "repeating input produced a repeating block — "
                            "codebook confirmed; run crack"}
        seen[blk] = i // bs
    return {"ecb": False, "block_size": bs,
            "note": "no repeated block under 4 identical blocks of input "
                    "— not ECB, or input does not reach the cipher, or a "
                    "random prefix breaks alignment"}


def prefix_pad(oracle, bs):
    """Bytes needed before our input so a full repeated block aligns.
    Returns (pad_len, anchor_offset) or None if alignment never reached
    (constant prefix assumed; random prefix defeats this)."""
    for pad in range(bs):
        pt = bytes([0x58]) * pad + bytes(2 * bs)
        ct = oracle(pt)
        for i in range(0, len(ct) - 2 * bs + 1, bs):
            if ct[i:i + bs] == ct[i + bs:i + 2 * bs]:
                return {"pad": pad, "anchor_block": i // bs}
    return None


def crack(oracle, bs, max_req, budget):
    """Byte-at-a-time recovery of the appended secret after a controllable
    input. Assumes layout ECB(prefix_pad || our_input || SECRET)."""
    pad_info = prefix_pad(oracle, bs)
    if pad_info is None:
        return {"error": "could not align a repeated block — random prefix "
                         "or not ECB", "recovered": ""}
    pad = pad_info["pad"]
    anchor = pad_info["anchor_block"]

    def query_len(l):
        budget["n"] += 1
        if budget["n"] > max_req:
            raise RuntimeError("request budget exhausted at %d" % budget["n"])
        return oracle(bytes([0x41]) * pad + b"A" * l)

    secret = bytearray()
    base_len = len(query_len(0))
    for blk_idx in range(anchor, (base_len // bs) + 2):
        for pos in range(bs):
            short = bs - 1 - pos
            ref = query_len(short)
            target = ref[blk_idx * bs:(blk_idx + 1) * bs]
            known = b"A" * short + bytes(secret)
            hit = None
            for g in range(256):
                budget["n"] += 1
                if budget["n"] > max_req:
                    raise RuntimeError("budget exhausted — recovered so far "
                                       "returned partially")
                probe = oracle(bytes([0x41]) * pad + known + bytes([g]))
                if probe[blk_idx * bs:(blk_idx + 1) * bs] == target:
                    hit = g
                    break
            if hit is None:
                return {"recovered": secret.decode("utf-8", "replace"),
                        "recovered_hex": secret.hex(),
                        "requests": budget["n"], "done": True,
                        "note": "no byte matched — likely ran off the end "
                                "of the secret into padding"}
            secret.append(hit)
    return {"recovered": secret.decode("utf-8", "replace"),
            "recovered_hex": secret.hex(), "requests": budget["n"],
            "done": True}


def _selftest() -> int:
    """Toy 'AES': identity permutation blocks XORed with a fixed key —
    preserves the codebook property byte-at-a-time relies on."""
    bs = 16
    key = bytes(range(bs))
    secret = b"flag{ecb!}"
    prefix = b"HDR:"

    def toy(pt):
        data = prefix + pt + secret
        data += bytes([bs - len(data) % bs]) * (bs - len(data) % bs)
        return bytes(data[i] ^ key[i % bs] for i in range(len(data)))

    oracle = toy
    s = shape(oracle, bs)
    assert s["ecb"], s
    pi = prefix_pad(oracle, bs)
    assert pi and pi["pad"] == (bs - len(prefix) % bs) % bs, pi
    budget = {"n": 0}
    r = crack(oracle, bs, 100000, budget)
    assert r["recovered"].startswith("flag{ecb!}"), r
    # HTTP transport check: two probes prove the wrapper wires correctly
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            q = self.path.split("d=", 1)[-1].split("&")[0]
            try:
                ct = toy(bytes.fromhex(q))
            except ValueError:
                ct = b""
            self.send_response(200)
            self.end_headers()
            self.wfile.write(ct.hex().encode())

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    Thread(target=srv.serve_forever, daemon=True).start()
    try:
        o = make_oracle("http://127.0.0.1:%d/?d={PT}" % srv.server_port, "hex")
        assert o(b"A" * 16) == toy(b"A" * 16)
    finally:
        srv.shutdown()
    print("ecb_oracle selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", help="oracle URL; {PT}=hex pt, {PTB}=b64 pt")
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--resp", choices=["hex", "b64", "raw"], default="hex")
    ap.add_argument("--max-requests", type=int, default=256 * 4096)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("cmd", nargs="?", default="crack",
                    choices=["shape", "crack"])
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.url:
        ap.error("--url is required")
    oracle = make_oracle(a.url, a.resp)
    if a.cmd == "shape":
        print(json.dumps(shape(oracle, a.bs), indent=1))
        return 0
    budget = {"n": 0}
    try:
        out = crack(oracle, a.bs, a.max_requests, budget)
    except RuntimeError as e:
        out = {"error": str(e)}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
