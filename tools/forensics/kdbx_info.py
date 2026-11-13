#!/usr/bin/env python3
"""kdbx_info.py -- KeePass KDBX3/4 header inventory.

A `.kdbx` in a triage bundle raises one question before any cracking:
which KDF/cipher protects it, and how expensive is the password run?
`keepassxc-cli` is not assumed. The format opens with two magic
u32s, a version u32, then TLV header entries naming the cipher,
compression, master seed, transform seed/rounds, IV, and the inner
stream id -- everything `hashcat -m 13400` or a dictionary plan
needs, without touching the encrypted body. Decryption is not done
and is named as such.

  python3 tools/forensics/kdbx_info.py vault.kdbx
  python3 tools/forensics/kdbx_info.py --selftest
"""
import argparse
import json
import struct
import sys

SIG1, SIG2 = 0x9AA2D903, 0xB54BFB67
CIPHER = {"31c1f2e6bf714350be5805216afc5aff": "AES-256",
          "ad68f29f576f4bb9a36ad47af965346c": "ChaCha20",
          "d6038a2b8b6f4cb5a524339a31dbb59a": "TwoFish"}
HDR = {0: "end", 1: "comment", 2: "cipher_id", 3: "compression",
       4: "master_seed", 5: "transform_seed", 6: "transform_rounds",
       7: "encryption_iv", 8: "protected_stream_key",
       9: "stream_start", 10: "inner_random_id",
       11: "kdf_parameters", 12: "public_custom_data"}


def parse(data):
    if len(data) < 16:
        return {"error": "too small"}
    s1, s2, ver = struct.unpack("<III", data[:12])
    if s1 != SIG1 or s2 != SIG2:
        return {"error": "not kdbx (bad signature)"}
    major = ver >> 16
    out = {"kdbx_version": "%d.%d" % (ver >> 16, ver & 0xFFFF),
           "fields": {}}
    pos = 12
    while pos + 3 <= len(data):
        hid = data[pos]
        pos += 1
        if major >= 4:
            hlen = struct.unpack("<I", data[pos:pos + 4])[0]
            pos += 4
        else:
            hlen = struct.unpack("<H", data[pos:pos + 2])[0]
            pos += 2
        val = data[pos:pos + hlen]
        pos += hlen
        nm = HDR.get(hid, "hdr-%d" % hid)
        if hid == 2 and len(val) == 16:
            out["fields"]["cipher"] = CIPHER.get(
                val.hex(), "uuid:" + val.hex())
        elif hid == 3:
            out["fields"]["compression"] = "gzip" if val == b"\x01" \
                else "none"
        elif hid in (6,):
            if len(val) == 8:
                out["fields"]["transform_rounds"] = struct.unpack(
                    "<Q", val)[0]
        elif hid == 11:
            out["fields"]["kdf_parameters"] = "variant-dict %dB" % \
                len(val)
        elif hid == 0:
            break
        elif len(val) <= 32:
            out["fields"][nm] = val.hex()
        else:
            out["fields"][nm] = "%d bytes" % len(val)
    out["note"] = ("header inventory only -- decrypt needs the master "
                   "key; transform_rounds estimates the dictionary-"
                   "attack cost")
    return out


def _selftest():
    def hdr(i, v):
        return bytes([i]) + struct.pack("<H", len(v)) + v
    blob = struct.pack("<III", SIG1, SIG2, 0x00030001)
    blob += hdr(2, bytes.fromhex(
        "31c1f2e6bf714350be5805216afc5aff"))
    blob += hdr(3, b"\x01")
    blob += hdr(4, b"\xde\xad" * 16)
    blob += hdr(5, b"\xbe\xef" * 16)
    blob += hdr(6, struct.pack("<Q", 600000))
    blob += hdr(7, b"\x01" * 16)
    blob += hdr(0, b"\r\n\r\n")
    r = parse(blob)
    f = r["fields"]
    assert f["cipher"] == "AES-256", f
    assert f["compression"] == "gzip"
    assert f["transform_rounds"] == 600000
    print("kdbx_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="KeePass kdbx inventory")
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
