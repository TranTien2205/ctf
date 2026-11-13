#!/usr/bin/env python3
"""shellbags.py -- Shellbag (BagMRU) ITEMIDLIST decoder.

Shellbags record every folder the user browsed in Explorer -- the
evidence that survives after the folder itself is deleted. The data
lives in `NTUSER.DAT` under `Software\\Microsoft\\Windows\\Shell\\
BagMRU` and in `UsrClass.dat` under `Local Settings\\Software\\
Microsoft\\Windows\\Shell\\BagMRU`: each numbered child key owns an
ITEMIDLIST stored as the parent's same-named value. This walks that
tree through tools/forensics/hive_parse.py, decodes each SHITEMID
type (drive 0x2F, CLSID 0x1F, file-system items 0x31/0x32/0x35/0x36/
0x3A/0xB1/0x74, network/URI 0x46/0x47/0x61/0x71), and rebuilds the
absolute path per node with the hive's last-write time -- answered
questions: "did the user open X", "which folders existed".

Name recovery is honest: file-system items carry a FAT-era DOS name
and, on newer items, an extension block with a UTF-16 long name at a
declared offset; both are surfaced, and types outside the handled set
report their hex type and byte length instead of a guessed name.

  python3 tools/forensics/shellbags.py NTUSER.DAT
  python3 tools/forensics/shellbags.py UsrClass.dat --grep flag
  python3 tools/forensics/shellbags.py --selftest
"""
import argparse
import datetime
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hive_parse  # noqa: E402

BAGMRU_PATHS = [
    "Software\\Microsoft\\Windows\\Shell\\BagMRU",
    "Local Settings\\Software\\Microsoft\\Windows\\Shell\\BagMRU",
    "Local Settings\\Software\\Microsoft\\Windows\\Shell\\Bags",
]
CLSID = {
    "20d04fe03aea1069a2d808002b30309d": "Desktop",
    "f2df70c54f8111cf8d3d00a0c90f5444": "Control Panel",
    "645ff0405081101b9f0800aa002f954e": "Recycle Bin",
    "208d2c603aea1069a2d708002b30309d": "Network Neighborhood",
    "085303763ae91069a64d08002b30309d": "My Computer",
}


def _fat_dt(v):
    d, t = v >> 16, v & 0xFFFF
    try:
        return "%04d-%02d-%02d %02d:%02d:%02d" % (
            1980 + (d >> 9), (d >> 5) & 15, d & 31,
            t >> 11, (t >> 5) & 63, (t & 31) * 2)
    except Exception:
        return "0x%x" % v


def _guid(b):
    if len(b) < 16:
        return b.hex()
    a, c, e = struct.unpack("<IHH", b[:8])
    return ("%08x-%04x-%04x-%02x%02x-%s"
            % (a, c, e, b[8], b[9], b[10:16].hex())).replace("-", "")


def item(item):
    """One SHITEMID -> dict(type, name candidates, size, mtime)."""
    cb = len(item)
    if cb < 3:
        return {"raw": item.hex()}
    t = item[2]
    out = {"type": "0x%02x" % t}
    if t == 0x2F and cb >= 4:                    # drive
        out["name"] = item[3:cb].split(b"\x00")[0].decode(
            "latin-1", "replace")
        return out
    if t == 0x1F and cb >= 20:                   # CLSID
        g = _guid(item[4:20])
        out["name"] = CLSID.get(g, g)
        return out
    if t in (0x31, 0x32, 0x35, 0x36, 0x3A, 0xB1, 0x74, 0x30, 0x42):
        # FS item: size u32 @4, FAT datetime u32 @8, attrs u16 @12,
        # short name ASCII from 14; extension block may carry a
        # u16 name-offset (0x14+) to a UTF-16 long name.
        if cb >= 14:
            out["size"], = struct.unpack("<I", item[4:8])
            out["mtime"] = _fat_dt(struct.unpack("<I", item[8:12])[0])
            out["attrs"] = hex(struct.unpack("<H", item[12:14])[0])
        tail = item[14:]
        nul = tail.find(b"\x00")
        dos = tail[:nul if nul > 0 else len(tail)]
        if any(0x20 <= b < 0x7F for b in dos):
            out["dos_name"] = dos.decode("latin-1", "replace")
        # long-name: scan for a plausible u16 offset (>=0x14) into a
        # UTF-16 string, taken from the field at 10 or the extension
        for offpos in (10, 12):
            if cb >= offpos + 2:
                off, = struct.unpack("<H", item[offpos:offpos + 2])
                if 0x14 <= off < cb - 2:
                    cand = item[off:]
                    nul = cand.find(b"\x00\x00")
                    s = cand[:nul if nul > 0 else len(cand)].decode(
                        "utf-16-le", "replace")
                    if sum(ch.isprintable() for ch in s) >= 2:
                        out["long_name"] = s
                        break
        return out
    if t in (0x46, 0x47):                        # URI-ish
        txt = item[3:].replace(b"\x00", b"").decode("latin-1", "replace")
        out["name"] = txt[:64]
        return out
    if t in (0x61, 0x71):                        # network/remote share
        txt = item[4:].replace(b"\x00", b"").decode("latin-1", "replace")
        out["name"] = txt[:64]
        return out
    out["raw_len"] = cb
    return out


