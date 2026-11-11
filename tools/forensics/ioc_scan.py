#!/usr/bin/env python3
"""ioc_scan.py -- strings + IOC extraction from any blob (strings fallback).

Usage:
  python3 tools/forensics/ioc_scan.py dump.raw
  python3 tools/forensics/ioc_scan.py dump.raw --min 6 --utf16
  python3 tools/forensics/ioc_scan.py dump.raw --pattern "flag\\{[^}]+\\}"
  python3 tools/forensics/ioc_scan.py --selftest

Extracts printable-ASCII runs (--min length), optional UTF-16LE
runs (--utf16, e.g. Windows memory/registry), and pulls IOC
classes out of those strings: ipv4, url, email, domain-ish tokens,
unc paths, env vars, plus any --pattern regex. Each hit carries
its byte offset so it can be dropped into a timeline or carved
back out. On a Windows box `strings`/`grep -a` are absent; this
is the day-zero path for memory dumps, pcaps and disk images.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

PRINTABLE = set(range(0x20, 0x7F)) | {0x09}
IOC = {
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "url": r"https?://[^\s\"'<>]+",
    "email": r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b",
    "unc": r"\\\\[\w.$-]+\\[\w .$\\/:-]+",
    "envvar": r"%(?:APPDATA|TEMP|USERPROFILE|PROGRAMDATA"
              r"|LOCALAPPDATA|SYSTEMROOT|WINDIR)%[^ \t\"']*",
    "winpath": r"\b[A-Za-z]:\\[^\"'<>\n|]+",
    "nixpath": r"(?<![\w/])/(?:etc|home|var|tmp|usr|opt|root|proc)"
               r"/[\w./-]+",
    "flag": r"\b[A-Za-z0-9_]{2,20}\{[^\x00-\x20}]{4,80}\}",
    "b64blob": r"(?<![\w/+=])[A-Za-z0-9+/]{20,}={0,2}(?![\w/+=])",
    "privkey": r"-----BEGIN [A-Z0-9 ]{3,40}PRIVATE KEY-----",
    "aws_akid": r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "api_token": r"\b(?:ghp_|github_pat_|glpat-|xox[baprs]-|sk-[A-Za-z0-9]|hf_)"
                r"[A-Za-z0-9_-]{16,80}\b",
    "jwt": r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"
           r"\.[A-Za-z0-9_-]{8,}\b",
    "passwd_kv": r"(?i)\b(?:passw(?:or)?d|secret|api[_-]?key|token)"
                 r"[\"'\s]{0,4}[:=][\"'\s]{0,4}[^\s\"',;\\]{5,60}",
    "shadow_hash": r"\$[156ay]\$[./A-Za-z0-9$,]{10,80}"
                   r"|\$2[abxy]\$\d{2}\$[./A-Za-z0-9]{53}",
    "cred_in_url": r"https?://[\w.~-]{2,40}:[^@\s]{3,50}@[\w.-]+",
    "eth_privkey": r"\b0x[0-9a-fA-F]{64}\b",
    "eth_addr": r"\b0x[0-9a-fA-F]{40}\b",
}


def ascii_strings(d, minlen):
    out, start = [], None
    for i, b in enumerate(d):
        if b in PRINTABLE:
            if start is None:
                start = i
        else:
            if start is not None and i - start >= minlen:
                out.append((start, d[start:i].decode("ascii")))
            start = None
    if start is not None and len(d) - start >= minlen:
        out.append((start, d[start:].decode("ascii")))
    return out


def utf16_strings(d, minlen):
    out = []
    for base in (0, 1):                  # data need not be aligned
        i = base
        n = len(d) - (len(d) % 2)
        while i < n - 1:
            if d[i + 1] == 0 and d[i] in PRINTABLE:
                start = i
                while i < n - 1 and d[i + 1] == 0 \
                        and d[i] in PRINTABLE:
                    i += 2
                if (i - start) // 2 >= minlen:
                    out.append((start, d[start:i]
                                .decode("utf-16-le", "replace")))
            else:
                i += 2
    return out


def scan(d, minlen=4, utf16=False, pattern=None, max_strings=20000):
    strs = ascii_strings(d, minlen)
    if utf16:
        strs += [(o, s) for o, s in utf16_strings(d, minlen)]
        strs.sort()
    strs = strs[:max_strings]
    hits = {k: [] for k in IOC}
    if pattern:
        hits["custom"] = []
    pats = dict(IOC)
    if pattern:
        pats["custom"] = pattern
    for off, s in strs:
        for name, rx in pats.items():
            for m in re.finditer(rx, s):
                hits[name].append({"offset": off + m.start(),
                                   "value": m.group(0)})
    for name in hits:
        seen, ded = set(), []
        for h in hits[name]:
            if h["value"] not in seen:
                seen.add(h["value"])
                ded.append(h)
        hits[name] = ded[:500]
    return {"strings": [{"offset": o, "text": s}
                        for o, s in strs[:5000]],
            "string_count": len(strs),
            "iocs": {k: v for k, v in hits.items() if v}}


def _selftest():
    blob = (b"\x00" * 16
            + b"call 10.20.30.40 and fetch https://evil.example/x "
            + b"mail a.b-c@sub.example.co flag{n0t_r34l} "
            + b"see C:\\Users\\x\\Desktop\\loot.zip "
            + b"%APPDATA%\\Roaming\\k "
            + b"-----BEGIN RSA PRIVATE KEY----- "
            + b"aws AKIAIOSFODNN7EXAMPLE "
            + b"tok ghp_abcdefghij0123456789ABCDEF "
            + b"cfg password:Sup3rS3cret! "
            + b"hash $6$rounds$saltstring$abcdEFGH "
            + b"basic https://admin:hunter22@10.0.0.9/ "
            + "wide string here".encode("utf-16-le")
            + b"\x00" * 8)
    r = scan(blob, minlen=5, utf16=True,
             pattern=r"flag\{[^}]+\}")
    vals = {k: {h["value"] for h in v} for k, v in
            r["iocs"].items()}
    assert "10.20.30.40" in vals.get("ipv4", set()), vals
    assert "https://evil.example/x" in vals.get("url", set())
    assert "a.b-c@sub.example.co" in vals.get("email", set())
    assert "flag{n0t_r34l}" in vals.get("flag", set()), vals
    assert "flag{n0t_r34l}" in vals.get("custom", set())
    assert any(v.startswith("C:\\Users")
               for v in vals.get("winpath", set())), vals
    assert any("PRIVATE KEY" in v for v in vals.get("privkey", set())), vals
    assert "AKIAIOSFODNN7EXAMPLE" in vals.get("aws_akid", set()), vals
    assert any(v.startswith("ghp_") for v in vals.get("api_token", set())), vals
    assert any("Sup3rS3cret" in v for v in vals.get("passwd_kv", set())), vals
    assert any(v.startswith("$6$") for v in vals.get("shadow_hash", set())), vals
    assert any("admin:hunter22@" in v for v in vals.get("cred_in_url", set())), vals
    assert any("wide string here" in s["text"]
               for s in r["strings"]), r["strings"]
    print("ioc_scan selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="strings + IOC extraction from a blob")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--min", type=int, default=4,
                    help="min string length")
    ap.add_argument("--utf16", action="store_true",
                    help="also extract UTF-16LE strings")
    ap.add_argument("--pattern", help="extra regex to hunt")
    ap.add_argument("--strings-only", action="store_true",
                    help="just the string list, no IOC pass")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    r = scan(Path(a.file).read_bytes(), a.min, a.utf16,
             a.pattern)
    if a.strings_only:
        for s in r["strings"]:
            print(f"{s['offset']:08x} {s['text']}")
    else:
        print(json.dumps(r, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
