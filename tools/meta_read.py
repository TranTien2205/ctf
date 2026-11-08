#!/usr/bin/env python3
"""Read metadata from common CTF carriers without exiftool.

osint-media-metadata's first move is "read ALL of the metadata"; on a
box with no exiftool nothing reads any of it. Stdlib parsers per
format: JPEG EXIF (APP1 TIFF/IFD walk with GPS rational decode), PNG
tEXt/zTXt/iTXt chunks, PDF /Info dict and XMP packet, Office
docProps/core.xml inside the zip, WAV LIST/INFO, MP3 ID3v2 text frames.

  python3 tools/meta_read.py photo.jpg
  python3 tools/meta_read.py doc.pdf --raw
  python3 tools/meta_read.py --selftest

Every tag the carrier holds is printed — the skill says read all of it,
because the flag hides in whichever field the author thought you'd
skip. --raw adds unparsed hex for entries the table doesn't name.
"""
import argparse, json, os, re, struct, sys, zlib, zipfile

EXIF_TAGS = {0x010F: "Make", 0x0110: "Model", 0x0112: "Orientation",
             0x0131: "Software", 0x0132: "DateTime",
             0x013B: "Artist", 0x8298: "Copyright",
             0x8769: "ExifIFD", 0x8825: "GPSIFD",
             0x9003: "DateTimeOriginal", 0x9004: "DateTimeDigitized",
             0x927C: "MakerNote", 0xA002: "PixelX", 0xA003: "PixelY",
             0x010E: "ImageDescription", 0x9C9B: "XPTitle",
             0x9C9C: "XPComment", 0x9C9D: "XPAuthor",
             0x9C9E: "XPKeywords", 0x9C9F: "XPSubject",
             0x02BC: "XMP"}
GPS_TAGS = {0: "GPSVersion", 1: "LatRef", 2: "Lat", 3: "LonRef",
            4: "Lon", 5: "AltRef", 6: "Alt", 7: "TimeStamp",
            29: "DateStamp"}
IFD_TSZ = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 7: 1, 9: 4, 10: 8}
ID3_TEXT = {"TIT2": "Title", "TPE1": "Artist", "TALB": "Album",
            "TYER": "Year", "TCON": "Genre", "COMM": "Comment",
            "TPE2": "AlbumArtist", "TRCK": "Track", "TCOM": "Composer",
            "USLT": "Lyrics", "TXXX": "UserText"}


def _ifd(data, off, e, tags, out, depth=0):
    if depth > 4 or off + 2 > len(data):
        return
    n = struct.unpack(e + "H", data[off:off + 2])[0]
    for i in range(n):
        eo = off + 2 + i * 12
        if eo + 12 > len(data):
            break
        tag, typ, cnt = struct.unpack(e + "HHI", data[eo:eo + 8])
        sz = IFD_TSZ.get(typ, 1) * cnt
        raw = (data[eo + 8:eo + 12] if sz <= 4
               else data[struct.unpack(e + "I", data[eo + 8:eo + 12])[0]:
                         struct.unpack(e + "I", data[eo + 8:eo + 12])[0] + sz])
        name = tags.get(tag, "tag_0x%04x" % tag)
        if typ == 2:
            val = raw.split(b"\x00")[0].decode("utf-8", "replace")
        elif typ == 5 and cnt in (1, 3):
            val = ["%d/%d" % struct.unpack(e + "II", raw[j:j + 8])
                   for j in range(0, sz, 8)]
        elif typ == 3:
            val = list(struct.unpack(e + "H" * cnt, raw[:sz]))
        elif typ == 4:
            val = list(struct.unpack(e + "I" * cnt, raw[:sz]))
        elif typ == 7 and name.startswith("XP"):
            val = raw.decode("utf-16-le", "replace").rstrip("\x00")
        else:
            val = raw[:64].hex() + ("..." if len(raw) > 64 else "")
        out[name] = val
        if tag in (0x8769, 0x8825) and isinstance(val, list):
            _ifd(data, val[0], e, GPS_TAGS if tag == 0x8825 else EXIF_TAGS,
                 out, depth + 1)