def itemidlist(raw):
    """chain of SHITEMIDs -> last component's decoded name + all parts."""
    parts = []
    pos = 0
    while pos + 2 <= len(raw):
        cb, = struct.unpack("<H", raw[pos:pos + 2])
        if cb == 0:
            break
        parts.append(item(raw[pos:pos + cb]))
        pos += cb
    name = None
    for p in reversed(parts):
        for k in ("long_name", "name", "dos_name"):
            if p.get(k):
                name = p[k]
                break
        if name:
            break
    return {"parts": parts,
            "name": name or (parts[-1]["type"] if parts else "?")}


def _walk(hv, node, parent_vals, prefix, out):
    subs = hv.sub_offsets(node["sublist"]) + \
        hv.sub_offsets(node["sublist_v"])
    for off in subs:
        child = hv.nk(off)
        if not child:
            continue
        raw = parent_vals.get(child["name"])
        dec = itemidlist(raw) if raw else {"name": "?", "parts": []}
        path = (prefix + "\\" + dec["name"]) if prefix else dec["name"]
        out.append({"path": path, "mtime": child["time"],
                    "item_count": len(dec["parts"]),
                    "last_item": dec["parts"][-1] if dec["parts"] else {}})
        _walk(hv, child,
              {v["name"]: v["raw"] for v in hv.values(child)}, path, out)


def shellbags(path):
    hv = hive_parse.Hive(path)
    found = []
    for p in BAGMRU_PATHS:
        node, _parts = hv.find(p)
        if node:
            vals = {v["name"]: v["raw"] for v in hv.values(node)}
            out = []
            _walk(hv, node, vals, "", out)
            found.append({"bagmru": p, "entries": out})
    return found


def _selftest():
    # BagMRU: parent's value "0" holds child key "0"'s ITEMIDLIST.
    drive = struct.pack("<HB", 9, 0x2F) + b"C:\\\x00\x00\x00"
    folder = struct.pack("<HBBIIH", 0x1E, 0x31, 0x00,
                         1234, 0x00205720, 0x0024) \
        + b"FLAG~1\x00" + b"\x00" * (0x1E - 14 - 8)
    idl = drive + folder + b"\x00\x00"
    import tempfile
    kids = {"BagMRU": {"sub": {"0": {"sub": {}, "vals": []}},
                       "vals": [("0", 3, idl)]}}
    path = os.path.join(tempfile.mkdtemp(), "t.dat")
    open(path, "wb").write(hive_parse._mkhive("ROOT", kids))
    hv = hive_parse.Hive(path)
    node, _ = hv.find("BagMRU")
    vals = {v["name"]: v["raw"] for v in hv.values(node)}
    out = []
    _walk(hv, node, vals, "", out)
    assert len(out) == 1, out
    assert "FLAG" in out[0]["path"], out
    parts = itemidlist(idl)["parts"]
    assert parts[0]["name"] == "C:\\", parts
    assert parts[1].get("dos_name") == "FLAG~1", parts
    assert parts[1]["size"] == 1234
    print("shellbags selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="BagMRU shellbag decoder")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--grep")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    res = shellbags(a.path)
    if a.grep:
        g = a.grep.lower()
        for bag in res:
            bag["entries"] = [e for e in bag["entries"]
                              if g in e["path"].lower()]
    print(json.dumps({"bags": res,
                      "entries": sum(len(b["entries"]) for b in res)},
                     indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
