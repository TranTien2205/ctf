#!/usr/bin/env python3
"""luks_info.py -- LUKS encrypted-volume header inventory.

A `.dd` that starts with `LUKS` magic is a dead end for fs readers
until you know what is inside: LUKS1's 592-byte header carries the
cipher/mode/hash, key size, payload offset, and eight key slots with
their KDF parameters (iterations, salt, stripes). LUKS2 replaces it
with a binary header plus a JSON metadata area -- read that JSON and
the whole config is visible. This answers "is it encrypted, with
what, and which slots are live" without cryptsetup.

  python3 tools/forensics/luks_info.py vol.img
  python3 tools/forensics/luks_info.py --selftest
"""
import argparse
import json
import struct

SLOT_ACTIVE = {0x00000000: "disabled", 0x00AC71F3: "active",
               0x0002AC71: "cleared"}


def _luks1(d):
    ver = struct.unpack(">H", d[6:8])[0]
    out = {"luks_version": ver,
           "cipher": d[8:40].split(b"\x00")[0].decode("latin-1"),
           "cipher_mode": d[40:72].split(b"\x00")[0].decode("latin-1"),
           "hash": d[72:104].split(b"\x00")[0].decode("latin-1"),
           "payload_offset_sectors": struct.unpack(">I", d[104:108])[0],
           "key_bytes": struct.unpack(">I", d[108:112])[0],
           "mk_digest_iterations": struct.unpack(">I", d[132:136])[0],
           "slots": []}
    for i in range(8):
        off = 136 + i * 48
        state, = struct.unpack(">I", d[off:off + 4])
        iters, = struct.unpack(">I", d[off + 4:off + 8])
        salt = d[off + 8:off + 40].hex()
        mat_off, stripes = struct.unpack(">II", d[off + 40:off + 48])
        out["slots"].append({
            "slot": i, "state": SLOT_ACTIVE.get(state, "0x%x" % state),
            "iterations": iters, "salt": salt[:16] + "...",
            "key_material_offset_sectors": mat_off,
            "stripes": stripes})
    return out


def _luks2(d):
    ver = struct.unpack(">H", d[6:8])[0]
    hdr_size = struct.unpack(">Q", d[8:16])[0]
    out = {"luks_version": ver, "header_size": hdr_size,
           "label": d[88:152].split(b"\x00")[0].decode("latin-1")}
    j = d[4096:4096 + hdr_size * 512 - 4096] if hdr_size > 8 else b""
    end = j.find(b"\x00")
    if end > 0:
        try:
            meta = json.loads(j[:end])
            out["config"] = meta
            segs = meta.get("segments", {})
            for name, seg in segs.items():
                out.setdefault("segments", []).append({
                    "id": name, "type": seg.get("type"),
                    "cipher": seg.get("encryption"),
                    "offset": seg.get("offset"),
                    "integrity": seg.get("integrity")})
            for name, ks in meta.get("keyslots", {}).items():
                out.setdefault("slots", []).append({
                    "slot": name, "type": ks.get("type"),
                    "kdf": (ks.get("kdf") or {}).get("type"),
                    "area_offset": (ks.get("area") or {}).get("offset")})
        except ValueError:
            out["warning"] = "JSON area unreadable"
    return out


def parse(data):
    if len(data) < 592 or data[:6] != b"LUKS\xba\xbe":
        return {"error": "not a LUKS volume"}
    ver = struct.unpack(">H", data[6:8])[0]
    if ver == 1:
        return _luks1(data)
    if ver == 2:
        return _luks2(data)
    return {"error": "unknown LUKS version %d" % ver,
            "luks_version": ver}


def _selftest():
    d = bytearray(4096 + 512)
    d[:6] = b"LUKS\xba\xbe"
    struct.pack_into(">H", d, 6, 1)
    d[8:8 + 8] = b"aes\x00".ljust(8, b"\x00")
    d[40:48] = b"xts-pla\x00"
    d[72:79] = b"sha256\x00"
    struct.pack_into(">III", d, 104, 4096, 32, 250000)
    struct.pack_into(">II", d, 136, 0x00AC71F3, 200000)
    d[144:176] = b"\x11" * 32
    struct.pack_into(">II", d, 176, 8, 4000)
    struct.pack_into(">I", d, 136 + 48, 0)  # slot1 disabled
    out = parse(bytes(d))
    assert out["luks_version"] == 1
    assert out["cipher"] == "aes" and out["cipher_mode"] == "xts-pla"
    assert out["slots"][0]["state"] == "active"
    assert out["slots"][0]["key_material_offset_sectors"] == 8
    assert out["slots"][1]["state"] == "disabled"
    # LUKS2: binary hdr + JSON at 4096
    d2 = bytearray(4096 + 4096)
    d2[:6] = b"LUKS\xba\xbe"
    struct.pack_into(">H", d2, 6, 2)
    struct.pack_into(">Q", d2, 8, 16)      # hdr size in sectors
    d2[88:88 + 5] = b"mylab"
    meta = {"segments": {"0": {"type": "crypt",
                              "encryption": "aes-xts-plain64",
                              "offset": "16777216"}},
            "keyslots": {"0": {"type": "luks2",
                               "kdf": {"type": "argon2i"},
                               "area": {"offset": "32768"}}}}
    d2[4096:4096 + len(json.dumps(meta))] = json.dumps(meta).encode()
    out2 = parse(bytes(d2))
    assert out2["luks_version"] == 2 and out2["label"] == "mylab"
    assert out2["segments"][0]["cipher"] == "aes-xts-plain64", out2
    assert out2["slots"][0]["kdf"] == "argon2i", out2
    assert parse(b"junk")["error"]
    print("luks_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="LUKS header inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    print(json.dumps(parse(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
