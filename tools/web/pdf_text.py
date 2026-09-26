#!/usr/bin/env python3
"""Extract text from a PDF a target returned.

Three extractors, tried in order; the JSON always names the one that actually
produced the text and records why the earlier ones were skipped or failed:

  mutool   `mutool draw -F txt` - fastest, best layout, needs the binary
  pypdf    pure Python, needs the pypdf package
  stdlib   zlib inflate of every stream plus a Tj/TJ operand scrape; no
           dependency at all, so this path always exists

The source may be a local path or a URL fetched through ``httpkit``, because a
PDF is often just the output channel of a read primitive and should not have to
be saved by hand first. Every outcome is a dict: a missing extractor, a corrupt
file and an empty page all come back as recorded results, never exceptions.

CLI:
    python3 tools/web/pdf_text.py /tmp/report.pdf
    python3 tools/web/pdf_text.py https://host/render?file=/etc/passwd --find-flag
    python3 tools/web/pdf_text.py --selftest
"""
import argparse
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zlib

try:                                     # importable as tools.web.pdf_text ...
    from . import httpkit
except ImportError:                      # ... and runnable as a script
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import httpkit

ORDER = ("mutool", "pypdf", "stdlib")
FLAG_RE = r"[A-Za-z0-9_\-]{2,24}\{[^}\r\n]{1,200}\}"
_TEXT_OPS = {b"Tj", b"TJ", b"'", b'"'}
_BREAK_OPS = {b"Td", b"TD", b"T*", b"ET"}


# --------------------------------------------------------------------------- #
# loading
# --------------------------------------------------------------------------- #
def load_pdf(source, headers=None, timeout=15, max_bytes=16 << 20):
    """Return {'ok', 'kind', 'data'|'error', ...} for a path or an http(s) URL."""
    if re.match(r"(?i)^https?://", source):
        resp = httpkit.request(source, headers=headers, timeout=timeout,
                               max_bytes=max_bytes)
        data = resp.get("body_bytes") or b""
        return {
            "ok": bool(resp.get("ok")) and bool(data),
            "kind": "url",
            "source": source,
            "status": resp.get("status"),
            "content_type": resp.get("headers", {}).get("Content-Type"),
            "data": data,
            "error": resp.get("error") or (None if data else "empty response body"),
        }
    try:
        with open(source, "rb") as handle:
            data = handle.read(max_bytes)
    except OSError as exc:
        return {"ok": False, "kind": "path", "source": source, "data": b"",
                "error": "%s: %s" % (type(exc).__name__, exc)}
    return {"ok": bool(data), "kind": "path", "source": source, "data": data,
            "error": None if data else "file is empty"}


def looks_like_pdf(data):
    return data[:1024].find(b"%PDF-") >= 0


