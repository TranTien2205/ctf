#!/usr/bin/env python3
"""cpio_read.py -- list/extract newc-format cpio and ar archives.

Firmware bundles and initramfs images arrive as cpio (newc ASCII
hex header), static libraries and .deb members as ar (`!<arch>`).
`cpio` and `ar` binaries are absent here; both formats are trivial
enough to walk in stdlib.

  python3 tools/forensics/cpio_read.py init.cpio list
  python3 tools/forensics/cpio_read.py init.cpio get init
  python3 tools/forensics/cpio_read.py lib.a list
  python3 tools/forensics/cpio_read.py --selftest

`get` writes member bytes to stdout. cpio supports newc (070701)
and crc (070702); entries are 4-byte aligned, TRAILER!!! ends the
archive. ar reads the 60-byte headers and decodes `#1/N` extended
names. JSON out for list mode.
"""
import argparse
import json
import struct
import sys


def cpio_entries(data):
    out, off = [], 0
    while off + 110 <= len(data):
        if data[off:off + 6] not in (b"070701", b"070702"):
            break
        h = data[off:off + 110]
        f = [int(h[6 + i * 8:14 + i * 8], 16) for i in range(13)]
        namesize, filesize = f[11], f[6]
        name = data[off + 110:off + 110 + namesize - 1].decode(
            "utf-8", "replace")
        off += (110 + namesize + 3) & ~3
        out.append({"name": name, "size": filesize,
                    "mode": f[1], "offset": off})
        off += (filesize + 3) & ~3
        if name == "TRAILER!!!":
            break
    return out


def ar_entries(data):
    if data[:8] != b"!<arch>\n":
        return None
    out, off, names = [], 8, {}
    while off + 60 <= len(data):
        h = data[off:off + 60]
        raw_name = h[0:16].decode("ascii", "replace").strip()
        size = int(h[48:58].decode("ascii", "replace").strip() or 0)
        body_off = off + 60
        if raw_name == "//":
            n = 0
            for line in data[body_off:body_off + size].split(b"\n"):
                names[n] = line.decode("utf-8", "replace").rstrip("/")
                n += len(line) + 1
            name = "//"
        elif raw_name == "/":
            name = "/ (symbol table)"
        elif raw_name.startswith("#1/"):
            nlen = int(raw_name[3:])
            name = data[body_off:body_off + nlen].decode(
                "utf-8", "replace")
            body_off += nlen
            size -= nlen
        elif raw_name.startswith("/") and raw_name[1:].isdigit():
            name = names.get(int(raw_name[1:]), raw_name)
        else:
            name = raw_name.rstrip("/")
        if name not in ("//", "/ (symbol table)"):
            out.append({"name": name, "size": size,
                        "offset": body_off})
        off += 60 + size + (size & 1)
    return out


def detect(data):
    if data[:6] in (b"070701", b"070702"):
        return "cpio"
    if data[:8] == b"!<arch>\n":
        return "ar"
    return None


def entries(data):
    t = detect(data)
    if t == "cpio":
        return cpio_entries(data)
    if t == "ar":
        return ar_entries(data)
    return None


def _selftest():
    def cent(name, body):
        nb, fb = name.encode() + b"\x00", body
        hdr = b"070701" + b"".join(
            f"{v:08x}".encode() for v in
            [0, 0o100644, 0, 0, 0, 0, len(fb), 0, 0, 0, 0,
             len(nb), 0])
        pad = (110 + len(nb) + 3) & ~3
        e = hdr + nb + b"\x00" * (pad - 110 - len(nb)) + fb
        e += b"\x00" * (-len(e) % 4)
        return e
    cpio = cent("flag.txt", b"flag{cpio_member}") + \
        cent("TRAILER!!!", b"") + b"\x00" * 64
    ents = cpio_entries(cpio)
    assert ents[0]["name"] == "flag.txt", ents
    body = cpio[ents[0]["offset"]:
                ents[0]["offset"] + ents[0]["size"]]
    assert body == b"flag{cpio_member}", body
    # ar: extended-name table + one member
    longtab = b"verylongmembername.txt/\n"
    ar = b"!<arch>\n"
    ar += b"//              0           0     0     644     %-10d`\n" \
        % len(longtab) + longtab
    ar += (b"/0              0           0     0     644     %-10d`\n"
           % len(longtab) + b"ARBYTES" + b"\x00" * (len(longtab) - 7))
    aents = ar_entries(ar)
    assert aents and aents[0]["name"] == "verylongmembername.txt", aents
    print("cpio_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="cpio/ar archive reader")
    ap.add_argument("archive", nargs="?")
    ap.add_argument("cmd", nargs="?", choices=["list", "get"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.archive and a.cmd):
        ap.error("archive and cmd required")
    data = open(a.archive, "rb").read()
    ents = entries(data)
    if ents is None:
        sys.exit("not a newc cpio or ar archive")
    if a.cmd == "list":
        print(json.dumps({"entries": [
            e for e in ents if e["name"] != "TRAILER!!!"]}, indent=1))
        return
    hit = next((e for e in ents if e["name"] == a.name), None)
    if not hit:
        sys.exit(f"{a.name}: not in archive")
    sys.stdout.buffer.write(
        data[hit["offset"]:hit["offset"] + hit["size"]])


if __name__ == "__main__":
    raise SystemExit(main())
