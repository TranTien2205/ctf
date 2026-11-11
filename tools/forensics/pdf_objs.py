#!/usr/bin/env python3
"""pdf_objs.py -- list PDF objects, decode streams, surface payloads.

pdf_text answers "what does the page say". A puzzle/maldoc PDF hides
in the objects instead: /JS and /JavaScript actions, /OpenAction,
/EmbeddedFile streams, /Launch, /URI, unusual /Filter chains. This
walks `N G obj ... endobj` regions, inflates FlateDecode streams,
and reports every payload-bearing key with a preview.

  python3 tools/forensics/pdf_objs.py doc.pdf
  python3 tools/forensics/pdf_objs.py doc.pdf --extract 12
  python3 tools/forensics/pdf_objs.py --selftest

Extraction writes the decoded stream to stdout (binary-safe) so it
can be piped to file. No xref reliance: objects are found by their
`N G obj` delimiters, which survives damaged/truncated files.
"""
import argparse
import json
import re
import sys
import zlib

OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)endobj", re.S)
STREAM = re.compile(rb"stream\r?\n(.*?)\r?\nendstream", re.S)
INTEREST = ("/JS", "/JavaScript", "/OpenAction", "/AA", "/Launch",
            "/EmbeddedFile", "/EmbeddedFiles", "/URI", "/SubmitForm",
            "/RichMedia", "/Names")


def objects(data):
    out = []
    for m in OBJ.finditer(data):
        num, gen, body = int(m.group(1)), int(m.group(2)), m.group(3)
        o = {"obj": num, "gen": gen, "offset": m.start(),
             "size": m.end() - m.start()}
        keys = sorted({k.decode() for k in
                       re.findall(rb"/([A-Za-z0-9]+)", body)})
        o["keys"] = keys
        hits = [k for k in keys if "/" + k in INTEREST]
        sm = STREAM.search(body)
        if sm:
            raw = sm.group(1)
            o["stream_len"] = len(raw)
            if "/FlateDecode" in body.decode("latin-1", "replace"):
                try:
                    dec = zlib.decompress(raw)
                    o["decoded_len"] = len(dec)
                    o["decoded_preview"] = dec[:200].decode(
                        "latin-1", "replace")
                except zlib.error:
                    o["decode_error"] = "flate failed — try " \
                                        "skipping leading bytes"
            else:
                o["decoded_preview"] = raw[:200].decode(
                    "latin-1", "replace")
        if hits:
            o["interesting_keys"] = hits
        out.append(o)
    return out


def extract(data, num):
    for m in OBJ.finditer(data):
        if int(m.group(1)) == num:
            sm = STREAM.search(m.group(3))
            if not sm:
                return m.group(3).strip()
            raw = sm.group(1)
            if b"/FlateDecode" in m.group(3):
                try:
                    return zlib.decompress(raw)
                except zlib.error:
                    return raw
            return raw
    return None


def _selftest():
    js = zlib.compress(b"app.alert('flag{pdf_obj}');")
    pdf = (b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /OpenAction 2 0 R"
           b" >>\nendobj\n"
           b"2 0 obj\n<< /S /JavaScript /JS 3 0 R >>\nendobj\n"
           b"3 0 obj\n<< /Length " + str(len(js)).encode() +
           b" /Filter /FlateDecode >>\nstream\n" + js +
           b"\nendstream\nendobj\n"
           b"4 0 obj\n<< /Type /EmbeddedFile >>\nendobj\n%%EOF")
    objs = objects(pdf)
    cat = next(o for o in objs if o["obj"] == 1)
    assert "OpenAction" in cat["interesting_keys"], cat
    st = next(o for o in objs if o["obj"] == 3)
    assert "flag{pdf_obj}" in st["decoded_preview"], st
    assert extract(pdf, 3) == b"app.alert('flag{pdf_obj}');"
    print("pdf_objs selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="PDF object inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--extract", type=int, metavar="OBJ")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("pdf path required")
    data = open(a.path, "rb").read()
    if a.extract is not None:
        blob = extract(data, a.extract)
        if blob is None:
            sys.exit(f"obj {a.extract} not found")
        sys.stdout.buffer.write(blob)
        return
    objs = objects(data)
    interesting = [o for o in objs if o.get("interesting_keys")]
    print(json.dumps({"objects": len(objs),
                      "interesting": interesting,
                      "all": objs}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