# --------------------------------------------------------------------------- #
# extractor 1: mutool
# --------------------------------------------------------------------------- #
def extract_mutool(data, timeout=30):
    exe = shutil.which("mutool")
    if not exe:
        return {"extractor": "mutool", "ok": False, "reason": "mutool not on PATH",
                "text": "", "pages": None}
    tmp = tempfile.NamedTemporaryFile(prefix="pdftext-", suffix=".pdf", delete=False)
    try:
        tmp.write(data)
        tmp.close()
        try:
            proc = subprocess.run([exe, "draw", "-F", "txt", "-o", "-", tmp.name],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  timeout=timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            return {"extractor": "mutool", "ok": False, "text": "", "pages": None,
                    "reason": "%s: %s" % (type(exc).__name__, exc)}
        text = proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        return {"extractor": "mutool", "ok": bool(text.strip()),
                "text": text, "pages": None, "exe": exe,
                "returncode": proc.returncode,
                "reason": None if text.strip() else (stderr or "no text produced"),
                "stderr": stderr[:400] or None}
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


# --------------------------------------------------------------------------- #
# extractor 2: pypdf
# --------------------------------------------------------------------------- #
def extract_pypdf(data):
    try:
        import pypdf                                    # optional dependency
    except ImportError:
        try:
            import PyPDF2 as pypdf                      # older name, same API
        except ImportError:
            return {"extractor": "pypdf", "ok": False, "text": "", "pages": None,
                    "reason": "neither pypdf nor PyPDF2 is installed"}
    # pypdf logs 'invalid pdf header' / 'EOF marker not found' straight to
    # stderr, which corrupts a JSON-consuming pipeline. The reason belongs in the
    # attempt record, not in the operator's terminal.
    logging.getLogger("pypdf").setLevel(logging.CRITICAL)
    logging.getLogger("PyPDF2").setLevel(logging.CRITICAL)
    try:
        reader = pypdf.PdfReader(io.BytesIO(data), strict=False)
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:                            # one bad page, keep going
                pages.append("")
        text = "\n".join(pages)
    except Exception as exc:
        return {"extractor": "pypdf", "ok": False, "text": "", "pages": None,
                "reason": "%s: %s" % (type(exc).__name__, exc)}
    return {"extractor": "pypdf", "ok": bool(text.strip()), "text": text,
            "pages": len(pages), "version": getattr(pypdf, "__version__", None),
            "reason": None if text.strip() else "no text produced"}


# --------------------------------------------------------------------------- #
# extractor 3: stdlib zlib + content-stream scrape
# --------------------------------------------------------------------------- #
def iter_streams(data):
    """Yield (offset, decoded_bytes, how) for every stream ... endstream."""
    pos = 0
    while True:
        start = data.find(b"stream", pos)
        if start < 0:
            return
        cursor = start + 6
        if data[cursor:cursor + 2] == b"\r\n":
            cursor += 2
        elif data[cursor:cursor + 1] in (b"\n", b"\r"):
            cursor += 1
        end = data.find(b"endstream", cursor)
        if end < 0:
            return
        raw = data[cursor:end]
        pos = end + 9
        decoded, how = _inflate(raw)
        yield start, decoded, how


def _inflate(raw):
    for candidate in (raw, raw.rstrip(b"\r\n"), raw.lstrip(b"\r\n").rstrip(b"\r\n")):
        try:
            return zlib.decompress(candidate), "flate"
        except zlib.error:
            pass
        try:                                   # truncated / raw deflate
            obj = zlib.decompressobj(-15)
            out = obj.decompress(candidate)
            if out:
                return out, "raw-deflate"
        except zlib.error:
            pass
        try:
            obj = zlib.decompressobj()
            out = obj.decompress(candidate)
            if out:
                return out, "flate-partial"
        except zlib.error:
            pass
    return raw, "stored"


def scrape_tokens(blob):
    """Collect Tj/TJ/'/\" operands from a decoded content stream, in order.

    Returns a list of byte chunks; the literal b"\n" marks a line break emitted
    by a positioning or text-end operator. The operands are returned RAW because
    a Type0/Identity-H font makes them 2-byte glyph ids, not characters, and the
    ToUnicode CMap is the only thing that can turn them back into text.
    """
    out = []
    pending = []
    nums = []
    last_tm_y = None
    i, n = 0, len(blob)

    def flush():
        if pending:
            out.append(b"".join(pending))
            del pending[:]

    while i < n:
        ch = blob[i:i + 1]
        if ch == b"(":
            literal, i = _read_literal(blob, i + 1)
            pending.append(literal)
            continue
        if ch == b"<" and blob[i + 1:i + 2] != b"<":
            close = blob.find(b">", i + 1)
            if close < 0:
                break
            hexed = re.sub(rb"[^0-9A-Fa-f]", b"", blob[i + 1:close])
            if len(hexed) % 2:
                hexed += b"0"
            try:
                pending.append(bytes.fromhex(hexed.decode("ascii")))
            except ValueError:
                pass
            i = close + 1
            continue
        if ch == b"%":                                   # comment to end of line
            nl = blob.find(b"\n", i)
            i = n if nl < 0 else nl + 1
            continue
        number = re.match(rb"[-+]?(?:\d+\.?\d*|\.\d+)", blob[i:i + 24])
        if number:
            try:
                nums.append(float(number.group(0)))
            except ValueError:
                pass
            i += len(number.group(0))
            continue
        match = re.match(rb"[A-Za-z*'\"]+", blob[i:i + 8])
        if match:
            op = match.group(0)
            if op in _TEXT_OPS:
                flush()
            elif op in (b"T*", b"ET"):
                flush()
                out.append(b"\n")
            elif op in (b"Td", b"TD"):
                # A break only when the line actually moves vertically. A PDF
                # that positions every glyph run with its own Td - which every
                # renderer-generated PDF does - otherwise comes back one
                # character per line.
                flush()
                if len(nums) >= 2 and abs(nums[-1]) > 1e-9:
                    out.append(b"\n")
            elif op == b"Tm":
                flush()
                if len(nums) >= 6:
                    if last_tm_y is not None and abs(nums[-1] - last_tm_y) > 1e-9:
                        out.append(b"\n")
                    last_tm_y = nums[-1]
            else:
                del pending[:]
            nums = []
            i += len(op)
            continue
        i += 1
    if pending:
        out.append(b"".join(pending))
    return out


def scrape_content_stream(blob):
    """scrape_tokens, decoded as latin-1. Correct only for simple 1-byte fonts."""
    text = b"".join(scrape_tokens(blob)).decode("latin-1")
    return re.sub(r"\n{3,}", "\n\n", text)


# --- ToUnicode CMap ------------------------------------------------------- #
_HEX = rb"<([0-9A-Fa-f\s]+)>"


def _hexval(raw):
    cleaned = re.sub(rb"\s", b"", raw)
    if len(cleaned) % 2:
        cleaned += b"0"
    return cleaned.decode("ascii"), int(cleaned, 16) if cleaned else 0


def _utf16_text(raw):
    cleaned, _ = _hexval(raw)
    try:
        data = bytes.fromhex(cleaned)
    except ValueError:
        return ""
    if len(data) % 2:
        data += b"\x00"
    return data.decode("utf-16-be", "replace")


def parse_tounicode(data):
    """Merge every ToUnicode CMap in the file into {code: str}.

    One merged map, not one per font: the scraper does not track which font is
    current, so a document with two conflicting subset fonts can mis-map. That
    is a stated limit of the no-dependency path, reported as
    `cmap_sources` in the JSON - prefer mutool or pypdf when it matters.
    """
    cmap, sources = {}, 0
    for _, blob, _how in iter_streams(data):
        if b"begincmap" not in blob:
            continue
        sources += 1
        for block in re.findall(rb"beginbfchar(.*?)endbfchar", blob, re.S):
            for src, dst in re.findall(_HEX + rb"\s*" + _HEX, block):
                _, code = _hexval(src)
                cmap[code] = _utf16_text(dst)
        for block in re.findall(rb"beginbfrange(.*?)endbfrange", blob, re.S):
            for lo, hi, dst in re.findall(_HEX + rb"\s*" + _HEX + rb"\s*" + _HEX, block):
                _, low = _hexval(lo)
                _, high = _hexval(hi)
                start = _utf16_text(dst)
                if not start or high < low or high - low > 65535:
                    continue
                base = ord(start[-1])
                prefix = start[:-1]
                for offset in range(high - low + 1):
                    cmap[low + offset] = prefix + chr(base + offset)
    return cmap, sources


def decode_tokens(chunks, cmap=None, code_bytes=2):
    """Join scraped chunks; map through a ToUnicode CMap when one is supplied."""
    pieces = []
    for chunk in chunks:
        if chunk == b"\n":
            pieces.append("\n")
            continue
        if cmap:
            step = code_bytes
            if len(chunk) % step:
                chunk = chunk + b"\x00" * (step - len(chunk) % step)
            out = []
            for index in range(0, len(chunk), step):
                code = int.from_bytes(chunk[index:index + step], "big")
                out.append(cmap.get(code, ""))
            pieces.append("".join(out))
        else:
            pieces.append(chunk.decode("latin-1"))
    return re.sub(r"\n{3,}", "\n\n", "".join(pieces))


def printable_ratio(text):
    if not text:
        return 0.0
    good = sum(1 for ch in text if ch.isprintable() or ch in "\n\t ")
    return round(good / len(text), 4)


_ESCAPES = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f",
            b"(": b"(", b")": b")", b"\\": b"\\"}


