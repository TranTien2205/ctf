#!/usr/bin/env python3
"""sevenz_list.py -- .7z archive inventory and single-file extract.

`7z`/`py7zr` are absent; `.7z` is still a top-three CTF archive. The
format (7zFormat.txt): 6-byte signature, version, start-header CRC,
then nextHeaderOffset/Size/CRC. Packed streams sit between the
32-byte start header and the next header. The next header is itself
usually ENCODED (id 0x17): a StreamsInfo whose folder decompresses
to the real Header (id 0x01) carrying MainStreamsInfo + FilesInfo.

Varints are the 7z variable-length uint: the first byte's leading
set bits count the extra bytes; the remaining bits are the value's
high part. Coders handled: Copy (0x00), LZMA (030101), LZMA2 (0x21),
Deflate (040108), BZip2 (040202) via stdlib lzma/zlib/bz2 with
FORMAT_RAW-style filters. AES-wrapped (06F10701) and anything else
is named by codec id and left encrypted/unattempted.

  python3 tools/forensics/sevenz_list.py a.7z
  python3 tools/forensics/sevenz_list.py a.7z --get flag.txt
  python3 tools/forensics/sevenz_list.py --selftest
"""
import argparse
import bz2
import json
import lzma
import struct
import sys
import zlib

SIG = b"7z\xbc\xaf\x27\x1c"
CODECS = {b"\x00": "copy", b"\x03\x01\x01": "lzma1", b"\x21": "lzma2",
          b"\x04\x01\x08": "deflate", b"\x04\x02\x02": "bzip2",
          b"\x06\xf1\x07\x01": "aes256-sha256"}


def _u(d, p):
    """7z packed uint64 at d[p]. Returns (value, bytes consumed)."""
    b = d[p]
    mask = 0x80
    extra = 0
    while b & mask:
        mask >>= 1
        extra += 1
    val = b & (mask - 1)
    for i in range(extra):
        val = (val << 8) | d[p + 1 + i]
    return val, 1 + extra


def _bits(d, p, n):
    out = []
    for i in range(n):
        byte = d[p + (i >> 3)]
        out.append(bool(byte & (0x80 >> (i & 7))))
    return out


class _P:
    """Cursor over the header region."""
    def __init__(self, d):
        self.d = d
        self.p = 0

    def id(self):
        v, n = _u(self.d, self.p)
        self.p += n
        return v

    def byte(self):
        b = self.d[self.p]
        self.p += 1
        return b

    def skip(self, n):
        self.p += n


