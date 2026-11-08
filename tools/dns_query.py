#!/usr/bin/env python3
"""DNS record query + zone-transfer attempt + crt.sh SAN fetch, stdlib.

osint-infra-records's whole loop is dig/whois/curl; on this box none
exist. UDP wire-format queries for the data-carrying types (TXT first —
that is where flags get planted), a bounded TCP AXFR attempt for the
zone-transfer check, and the crt.sh JSON fetch that leaks sibling
hostnames.

  python3 tools/dns_query.py --name example.com --type TXT
  python3 tools/dns_query.py --name example.com --type ANY --server 1.1.1.1
  python3 tools/dns_query.py --name example.com --axfr --server ns1.example.com
  python3 tools/dns_query.py --crtsh example.com
  python3 tools/dns_query.py --selftest

Bounded: one UDP exchange per type, one TCP connection for AXFR, one
HTTPS GET for crt.sh. NXDOMAIN/timeout/refused are reported as data,
not retried silently.
"""
import argparse, json, os, random, re, socket, struct, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "web"))
import httpkit  # noqa: E402

TYPES = {"A": 1, "NS": 2, "CNAME": 5, "SOA": 6, "PTR": 12, "MX": 15,
         "TXT": 16, "AAAA": 28, "SRV": 33, "CAA": 257, "ANY": 255}
RTYPES = {v: k for k, v in TYPES.items()}


def _qname(name):
    return b"".join(bytes([len(p)]) + p.encode()
                    for p in name.split(".")) + b"\x00"


def _rname(buf, off, depth=0):
    labels = []
    while off < len(buf) and depth < 64:
        ln = buf[off]
        if ln == 0:
            return ".".join(labels), off + 1
        if ln & 0xC0 == 0xC0:
            ptr = ((ln & 0x3F) << 8) | buf[off + 1]
            sub, _ = _rname(buf, ptr, depth + 1)
            labels.append(sub)
            return ".".join(labels), off + 2
        labels.append(buf[off + 1:off + 1 + ln].decode("utf-8", "replace"))
        off += 1 + ln
    return ".".join(labels), off


def _parse_rrs(buf, off, count):
    out = []
    for _ in range(count):
        name, off = _rname(buf, off)
        if off + 10 > len(buf):
            break
        typ, _cls, ttl, rdlen = struct.unpack(">HHIH", buf[off:off + 10])
        off += 10
        rd = buf[off:off + rdlen]
        off += rdlen
        t = RTYPES.get(typ, "T%d" % typ)
        if t == "A" and rdlen == 4:
            val = ".".join(str(b) for b in rd)
        elif t == "AAAA" and rdlen == 16:
            val = socket.inet_ntop(socket.AF_INET6, rd)
        elif t in ("NS", "CNAME", "PTR"):
            val, _ = _rname(buf, off - rdlen)
        elif t == "MX":
            pref, off2 = struct.unpack(">H", rd[:2])[0], off - rdlen + 2
            val, _ = _rname(buf, off2)
            val = "%d %s" % (pref, val)
        elif t == "TXT":
            val = _txt(rd)
        elif t == "SOA":
            mname, p = _rname(buf, off - rdlen)
            rname2, p = _rname(buf, p)
            val = "%s %s" % (mname, rname2)
        else:
            val = rd.hex()
        out.append({"type": t, "name": name, "ttl": ttl, "data": val})
    return out


def _txt(rd):
    out, i = [], 0
    while i < len(rd):
        ln = rd[i]
        out.append(rd[i + 1:i + 1 + ln].decode("utf-8", "replace"))
        i += 1 + ln
    return "".join(out)