def _read_literal(blob, i):
    """Read a PDF literal string body starting after '('. Returns (bytes, next_i)."""
    out = bytearray()
    depth = 1
    n = len(blob)
    while i < n:
        ch = blob[i:i + 1]
        if ch == b"\\":
            nxt = blob[i + 1:i + 2]
            if nxt in _ESCAPES:
                out += _ESCAPES[nxt]
                i += 2
                continue
            octal = re.match(rb"[0-7]{1,3}", blob[i + 1:i + 4])
            if octal:
                out.append(int(octal.group(0), 8) & 0xFF)
                i += 1 + len(octal.group(0))
                continue
            if nxt in (b"\n", b"\r"):                    # line continuation
                i += 2
                continue
            out += nxt
            i += 2
            continue
        if ch == b"(":
            depth += 1
            out += ch
            i += 1
            continue
        if ch == b")":
            depth -= 1
            if depth == 0:
                return bytes(out), i + 1
            out += ch
            i += 1
            continue
        out += ch
        i += 1
    return bytes(out), i


def extract_stdlib(data, min_printable=0.80):
    """No-dependency extraction: inflate every stream, scrape Tj/TJ, then, when
    the raw scrape is not printable text, re-decode it through the ToUnicode
    CMap (that is what a Type0/Identity-H subset font needs)."""
    token_sets, streams, inflated = [], 0, 0
    for _, blob, how in iter_streams(data):
        streams += 1
        if how != "stored":
            inflated += 1
        if not (b"Tj" in blob or b"TJ" in blob or b"BT" in blob):
            continue
        tokens = scrape_tokens(blob)
        if tokens:
            token_sets.append(tokens)

    raw = "\n".join(decode_tokens(t).strip() for t in token_sets).strip()
    ratio = printable_ratio(raw)
    text, how_decoded = raw, "latin-1"
    cmap, cmap_sources = ({}, 0)
    if ratio < min_printable or not raw:
        cmap, cmap_sources = parse_tounicode(data)
        if cmap:
            mapped = "\n".join(decode_tokens(t, cmap).strip()
                                for t in token_sets).strip()
            if printable_ratio(mapped) > ratio and mapped:
                text, how_decoded, ratio = mapped, "tounicode-cmap", printable_ratio(mapped)
    ok = bool(text.strip()) and ratio >= min_printable
    reason = None
    if not text.strip():
        reason = "no Tj/TJ operands in %d stream(s)" % streams
    elif not ok:
        reason = ("scraped text is %.0f%% printable, below the %.0f%% floor: the "
                  "font encoding is not recoverable without the ToUnicode CMap"
                  % (ratio * 100, min_printable * 100))
    return {"extractor": "stdlib", "ok": ok, "text": text, "pages": None,
            "streams_seen": streams, "streams_inflated": inflated,
            "decoded_via": how_decoded, "printable_ratio": ratio,
            "cmap_entries": len(cmap), "cmap_sources": cmap_sources,
            "reason": reason}


