#!/usr/bin/env python3
"""pgp_parse.py -- OpenPGP packet inventory (RFC4880).

A `.pgp`/`.gpg`/`.asc` handout's first question is always "what kind
of packets are these" — a public key block, a detached signature, or
a message? `gpg --list-packets` is not assumed. This walks old- and
new-format packet headers, names every packet type, and surfaces the
fields that pick the attack: public-key algorithm IDs and key sizes,
User IDs, signature issuer keyids/hash algos, and which symmetric
cipher a message claims. Inventory only — it never decrypts and says
so when a packet is encrypted.

  python3 tools/pgp_parse.py file.pgp
  python3 tools/pgp_parse.py --armor msg.asc
  python3 tools/pgp_parse.py --selftest
"""
import argparse
import base64
import json
import struct
import sys

PKT = {0: "reserved", 1: "pk-enc-session-key", 2: "signature",
       3: "sk-enc-session-key", 4: "one-pass-sig", 5: "secret-key",
       6: "public-key", 7: "secret-subkey", 8: "compressed",
       9: "sym-encrypted", 10: "marker", 11: "literal-data",
       12: "trust", 13: "user-id", 14: "public-subkey",
       17: "user-attribute", 18: "sym-enc-integrity", 19: "mdc",
       60: "private", 63: "private"}
PKALG = {1: "RSA", 2: "RSA-encrypt-only", 3: "RSA-sign-only",
         16: "ElGamal", 17: "DSA", 18: "ECDH", 19: "ECDSA",
         20: "ElGamal-split", 21: "DH", 22: "EdDSA"}
SYMALG = {0: "plain", 1: "IDEA", 2: "3DES", 3: "CAST5", 4: "Blowfish",
          7: "AES-128", 8: "AES-192", 9: "AES-256", 10: "Twofish",
          11: "Camellia-128", 12: "Camellia-192", 13: "Camellia-256"}
HASHALG = {1: "MD5", 2: "SHA-1", 3: "RIPEMD-160", 8: "SHA-256",
           9: "SHA-384", 10: "SHA-512", 11: "SHA-224"}


def _mpi(b, i):
    bits = struct.unpack(">H", b[i:i + 2])[0]
    n = (bits + 7) // 8
    return bits, i + 2 + n


def _key_body(b):
    ver = b[0]
    out = {"version": ver}
    if ver not in (3, 4):
        return out
    out["created"] = struct.unpack(">I", b[1:5])[0]
    alg = b[5] if ver == 4 else b[7]
    out["pkalg"] = PKALG.get(alg, "alg-%d" % alg)
    i = 6 if ver == 4 else 8
    if alg in (1, 2, 3):                             # RSA: n, e
        nbits, i = _mpi(b, i)
        out["key_bits"] = nbits
        _ebits, i = _mpi(b, i)
    elif alg == 17:                                  # DSA: p,q,g,y
        nbits, i = _mpi(b, i)
        out["key_bits"] = nbits
    return out


def _sig_body(b):
    ver = b[0]
    out = {"version": ver}
    if ver == 4:
        out["sig_type"] = b[1]
        out["pkalg"] = PKALG.get(b[2], b[2])
        out["hashalg"] = HASHALG.get(b[3], b[3])
        hlen = struct.unpack(">H", b[4:6])[0]
        sub = b[6:6 + hlen]
        j = 0
        while j + 2 <= len(sub):
            slen = sub[j]
            styp = sub[j + 1]
            sval = sub[j + 2:j + 2 + slen - 1]
            if styp == 16 and len(sval) == 8:        # issuer keyid
                out["issuer_keyid"] = "0x%016x" % struct.unpack(
                    ">Q", sval)[0]
            j += 1 + slen
    return out