def query(name, qtype, server=None, timeout=5):
    qid = random.randrange(65536)
    pkt = struct.pack(">HHHHHH", qid, 0x0100, 1, 0, 0, 0)
    pkt += _qname(name) + struct.pack(">HH", TYPES.get(qtype, 255), 1)
    server = server or _sysdns()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(pkt, (server, 53))
        buf, _ = s.recvfrom(4096)
    except (socket.timeout, OSError) as e:
        return {"error": "no response from %s: %s" % (server, e),
                "records": []}
    finally:
        s.close()
    if len(buf) < 12:
        return {"error": "short response", "records": []}
    rid, flags, qd, an, _ns, _ar = struct.unpack(">HHHHHH", buf[:12])
    rcode = flags & 0xF
    off = 12
    for _ in range(qd):
        _n, off = _rname(buf, off)
        off += 4
    recs = _parse_rrs(buf, off, an)
    return {"server": server, "rcode": rcode,
            "rcode_name": {0: "NOERROR", 3: "NXDOMAIN", 5: "REFUSED"}
            .get(rcode, str(rcode)),
            "records": recs,
            "note": "TXT records are the flag carrier — read every "
                    "string, not the first"}


def _sysdns():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 53))
        return s.getsockname()[0]
    except OSError:
        return "8.8.8.8"


def axfr(name, server, timeout=8):
    """One bounded zone-transfer attempt over TCP."""
    qid = random.randrange(65536)
    pkt = struct.pack(">HHHHHH", qid, 0x0100, 1, 0, 0, 0)
    pkt += _qname(name) + struct.pack(">HH", 252, 1)
    try:
        s = socket.create_connection((server, 53), timeout)
        s.settimeout(timeout)
        s.sendall(struct.pack(">H", len(pkt)) + pkt)
        hdr = _recv(s, 2)
        if not hdr:
            return {"transferred": False, "reason": "no response"}
        buf = _recv(s, struct.unpack(">H", hdr)[0])
        s.close()
    except (socket.timeout, OSError) as e:
        return {"transferred": False, "reason": str(e)}
    if not buf or len(buf) < 12:
        return {"transferred": False, "reason": "short/empty answer"}
    _rid, flags, qd, an, _n, _r = struct.unpack(">HHHHHH", buf[:12])
    if flags & 0xF:
        return {"transferred": False,
                "reason": "rcode %d (refused is the expected answer)"
                          % (flags & 0xF)}
    off = 12
    for _ in range(qd):
        _x, off = _rname(buf, off)
        off += 4
    recs = _parse_rrs(buf, off, an)
    return {"transferred": bool(recs), "records": recs,
            "note": "a successful AXFR is a real finding — every record "
                    "of the zone just listed itself"}


def _recv(s, n):
    out = b""
    while len(out) < n:
        c = s.recv(n - len(out))
        if not c:
            return out or None
        out += c
    return out


def crtsh(domain):
    r = httpkit.request(
        "https://crt.sh/?q=%25.%s&output=json" % domain, timeout=20)
    if not r["ok"]:
        return {"error": r["error"], "names": []}
    try:
        rows = json.loads(r["body"])
    except ValueError:
        return {"error": "crt.sh did not return JSON", "names": []}
    names = sorted({n.strip().lower()
                    for row in rows
                    for n in row.get("name_value", "").split("\n")
                    if "*" not in n})
    return {"names": names, "count": len(names),
            "note": "internal-looking SANs are the real next step — "
                    "feed them back through --type TXT/A"}


_WHOIS_KEYS = ("domain name", "registrar", "whois server",
               "updated date", "creation date", "registrar registration "
               "expiration date", "registry expiry date", "expiry date",
               "name server", "domain status", "status", "dnssec",
               "registrant organization", "registrant org",
               "registrant country")


def _whois_field(body, key):
    vals = []
    for line in body.splitlines():
        if line.split(":", 1)[0].strip().lower() == key:
            v = line.split(":", 1)[1].strip()
            if v and v not in vals:
                vals.append(v)
    return vals


def whois_parse(body, server=None):
    """Whois text -> curated fields; repeats kept as lists."""
    out = {"server": server, "fields": {}, "emails": []}
    for key in _WHOIS_KEYS:
        vals = _whois_field(body, key)
        if vals:
            out["fields"][key] = vals if len(vals) > 1 else vals[0]
    emails = sorted({m.group(0) for m in
                     re.finditer(
                         r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                         body)})
    out["emails"] = emails
    out["raw_head"] = body[:400]
    return out