EXTRACTORS = {"mutool": extract_mutool, "pypdf": extract_pypdf,
              "stdlib": extract_stdlib}


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def extract(source, prefer=None, headers=None, timeout=15, grep=None,
            find_flag=False, max_bytes=16 << 20, all_extractors=False):
    """Extract text from a PDF path or URL. Returns a JSON-ready dict."""
    loaded = load_pdf(source, headers=headers, timeout=timeout, max_bytes=max_bytes)
    result = {
        "mode": "pdf-text",
        "source": source,
        "source_kind": loaded["kind"],
        "bytes": len(loaded.get("data") or b""),
        "looks_like_pdf": looks_like_pdf(loaded.get("data") or b""),
        "extractor": None,
        "attempts": [],
        "text": "",
        "chars": 0,
        "pages": None,
    }
    if loaded["kind"] == "url":
        result["http_status"] = loaded.get("status")
        result["content_type"] = loaded.get("content_type")
    if not loaded["ok"]:
        result["error"] = loaded.get("error") or "could not read source"
        return result
    data = loaded["data"]
    if not result["looks_like_pdf"]:
        result["warning"] = "no %PDF- header in the first 1024 bytes; extracting anyway"

    order = list(ORDER)
    if prefer:
        order = [prefer] + [name for name in order if name != prefer]
    for name in order:
        attempt = EXTRACTORS[name](data)
        text = attempt.pop("text", "")
        result["attempts"].append(attempt)
        if attempt.get("ok"):
            result["extractor"] = name
            result["text"] = text
            result["chars"] = len(text)
            result["pages"] = attempt.get("pages")
            if not all_extractors:
                break
    if result["extractor"] is None:
        result["error"] = "every extractor returned empty text"

    text = result["text"]
    result["lines"] = len([line for line in text.splitlines() if line.strip()])
    if grep:
        try:
            pattern = re.compile(grep)
        except re.error as exc:
            result["grep"] = {"pattern": grep, "error": str(exc)}
        else:
            hits = [m.group(0) for m in pattern.finditer(text)]
            result["grep"] = {"pattern": grep, "count": len(hits), "matches": hits[:50]}
    if find_flag:
        hits = sorted(set(re.findall(FLAG_RE, text)))
        result["flag_candidates"] = {
            "pattern": FLAG_RE, "count": len(hits), "values": hits[:20],
            "note": "candidate only: a flag counts after tools/hooks.py pre-flag",
        }
    return result


# --------------------------------------------------------------------------- #
# local PDF generation (validation fixture, and a handy one-liner)
# --------------------------------------------------------------------------- #
def _pdf_escape(raw):
    return (raw.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)"))


