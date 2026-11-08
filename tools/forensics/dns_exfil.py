#!/usr/bin/env python3
"""Reassemble data smuggled out inside DNS query names (DNS tunnelling/exfil).

Classic CTF shape: a capture full of queries like
  3f2a.aGVsbG8gd29y.bGQ.example.com  or  deadbeef01.attacker.tld
where every subdomain label above the controlled domain carries one
encoded chunk. This tool extracts the queries in packet order (or by a
leading index label), strips the suffix domain, joins the chunks and
tries hex / base32 / base64 decoders — reporting whichever produces
printable output.

Input is either a pcap (uses pcap_parse's stdlib parser) or a text file
with one query name per line (--names). Bounded: query count capped,
decoded output capped at 8 MiB.

  python3 tools/forensics/dns_exfil.py --pcap cap.pcap
  python3 tools/forensics/dns_exfil.py --names queries.txt --domain evil.tld
  python3 tools/forensics/dns_exfil.py --selftest
"""
import argparse, base64, binascii, collections, json, os, re, struct, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcap_parse import parse_pcap, _decode, _dns_name

_MAXQ = 200_000
_HEX = re.compile(r"^[0-9a-fA-F]+$")
_B32 = re.compile(r"^[A-Z2-7]+=*$")
_B64 = re.compile(r"^[A-Za-z0-9+/]+={0,2}$")


def queries_from_pcap(path):
    lt, pkts, err = parse_pcap(path)
    if err:
        return None, err
    out = []
    for _ts, raw in pkts[:_MAXQ]:
        d = _decode(raw)
        if not d or d[0] != "udp" or (d[3] != 53 and d[4] != 53):
            continue
        pay = d[5]
        if len(pay) < 12 or struct.unpack(">H", pay[4:6])[0] < 1:
            continue
        name, _ = _dns_name(pay, 12)
        if name:
            out.append(name.lower())
    return out, None


def guess_domain(names):
    """Most common trailing 2-3 label suffix = the controlled domain."""
    cnt = collections.Counter()
    for n in names:
        lab = n.split(".")
        for k in (2, 3):
            if len(lab) > k:
                cnt[".".join(lab[-k:])] += 1
    return cnt.most_common(1)[0][0] if cnt else ""


def chunks(names, domain):
    """Strip suffix; yield (index-or-None, chunk-string) in packet order."""
    seq = []
    suffix = "." + domain if domain else ""
    for n in names:
        if domain and not n.endswith(suffix):
            continue
        head = n[: -len(suffix)] if suffix else n
        head = head.strip(".")
        if not head:
            continue
        lab = head.split(".")
        idx = None
        if lab[0].isdigit() and len(lab) > 1:
            idx, lab = int(lab[0]), lab[1:]
        seq.append((idx, "".join(lab)))
    if any(i is not None for i, _ in seq):
        seq.sort(key=lambda t: (t[0] is None, t[0]))
    return [c for _i, c in seq]


def try_decoders(blob):
    """Try hex / base32 / base64 on the joined chunk string."""
    cand = []
    s = re.sub(r"[^A-Za-z0-9+/=]", "", blob)
    up = s.upper()
    if len(s) % 2 == 0 and _HEX.match(s):
        try:
            cand.append(("hex", binascii.unhexlify(s)))
        except binascii.Error:
            pass
    b32pad = (-len(up)) % 8
    if _B32.match(up + "=" * b32pad):
        try:
            cand.append(("base32", base64.b32decode(up + "=" * b32pad)))
        except binascii.Error:
            pass
    pad = (-len(s)) % 4
    if _B64.match(s + "=" * pad):
        try:
            cand.append(("base64", base64.b64decode(s + "=" * pad)))
        except binascii.Error:
            pass
    return cand


def score(pt):
    if not pt:
        return -1
    good = sum(32 <= b < 127 or b in (9, 10, 13) for b in pt)
    return good / len(pt)


def _selftest() -> int:
    pt = b"flag{dn5_3xfil_w0rks} and some more plaintext to decode!!"
    enc = base64.b32encode(pt).decode().rstrip("=")
    dom = "evil.tld"
    names = []
    for i in range(0, len(enc), 30):
        names.append(f"{i//30}.{enc[i:i+30]}.{dom}")
    names.append("www.google.com")  # noise query that must be skipped
    c = chunks(names, dom)
    cand = try_decoders("".join(c))
    best = max(cand, key=lambda t: score(t[1]))
    assert best[0] == "base32", best
    assert best[1] == pt, best[1]
    assert guess_domain(names) == dom
    # also verify the file-based path
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n".join(names))
        path = f.name
    try:
        loaded = [l.strip().lower() for l in open(path) if l.strip()]
        c2 = chunks(loaded, guess_domain(loaded))
        cand2 = try_decoders("".join(c2))
        assert max(cand2, key=lambda t: score(t[1]))[1] == pt
    finally:
        os.unlink(path)
    print("dns_exfil selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pcap")
    ap.add_argument("--names", help="text file, one query name per line")
    ap.add_argument("--domain", help="controlled suffix; default: auto-detect")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.pcap:
        names, err = queries_from_pcap(a.pcap)
        if err:
            print(json.dumps({"error": err}))
            return 1
    elif a.names:
        names = [l.strip().lower() for l in open(a.names, errors="replace")
                 if l.strip()][: _MAXQ]
    else:
        ap.error("one of --pcap or --names is required")
    dom = a.domain or guess_domain(names)
    cs = chunks(names, dom)
    blob = "".join(cs)
    cands = [(enc, data[: 8 << 20]) for enc, data in try_decoders(blob)]
    ranked = sorted(cands, key=lambda t: -score(t[1]))
    out = {
        "domain": dom, "queries_total": len(names),
        "queries_matching": len(cs), "chunk_bytes": len(blob),
        "candidates": [
            {"encoding": e, "printable_ratio": round(score(d), 3),
             "decoded_len": len(d),
             "head": d[:120].decode("utf-8", "replace"),
             "decoded_hex_head": d[:64].hex()}
            for e, d in ranked],
        "note": ("no decoder produced output — labels may be raw text, "
                 "encrypted, or the domain guess is wrong")
        if not ranked else "best candidate first; verify against flag format",
    }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