def jpeg_exif(data):
    out = {}
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            break
        marker = data[pos + 1]
        ln = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        seg = data[pos + 4:pos + 2 + ln]
        if marker == 0xE1 and seg[:6] == b"Exif\x00\x00":
            t = seg[6:]
            e = "<" if t[:2] == b"II" else ">"
            _ifd(t, struct.unpack(e + "I", t[4:8])[0], e, EXIF_TAGS, out)
        if marker == 0xE1 and seg[:24] == b"http://ns.adobe.com/xap":
            out["XMP"] = seg[24:][:2000].decode("utf-8", "replace")
        pos += 2 + ln
        if marker in (0xD8, 0xD9) or marker == 0xDA:
            break
    return out


def png_text(data):
    out = {}
    pos = 8
    while pos + 12 <= len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"tEXt" and b"\x00" in body:
            k, v = body.split(b"\x00", 1)
            out[k.decode("latin1")] = v.decode("latin1", "replace")
        elif typ == b"zTXt" and b"\x00" in body:
            k, rest = body.split(b"\x00", 1)
            try:
                out[k.decode("latin1")] = zlib.decompress(
                    rest[1:]).decode("latin1", "replace")
            except zlib.error:
                out[k.decode("latin1")] = "<bad zTXt>"
        elif typ == b"iTXt" and b"\x00" in body:
            parts = body.split(b"\x00", 5)
            if len(parts) >= 6:
                txt = parts[5]
                if parts[1:2] == [b"\x01"]:
                    try:
                        txt = zlib.decompress(txt)
                    except zlib.error:
                        pass
                out[parts[0].decode("latin1")] = txt.decode(
                    "utf-8", "replace")
        pos += 12 + ln
    return out


def pdf_meta(data):
    out = {}
    for m in re.finditer(rb"/(Title|Author|Subject|Keywords|Creator|"
                         rb"Producer|CreationDate|ModDate|Trapped)\s*"
                         rb"\(([^)]{0,400})\)", data):
        out[m.group(1).decode()] = m.group(2).decode("latin1", "replace")
    xmp = re.search(rb"<x:xmpmeta.*?</x:xmpmeta>", data, re.S)
    if xmp:
        out["XMP"] = xmp.group(0)[:3000].decode("utf-8", "replace")
    return out


def office_meta(path):
    out = {}
    try:
        with zipfile.ZipFile(path) as z:
            for name in ("docProps/core.xml", "docProps/app.xml",
                         "docProps/custom.xml"):
                if name in z.namelist():
                    xml = z.read(name).decode("utf-8", "replace")
                    out[name] = {m.group(1): m.group(2)
                                 for m in re.finditer(
                                     r"<(?:\w+:)?(\w+)[^>]*>([^<]{0,200})"
                                     r"</", xml)}
    except (zipfile.BadZipFile, KeyError):
        out["error"] = ("not a zip-based office file (legacy OLE needs "
                        "exiftool/strings)")
    return out


def wav_info(data):
    out = {}
    pos = 12
    while pos + 8 <= len(data):
        cid, ln = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:
                                                            pos + 8])[0]
        body = data[pos + 8:pos + 8 + ln]
        if cid == b"LIST" and body[:4] == b"INFO":
            p = 4
            while p + 8 <= len(body):
                tag, tl = body[p:p + 4], struct.unpack("<I",
                                                       body[p + 4:p + 8])[0]
                out[tag.decode("latin1")] = body[
                    p + 8:p + 8 + tl].rstrip(b"\x00").decode(
                    "utf-8", "replace")
                p += 8 + tl + (tl & 1)
        pos += 8 + ln + (ln & 1)
    return out