def build_pdf(lines, compress=True):
    """Build a minimal one-page PDF containing `lines`. Deterministic bytes."""
    content = bytearray(b"BT\n/F1 12 Tf\n14 TL\n72 720 Td\n")
    for line in lines:
        raw = line.encode("latin-1", "replace") if isinstance(line, str) else line
        content += b"(" + _pdf_escape(raw) + b") Tj\nT*\n"
    content += b"ET\n"
    stream = zlib.compress(bytes(content), 9) if compress else bytes(content)
    filt = b" /Filter /FlateDecode" if compress else b""
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + filt + b" >>\nstream\n"
        + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += str(index).encode() + b" 0 obj\n" + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 " + str(len(objs) + 1).encode() + b"\n"
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += ("%010d 00000 n \n" % off).encode()
    out += (b"trailer\n<< /Size " + str(len(objs) + 1).encode()
            + b" /Root 1 0 R >>\nstartxref\n" + str(xref).encode() + b"\n%%EOF\n")
    return bytes(out)


def selftest():
    """Build PDFs locally and run all three extractors against them."""
    marker = "CTFV2{pdf_text_selftest}"
    lines = [marker, "root:x:0:0:root:/root:/bin/sh", "second line here"]
    cases, failures = [], 0
    tmpdir = tempfile.mkdtemp(prefix="pdf_text-selftest-")
    for compress in (True, False):
        path = os.path.join(tmpdir, "flate.pdf" if compress else "stored.pdf")
        with open(path, "wb") as handle:
            handle.write(build_pdf(lines, compress=compress))
        for name in ORDER:
            res = extract(path, prefer=name)
            got = res["extractor"] == name and marker in res["text"]
            skipped = any(a["extractor"] == name and not a.get("ok")
                          and "not on PATH" in (a.get("reason") or "")
                          for a in res["attempts"])
            cases.append({"pdf": os.path.basename(path), "compressed": compress,
                          "extractor": name, "marker_found": marker in res["text"],
                          "extractor_used": res["extractor"],
                          "chars": res["chars"],
                          "pass": bool(got) or skipped,
                          "note": "extractor unavailable, fell through" if skipped and not got else None})
            if not (got or skipped):
                failures += 1
    return {"mode": "pdf-text-selftest", "tmpdir": tmpdir, "marker": marker,
            "cases": cases, "total": len(cases), "failures": failures,
            "verdict": "PASS" if failures == 0 else "FAIL"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF (local path or URL) with mutool, "
                    "pypdf or a stdlib zlib+Tj/TJ fallback.")
    parser.add_argument("source", nargs="?", help="local path or http(s) URL")
    parser.add_argument("--extractor", choices=ORDER,
                        help="try this extractor first (others stay as fallback)")
    parser.add_argument("--all", action="store_true",
                        help="run every extractor and report each attempt")
    parser.add_argument("-H", "--header", action="append", default=[],
                        help="extra request header, 'Name: value' (URL sources)")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--max-bytes", type=int, default=16 << 20)
    parser.add_argument("--grep", help="regex to report matches of, in the text")
    parser.add_argument("--find-flag", action="store_true",
                        help="report flag-shaped candidates (candidates, not flags)")
    parser.add_argument("--max-chars", type=int, default=20000,
                        help="truncate the text field in the JSON (0 = no limit)")
    parser.add_argument("--text-only", action="store_true",
                        help="print the extracted text to stdout instead of JSON")
    parser.add_argument("--make-pdf", metavar="PATH",
                        help="write a minimal test PDF here and exit")
    parser.add_argument("--make-pdf-line", action="append", default=[],
                        help="a line of text for --make-pdf (repeatable)")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--compact", action="store_true", help="one-line JSON")
    args = parser.parse_args(argv)

    if args.selftest:
        out = selftest()
        httpkit.jprint(out, compact=args.compact)
        return 0 if out["verdict"] == "PASS" else 1
    if args.make_pdf:
        lines = args.make_pdf_line or ["CTFV2{generated_pdf}", "line two"]
        data = build_pdf(lines)
        with open(args.make_pdf, "wb") as handle:
            handle.write(data)
        httpkit.jprint({"mode": "pdf-text-make", "path": args.make_pdf,
                        "bytes": len(data), "lines": lines}, compact=args.compact)
        return 0
    if not args.source:
        parser.error("provide a source path or URL, or --selftest / --make-pdf")

    out = extract(args.source, prefer=args.extractor,
                  headers=httpkit.parse_headers(args.header),
                  timeout=args.timeout, grep=args.grep, find_flag=args.find_flag,
                  max_bytes=args.max_bytes, all_extractors=args.all)
    if args.text_only:
        sys.stdout.write(out["text"])
        return 0 if out["extractor"] else 1
    if args.max_chars and len(out["text"]) > args.max_chars:
        out["truncated"] = {"shown": args.max_chars, "total": len(out["text"])}
        out["text"] = out["text"][:args.max_chars]
    httpkit.jprint(out, compact=args.compact)
    return 0 if out["extractor"] else 1


if __name__ == "__main__":
    sys.exit(main())