def walk(b, depth=0, limit=100):
    out = []
    i = 0
    while i < len(b) and limit > 0:
        limit -= 1
        h = b[i]
        i += 1
        if not h & 0x80:
            out.append({"error": "unsynced at %d" % (i - 1)})
            break
        if h & 0x40:                                 # new format
            typ = h & 0x3F
            l1 = b[i]
            i += 1
            if l1 < 192:
                n = l1
            elif l1 < 224:
                n = ((l1 - 192) << 8) + b[i] + 192
                i += 1
            elif l1 == 255:
                n = struct.unpack(">I", b[i:i + 4])[0]
                i += 4
            else:                                    # partial length
                n = 1 << (l1 & 0x1F)
                out.append({"type": PKT.get(typ, typ),
                            "partial": True, "len": n})
                i += n
                continue
        else:                                        # old format
            typ = (h >> 2) & 0xF
            lt = h & 3
            if lt == 0:
                n = b[i]; i += 1
            elif lt == 1:
                n = struct.unpack(">H", b[i:i + 2])[0]; i += 2
            elif lt == 2:
                n = struct.unpack(">I", b[i:i + 4])[0]; i += 4
            else:
                n = len(b) - i
        body = b[i:i + n]
        ent = {"type": PKT.get(typ, "type-%d" % typ), "len": n}
        if typ in (5, 6, 7, 14) and len(body) >= 7:
            ent.update(_key_body(body))
        elif typ == 13:
            ent["user_id"] = body.decode("utf-8", "replace")
        elif typ == 2 and len(body) > 6:
            ent.update(_sig_body(body))
        elif typ == 9:
            ent["encrypted"] = True
            ent["note"] = "algorithm lives in the session-key packet"
        elif typ == 18:
            ent["encrypted"] = True
            ent["protected"] = "MDC (integrity-protected)"
        elif typ == 1 and len(body) > 10:
            ent["keyid"] = "0x%016x" % struct.unpack(">Q", body[1:9])[0]
            ent["pkalg"] = PKALG.get(body[9], body[9])
            ent["encrypted"] = True
        elif typ == 3 and len(body) > 4:
            ent["symalg"] = SYMALG.get(body[1], body[1])
            ent["encrypted"] = True
        out.append(ent)
        i += n
    return out


def parse(data, armor=False):
    if armor or data.lstrip().startswith(b"-----BEGIN"):
        try:
            lines = data.decode("utf-8", "replace").splitlines()
            body = [l for l in lines
                    if l and not l.startswith("-----")
                    and not l.startswith("=")
                    and ":" not in l[:20]]
            data = base64.b64decode("".join(body))
        except Exception as exc:
            return {"error": "armor decode failed: %s" % exc}
    pkts = walk(data)
    return {"packets": pkts, "count": len(pkts),
            "encrypted": any(p.get("encrypted") for p in pkts),
            "user_ids": [p["user_id"] for p in pkts if "user_id" in p],
            "key_ids": [p.get("issuer_keyid") or p.get("keyid")
                        for p in pkts
                        if p.get("issuer_keyid") or p.get("keyid")],
            "note": "inventory only -- encrypted bodies not decrypted"}


def _selftest():
    # public-key packet (v4 RSA), user-id, signature packet
    def npkt(tag, body):
        return bytes([0xC0 | tag]) + _len(len(body)) + body
    def _len(n):
        if n < 192:
            return bytes([n])
        if n < 8383:
            return bytes([192 + ((n - 192) >> 8), (n - 192) & 0xFF])
        return b"\xff" + struct.pack(">I", n)
    key = (b"\x04" + struct.pack(">I", 0x60000000) + b"\x01"
           + struct.pack(">H", 1024) + b"\xaa" * 128
           + struct.pack(">H", 17) + b"\x01\x00\x01")
    uid = b"Tester <t@t>"
    sub = bytes([9, 16]) + b"\xde\xad\xbe\xef\x12\x34\x56\x78"
    sig = (b"\x04" + b"\x13" + b"\x01" + b"\x08"
           + struct.pack(">H", len(sub)) + sub
           + struct.pack(">H", 0) + b"\x00" * 20)
    blob = npkt(6, key) + npkt(13, uid) + npkt(2, sig)
    r = parse(blob)
    pk = r["packets"][0]
    assert pk["type"] == "public-key" and pk["key_bits"] == 1024, pk
    assert pk["pkalg"] == "RSA"
    assert r["user_ids"] == ["Tester <t@t>"]
    assert r["key_ids"] == ["0xdeadbeef12345678"], r["key_ids"]
    # encrypted: sk session + sym-enc-integrity
    blob2 = (npkt(3, b"\x04" + b"\x09\x04\x00" + b"\x00" * 10)
             + npkt(18, b"\x01" + b"\x00" * 20))
    r2 = parse(blob2)
    assert r2["encrypted"] and r2["packets"][0]["symalg"] == "AES-256"
    print("pgp_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="OpenPGP packet inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--armor", action="store_true",
                    help="input is ASCII-armored")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    print(json.dumps(parse(open(a.path, "rb").read(), a.armor),
                     indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
