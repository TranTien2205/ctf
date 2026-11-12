#!/usr/bin/env python3
"""ab_extract.py -- Android backup (.ab) inventory and extraction.

`adb backup` files are a text header, an optional DEFLATE stream, and
a tar archive: "ANDROID BACKUP\n<ver>\n<0|1 compressed>\n<enc>\n...".
There is no `abe.jar` or `android-backup-extractor` binary to assume
here. This tool parses the header, inflates when the header says the
payload is compressed, and lists or extracts the tar members with the
stdlib `tarfile`. An AES-256-encrypted backup is reported honestly --
PBKDF2+CBC decryption is possible offline but only pays when the
challenge supplies the passphrase, so the tool names the header fields
and stops.

  python3 tools/forensics/ab_extract.py backup.ab
  python3 tools/forensics/ab_extract.py backup.ab --list
  python3 tools/forensics/ab_extract.py backup.ab --extract NAME [--to DIR]
  python3 tools/forensics/ab_extract.py --selftest
"""
import argparse
import io
import json
import tarfile
import zlib
import sys


def parse(data):
    if not data.startswith(b"ANDROID BACKUP\n"):
        return {"error": "not an android backup (missing magic)"}
    rest = data.split(b"\n", 1)[1]
    fields = {}
    for name in ("version", "compressed", "encryption"):
        line, _, rest = rest.partition(b"\n")
        fields[name] = line.decode("ascii", "replace")
    out = {"format": "android_backup", "version": fields["version"],
           "compressed": fields["compressed"] == "1",
           "encryption": fields["encryption"]}
    if fields["encryption"] != "none":
        # Five more header lines carry the KDF parameters.
        names = ["user_salt", "master_checksum", "pbkdf2_rounds",
                 "userkey_iv", "master_key_blob"]
        for name in names:
            line, _, rest = rest.partition(b"\n")
            fields[name] = line.decode("ascii", "replace")
        out["kdf"] = {k: (v[:80] + ("..." if len(v) > 80 else ""))
                      for k, v in fields.items() if k in names}
        out["note"] = ("payload is AES-256-CBC under a passphrase-derived "
                       "key; decryption needs the passphrase -- stopped "
                       "at the header on purpose")
        return out
    body = rest
    if out["compressed"]:
        try:
            body = zlib.decompress(body)
        except zlib.error as exc:
            return {**out, "error": "deflate failed: %s" % exc}
    out["payload_size"] = len(body)
    try:
        tf = tarfile.open(fileobj=io.BytesIO(body))
        members = [{"name": m.name, "size": m.size, "type": m.type.decode(
            "ascii", "replace")} for m in tf.getmembers()]
        out["members"] = members
        out["member_count"] = len(members)
        hits = [m["name"] for m in members if "flag" in m["name"].lower()]
        if hits:
            out["flag_named_members"] = hits
    except tarfile.TarError as exc:
        out["error"] = "tar parse failed: %s" % exc
    return out


def _selftest():
    bio = io.BytesIO()
    with tarfile.open(fileobj=bio, mode="w") as tf:
        for name, payload in (("apps/x/db/flag.db", b"flag{in_ab}"),
                              ("shared/0/a.txt", b"hello")):
            ti = tarfile.TarInfo(name)
            ti.size = len(payload)
            tf.addfile(ti, io.BytesIO(payload))
    tarb = bio.getvalue()
    for comp in ("0", "1"):
        body = zlib.compress(tarb) if comp == "1" else tarb
        blob = ("ANDROID BACKUP\n5\n%s\nnone\n" % comp).encode() + body
        r = parse(blob)
        assert r["member_count"] == 2, (comp, r)
        assert "apps/x/db/flag.db" in r["flag_named_members"], r
    enc = parse(b"ANDROID BACKUP\n5\n1\nAES-256\n"
                b"aa\nbb\n10000\ncc\ndd\npayload")
    assert enc["kdf"]["pbkdf2_rounds"] == "10000", enc
    assert "note" in enc
    print("ab_extract selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="Android backup inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--extract", metavar="NAME")
    ap.add_argument("--to", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    if a.extract:
        rest = data.split(b"\n", 4)[4] if data.startswith(
            b"ANDROID BACKUP\n") else b""
        if data.split(b"\n")[3] == b"1":
            rest = zlib.decompress(rest)
        with tarfile.open(fileobj=io.BytesIO(rest)) as tf:
            m = tf.getmember(a.extract)
            out = tf.extractfile(m).read()
            dest = "%s/%s" % (a.to, m.name.replace("/", "_"))
            open(dest, "wb").write(out)
            print(json.dumps({"wrote": dest, "size": len(out)}))
        return
    print(json.dumps(parse(data), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