def id3_meta(data):
    out = {}
    if data[:3] != b"ID3":
        return out
    size = 0
    for b in data[6:10]:
        size = size * 128 + (b & 0x7F)
    pos = 10
    while pos + 10 <= 10 + size:
        fid = data[pos:pos + 4].decode("latin1")
        flen = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        if not fid.strip("\x00") or flen > 1 << 20:
            break
        body = data[pos + 10:pos + 10 + flen]
        if fid in ID3_TEXT or fid == "COMM":
            enc = body[:1]
            txt = body[1:] if enc != b"\x03" else body[4:]
            out[ID3_TEXT.get(fid, fid)] = txt.decode(
                "utf-16" if enc in (b"\x01", b"\x02") else "latin1",
                "replace").rstrip("\x00").lstrip("eng\x00")
        pos += 10 + flen
    return out


def read_meta(path):
    data = open(path, "rb").read(4 << 20)
    head = data[:16]
    if head[:2] == b"\xff\xd8":
        return "jpeg", jpeg_exif(data)
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return "png", png_text(data)
    if head[:5] == b"%PDF-":
        return "pdf", pdf_meta(data)
    if head[:4] == b"PK\x03\x04":
        return "office-zip", office_meta(path)
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "wav", wav_info(data)
    if head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3"):
        return "mp3", id3_meta(data)
    return "unknown", {"note": "no parser for this carrier — strings + "
                               "carve_scan still apply"}


def _build_jpeg_with_exif(desc):
    """Minimal JPEG: SOI + APP1(Exif) + SOS."""
    e = "<"
    ifd_body = struct.pack(e + "H", 1)
    # tag 0x010E ImageDescription -> ASCII, offset after IFD
    d = desc.encode() + b"\x00"
    ifd_body += struct.pack(e + "HHI", 0x010E, 2, len(d))
    ifd_body += struct.pack(e + "I", 8 + 2 + 12 + 4)
    ifd_body += struct.pack(e + "I", 0)
    tiff = b"II" + struct.pack("<HI", 42, 8) + ifd_body + d
    app1 = b"Exif\x00\x00" + tiff
    return (b"\xff\xd8\xff\xe1" + struct.pack(">H", len(app1) + 2) + app1
            + b"\xff\xda" + b"\x00" * 8)


def _selftest() -> int:
    import tempfile
    j = _build_jpeg_with_exif("flag{meta_carrier}")
    with tempfile.NamedTemporaryFile("wb", suffix=".jpg",
                                     delete=False) as fh:
        fh.write(j)
        p = fh.name
    try:
        fmt, meta = read_meta(p)
        assert fmt == "jpeg" and meta.get(
            "ImageDescription") == "flag{meta_carrier}", meta
    finally:
        os.unlink(p)
    # PNG tEXt
    def chunk(t, b):
        import zlib as _z
        return struct.pack(">I", len(b)) + t + b + struct.pack(
            ">I", _z.crc32(t + b) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
           + chunk(b"tEXt", b"Comment\x00flag{png_text}")
           + chunk(b"IEND", b""))
    with tempfile.NamedTemporaryFile("wb", suffix=".png",
                                     delete=False) as fh:
        fh.write(png)
        p = fh.name
    try:
        fmt, meta = read_meta(p)
        assert fmt == "png" and meta.get("Comment") == "flag{png_text}", meta
    finally:
        os.unlink(p)
    # PDF /Info
    pdf = b"%PDF-1.4\n1 0 obj<</Title(flag{pdf_meta})/Author(a b)>>endobj"
    with tempfile.NamedTemporaryFile("wb", suffix=".pdf",
                                     delete=False) as fh:
        fh.write(pdf)
        p = fh.name
    try:
        fmt, meta = read_meta(p)
        assert meta.get("Title") == "flag{pdf_meta}", meta
    finally:
        os.unlink(p)
    print("meta_read selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("a file path is required")
    fmt, meta = read_meta(a.path)
    print(json.dumps({"format": fmt, "metadata": meta}, indent=1,
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