def _whois_query(host, question, timeout):
    s = socket.create_connection((host, 43), timeout)
    try:
        s.sendall(question.encode("utf-8", "replace") + b"\r\n")
        out = b""
        while len(out) < 512 * 1024:
            d = s.recv(4096)
            if not d:
                break
            out += d
    finally:
        s.close()
    return out.decode("utf-8", "replace")


def whois(target, timeout=10):
    """TCP/43 whois: bootstrap the TLD server from whois.iana.org, then
    query it. Works on names and bare IPs (ARIN-family referral)."""
    if all(c.isdigit() or c == "." for c in target):
        host = "whois.arin.net"
        try:
            return whois_parse(_whois_query(host, "n " + target,
                                            timeout), host)
        except OSError as e:
            return {"error": "%s query failed: %s" % (host, e)}
    tld = target.rsplit(".", 1)[-1].lower()
    try:
        iana = _whois_query("whois.iana.org", tld, timeout)
    except OSError as e:
        return {"error": "iana bootstrap failed: %s" % e}
    server = (_whois_field(iana, "whois") or [None])[0]
    if not server:
        return {"error": "iana has no whois server for .%s" % tld,
                "iana_head": iana[:400]}
    try:
        return whois_parse(_whois_query(server, target, timeout), server)
    except OSError as e:
        return {"error": "%s query failed: %s" % (server, e)}


def _selftest() -> int:
    """Parse a canned DNS TXT answer; network paths stay untested
    offline — they are one socket each by construction."""
    name_wire = _qname("x.example")
    q = struct.pack(">HHHHHH", 1, 0x0100, 1, 0, 0, 0) + name_wire + \
        struct.pack(">HH", 16, 1)
    txt = b"\x10flag{dns_txt!}"
    ans = name_wire + struct.pack(">HHIH", 16, 1, 300, len(txt) + 0) + txt
    resp = struct.pack(">HHHHHH", 1, 0x8180, 1, 1, 0, 0)
    body = q[12:] + ans
    buf = resp + body
    off = 12
    _n, off = _rname(buf, off)
    off += 4
    recs = _parse_rrs(buf, off, 1)
    assert recs and recs[0]["type"] == "TXT" and \
        recs[0]["data"] == "flag{dns_txt!}", recs
    # name compression pointer
    buf2 = b"\x00" * 12 + name_wire + b"\x00" * 4 + \
        b"\xc0\x0c" + struct.pack(">HHIH", 5, 1, 60, 7) + name_wire
    n, o = _rname(buf2, 27)
    assert n == "x.example", (n, o)
    # whois parser on a canned body
    body = ("Domain Name: EXAMPLE.COM\r\n"
            "Registrar: Example Registrar, LLC\r\n"
            "Name Server: NS1.EXAMPLE.COM\r\nName Server: NS2.EXAMPLE.COM\r\n"
            "Registrant Email: admin@example.com\r\n")
    w = whois_parse(body, "whois.example")
    assert w["fields"]["name server"] == ["NS1.EXAMPLE.COM",
                                          "NS2.EXAMPLE.COM"], w
    assert w["fields"]["registrar"] == "Example Registrar, LLC", w
    assert w["emails"] == ["admin@example.com"], w
    print("dns_query selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--name")
    ap.add_argument("--type", default="TXT",
                    choices=sorted(TYPES))
    ap.add_argument("--server")
    ap.add_argument("--axfr", action="store_true")
    ap.add_argument("--crtsh", metavar="DOMAIN")
    ap.add_argument("--whois", metavar="TARGET",
                    help="TCP/43 whois on a domain or IP")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.whois:
        print(json.dumps(whois(a.whois), indent=1))
        return 0
    if a.crtsh:
        print(json.dumps(crtsh(a.crtsh), indent=1))
        return 0
    if not a.name:
        ap.error("--name is required")
    if a.axfr:
        if not a.server:
            ap.error("--axfr needs --server (a nameserver from an NS "
                     "lookup)")
        print(json.dumps(axfr(a.name, a.server), indent=1))
        return 0
    print(json.dumps(query(a.name, a.type, a.server), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
