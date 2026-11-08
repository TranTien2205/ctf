#!/usr/bin/env python3
"""carve_scan.py — embedded-file and trailing-data scan. Stdlib only.

forensics-stego's carrier table names zsteg/steghide/binwalk — all absent on a
Windows contest box. The 80% case is mechanical: a second file appended past
the container's real end, or an embedded blob at a magic offset. This scans
every byte offset for known magics, reports where each candidate file starts,
flags data trailing a container that should end, and extracts printable runs —
with a flag-format pass over both. It reports offsets and excerpts; whether a
carved blob is the flag is the agent's call.

    python3 tools/forensics/carve_scan.py blob.bin
    python3 tools/forensics/carve_scan.py blob.bin --extract out/
    python3 tools/forensics/carve_scan.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

_MAX_FILE = 64 << 20        # 64 MiB input cap
_MAX_HITS_PER_MAGIC = 32
_MAX_CARVE = 8 << 20        # extracted blob capped at 8 MiB
_MIN_RUN = 6                # printable strings shorter than this are noise

_SIGS = [
    (b"\x89PNG\r\n\x1a\n", "png", ".png"),
    (b"\xff\xd8\xff", "jpeg", ".jpg"),
    (b"GIF87a", "gif", ".gif"), (b"GIF89a", "gif", ".gif"),
    (b"PK\x03\x04", "zip", ".zip"), (b"PK\x05\x06", "zip-eocd", None),
    (b"%PDF", "pdf", ".pdf"),
    (b"\x1f\x8b\x08", "gzip", ".gz"),
    (b"BM", "bmp", ".bmp"),
    (b"\x7fELF", "elf", ".elf"),
    (b"MZ", "pe-or-dos", ".exe"),
    (b"7z\xbc\xaf\x27\x1c", "7z", ".7z"),
    (b"Rar!\x1a\x07", "rar", ".rar"),
    (b"RIFF", "riff-wav-avi", ".riff"),
    (b"SQLite format 3\x00", "sqlite", ".db"),
    (b"ID3", "mp3-id3", ".mp3"),
    (b"OggS", "ogg", ".ogg"),
    (b"\x42\x5a\x68", "bzip2", ".bz2"),
    (b"\xfd7zXZ\x00", "xz", ".xz"),
]

# formats whose end is detectable: appended data after the end marker is
# the classic hide. JPEG ends at FFD9, PNG at IEND, GIF at 3B, ZIP at EOCD.
_END_MARKERS = [(b"\xff\xd9", "jpeg-eoi"), (b"IEND", "png-iend"),
                (b"PK\x05\x06", "zip-eocd")]

_FLAGISH = re.compile(rb"[A-Za-z0-9_]{2,24}\{[^\x00-\x1f}]{4,96}\}")
_PRINTABLE = re.compile(rb"[\x20-\x7e]{%d,}" % _MIN_RUN)


def scan(data: bytes, path: str) -> dict:
    hits = {}
    for magic, name, ext in _SIGS:
        offs = []
        start = 0
        while len(offs) < _MAX_HITS_PER_MAGIC:
            i = data.find(magic, start)
            if i == -1:
                break
            if name == "bmp" and not (data[i:i+6][4:6] in (b"\x00\x00", b"\x36\x00")):
                start = i + 2           # 'BM' alone false-positives constantly
                continue
            offs.append(i)
            start = i + 1
        if offs:
            hits[name] = {"offsets": offs, "ext": ext}
    trailing = []
    for end_magic, name in _END_MARKERS:
        i = data.rfind(end_magic)
        if i != -1:
            end_pos = i + len(end_magic) + (20 if name == "zip-eocd" else 0)
            if end_pos < len(data):
                trailing.append({"after": name, "at": end_pos,
                                 "trailing_bytes": len(data) - end_pos,
                                 "head": data[end_pos:end_pos + 32].hex()})
    runs = []
    for m in _PRINTABLE.finditer(data):
        flag = bool(_FLAGISH.search(m.group()))
        runs.append({"offset": m.start(), "len": len(m.group()),
                     "text": m.group().decode()[:120], "flagish": flag})
    flag_hits = [{"offset": m.start(), "match": m.group().decode("utf-8", "replace")}
                 for m in _FLAGISH.finditer(data)]
    return {"file": path, "bytes": len(data), "magics": hits,
            "trailing": trailing, "printable_runs": len(runs),
            "flagish_runs": [r for r in runs if r["flagish"]][:10],
            "flag_format_hits": flag_hits[:10],
            "runs_sample": runs[:15]}


def _selftest() -> int:
    import tempfile
    jpeg = b"\xff\xd8\xff\xe0" + b"JFIF" + b"\x00" * 64 + b"\xff\xd9"
    zipb = b"PK\x03\x04" + b"\x00" * 30 + b"flag{hidden_in_zip}"
    blob = jpeg + zipb + b"trailing junk"
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "b.bin")
        open(p, "wb").write(blob)
        out = scan(blob, p)
        assert "jpeg" in out["magics"] and "zip" in out["magics"]
        assert out["magics"]["zip"]["offsets"][0] == len(jpeg)
        assert any(t["after"] == "jpeg-eoi" for t in out["trailing"])
        assert out["flag_format_hits"][0]["match"] == "flag{hidden_in_zip}"
    print("carve_scan selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?")
    ap.add_argument("--extract", metavar="DIR",
                    help="write each magic hit to DIR/offset_name.ext")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.file:
        ap.print_help()
        return 2
    data = open(args.file, "rb").read(_MAX_FILE)
    out = scan(data, args.file)
    if args.extract:
        os.makedirs(args.extract, exist_ok=True)
        written = []
        for name, h in out["magics"].items():
            for off in h["offsets"]:
                if not h["ext"]:
                    continue
                dest = os.path.join(args.extract, f"{off:08x}_{name}{h['ext']}")
                with open(dest, "wb") as fh:
                    fh.write(data[off:off + _MAX_CARVE])
                written.append(dest)
        out["extracted"] = written
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
