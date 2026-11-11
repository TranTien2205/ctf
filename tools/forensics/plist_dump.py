#!/usr/bin/env python3
"""plist_dump.py -- dump .plist files (XML or binary) as JSON.

macOS/iOS artifacts — Info.plist, preferences, .mobileconfig,
receipt data — are property lists; plistlib reads both encodings
but has no CLI. This is the bounded wrapper: file in, JSON out,
base64 for data blobs, ISO for datetimes.

  python3 tools/forensics/plist_dump.py Info.plist
  python3 tools/forensics/plist_dump.py prefs.plist --key a.b.c
  python3 tools/forensics/plist_dump.py --selftest
"""
import argparse
import base64
import datetime
import json
import plistlib
import sys


def conv(o):
    if isinstance(o, dict):
        return {k: conv(v) for k, v in o.items()}
    if isinstance(o, list):
        return [conv(v) for v in o]
    if isinstance(o, bytes):
        return {"__data__": base64.b64encode(o).decode()}
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    return o


def get(o, path):
    for p in path.split("."):
        if isinstance(o, dict) and p in o:
            o = o[p]
        elif isinstance(o, list) and p.isdigit():
            o = o[int(p)]
        else:
            raise KeyError(path)
    return o


def _selftest():
    import io
    obj = {"Label": "com.evil.agent", "Flag": "flag{plist_key}",
           "Blob": b"\xde\xad", "When": datetime.datetime(
               2024, 1, 1, 12, 0)}
    raw = plistlib.dumps(obj, fmt=plistlib.FMT_BINARY)
    back = plistlib.loads(raw)
    j = conv(back)
    assert j["Flag"] == "flag{plist_key}" and j["Blob"]["__data__"]
    assert get(back, "Label") == "com.evil.agent"
    xml = plistlib.dumps(obj, fmt=plistlib.FMT_XML)
    assert plistlib.loads(xml)["Flag"] == "flag{plist_key}"
    print("plist_dump selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="plist to JSON dump")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--key", dest="sub")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("plist path required")
    obj = plistlib.load(open(a.path, "rb"))
    if a.sub:
        try:
            obj = get(obj, a.sub)
        except KeyError:
            sys.exit(f"{a.sub}: no such key path")
    print(json.dumps(conv(obj), indent=1, default=str))


if __name__ == "__main__":
    raise SystemExit(main())