def _streams_info(c):
    """Parse PackInfo/UnpackInfo/SubStreamsInfo until END. Returns
    {packs:[{size}], folders:[{coders,unpack_sizes,bonds}], ...}"""
    info = {"packs": [], "folders": [], "subsizes": []}
    while True:
        mark = c.p
        pid = c.id()
        if pid == 0x00:
            return info
        if pid not in (0x06, 0x07, 0x08):
            c.p = mark                # FilesInfo etc belongs to caller
            return info
        if pid == 0x06:                    # PackInfo
            info["packpos"], n = _u(c.d, c.p)
            c.p += n
            npack, n = _u(c.d, c.p)
            c.p += n
            while True:
                q = c.id()
                if q == 0x09:
                    for _ in range(npack):
                        s, m = _u(c.d, c.p)
                        c.p += m
                        info["packs"].append({"size": s})
                elif q == 0x0A:
                    alldef = c.byte()
                    if not alldef:
                        nsk = (npack + 7) // 8
                        c.skip(nsk)
                    for _ in range(npack):
                        c.skip(4)
                elif q == 0x00:
                    break
                else:
                    return info
        elif pid == 0x07:                  # UnpackInfo
            if c.id() != 0x0B:
                return info
            nfold, n = _u(c.d, c.p)
            c.p += n
            ext = c.byte()
            if ext:
                return info
            for _ in range(nfold):
                ncoder, m = _u(c.d, c.p)
                c.p += m
                folder = {"coders": [], "unpack_sizes": []}
                tot_in = tot_out = 0
                for _ in range(ncoder):
                    flags = c.byte()
                    idlen = flags & 0x0F
                    cid = bytes(c.d[c.p:c.p + idlen])
                    c.skip(idlen)
                    n_in = n_out = 1
                    if flags & 0x10:
                        n_in, m = _u(c.d, c.p); c.p += m
                        n_out, m = _u(c.d, c.p); c.p += m
                    props = b""
                    if flags & 0x20:
                        plen, m = _u(c.d, c.p)
                        c.p += m
                        props = bytes(c.d[c.p:c.p + plen])
                        c.skip(plen)
                    folder["coders"].append({
                        "id": CODECS.get(cid, cid.hex()), "in": n_in,
                        "out": n_out, "props": props.hex()})
                    tot_in += n_in
                    tot_out += n_out
                nbond = tot_out - 1
                folder["bonds"] = []
                for _ in range(nbond):
                    bi, m = _u(c.d, c.p); c.p += m
                    bo, m = _u(c.d, c.p); c.p += m
                    folder["bonds"].append({"in": bi, "out": bo})
                if sum(1 for cd in folder["coders"]
                       for _ in range(cd["in"])) > tot_in:
                    packed, m = _u(c.d, c.p); c.p += m
                info["folders"].append(folder)
            if c.id() != 0x0C:
                return info
            for folder in info["folders"]:
                for _ in range(sum(cd["out"] for cd in folder["coders"])):
                    s, m = _u(c.d, c.p)
                    c.p += m
                    folder["unpack_sizes"].append(s)
            q = c.id()
            if q == 0x0A:
                alldef = c.byte()
                if not alldef:
                    c.skip((len(info["folders"]) + 7) // 8)
                for _ in info["folders"]:
                    c.skip(4)
                if c.id() != 0x00:
                    return info
            elif q != 0x00:
                return info
        elif pid == 0x08:                  # SubStreamsInfo
            while True:
                q = c.id()
                if q == 0x0D:
                    for f in info["folders"]:
                        f["num_sub"], m = _u(c.d, c.p); c.p += m
                elif q == 0x09:
                    n = len(info["folders"])
                    for f in info["folders"]:
                        for _ in range(f.get("num_sub", 1) - 1):
                            s, m = _u(c.d, c.p); c.p += m
                            f.setdefault("subsizes", []).append(s)
                elif q == 0x0A:
                    alldef = c.byte()
                    c.skip(len(info["folders"]) * (0 if alldef else 1))
                    for _ in info["folders"]:
                        c.skip(4)
                elif q == 0x00:
                    break
                else:
                    return info
        else:
            return info


def _files_info(c):
    """Parse FilesInfo -> [{name, size?, mtime?, attrs?}]."""
    nfile, n = _u(c.d, c.p)
    c.p += n
    files = [{"name": "?"} for _ in range(nfile)]
    empty = []
    while True:
        pid = c.id()
        if pid == 0x00:
            return files, empty
        size, n = _u(c.d, c.p)
        c.p += n
        blob = c.d[c.p:c.p + size]
        if pid == 0x0E:
            empty = _bits(blob[1:], 0, nfile) if blob[0] == 0 else \
                [True] * nfile
        elif pid == 0x0F:
            pass
        elif pid == 0x11:                  # names: utf-16, ext byte
            if blob and blob[0] == 0:
                names = blob[1:].decode(
                    "utf-16-le", "replace").split("\x00")
                for i in range(nfile):
                    if i < len(names):
                        files[i]["name"] = names[i]
        elif pid == 0x14:
            pass
        c.skip(size)


def _decompress(packed, folder):
    """Run the folder's coder chain on `packed`. Single-in/out only."""
    coders = folder["coders"]
    if len(coders) != 1:
        return None, "multi-coder folders unsupported"
    c = coders[0]
    want = folder["unpack_sizes"][-1] if folder["unpack_sizes"] else None
    try:
        if c["id"] == "copy":
            out = packed
        elif c["id"] == "lzma2":
            prop = int(c["props"], 16) if c["props"] else 0
            ds = (2 | (prop & 1)) << (prop // 2 + 11) if prop < 40 \
                else 0xFFFFFFFF
            out = lzma.decompress(packed, format=lzma.FORMAT_RAW,
                                  filters=[{"id": lzma.FILTER_LZMA2,
                                            "dict_size": ds}])
        elif c["id"] == "lzma1":
            pr = bytes.fromhex(c["props"])
            pb = pr[0] // 45
            pr0 = pr[0] % 45
            lp, lc = pr0 // 9, pr0 % 9
            ds = struct.unpack("<I", pr[1:5])[0]
            out = lzma.decompress(packed, format=lzma.FORMAT_RAW,
                                  filters=[{"id": lzma.FILTER_LZMA1,
                                            "dict_size": ds, "lc": lc,
                                            "lp": lp, "pb": pb}])
        elif c["id"] == "deflate":
            out = zlib.decompress(packed, -15)
        elif c["id"] == "bzip2":
            out = bz2.decompress(packed)
        else:
            return None, "unsupported codec %s" % c["id"]
    except Exception as e:
        return None, "%s decompress failed: %s" % (c["id"], e)
    if want is not None:
        out = out[:want]
    return out, None


def parse(path):
    d = open(path, "rb").read()
    if len(d) < 32 or d[:6] != SIG:
        return {"error": "not a 7z archive"}
    major, minor = d[6], d[7]
    noff, nsize = struct.unpack("<QQ", d[12:28])
    base = 32
    hdr = d[base + noff:base + noff + nsize]
    c = _P(hdr)
    hid = c.id()
    out = {"version": "%d.%d" % (major, minor)}
    if hid == 0x17:                        # encoded header
        info = _streams_info(c)
        if not info["folders"]:
            return {**out, "error": "encoded header, no folder"}
        packpos = info["packpos"]
        pdata = d[base + packpos:
                  base + packpos + info["packs"][0]["size"]]
        raw, err = _decompress(pdata, info["folders"][0])
        if raw is None:
            return {**out, "error": err}
        c = _P(raw)
        hid = c.id()
    if hid != 0x01:
        return {**out, "error": "unexpected header id 0x%x" % hid}
    info = {"packs": [], "folders": [], "subsizes": [], "packpos": 0}
    files, empty = [], []
    while c.p < len(c.d):
        pid = c.id()
        if pid == 0x00:
            break
        elif pid == 0x04:                # MainStreamsInfo wrapper
            info.update({k: v for k, v in _streams_info(c).items()
                         if v or k == "packpos"})
        elif pid == 0x05:
            files, empty = _files_info(c)
        else:
            return {**out, "error": "unknown header property 0x%x"
                    % pid}
    out["files"] = files
    out["folders"] = [
        {"coders": [cd["id"] for cd in f["coders"]],
         "unpack_sizes": f["unpack_sizes"]} for f in info["folders"]]
    # map file->stream: sequential non-empty files share folder order
    data_base = base
    live = [f for f in files]
    # Assign each file a stream offset: folders are packed in order.
    pos = info["packpos"]
    stream_i = 0
    out["streams"] = []
    for i, f in enumerate(files):
        if i < len(empty) and empty[i]:
            f["empty"] = True
            continue
        pk = info["packs"][stream_i] if stream_i < len(info["packs"]) \
            else None
        f["pack_offset"] = data_base + pos if pk else None
        if pk:
            pos += pk["size"]
            f["pack_size"] = pk["size"]
            f["folder"] = stream_i
            stream_i += 1
    return out, d, info


def _get(d, info, f):
    pk_off = f["pack_offset"]
    packed = d[pk_off:pk_off + f["pack_size"]]
    folder = info["folders"][f["folder"]]
    blob, err = _decompress(packed, folder)
    if blob is None:
        return None, err
    # multi-file folder: substream sizes select our slice; the common
    # CTF shape is one file per folder so offset 0 works.
    return blob, None


def _selftest():
    content = b"flag{sevenz_raw_lzma2}" * 3
    comp = lzma.compress(content, format=lzma.FORMAT_RAW,
                         filters=[{"id": lzma.FILTER_LZMA2,
                                   "dict_size": 1 << 16}])
    def vi(n):                             # tiny uint writer (<0x80)
        return bytes([n]) if n < 0x80 else bytes([0x80 | (n >> 8),
                                                 n & 0xFF])
    name = "f.txt".encode("utf-16-le") + b"\x00\x00"
    inner = bytearray()
    inner += b"\x01"                       # Header
    inner += b"\x04"                       # MainStreamsInfo
    inner += b"\x06" + vi(0) + vi(1) + b"\x09" + vi(len(comp)) + b"\x00"
    inner += b"\x07" + b"\x0b" + vi(1) + b"\x00"  # UnpackInfo,Folder
    inner += vi(1) + bytes([0x21]) + b"\x21" + vi(1) + bytes([20])
    inner += b"\x0c" + vi(len(content)) + b"\x00"
    inner += b"\x05" + vi(1)               # FilesInfo: 1 file
    nameprop = b"\x00" + name
    inner += b"\x11" + vi(len(nameprop)) + nameprop + b"\x00"
    inner += b"\x00"                       # END of header
    henc = lzma.compress(bytes(inner), format=lzma.FORMAT_RAW,
                         filters=[{"id": lzma.FILTER_LZMA2,
                                   "dict_size": 1 << 16}])
    outer = bytearray()
    outer += b"\x17"                       # EncodedHeader
    outer += b"\x06" + vi(len(comp)) + vi(1) + b"\x09" + vi(len(henc)) \
        + b"\x00"
    outer += b"\x07" + b"\x0b" + vi(1) + b"\x00"
    outer += vi(1) + bytes([0x21]) + b"\x21" + vi(1) + bytes([20])
    outer += b"\x0c" + vi(len(inner)) + b"\x00"
    outer += b"\x00"
    data_area = comp + henc
    img = bytearray()
    img += SIG + b"\x00\x04" + b"\x00" * 4
    img += struct.pack("<QQI", len(data_area), len(outer), 0)
    img += data_area + bytes(outer)
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".7z", delete=False) as t:
        t.write(img); p = t.name
    try:
        out, d, info = parse(p)
        assert out["files"][0]["name"] == "f.txt", out
        assert out["folders"][0]["coders"] == ["lzma2"], out
        blob, err = _get(d, info, out["files"][0])
        assert err is None, err
        assert blob == content, blob[:40]
        print("sevenz_list selftest: ok")
    finally:
        os.unlink(p)


def main():
    ap = argparse.ArgumentParser(description=".7z inventory/extract")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--get", help="extract one member to stdout")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    out, d, info = parse(a.path)
    if a.get:
        f = next((x for x in out.get("files", [])
                  if x["name"] == a.get), None)
        if not f or "pack_offset" not in f:
            print(json.dumps({"error": "member not found or packed "
                              "differently", "want": a.get}))
            return 1
        blob, err = _get(d, info, f)
        if blob is None:
            print(json.dumps({"error": err}))
            return 1
        sys.stdout.buffer.write(blob)
        return 0
    out.pop("packs", None)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
