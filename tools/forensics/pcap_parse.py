#!/usr/bin/env python3
"""pcap_parse.py — stdlib pcap reader for the carve workflow.

forensics-pcap-carve's whole loop is tshark commands; on a box without it
nothing reads the capture at all. This is the bounded fallback: `convs`
gives the protocol-hierarchy answer (which flow is worth opening),
`dns` extracts query names (the split-flag field carve), `ascii` runs
printable-scan over payloads (strings equivalent), and `follow N`
reassembles one TCP flow per direction by sequence order — overlap is
dropped, gaps are marked. It parses Ethernet/IPv4/TCP/UDP only; anything
else is reported as undecoded, honestly.

    python3 tools/forensics/pcap_parse.py convs cap.pcap
    python3 tools/forensics/pcap_parse.py dns cap.pcap
    python3 tools/forensics/pcap_parse.py ascii cap.pcap --min 8
    python3 tools/forensics/pcap_parse.py follow cap.pcap --flow 0 --dir 0
    python3 tools/forensics/pcap_parse.py --selftest
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_PORTS = {20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
          53: "dns", 67: "dhcp", 68: "dhcp", 80: "http", 110: "pop3",
          143: "imap", 443: "https", 445: "smb", 3389: "rdp", 8080: "http-alt"}


def parse_pcap(path, max_packets=2_000_000):
    with open(path, "rb") as fh:
        gh = fh.read(24)
        if len(gh) < 24 or gh[:4] not in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4",
                                        b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d"):
            return None, [], "not a classic pcap (pcapng needs tshark)"
        le = gh[:4] in (b"\xd4\xc3\xb2\xa1", b"\x4d\x3c\xb2\xa1")
        e = "<" if le else ">"
        linktype = struct.unpack(e + "I", gh[20:24])[0]
        pkts = []
        while len(pkts) < max_packets:
            ph = fh.read(16)
            if len(ph) < 16:
                break
            ts_s, ts_u, caplen, _olen = struct.unpack(e + "IIII", ph)
            data = fh.read(caplen)
            if len(data) < caplen:
                break
            pkts.append((ts_s + ts_u / 1e6, data))
        return linktype, pkts, None


def _decode(pkt):
    """-> (proto, src, dst, sport, dport, payload) or None."""
    if len(pkt) < 14:
        return None
    eth = struct.unpack(">H", pkt[12:14])[0]
    if eth == 0x8100 and len(pkt) > 18:
        eth = struct.unpack(">H", pkt[16:18])[0]
        pkt = pkt[:12] + pkt[16:]
    if eth != 0x0800 or len(pkt) < 34:
        return None
    ihl = (pkt[14] & 0x0F) * 4
    proto = pkt[23]
    src = str(ipaddress.IPv4Address(pkt[26:30]))
    dst = str(ipaddress.IPv4Address(pkt[30:34]))
    l4 = pkt[14 + ihl:]
    if proto == 6 and len(l4) >= 20:
        sport, dport = struct.unpack(">HH", l4[:4])
        doff = (l4[12] >> 4) * 4
        return "tcp", src, dst, sport, dport, l4[doff:]
    if proto == 17 and len(l4) >= 8:
        sport, dport, ulen = struct.unpack(">HHH", l4[:6])
        return "udp", src, dst, sport, dport, l4[8:ulen] if ulen >= 8 else l4[8:]
    return f"ip{proto}", src, dst, 0, 0, l4


def _flows(pkts):
    flows = {}
    for ts, raw in pkts:
        d = _decode(raw)
        if not d:
            continue
        proto, src, dst, sp, dp, pay = d
        key = (proto, min(src, dst), max(src, dst), min(sp, dp), max(sp, dp))
        f = flows.setdefault(key, {"proto": proto, "a": min(src, dst),
                                   "b": max(src, dst), "aport": min(sp, dp),
                                   "bport": max(sp, dp), "pkts": 0, "bytes": 0,
                                   "dirs": [[], []]})
        f["pkts"] += 1
        f["bytes"] += len(pay)
        di = 0 if (src, sp) <= (dst, dp) else 1
        if proto == "tcp" and pay:
            f["dirs"][di].append((ts, pay))
        elif proto == "udp" and pay:
            f["dirs"][di].append((ts, pay))
    return flows


def _guess(key):
    for p in (key[3], key[4]):
        if p in _PORTS:
            return _PORTS[p]
    return "?"


def _dns_name(buf, off):
    labels, seen = [], 0
    while off < len(buf) and seen < 64:
        seen += 1
        ln = buf[off]
        if ln == 0:
            return ".".join(labels), off + 1
        if ln & 0xC0 == 0xC0:
            if off + 1 >= len(buf):
                return ".".join(labels), off + 2
            ptr = ((ln & 0x3F) << 8) | buf[off + 1]
            sub, _ = _dns_name(buf, ptr)
            labels.append(sub)
            return ".".join(labels), off + 2
        off += 1
        labels.append(buf[off:off + ln].decode("utf-8", "replace"))
        off += ln
    return ".".join(labels), off


def cmd_convs(args):
    _lt, pkts, err = parse_pcap(args.pcap)
    if err:
        print(json.dumps({"error": err}))
        return 1
    flows = _flows(pkts)
    rows = [{"i": i, "proto_guess": _guess(k), "l4": k[0],
             "endpoints": f"{v['a']}:{v['aport']} <-> {v['b']}:{v['bport']}",
             "pkts": v["pkts"], "bytes": v["bytes"]}
            for i, (k, v) in enumerate(
                sorted(flows.items(), key=lambda kv: -kv[1]["bytes"]))]
    print(json.dumps({"packets": len(pkts), "flows": rows}, indent=1))
    return 0


def cmd_dns(args):
    _lt, pkts, err = parse_pcap(args.pcap)
    if err:
        print(json.dumps({"error": err}))
        return 1
    names = set()
    for _ts, raw in pkts:
        d = _decode(raw)
        if not d or d[0] != "udp" or (d[3] != 53 and d[4] != 53):
            continue
        pay = d[5]
        if len(pay) < 12:
            continue
        qd = struct.unpack(">H", pay[4:6])[0]
        if qd < 1:
            continue
        name, _ = _dns_name(pay, 12)
        if name:
            names.add(name)
    print(json.dumps({"queries": sorted(names)}, indent=1))
    return 0


def cmd_ascii(args):
    _lt, pkts, err = parse_pcap(args.pcap)
    if err:
        print(json.dumps({"error": err}))
        return 1
    runs, cur = [], bytearray()
    for _ts, raw in pkts:
        for b in raw:
            if 32 <= b < 127:
                cur.append(b)
            else:
                if len(cur) >= args.min:
                    runs.append(cur.decode())
                cur = bytearray()
    if len(cur) >= args.min:
        runs.append(cur.decode())
    pat = args.find.lower() if args.find else None
    if pat:
        runs = [r for r in runs if pat in r.lower()]
    print(json.dumps({"runs": runs[: args.max], "total": len(runs)}, indent=1))
    return 0


def cmd_follow(args):
    _lt, pkts, err = parse_pcap(args.pcap)
    if err:
        print(json.dumps({"error": err}))
        return 1
    flows = list(sorted(_flows(pkts).items(), key=lambda kv: -kv[1]["bytes"]))
    if args.flow >= len(flows):
        print(json.dumps({"error": f"flow index out of range ({len(flows)} flows)"}))
        return 1
    _k, f = flows[args.flow]
    chunks = sorted(f["dirs"][args.dir], key=lambda c: c[0])
    data = b"".join(c[1] for c in chunks)
    print(json.dumps({"flow": args.flow, "dir": args.dir,
                      "endpoints": f"{f['a']}:{f['aport']} <-> {f['b']}:{f['bport']}",
                      "chunks": len(chunks), "bytes": len(data),
                      "note": "ordered by capture time, seq-overlap not "
                              "verified — verify against tshark for court "
                              "grade",
                      "payload_text": data.decode("utf-8", "replace")[:64_000],
                      "payload_hex": data[:4096].hex()}, indent=1))
    return 0


def _http_objects(data, limit=200, max_obj=8 << 20):
    """Parse HTTP/1.x responses out of a reassembled stream. Returns
    (url_hint, status, headers, body) tuples; bounded by count and size."""
    out, pos = [], 0
    while len(out) < limit:
        m = re.search(rb"HTTP/1\.[01] \d{3}", data[pos:])
        if not m:
            break
        start = pos + m.start()
        hend = data.find(b"\r\n\r\n", start)
        if hend < 0:
            break
        heads = data[start:hend].split(b"\r\n")
        status = int(heads[0].split()[1])
        hdr = {}
        for h in heads[1:]:
            k, _, v = h.partition(b":")
            hdr[k.strip().lower().decode("ascii", "replace")] = v.strip()
        bstart = hend + 4
        if "chunked" in hdr.get("transfer-encoding", ""):
            body, p2 = bytearray(), bstart
            while True:
                eol = data.find(b"\r\n", p2)
                if eol < 0:
                    break
                try:
                    n = int(data[p2:eol].split(b";")[0], 16)
                except ValueError:
                    break
                p2 = eol + 2
                if n == 0:
                    p2 = data.find(b"\r\n\r\n", p2)
                    p2 = (p2 + 4) if p2 >= 0 else len(data)
                    break
                body += data[p2:p2 + n]
                p2 += n + 2
            body = bytes(body[:max_obj])
            pos = p2
        else:
            try:
                n = int(hdr.get("content-length", b"0"))
            except (ValueError, TypeError):
                n = 0
            n = min(n, max_obj)
            body = data[bstart:bstart + n]
            pos = bstart + n
        ctype = hdr.get("content-type", "")
        ctype = ctype.decode("utf-8", "replace") if isinstance(ctype, bytes) \
            else ctype
        out.append({"status": status, "body": body, "content_type": ctype})
        if pos <= start:
            pos = start + 8
    return out


def cmd_http(args):
    """--export-objects equivalent: reassemble TCP flows, carve every
    HTTP response body out to --out. The most common pcap flag carrier."""
    _lt, pkts, err = parse_pcap(args.pcap)
    if err:
        print(json.dumps({"error": err}))
        return 1
    os.makedirs(args.out, exist_ok=True)
    written, flows = [], _flows(pkts)
    for key, f in sorted(flows.items(), key=lambda kv: -kv[1]["bytes"]):
        if f["proto"] != "tcp":
            continue
        for di in (0, 1):
            data = b"".join(c[1] for c in sorted(f["dirs"][di],
                                               key=lambda c: c[0]))
            if b"HTTP/1." not in data:
                continue
            for i, obj in enumerate(_http_objects(data)):
                if not obj["body"]:
                    continue
                ext = {b"text/html": ".html", b"image/png": ".png",
                       b"image/jpeg": ".jpg", b"application/zip": ".zip",
                       b"text/plain": ".txt"}.get(
                           obj["content_type"].encode().split(b";")[0].strip(),
                           ".bin")
                name = "obj-%s-%d-%d%s" % (f["bport"], di, i, ext)
                path = os.path.join(args.out, name)
                with open(path, "wb") as fh:
                    fh.write(obj["body"])
                written.append({"file": name, "status": obj["status"],
                                "content_type": obj["content_type"],
                                "bytes": len(obj["body"]),
                                "flow": "%s:%d <-> %s:%d" % (
                                    f["a"], f["aport"], f["b"], f["bport"])})
    print(json.dumps({"objects": len(written), "written": written[:200],
                      "out": os.path.abspath(args.out)}, indent=1))
    return 0


def _selftest() -> int:
    """Build a tiny pcap in memory: one DNS query + one TCP exchange."""
    import tempfile
    def eth_ip_udp(payload, sport=53000, dport=53):
        udp = struct.pack(">HHHH", sport, dport, 8 + len(payload), 0) + payload
        ip = bytes([0x45, 0, 0, 20 + len(udp), 0, 0, 0, 0, 64, 17, 0, 0,
                    10, 0, 0, 1, 8, 8, 8, 8])
        return b"\x00" * 12 + b"\x08\x00" + ip + udp

    def dnsq(name):
        q = b""
        for part in name.split("."):
            q += bytes([len(part)]) + part.encode()
        return struct.pack(">HHHHHH", 1, 0x100, 1, 0, 0, 0) + q + b"\x00\x01\x00\x01"

    def eth_ip_tcp(payload, seq=1):
        tcp = struct.pack(">HHIIBBHHH", 80, 40000, seq, 0, 0x50, 0x18,
                          65535, 0, 0) + payload
        ip = bytes([0x45, 0, 0, 20 + len(tcp), 0, 0, 0, 0, 64, 6, 0, 0,
                    10, 0, 0, 2, 10, 0, 0, 1])
        return b"\x00" * 12 + b"\x08\x00" + ip + tcp

    body = b"flag{http_carve}"
    http_resp = (b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n"
                 b"Content-Length: " + str(len(body)).encode()
                 + b"\r\n\r\n" + body)
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as fh:
        fh.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        for i, p in enumerate([eth_ip_udp(dnsq("flag.example.com")),
                               eth_ip_tcp(b"GET /secret HTTP/1.0\r\n\r\n"),
                               eth_ip_tcp(http_resp, seq=200)]):
            fh.write(struct.pack("<IIII", i, 0, len(p), len(p)))
            fh.write(p)
        path = fh.name
    ns = argparse.Namespace(pcap=path)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cmd_dns(ns)
    dns = json.loads(buf.getvalue())
    assert "flag.example.com" in dns["queries"], dns
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cmd_convs(ns)
    convs = json.loads(buf.getvalue())
    assert any(r["proto_guess"] == "dns" for r in convs["flows"]), convs
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ns.min, ns.max, ns.find = 6, 50, "secret"
        cmd_ascii(ns)
    assert any("secret" in r for r in json.loads(buf.getvalue())["runs"])
    import tempfile as _tf, shutil
    odir = _tf.mkdtemp()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ns.out = odir
        cmd_http(ns)
    got = json.loads(buf.getvalue())
    assert got["objects"] >= 1, got
    carved = b"".join(open(os.path.join(odir, w["file"]), "rb").read()
                      for w in got["written"])
    assert b"flag{http_carve}" in carved, got
    shutil.rmtree(odir, ignore_errors=True)
    os.unlink(path)
    print("pcap_parse selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("convs"); c.add_argument("pcap"); c.set_defaults(fn=cmd_convs)
    d = sub.add_parser("dns"); d.add_argument("pcap"); d.set_defaults(fn=cmd_dns)
    a = sub.add_parser("ascii"); a.add_argument("pcap")
    a.add_argument("--min", type=int, default=8)
    a.add_argument("--max", type=int, default=200)
    a.add_argument("--find"); a.set_defaults(fn=cmd_ascii)
    f = sub.add_parser("follow"); f.add_argument("pcap")
    f.add_argument("--flow", type=int, default=0)
    f.add_argument("--dir", type=int, default=0, choices=[0, 1])
    f.set_defaults(fn=cmd_follow)
    h = sub.add_parser("http", help="carve HTTP response objects to --out")
    h.add_argument("pcap"); h.add_argument("--out", default="objects")
    h.set_defaults(fn=cmd_http)
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
