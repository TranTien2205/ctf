#!/usr/bin/env python3
"""zip_crack.py -- dictionary attack on ZipCrypto-encrypted entries.

Usage:
  python3 tools/zip_crack.py secret.zip words.txt
  python3 tools/zip_crack.py --selftest

Traditional ZipCrypto (general-purpose bit 0): keys seed to
[0x12345678, 0x23456789, 0x34567890]; each plaintext byte rolls the
three keys through crc32/lcg, and the keystream byte comes from key2.
The 12-byte header's last byte is the high byte of the entry CRC (or
of the DOS mtime when flag bit 3 is set) - it rejects a wrong
password in 12 bytes instead of a full decrypt. AES-encrypted
(WinZip) entries are reported, not attacked.
"""
import argparse
import binascii
import json
import struct
import tempfile
import zipfile
from pathlib import Path

CRC = binascii.crc32


def _ktab():
    # crc32 table for the key update (poly 0xEDB88320)
    t = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = (c >> 1) ^ 0xEDB88320 if c & 1 else c >> 1
        t.append(c)
    return t


_T = _ktab()


def _upd(keys, b):
    keys[0] = _T[(keys[0] ^ b) & 0xFF] ^ (keys[0] >> 8)
    keys[1] = (keys[1] + (keys[0] & 0xFF)) * 134775813 + 1
    keys[1] &= 0xFFFFFFFF
    keys[2] = _T[(keys[2] ^ (keys[1] >> 24)) & 0xFF] ^ (keys[2] >> 8)


def _init(pwd):
    k = [0x12345678, 0x23456789, 0x34567890]
    for b in pwd:
        _upd(k, b)
    return k


def _stream(keys):
    t = ((keys[2] | 2) & 0xFFFFFFFF)
    return ((t * (t ^ 1)) >> 8) & 0xFF


def decrypt(keys, data):
    out = bytearray()
    for c in data:
        p = c ^ _stream(keys)
        _upd(keys, p)
        out.append(p)
    return bytes(out)


def encrypt(keys, data):
    out = bytearray()
    for p in data:
        c = p ^ _stream(keys)
        _upd(keys, p)
        out.append(c)
    return bytes(out)


def encrypted_entries(path):
    zf = zipfile.ZipFile(path)
    out = []
    for i in zf.infolist():
        if i.flag_bits & 1:
            out.append(i)
    zf.close()
    return out


def _entry_bytes(path, info):
    raw = Path(path).read_bytes()
    # local header: sig + 26 bytes then name+extra
    pos = raw.find(b"PK\x03\x04")
    nl, el = struct.unpack("<HH", raw[pos + 26:pos + 30])
    return raw[pos + 30 + nl + el:pos + 30 + nl + el + info.compress_size]


def crack(path, wordlist):
    infos = encrypted_entries(path)
    if not infos:
        return {"error": "no ZipCrypto-encrypted entries"}
    info = infos[0]
    blob = _entry_bytes(path, info)[:12 + 4096]
    # check byte: high byte of CRC, or of mtime if bit 3 set
    chk = (info.CRC >> 24) & 0xFF if not info.flag_bits & 8 else \
        (info.date_time[5] * 2 | info.date_time[4] << 5) & 0xFF
    tried = 0
    for line in Path(wordlist).read_bytes().splitlines():
        tried += 1
        k = _init(line.strip())
        if decrypt(k, blob[:12])[11] == chk:
            zf = zipfile.ZipFile(path)
            try:
                data = zf.read(info, pwd=line.strip())
                ok = CRC(data) & 0xFFFFFFFF == info.CRC
            except Exception:
                ok = False
            zf.close()
            return {"password": line.strip().decode("utf-8",
                                                    "replace"),
                    "verified": ok, "entry": info.filename,
                    "tried": tried}
    return {"password": None, "tried": tried}


def _selftest():
    # hand-build a minimal zip with an encrypted stored entry
    pt = b"flag{zipcrypto_is_fallible}"
    pwd = b"hunter2"
    k = _init(pwd)
    hdr = bytearray(b"\xAA" * 12)
    crc = CRC(pt) & 0xFFFFFFFF
    hdr[11] = (crc >> 24) & 0xFF
    blob = encrypt(k, bytes(hdr) + pt)
    name = b"f.txt"
    zf_path = Path(tempfile.mkdtemp()) / "s.zip"
    local = (b"PK\x03\x04" + struct.pack("<HHHHHIIIHH",
             20, 1, 0, 0, 0, crc, len(blob), len(pt) + 12,
             len(name), 0) + name + blob)
    # flags bit0=encrypted; sizes: compressed=blob len, uncomp=pt len
    local = (b"PK\x03\x04" + struct.pack("<HHHHHIIIHH",
             20, 1, 0, 0, 0, crc, len(blob), len(pt),
             len(name), 0) + name + blob)
    cent = (b"PK\x01\x02" + struct.pack("<HHHHHHIIIHHHHHII",
            20, 20, 1, 0, 0, 0, crc, len(blob), len(pt),
            len(name), 0, 0, 0, 0, 0, 0) + name)
    end = (b"PK\x05\x06" + struct.pack("<HHHHIIH",
           0, 0, 1, 1, len(cent), len(local), 0))
    zf_path.write_bytes(local + cent + end)
    # sanity: stdlib zipfile can read it with the password
    try:
        zf = zipfile.ZipFile(zf_path)
        got = zf.read("f.txt", pwd=pwd)
        zf.close()
        assert got == pt, got
    except Exception as e:
        raise AssertionError(f"stdlib could not read fixture: {e}")
    wl = Path(tempfile.mkdtemp()) / "w.txt"
    wl.write_bytes(b"letmein\nhunter2\nadmin\n")
    r = crack(zf_path, wl)
    assert r["password"] == "hunter2" and r["verified"], r
    print("zip_crack selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="dictionary attack on ZipCrypto entries")
    ap.add_argument("file", nargs="?")
    ap.add_argument("wordlist", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file or not a.wordlist:
        ap.error("file and wordlist required")
    print(json.dumps(crack(a.file, a.wordlist), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
