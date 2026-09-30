#!/usr/bin/env python3
"""Recover a front-end's real sources from its bundle or source map, and inventory every endpoint.

A missed endpoint is the most common reason a web challenge stalls, and when the
app ships only a bundle the endpoint list, the client route table and sometimes a
key are all already there, just minified. Re-deriving that by hand is a long grep
session under contest time: find the sourceMappingURL comment, guess the .map
sibling, decode an inline data URI, un-base64 sourcesContent one entry at a time,
then grep the result for paths and remember which file each hit came from. This
does that pass once. It records which method found the map, writes sourcesContent
back to disk while refusing any source path that would escape the output
directory (a source map is attacker-controlled data, and the sources array is a
list of filenames somebody else chose), and prints one de-duplicated endpoint
inventory with the file, line and column of every hit.

Every empty category is reported with its case count, because "0 of 41 quoted
literals looked like a path" is a finding and an empty section is not. Those
counts are counts of what was measured, never of what was listed: --max-hits is
a display cap and is kept out of every ratio. Nothing here claims a secret
candidate is valid: entropy and shape are reported, the verdict stays
"candidate", and validating it is a probe, not a parse.

The inputs are independent: a dead --url does not discard a --file bundle beside
it. An inventory built from inputs that did not all land is not offered as
complete -- a read that failed, was cut at --max-bytes, or was dropped by
--max-scripts is counted, named in the negatives, and marks the verdict PARTIAL,
because a short inventory that does not say so reads as a clean small one.

    python3 tools/web/bundle_miner.py --selftest
    python3 tools/web/bundle_miner.py --url http://host/ --out /tmp/src
    python3 tools/web/bundle_miner.py --file main.1a2b.js --out /tmp/src
    python3 tools/web/bundle_miner.py --map main.js.map --out /tmp/src --compact
"""
import argparse
import base64
import bisect
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import httpkit  # noqa: E402

# Both comment forms are in the wild: '//#' is the current spec, '//@' is what
# older webpack/uglify emitted and what a dated challenge image still ships.
SOURCEMAP_COMMENT = re.compile(
    r"(?://[#@]|/\*[#@])\s*sourceMappingURL\s*=\s*([^\s'\"*]+)")

# One JS string literal. The two alternatives are mutually exclusive (one starts
# with a backslash, the other cannot be one), so this cannot backtrack badly on a
# multi-megabyte single-line bundle. It will occasionally pick up the inside of a
# regex literal; that is noise in the inventory, never a wrong write to disk.
STRING_RX = re.compile(r"(['\"`])((?:\\.|(?!\1)[^\\])*)\1", re.S)
STRING_AT = re.compile(r"\s*(['\"`])((?:\\.|(?!\1)[^\\])*)\1", re.S)

# A quoted absolute path. Kept deliberately tight: the chars a URL path, a
# template placeholder or an Express-style :param can hold, and nothing else.
ABS_PATH_RX = re.compile(r"^/(?:[A-Za-z0-9._~%!$&'()*+,;=:@\-]|/|\{[^{}]*\}|"
                         r"\$\{[^{}]*\}|\[[^\[\]]*\])*$")
# A relative path only counts when it names an API surface itself; accepting any
# 'a/b' would fill the inventory with MIME types and CSS class names.
REL_PATH_RX = re.compile(r"^(?:\./|\.\./)*(?:api|apis|graphql|gql|rest|auth|"
                         r"oauth|admin|internal|v[0-9]{1,2})"
                         r"(?:/[A-Za-z0-9._~%$:{}\[\]\-]+)*/?$", re.I)
FULL_URL_RX = re.compile(r"^(https?)://([^/\s]+)(/[^\s]*)?$", re.I)
PARAMETERISED = re.compile(r"\$\{|\{[A-Za-z_]|:[A-Za-z_]|\*")

# Static assets are real paths but they are not attack surface; they are the bulk
# of what a naive path grep returns, so they are dropped unless asked for.
ASSET_SUFFIXES = (".js", ".mjs", ".cjs", ".css", ".map", ".png", ".jpg", ".jpeg",
                  ".gif", ".svg", ".ico", ".webp", ".avif", ".bmp", ".woff",
                  ".woff2", ".ttf", ".otf", ".eot", ".mp4", ".webm", ".mp3",
                  ".wav", ".pdf", ".txt", ".md", ".wasm")

HTTP_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
METHOD_NEARBY = re.compile(r"\bmethod\s*:\s*['\"`]?([A-Za-z]{3,7})", re.I)
# Minifiers rewrite true/false to !0/!1, so a bundle's feature flags are usually
# invisible to a grep for 'true'.
BOOL_KEY_RX = re.compile(r"""['"]?([A-Za-z_$][\w$]{2,60})['"]?\s*:\s*"""
                         r"""(!0|!1|true|false)(?![\w$])""")
FLAGGY_NAME = re.compile(r"(?i)(?:^|_|\b)(?:enable[ds]?|disabled?|is|has|allow|"
                         r"show|hide|use|feature|flag|toggle|debug|dev|devtools|"
                         r"admin|beta|alpha|experimental|mock|stub|bypass|skip|"
                         r"unsafe|insecure|verbose|trace|maintenance|preview|"
                         r"sandbox|expose|internal|override|force|legacy|"
                         r"opt(?:in|out))")
ENV_RX = re.compile(r"""\b(?:process\.env|import\.meta\.env)"""
                    r"""(?:\.([A-Za-z_$][\w$]*)"""
                    r"""|\[\s*['"]([^'"]{1,120})['"]\s*\])""")
# One alternation, not nine: every scan here crosses the whole bundle, and a
# 1 MB single-line bundle makes each one cost real contest seconds.
CALL_SITE_RX = re.compile(
    r"(?<![\w$.])(fetch|axios(?:\.(?:get|post|put|patch|delete|head|request))?)"
    r"\s*\(")
CALLEE_METHOD = {"axios.get": "GET", "axios.post": "POST", "axios.put": "PUT",
                 "axios.patch": "PATCH", "axios.delete": "DELETE",
                 "axios.head": "HEAD"}
# Client route tables: the object form ({path:"/x"}) and unminified JSX
# (<Route path="/x">). Both survive a build, the second only with a map.
ROUTE_KEY_RX = re.compile(r"""\bpath\s*(?::|=)\s*['"`]([^'"`]{1,200})['"`]""")
URL_KEY_RX = re.compile(r"""\b(url|baseURL|baseUrl|endpoint|uri|href|action)\s*:"""
                        r"""\s*['"`]([^'"`]{1,300})['"`]""")

# Driven by the keyword, not by a variable-length prefix. Written as one regex
# with '[\w$.-]{0,40}' in front of the keyword it cost 1.9s of a 3.7s run on a
# 1.2 MB bundle, because that prefix makes the engine retry at every offset; a
# literal alternation plus a local walk does the same job in a tenth of that.
SECRET_WORD_RX = re.compile(
    r"(?i)api[_\-]?key|apikey|secret|token|password|passwd|pwd|credential|"
    r"private[_\-]?key|client[_\-]?secret|auth[_\-]?key|access[_\-]?key|"
    r"signing[_\-]?key|bearer")
SECRET_ASSIGN_TAIL = re.compile(r"""['"]?\s*[:=]\s*['"]([^'"\\]{4,512})['"]""")
NAME_CHAR = re.compile(r"[\w$.\-]")
SECRET_NAME_SPAN = 40
# A JWT header is base64url of '{"' which is always 'eyJ'; the shape is therefore
# checkable, and the header is decodable, without asserting the token is valid.
JWT_RX = re.compile(r"\beyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{0,512}")
# Published provider prefixes. A match is a SHAPE match and nothing more.
CLOUD_SHAPES = (
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA|ABIA|ACCA|AGPA|AIDA|AIPA|"
                                     r"ANPA|ANVA|APKA|AROA|A3T[A-Z0-9])[A-Z0-9]{16}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}")),
    ("slack-token", re.compile(r"\bxox[abposr]-[0-9A-Za-z\-]{10,}")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("stripe-secret-key", re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{10,}")),
    ("pem-private-key", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("firebase-db-url", re.compile(r"\bhttps://[a-z0-9\-]{3,}\.firebaseio\.com")),
)
# Same reason as CALL_SITE_RX: one scan for all seven shapes. Every sub-pattern
# above is written with non-capturing groups only, so wrapping each in a named
# group is safe and match.lastgroup names the shape that fired.
CLOUD_RX = re.compile("|".join("(?P<%s>%s)" % (name.replace("-", "_"),
                                              pattern.pattern)
                               for name, pattern in CLOUD_SHAPES))
CLOUD_NAME = {name.replace("-", "_"): name for name, _ in CLOUD_SHAPES}
HIGH_ENTROPY_CHARSET = re.compile(r"^[A-Za-z0-9+/=_\-]+$")

REJECT_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
DRIVE_LETTER = re.compile(r"^[A-Za-z]:[\\/]")
URI_SCHEME = re.compile(r"^([A-Za-z][A-Za-z0-9+.\-]*):")
# Bundlers name real project files with a made-up scheme (webpack:///./src/App.js,
# vite://, ng://, turbopack://), so a scheme alone cannot be the rejection test or
# every webpack map would come back empty. These schemes are the ones that are a
# genuine locator rather than a virtual path, and they are refused whatever the
# policy: 'http://evil/x.js' as a source name is not a filename to normalise.
NETWORK_SCHEMES = frozenset((
    "http", "https", "ftp", "ftps", "sftp", "ws", "wss", "file", "data", "blob",
    "javascript", "about", "view-source", "gopher", "smb", "jar", "mailto"))


def shannon(text):
    """Bits of entropy per character. Reported, never used as a verdict."""
    if not text:
        return 0.0
    counts = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    total = float(len(text))
    return round(-sum((n / total) * math.log(n / total, 2)
                      for n in counts.values()), 3)


class LineIndex(object):
    """Offset -> (line, col). A minified bundle is one line, so the column is
    the only part of a location that actually distinguishes two hits."""

    def __init__(self, text):
        self.starts = [0]
        for match in re.finditer("\n", text):
            self.starts.append(match.end())

    def locate(self, offset):
        index = bisect.bisect_right(self.starts, offset) - 1
        return index + 1, offset - self.starts[index] + 1


def unescape_js(raw):
    """Just enough to undo the escapes that appear inside a path literal."""
    return raw.replace("\\/", "/").replace("\\\\", "\\")


# --------------------------------------------------------------------------- #
# source-map location: four methods, and which one fired is part of the report
# --------------------------------------------------------------------------- #
def decode_data_uri(uri):
    """-> (text, error). Handles the base64 and the percent-encoded form."""
    if not uri.startswith("data:"):
        return None, "not a data uri"
    head, _, payload = uri.partition(",")
    if not _:
        return None, "data uri has no comma"
    if ";base64" in head.lower():
        try:
            pad = "=" * (-len(payload) % 4)
            return base64.b64decode(payload + pad).decode("utf-8", "replace"), None
        except Exception as exc:                      # malformed attacker data
            return None, "%s: %s" % (type(exc).__name__, exc)
    return urllib.parse.unquote(payload), None


def parse_map(text):
    """-> (map_dict, error). A 200 of HTML for a .map request is a catch-all,
    not a map; that trap is why this refuses anything without a sources array."""
    try:
        data = json.loads(text)
    except ValueError as exc:
        return None, "not JSON: %s" % exc
    if not isinstance(data, dict):
        return None, "JSON is a %s, not an object" % type(data).__name__
    if not isinstance(data.get("sources"), list):
        return None, "no sources array (version=%r)" % data.get("version")
    return data, None


def map_candidates(unit_name):
    """Sibling names to try when no comment names a map."""
    out = [unit_name + ".map"]
    base, ext = os.path.splitext(unit_name)
    if ext and ext != ".map":
        out.append(base + ".map")
    return out


def fetch_text(location, timeout, headers, max_bytes):
    """-> (text, note, truncated). Local path or URL; never raises on transport
    failure.

    One byte MORE than max_bytes is always requested, because that extra byte is
    the only way to tell "the input ended" from "the cap ended it". Reading
    exactly max_bytes and reporting the bytes read is indistinguishable from a
    genuinely short file, and a bundle cut in half is a short endpoint inventory
    with nothing in the report saying so.
    """
    if re.match(r"^https?://", location, re.I):
        resp = httpkit.request(location, "GET", headers, None, timeout=timeout,
                               max_bytes=max_bytes + 1)
        if not resp["ok"]:
            return None, "transport failure: %s" % resp.get("error"), False
        if resp["status"] != 200:
            return None, "HTTP %s" % resp["status"], False
        raw = resp["body_bytes"]
        if len(raw) > max_bytes:
            return (raw[:max_bytes].decode("utf-8", "replace"),
                    "HTTP %s, TRUNCATED at --max-bytes %d (the response is "
                    "larger; this inventory is short)" % (resp["status"], max_bytes),
                    True)
        return (resp["body"], "HTTP %s, %d bytes" % (resp["status"], len(raw)),
                False)
    try:
        with open(location, "rb") as handle:
            raw = handle.read(max_bytes + 1)
    except OSError as exc:
        return None, "%s: %s" % (type(exc).__name__, exc), False
    if len(raw) > max_bytes:
        return (raw[:max_bytes].decode("utf-8", "replace"),
                "TRUNCATED at --max-bytes %d from disk (the file is larger; this "
                "inventory is short)" % max_bytes, True)
    return raw.decode("utf-8", "replace"), "%d bytes from disk" % len(raw), False


def locate_map(unit, timeout, headers, max_bytes, try_sibling=True):
    """Find this bundle's map. -> dict with method, and every attempt recorded."""
    attempts = []
    comment = None
    for match in SOURCEMAP_COMMENT.finditer(unit["text"]):
        comment = match.group(1)                      # last wins, as a loader would
    if comment:
        if comment.startswith("data:"):
            text, err = decode_data_uri(comment)
            attempts.append({"method": "inline-data-uri",
                             "reference": comment[:60] + "...", "note": err or "decoded"})
            if text:
                data, err2 = parse_map(text)
                if data:
                    return {"found": True, "method": "inline-data-uri",
                            "reference": "data:", "map": data, "attempts": attempts}
                attempts[-1]["note"] = err2
        else:
            target = resolve_ref(unit["name"], comment)
            text, note, trunc = fetch_text(target, timeout, headers, max_bytes)
            attempts.append({"method": "sourceMappingURL-comment",
                             "reference": target, "note": note,
                             "truncated": trunc})
            if text:
                data, err = parse_map(text)
                if data:
                    return {"found": True, "method": "sourceMappingURL-comment",
                            "reference": target, "map": data, "attempts": attempts}
                attempts[-1]["note"] = err
    if try_sibling:
        for candidate in map_candidates(unit["name"]):
            target = resolve_ref(unit["name"], os.path.basename(candidate)) \
                if "://" in unit["name"] else candidate
            text, note, trunc = fetch_text(target, timeout, headers, max_bytes)
            attempts.append({"method": "sibling-guess", "reference": target,
                             "note": note, "truncated": trunc})
            if text:
                data, err = parse_map(text)
                if data:
                    return {"found": True, "method": "sibling-guess",
                            "reference": target, "map": data, "attempts": attempts}
                attempts[-1]["note"] = err
    return {"found": False, "method": None, "map": None,
            "had_comment": bool(comment), "attempts": attempts}


def resolve_ref(unit_name, ref):
    """Resolve a map reference against the bundle it came from."""
    if re.match(r"^https?://", ref, re.I):
        return ref
    if "://" in unit_name:
        return urllib.parse.urljoin(unit_name, ref)
    return os.path.normpath(os.path.join(os.path.dirname(unit_name) or ".", ref))


# --------------------------------------------------------------------------- #
# writing sourcesContent back: the only place this tool touches the filesystem
# --------------------------------------------------------------------------- #
def safe_relpath(source, out_dir, scheme_policy):
    """-> (abs_target, relpath, note) or (None, None, reason).

    The containment check is the real boundary and runs on every path whatever
    the policy: a rejected path is one whose resolved target is not inside
    out_dir. The named forms below are the ways that happens in practice.
    """
    if not isinstance(source, str) or not source.strip():
        return None, None, "empty-source-name"
    if REJECT_CONTROL.search(source):
        return None, None, "control-characters-in-path"
    candidate = source.replace("\\", "/")
    note = None
    # Checked before the scheme test on purpose: 'C:/x' parses as scheme 'C'.
    if DRIVE_LETTER.match(candidate):
        return None, None, "windows-drive-letter"
    scheme = URI_SCHEME.match(candidate)
    if scheme:
        name = scheme.group(1).lower()
        if scheme_policy == "reject" or name in NETWORK_SCHEMES:
            return None, None, "url-scheme:%s" % name
        # Left over: a bundler's virtual scheme (webpack://app/./src/App.js).
        # Strip the scheme, the authority and the leading slashes, then let the
        # containment check below decide - webpack:///../../etc/passwd still dies.
        parts = urllib.parse.urlsplit(candidate)
        stripped = (parts.path or "").lstrip("/")
        if not stripped:
            return None, None, "url-scheme:%s with no path" % scheme.group(1)
        note = "normalised from scheme %s://%s" % (parts.scheme, parts.netloc)
        candidate = stripped
    if candidate.startswith("/"):
        return None, None, "absolute-path"
    normal = os.path.normpath(candidate)
    if normal in (".", "..") or normal.startswith("../") or normal == os.sep:
        return None, None, "traversal-above-out-dir"
    root = os.path.realpath(out_dir)
    target = os.path.realpath(os.path.join(root, normal))
    if target != root and not target.startswith(root + os.sep):
        return None, None, "resolves-outside-out-dir"
    if target == root:
        return None, None, "resolves-to-out-dir-itself"
    return target, normal, note


def write_sources(smap, out_dir, scheme_policy, skip_node_modules):
    """Reconstruct sourcesContent. Returns what was written, skipped, rejected."""
    sources = smap.get("sources") or []
    contents = smap.get("sourcesContent") or []
    root = smap.get("sourceRoot") or ""
    written, rejected, skipped, missing = [], [], [], []
    bytes_written = 0
    for index, source in enumerate(sources):
        content = contents[index] if index < len(contents) else None
        if not isinstance(source, str):
            rejected.append({"index": index, "source": repr(source),
                             "reason": "source name is not a string"})
            continue
        joined = source
        if root and not URI_SCHEME.match(source) and not source.startswith("/"):
            joined = root.rstrip("/") + "/" + source.lstrip("/")
        if content is None:
            missing.append(source)
        if skip_node_modules and "node_modules/" in joined.replace("\\", "/"):
            skipped.append(source)
            continue
        if out_dir is None:
            continue
        target, rel, note = safe_relpath(joined, out_dir, scheme_policy)
        if target is None:
            rejected.append({"index": index, "source": source, "reason": note})
            continue
        if content is None:
            continue                                  # nothing to write, not a rejection
        raw = content.encode("utf-8")
        try:
            parent = os.path.dirname(target)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(target, "wb") as handle:        # bytes: byte-for-byte, no
                handle.write(raw)                     # newline translation
        except OSError as exc:
            rejected.append({"index": index, "source": source,
                             "reason": "write failed: %s: %s"
                                       % (type(exc).__name__, exc)})
            continue
        bytes_written += len(raw)
        written.append({"source": source, "relpath": rel, "bytes": len(raw),
                        "note": note})
    return {"sources_total": len(sources),
            "sources_content_present": sum(1 for c in contents if c is not None),
            "written": written, "written_count": len(written),
            "bytes_written": bytes_written,
            "rejected": rejected, "rejected_count": len(rejected),
            "skipped_node_modules": len(skipped),
            "missing_content": len(missing),
            "source_root": root or None}


# --------------------------------------------------------------------------- #
# mining one text unit
# --------------------------------------------------------------------------- #
def classify_path(value, include_assets):
    """-> (kind, path, host) or None. One place decides what counts as a path."""
    if not value or len(value) > 400 or "\n" in value or " " in value:
        return None
    url = FULL_URL_RX.match(value)
    if url:
        path = url.group(3) or "/"
        if not include_assets and path.lower().endswith(ASSET_SUFFIXES):
            return None
        return "absolute-url", path, url.group(2)
    if value.startswith("//"):
        return None                                   # protocol-relative or a comment
    if value.startswith("/"):
        if len(value) < 2 or not ABS_PATH_RX.match(value):
            return None
        if not include_assets and value.lower().split("?")[0].endswith(ASSET_SUFFIXES):
            return None
        return "path-literal", value, None
    if REL_PATH_RX.match(value):
        if not include_assets and value.lower().endswith(ASSET_SUFFIXES):
            return None
        return "relative-api-path", value, None
    return None


class Inventory(object):
    """Accumulates across every unit so the endpoint list is deduplicated once."""

    def __init__(self, args):
        self.args = args
        self.endpoints = {}
        self.routes = {}
        self.bool_keys = {}
        self.env_refs = {}
        self.secrets = []
        self._secret_seen = set()
        # call_sites counts REQUEST call sites; call_sites_yielding_path counts
        # how many of those produced a classified path. Both are incremented at
        # the point of measurement in mine(), so neither is affected by
        # --max-hits, which is a display cap on the hits listed per endpoint.
        self.counts = {"units": 0, "chars": 0, "string_literals": 0,
                       "path_like_literals": 0, "call_sites": 0,
                       "call_sites_fetch_axios": 0, "call_sites_xhr_open": 0,
                       "call_sites_yielding_path": 0, "open_calls_not_xhr": 0,
                       "long_strings_examined": 0, "entropy_passed": 0}

    def add_endpoint(self, path, kind, unit, line, col, via, context,
                     method=None, host=None, prefix=None):
        entry = self.endpoints.setdefault(path, {
            "path": path, "kinds": set(), "methods": set(), "hosts": set(),
            "bases": set(), "hits": [], "hit_count": 0,
            "parameterised": bool(PARAMETERISED.search(path))})
        entry["kinds"].add(kind)
        if method:
            entry["methods"].add(method.upper())
        if host:
            entry["hosts"].add(host)
        if prefix:
            entry["bases"].add(prefix[:80])
        entry["hit_count"] += 1
        if len(entry["hits"]) < self.args.max_hits:
            hit = {"file": unit, "line": line, "col": col, "via": via,
                   "context": context}
            if prefix:
                hit["joined_to"] = prefix[:80]
            entry["hits"].append(hit)

    def add_secret(self, rule, name, value, unit, line, col):
        key = (rule, value)
        if key in self._secret_seen:
            return
        self._secret_seen.add(key)
        entropy = shannon(value)
        preview = value if self.args.show_secrets else (
            value if len(value) <= self.args.secret_preview
            else value[:self.args.secret_preview] + "...[+%d]"
                 % (len(value) - self.args.secret_preview))
        self.secrets.append({
            "rule": rule, "name": name, "value_preview": preview,
            "length": len(value), "entropy_bits_per_char": entropy,
            "entropy_total_bits": round(entropy * len(value), 1),
            "sha256_8": hashlib.sha256(value.encode("utf-8",
                                                    "surrogateescape")).hexdigest()[:8],
            "file": unit, "line": line, "col": col,
            "verdict": "candidate",
            "note": "shape and entropy only; this tool never validated it"})


def context_at(text, offset, width):
    start = max(0, offset - width)
    end = min(len(text), offset + width)
    return text[start:end].replace("\n", "\\n")


def mine(text, unit_name, inv):
    """Every extractor for one unit. Locations come from one LineIndex."""
    args = inv.args
    index = LineIndex(text)
    inv.counts["units"] += 1
    inv.counts["chars"] += len(text)

    def at(offset):
        return index.locate(offset)

    # 1. one pass over every quoted literal, asking both questions of it: does it
    #    look like a path, and is it long and high-entropy enough to be a key.
    #    Two passes over a multi-megabyte single-line bundle is the whole cost of
    #    this tool, so they share the scan.
    for match in STRING_RX.finditer(text):
        inv.counts["string_literals"] += 1
        raw = match.group(2)
        value = unescape_js(raw)
        hit = classify_path(value, args.include_assets)
        if hit:
            inv.counts["path_like_literals"] += 1
            kind, path, host = hit
            line, col = at(match.start(2))
            inv.add_endpoint(path, kind, unit_name, line, col, "string-literal",
                             context_at(text, match.start(), args.context),
                             host=host)
        if args.min_secret_len <= len(raw) <= 512 and HIGH_ENTROPY_CHARSET.match(raw):
            inv.counts["long_strings_examined"] += 1
            if shannon(raw) >= args.min_entropy:
                inv.counts["entropy_passed"] += 1
                line, col = at(match.start(2))
                inv.add_secret("high-entropy-string", "unnamed", raw, unit_name,
                               line, col)

    # 2. call sites, where the method is often visible next to the path.
    #    XHR is special: open(METHOD, URL), so both args are read.
    for match in re.finditer(r"\.open\s*\(", text):
        first = STRING_AT.match(text, match.end())
        method = first.group(2).strip().upper() if first else None
        if method not in HTTP_METHODS:
            # window.open(), modal.open(), db.open(): a `.open(` match is not by
            # itself an XHR request site, and counting it inflated the
            # "fetch/axios/XHR call sites" denominator with calls that were never
            # going to yield a path. Counted separately so the raw match count
            # stays visible rather than disappearing.
            inv.counts["open_calls_not_xhr"] += 1
            continue
        inv.counts["call_sites"] += 1
        inv.counts["call_sites_xhr_open"] += 1
        rest = text[first.end():]
        comma = re.match(r"\s*,", rest)
        if not comma:
            continue
        second = STRING_AT.match(text, first.end() + comma.end())
        if not second:
            continue
        value = unescape_js(second.group(2))
        hit = classify_path(value, args.include_assets)
        if hit:
            line, col = at(second.start(2))
            inv.counts["call_sites_yielding_path"] += 1
            inv.add_endpoint(hit[1], hit[0], unit_name, line, col, "xhr-open",
                             context_at(text, match.start(), args.context),
                             method=method, host=hit[2])

    for match in CALL_SITE_RX.finditer(text):
        callee = match.group(1)
        inv.counts["call_sites"] += 1
        inv.counts["call_sites_fetch_axios"] += 1
        literal = STRING_AT.match(text, match.end())
        via = "%s-first-arg" % callee
        prefix = None
        if not literal:
            # fetch(BASE + "/users") is the common minified shape; the first
            # literal within reach is the best available evidence, and it is
            # labelled differently so the operator can tell them apart.
            window = text[match.end():match.end() + args.lookahead]
            near = STRING_RX.search(window)
            if not near:
                continue
            literal, via = near, "%s-nearby-literal" % callee
            offset = match.end() + near.start(2)
            # The expression in front of the literal is what the real path is
            # joined to, so it is quoted verbatim: the inventory then holds a
            # fragment plus the name of its base, not a path nobody can use.
            prefix = window[:near.start()].strip() or None
        else:
            offset = literal.start(2)
        value = unescape_js(literal.group(2))
        hit = classify_path(value, args.include_assets)
        if not hit:
            continue
        inv.counts["call_sites_yielding_path"] += 1
        method = CALLEE_METHOD.get(callee)
        if not method:
            tail = text[match.end():match.end() + args.lookahead]
            found = METHOD_NEARBY.search(tail)
            if found and found.group(1).upper() in HTTP_METHODS:
                method = found.group(1).upper()
        line, col = at(offset)
        inv.add_endpoint(hit[1], hit[0], unit_name, line, col, via,
                         context_at(text, match.start(), args.context),
                         method=method, host=hit[2], prefix=prefix)

    # 3. url:/endpoint: config keys feed the same inventory
    for match in URL_KEY_RX.finditer(text):
        value = unescape_js(match.group(2))
        hit = classify_path(value, args.include_assets)
        if hit:
            line, col = at(match.start(2))
            inv.add_endpoint(hit[1], hit[0], unit_name, line, col,
                             "%s-key" % match.group(1),
                             context_at(text, match.start(), args.context),
                             host=hit[2])

    # 4. client route tables
    for match in ROUTE_KEY_RX.finditer(text):
        value = match.group(1)
        if not value or len(value) > 200:
            continue
        if not (value.startswith("/") or value in ("*", "")):
            continue
        line, col = at(match.start(1))
        entry = inv.routes.setdefault(value, {"path": value, "hits": [],
                                              "hit_count": 0})
        entry["hit_count"] += 1
        if len(entry["hits"]) < args.max_hits:
            entry["hits"].append({"file": unit_name, "line": line, "col": col,
                                  "context": context_at(text, match.start(),
                                                        args.context)})

    # 5. boolean config keys; !0/!1 is the minified form
    for match in BOOL_KEY_RX.finditer(text):
        name, raw = match.group(1), match.group(2)
        value = raw in ("!0", "true")
        line, col = at(match.start(1))
        entry = inv.bool_keys.setdefault(name, {
            "name": name, "values": set(), "flag_shaped_name":
                bool(FLAGGY_NAME.search(name)), "hits": [], "hit_count": 0})
        entry["values"].add(value)
        entry["hit_count"] += 1
        if len(entry["hits"]) < args.max_hits:
            entry["hits"].append({"file": unit_name, "line": line, "col": col,
                                  "literal": raw})

    # 6. build-time environment variables the bundle expected
    for match in ENV_RX.finditer(text):
        group = 1 if match.group(1) is not None else 2
        name = match.group(group)
        line, col = at(match.start(group))
        entry = inv.env_refs.setdefault(name, {"name": name, "hits": [],
                                               "hit_count": 0})
        entry["hit_count"] += 1
        if len(entry["hits"]) < args.max_hits:
            entry["hits"].append({"file": unit_name, "line": line, "col": col})

    # 7. secret candidates: named, shaped, then high-entropy. The named rule
    #    finds the keyword, widens to the whole identifier around it, then
    #    requires an assignment to a quoted value right after it.
    for match in SECRET_WORD_RX.finditer(text):
        start = match.start()
        while (start > 0 and match.start() - start < SECRET_NAME_SPAN
               and NAME_CHAR.match(text[start - 1])):
            start -= 1
        end = match.end()
        limit = min(len(text), match.end() + SECRET_NAME_SPAN)
        while end < limit and NAME_CHAR.match(text[end]):
            end += 1
        tail = SECRET_ASSIGN_TAIL.match(text, end)
        if not tail:
            continue
        line, col = at(tail.start(1))
        inv.add_secret("named-key-assignment", text[start:end], tail.group(1),
                       unit_name, line, col)
    for match in JWT_RX.finditer(text):
        token = match.group(0)
        line, col = at(match.start())
        header = decode_jwt_header(token)
        inv.add_secret("jwt-shaped", header or "jwt", token, unit_name, line, col)
        if header:
            inv.secrets[-1]["jwt_header_decoded"] = header
    for match in CLOUD_RX.finditer(text):
        shape = CLOUD_NAME.get(match.lastgroup, match.lastgroup)
        line, col = at(match.start())
        inv.add_secret(shape, shape, match.group(0), unit_name, line, col)


def decode_jwt_header(token):
    """-> the decoded header string, or None. Proves the shape, not the token."""
    head = token.split(".")[0]
    try:
        raw = base64.urlsafe_b64decode(head + "=" * (-len(head) % 4))
        obj = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        return None
    return json.dumps(obj, sort_keys=True) if isinstance(obj, dict) else None


# --------------------------------------------------------------------------- #
# --url: the entry page and one level of <script src>
# --------------------------------------------------------------------------- #
SCRIPT_SRC_RX = re.compile(r"""<script\b[^>]*?\bsrc\s*=\s*"""
                           r"""(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I | re.S)
INLINE_SCRIPT_RX = re.compile(r"""<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)"""
                              r"""</script\s*>""", re.I | re.S)
LINK_TAG_RX = re.compile(r"<link\b[^>]*>", re.I | re.S)
ATTR_RX = re.compile(r"""([A-Za-z_:][\w:.\-]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|"""
                     r"""([^\s>]+))""")


def scripts_from_html(html, parser_pref):
    """-> (src_list, inline_list, parser_used). bs4 when available and asked for,
    regex otherwise; both are exercised by the selftest so neither rots."""
    if parser_pref in ("auto", "bs4"):
        try:
            from bs4 import BeautifulSoup                   # optional dependency
        except ImportError:
            if parser_pref == "bs4":
                return [], [], "bs4-unavailable"
        else:
            backend = "html.parser"
            try:
                import lxml                                 # noqa: F401
                backend = "lxml"
            except ImportError:
                pass
            soup = BeautifulSoup(html, backend)
            srcs, inline = [], []
            for tag in soup.find_all("script"):
                src = tag.get("src")
                if src:
                    srcs.append(src)
                elif tag.string:
                    inline.append(tag.string)
                elif tag.decode_contents():
                    inline.append(tag.decode_contents())
            for tag in soup.find_all("link"):
                rel = " ".join(tag.get("rel") or []).lower()
                href = tag.get("href")
                if href and ("modulepreload" in rel or
                             (rel == "preload" and
                              (tag.get("as") or "").lower() == "script")):
                    srcs.append(href)
            return srcs, inline, "bs4+" + backend
    srcs = []
    for match in SCRIPT_SRC_RX.finditer(html):
        srcs.append(next(g for g in match.groups() if g is not None))
    inline = [m.group(1) for m in INLINE_SCRIPT_RX.finditer(html)
              if m.group(1).strip()]
    for tag in LINK_TAG_RX.finditer(html):
        attrs = {}
        for attr in ATTR_RX.finditer(tag.group(0)):
            attrs[attr.group(1).lower()] = next(
                (g for g in attr.groups()[1:] if g is not None), "")
        rel = (attrs.get("rel") or "").lower()
        href = attrs.get("href")
        if href and ("modulepreload" in rel or
                     (rel == "preload" and (attrs.get("as") or "").lower() == "script")):
            srcs.append(href)
    return srcs, inline, "regex-fallback"


def _fetch_entry_page(url, timeout, headers, max_bytes):
    """-> (html, note, truncated). Any status is parsed for <script src>: a SPA
    catch-all answering 404 still ships the bundle. Only a transport failure
    yields None."""
    resp = httpkit.request(url, "GET", headers, None, timeout=timeout,
                           max_bytes=max_bytes + 1)
    if not resp["ok"]:
        return None, "transport failure: %s" % resp.get("error"), False
    raw = resp["body_bytes"]
    if len(raw) > max_bytes:
        return (raw[:max_bytes].decode("utf-8", "replace"),
                "HTTP %s, TRUNCATED at --max-bytes %d (the response is larger; "
                "this inventory is short)" % (resp["status"], max_bytes), True)
    return (resp["body"], "HTTP %s, %d bytes" % (resp["status"], len(raw)), False)


def collect_units(args):
    """-> (units, fetch_log). A unit is one named blob of JavaScript to mine.

    Each input is independent. A dead --url ends the --url branch and nothing
    else: it used to `return` here, which silently discarded every --file bundle
    supplied alongside it, so the contest shape "the entry page plus the bundle I
    already saved" lost the saved bundle the moment the target blipped -- and the
    run still looked like a clean, small inventory. Every read is logged with
    kind="read" so run() can count how many inputs actually landed.
    """
    units, log = [], []
    headers = httpkit.parse_headers(args.header)
    if args.url:
        html, note, trunc = _fetch_entry_page(args.url, args.timeout, headers,
                                              args.max_bytes)
        log.append({"target": args.url, "kind": "read", "ok": html is not None,
                    "note": note, "truncated": trunc})
        if html is None:
            log.append({"target": args.url, "kind": "note", "ok": False,
                        "note": "entry page unreadable: no <script src> crawled. "
                                "--file and --map inputs are still read."})
        else:
            srcs, inline, parser = scripts_from_html(html, args.html_parser)
            log.append({"target": args.url, "kind": "note", "ok": True,
                        "note": "parser=%s, %d <script src>, %d inline"
                                % (parser, len(srcs), len(inline))})
            args._parser_used = parser
            args._script_srcs = srcs
            for number, body in enumerate(inline, 1):
                units.append({"name": "%s#inline-script-%d" % (args.url, number),
                              "text": body, "origin": "inline-script",
                              "truncated": False})
            seen = set()
            for ref in srcs:
                target = urllib.parse.urljoin(args.url, ref)
                if target in seen:
                    continue
                seen.add(target)
                if len(seen) > args.max_scripts:
                    log.append({"target": target, "kind": "skip", "ok": False,
                                "note": "skipped: --max-scripts %d reached"
                                        % args.max_scripts})
                    continue
                text, note, trunc = fetch_text(target, args.timeout, headers,
                                               args.max_bytes)
                log.append({"target": target, "kind": "read",
                            "ok": text is not None, "note": note,
                            "truncated": trunc})
                if text is not None:
                    units.append({"name": target, "text": text,
                                  "origin": "script-src", "truncated": trunc})
    for path in args.file or []:
        text, note, trunc = fetch_text(path, args.timeout, headers, args.max_bytes)
        log.append({"target": path, "kind": "read", "ok": text is not None,
                    "note": note, "truncated": trunc})
        if text is not None:
            units.append({"name": path, "text": text, "origin": "file",
                          "truncated": trunc})
    return units, log


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #
def run(args):
    inv = Inventory(args)
    args._parser_used = None
    args._script_srcs = []
    units, fetch_log = collect_units(args)
    headers = httpkit.parse_headers(args.header)

    bundles, maps = [], []
    maps_found = 0
    for unit in units:
        mine(unit["text"], unit["name"], inv)
        record = {"name": unit["name"], "origin": unit["origin"],
                  "chars": len(unit["text"]),
                  "lines": unit["text"].count("\n") + 1}
        record["minified"] = bool(unit["text"]) and (
            max([len(line) for line in unit["text"].split("\n")] or [0]) > 500)
        if args.no_sourcemap or unit["origin"] == "inline-script":
            record["sourcemap"] = {"found": False, "method": None,
                                   "note": "not searched"}
        else:
            located = locate_map(unit, args.timeout, headers, args.max_bytes,
                                 try_sibling=not args.no_sibling_guess)
            record["sourcemap"] = {"found": located["found"],
                                   "method": located["method"],
                                   "attempts": located["attempts"]}
            if located["found"]:
                maps_found += 1
                maps.append({"from": unit["name"], "method": located["method"],
                             "reference": located.get("reference"),
                             "map": located["map"]})
        bundles.append(record)

    for path in args.map or []:
        text, note, trunc = fetch_text(path, args.timeout, headers, args.max_bytes)
        if text is None:
            fetch_log.append({"target": path, "kind": "read", "ok": False,
                              "note": note, "truncated": False})
            continue
        data, err = parse_map(text)
        fetch_log.append({"target": path, "kind": "read",
                          "ok": data is not None,
                          "note": note if data else err, "truncated": trunc})
        if data:
            maps_found += 1
            maps.append({"from": path, "method": "explicit-map-argument",
                         "reference": path, "map": data})

    recovered, map_reports = [], []
    total_rejected = 0
    for entry in maps:
        result = write_sources(entry["map"], args.out, args.source_scheme,
                               args.skip_node_modules)
        total_rejected += result["rejected_count"]
        map_reports.append({"from": entry["from"], "method": entry["method"],
                            "reference": entry.get("reference"),
                            "file": entry["map"].get("file"),
                            "version": entry["map"].get("version"),
                            "sources_total": result["sources_total"],
                            "sources_content_present":
                                result["sources_content_present"],
                            "source_root": result["source_root"],
                            "written_count": result["written_count"],
                            "bytes_written": result["bytes_written"],
                            "rejected_count": result["rejected_count"],
                            "rejected": result["rejected"],
                            "skipped_node_modules": result["skipped_node_modules"],
                            "missing_content": result["missing_content"],
                            "written": result["written"][:args.max_listed]})
        # Mine the recovered source whether or not it reached disk: an endpoint
        # in a source file is the point, and --out may be absent.
        sources = entry["map"].get("sources") or []
        contents = entry["map"].get("sourcesContent") or []
        for index, source in enumerate(sources):
            if index >= len(contents) or contents[index] is None:
                continue
            if args.skip_node_modules and "node_modules/" in str(source):
                continue
            name = "%s!%s" % (os.path.basename(str(entry["from"])), source)
            mine(contents[index], name, inv)
            recovered.append({"source": source, "chars": len(contents[index])})

    endpoints = []
    for path in sorted(inv.endpoints):
        entry = inv.endpoints[path]
        endpoints.append({"path": path,
                          "methods": sorted(entry["methods"]),
                          "kinds": sorted(entry["kinds"]),
                          "hosts": sorted(entry["hosts"]),
                          # non-empty means this path is a FRAGMENT: it was found
                          # concatenated onto the named expression, so it is not
                          # requestable until that base is resolved
                          "joined_to_bases": sorted(entry["bases"]),
                          "parameterised": entry["parameterised"],
                          "hit_count": entry["hit_count"],
                          "hits": entry["hits"]})
    bool_keys = []
    for name in sorted(inv.bool_keys):
        entry = inv.bool_keys[name]
        bool_keys.append({"name": name, "values": sorted(entry["values"]),
                          "flag_shaped_name": entry["flag_shaped_name"],
                          "hit_count": entry["hit_count"],
                          "hits": entry["hits"]})
    feature_flags = [k for k in bool_keys if k["flag_shaped_name"]]
    routes = [inv.routes[p] for p in sorted(inv.routes)]
    env_refs = [inv.env_refs[n] for n in sorted(inv.env_refs)]
    secrets = sorted(inv.secrets,
                     key=lambda s: -s["entropy_total_bits"])[:args.max_listed]

    # Every read of every input went through fetch_log with kind="read", so the
    # accounting is derived from the record of what was read rather than restated.
    reads = [e for e in fetch_log if e.get("kind") == "read"]
    inputs_failed = len([e for e in reads if not e.get("ok")])
    inputs_truncated = len([e for e in reads if e.get("truncated")])
    inputs_skipped = len([e for e in fetch_log if e.get("kind") == "skip"])
    partial = inputs_failed or inputs_truncated or inputs_skipped

    counts = dict(inv.counts)
    counts.update({"inputs_read": len(reads),
                   "inputs_failed": inputs_failed,
                   "inputs_truncated": inputs_truncated,
                   "inputs_skipped": inputs_skipped,
                   "bundles": len(bundles), "sourcemaps_found": maps_found,
                   "sourcemaps_missing": len([b for b in bundles
                                              if not b["sourcemap"]["found"]]),
                   "recovered_sources_mined": len(recovered),
                   "source_paths_rejected": total_rejected,
                   "endpoints": len(endpoints), "routes": len(routes),
                   "boolean_config_keys": len(bool_keys),
                   "feature_flag_shaped": len(feature_flags),
                   "env_refs": len(env_refs),
                   "secret_candidates": len(inv.secrets)})

    # Requirement: a zero is a finding, so every category states its denominator.
    negatives = [
        "%d of %d units carried a source map (%d with a sourceMappingURL comment)"
        % (maps_found, len(bundles),
           len([b for b in bundles
                if b["sourcemap"].get("method") == "sourceMappingURL-comment"])),
        "%d of %d quoted string literals looked like an endpoint path"
        % (counts["path_like_literals"], counts["string_literals"]),
        # Both numbers are call sites counted in mine() at the moment of
        # measurement. The numerator used to count ENDPOINTS carrying a
        # call-site hit, which --max-hits truncates, so three fetch() calls to
        # one path reported "0 of 3" at the default cap and "1 of 3" at
        # --max-hits 10. A display cap must never reach an accounting line.
        "%d of %d fetch/axios/XHR call sites yielded a path "
        "(%d fetch/axios, %d XHR open; %d further .open( call(s) were not "
        "request sites)"
        % (counts["call_sites_yielding_path"], counts["call_sites"],
           counts["call_sites_fetch_axios"], counts["call_sites_xhr_open"],
           counts["open_calls_not_xhr"]),
        "%d of %d boolean config keys have a feature-flag-shaped name"
        % (len(feature_flags), len(bool_keys)),
        "%d of %d long base64/hex-charset strings passed the %.1f bits/char threshold"
        % (counts["entropy_passed"], counts["long_strings_examined"],
           args.min_entropy),
        "%d source paths were rejected as unsafe out of %d across %d map(s)"
        % (total_rejected, sum(m["sources_total"] for m in map_reports),
           len(map_reports)),
        # Appended last on purpose: the lines above are addressed by index
        # elsewhere. A read that failed, was cut at --max-bytes, or was dropped
        # by --max-scripts makes the inventory short, and a short inventory that
        # does not say so reads as a clean small one.
        "%d of %d inputs were read whole; %d failed, %d were TRUNCATED at "
        "--max-bytes %d, %d were skipped by --max-scripts %d"
        % (len(reads) - inputs_failed - inputs_truncated, len(reads),
           inputs_failed, inputs_truncated, args.max_bytes, inputs_skipped,
           args.max_scripts),
    ]

    verdict = ("%d endpoints, %d routes, %d env vars, %d secret candidates from "
               "%d unit(s) and %d recovered source(s)"
               % (len(endpoints), len(routes), len(env_refs), len(inv.secrets),
                  len(bundles), len(recovered)))
    if partial:
        # The headline is the one line an operator reads. An inventory built from
        # inputs that did not all land is PARTIAL, and saying so here is the
        # difference between "the app has 12 endpoints" and "12 is a floor".
        verdict += (" -- PARTIAL: %d input(s) unreadable, %d truncated at "
                    "--max-bytes, %d skipped by --max-scripts; this endpoint "
                    "count is a floor, not the inventory"
                    % (inputs_failed, inputs_truncated, inputs_skipped))

    report = {
        "mode": "bundle-miner",
        "inputs": {"url": args.url, "files": args.file or [],
                   "maps": args.map or [], "out": args.out,
                   "source_scheme_policy": args.source_scheme},
        "html_parser": args._parser_used,
        "optional_deps": {"bs4": _importable("bs4"), "lxml": _importable("lxml")},
        "script_srcs_seen": args._script_srcs,
        "fetch_log": fetch_log,
        "bundles": bundles,
        "sourcemaps": map_reports,
        "endpoints": endpoints,
        "routes": routes,
        "boolean_config_keys": bool_keys,
        "feature_flag_candidates": [k["name"] for k in feature_flags],
        "env_refs": env_refs,
        "secret_candidates": secrets,
        "secret_candidates_note": "every entry is a candidate: shape and entropy "
                                  "only, never validated against the target",
        "counts": counts,
        "negatives": negatives,
        "verdict_line": verdict,
        "next_action": "feed the endpoint inventory to tools/web/http_probe.py or "
                       "tools/web/id_sweep.py; a candidate secret is confirmed by "
                       "a probe, not by this parse",
    }
    if args.out and map_reports:
        report["out_dir_listing"] = _listing(args.out, args.max_listed)
    return report


def _importable(name):
    """find_spec, not __import__: importing bs4 just to report a boolean cost
    0.6s of every --file run, which is most of a small bundle's whole budget."""
    import importlib.util
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _listing(out_dir, limit):
    found = []
    for root, _dirs, files in os.walk(out_dir):
        for name in files:
            full = os.path.join(root, name)
            found.append({"relpath": os.path.relpath(full, out_dir),
                          "bytes": os.path.getsize(full)})
    found.sort(key=lambda item: item["relpath"])
    return {"total": len(found), "files": found[:limit]}


# --------------------------------------------------------------------------- #
# offline selftest: a fixture bundle, a real map, and a hostile map
# --------------------------------------------------------------------------- #
PLANTED_ENDPOINTS = ("/api/v1/users", "/api/v1/login", "/api/v1/session",
                     "/api/v1/keys", "/api/v1/profile", "/internal/debug/flag",
                     "/graphql")
PLANTED_JWT = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
               "eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9."
               "Qm9ndXNTaWduYXR1cmVGb3JBU2VsZnRlc3RPbmx5")
# Reachable by the entropy rule alone: no keyword names it, and it matches no
# provider prefix and no JWT shape. Its low-entropy twin is the same length, so
# the pair tests the threshold in both directions rather than only upward.
PLANTED_HIGH_ENTROPY = "Zm9vYmFyOTk3N2FiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MDEyMw"
PLANTED_LOW_ENTROPY = "aaaaaaaaaaaabbbbbbbbbbbbaaaaaaaaaaaabbbbbbbbbbbbaaaaaa"
PLANTED_SOURCE = (
    "import http from './http';\n"
    "\n"
    "// the admin surface only the recovered source names\n"
    "export async function adminFlag() {\n"
    "  const r = await fetch('/api/v1/admin/flag', { method: 'POST' });\n"
    "  return r.json();\n"
    "}\n"
    "\n"
    "export const ROUTES = [{ path: '/admin/secrets' }];\n"
    "export const API_KEY = 'AKIAIOSFODNN7EXAMPLE';\n"
)
PLANTED_SOURCE_2 = "export default { base: '/api/v1' };\n"


def _fixture_bundle(with_comment, comment_form="//#", map_ref="bundle.js.map"):
    body = (
        "(function(){var e={enableAdminPanel:!0,debugMode:!1,retries:3,"
        "maxUsers:50,isStaff:!1};"
        'var b=process.env.REACT_APP_API_BASE||import.meta.env.VITE_API_BASE;'
        'var r=[{path:"/admin/panel",c:1},{path:"/login",c:2},{path:"/",c:3}];'
        'fetch("/api/v1/session",{method:"POST",body:"{}"});'
        'fetch(b+"/api/v1/users");'
        'axios.get("/api/v1/profile");'
        'var x=new XMLHttpRequest();x.open("DELETE","/api/v1/keys");'
        'var cfg={url:"/api/v1/login",apiKey:"sk_test_51H8xQ2abcdefghijklmnop"};'
        'var t="%s";var hi="%s";var lo="%s";'
        'var dbg="/internal/debug/flag";var g="/graphql";'
        'var css="text/html";var asset="/static/js/main.4f2a.js";'
        "return e&&r&&cfg&&t&&hi&&lo&&dbg&&g&&css&&asset;})();"
        % (PLANTED_JWT, PLANTED_HIGH_ENTROPY, PLANTED_LOW_ENTROPY)
    )
    if with_comment:
        body += "\n%s sourceMappingURL=%s\n" % (comment_form, map_ref)
    return body


def _fixture_map(sources, contents, file_name="bundle.js"):
    return json.dumps({"version": 3, "file": file_name, "sources": sources,
                       "sourcesContent": contents, "names": [],
                       "mappings": "AAAA"})


def _args_for(**over):
    parser = build_parser()
    argv = []
    for key, value in over.items():
        flag = "--" + key.replace("_", "-")
        if value is True:
            argv.append(flag)
        elif isinstance(value, list):
            for item in value:
                argv += [flag, str(item)]
        elif value is not None:
            argv += [flag, str(value)]
    return parser.parse_args(argv)


def selftest(verbose=False, keep_fixture=False):
    """Offline. Fixture bundle + real map + hostile map + a loopback server."""
    import contextlib
    import http.server
    import io
    import shutil
    import threading

    checks = []

    def check(name, ok, detail, extra=None):
        entry = {"case": name, "pass": bool(ok), "detail": detail}
        if extra is not None and (verbose or not ok):
            entry["output"] = extra
        checks.append(entry)

    tmp = tempfile.mkdtemp(prefix="bundle_miner-selftest-")
    bundle_path = os.path.join(tmp, "bundle.js")
    with open(bundle_path, "w", encoding="utf-8") as handle:
        handle.write(_fixture_bundle(True))
    with open(bundle_path + ".map", "w", encoding="utf-8") as handle:
        handle.write(_fixture_map(
            ["webpack:///./src/admin.js", "src/config.js"],
            [PLANTED_SOURCE, PLANTED_SOURCE_2]))

    out1 = os.path.join(tmp, "out1")
    report = run(_args_for(file=[bundle_path], out=out1))

    paths = {e["path"] for e in report["endpoints"]}
    missing = [p for p in PLANTED_ENDPOINTS if p not in paths]
    check("every planted endpoint is recovered",
          not missing,
          "%d of %d planted endpoints present; missing=%s"
          % (len(PLANTED_ENDPOINTS) - len(missing), len(PLANTED_ENDPOINTS),
             missing or "none"),
          sorted(paths))

    check("the endpoint only the recovered source names is in the inventory",
          "/api/v1/admin/flag" in paths,
          "/api/v1/admin/flag present=%s" % ("/api/v1/admin/flag" in paths),
          sorted(paths))

    check("the sourceMappingURL comment is the method reported",
          report["sourcemaps"] and
          report["sourcemaps"][0]["method"] == "sourceMappingURL-comment",
          "method=%s" % (report["sourcemaps"][0]["method"]
                         if report["sourcemaps"] else None),
          report["bundles"][0]["sourcemap"] if report["bundles"] else None)

    # byte-for-byte: read back as bytes and compare to the planted UTF-8
    admin = os.path.join(out1, "src", "admin.js")
    config = os.path.join(out1, "src", "config.js")
    same = []
    for path, planted in ((admin, PLANTED_SOURCE), (config, PLANTED_SOURCE_2)):
        try:
            with open(path, "rb") as handle:
                same.append(handle.read() == planted.encode("utf-8"))
        except OSError:
            same.append(False)
    check("recovered sources match the planted content byte for byte",
          all(same) and len(same) == 2,
          "admin.js=%s config.js=%s (webpack:// scheme normalised to src/)"
          % tuple(same),
          report["sourcemaps"][0] if report["sourcemaps"] else None)

    jwt_hits = [s for s in report["secret_candidates"]
                if s["rule"] == "jwt-shaped"]
    check("the JWT is found and reported as a candidate, not a finding",
          jwt_hits and jwt_hits[0]["verdict"] == "candidate"
          and jwt_hits[0].get("jwt_header_decoded")
          and jwt_hits[0]["entropy_bits_per_char"] > 3.0,
          "rules=%s verdict=%s header=%s entropy=%s"
          % ([s["rule"] for s in report["secret_candidates"]][:6],
             jwt_hits[0]["verdict"] if jwt_hits else None,
             jwt_hits[0].get("jwt_header_decoded") if jwt_hits else None,
             jwt_hits[0]["entropy_bits_per_char"] if jwt_hits else None),
          report["secret_candidates"])

    # The entropy rule on its own: one string no keyword names and no provider
    # prefix matches, and its equal-length low-entropy twin that must NOT appear.
    # Keyed on the fingerprint, because value_preview is truncated by default.
    def fp(value):
        return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]

    entropy_hits = {s["sha256_8"]: s for s in report["secret_candidates"]
                    if s["rule"] == "high-entropy-string"}
    high = entropy_hits.get(fp(PLANTED_HIGH_ENTROPY))
    low_reported = fp(PLANTED_LOW_ENTROPY) in entropy_hits
    check("the entropy rule finds an unnamed key and the threshold excludes its twin",
          high is not None
          and high["entropy_bits_per_char"] >= 3.6
          and high["length"] == len(PLANTED_HIGH_ENTROPY)
          and not low_reported
          and report["counts"]["long_strings_examined"]
              > report["counts"]["entropy_passed"],
          "high=%s bits/char over %s chars, low-entropy twin of the same length "
          "reported=%s, %d of %d long strings passed 3.6 bits/char"
          % (high["entropy_bits_per_char"] if high else None,
             high["length"] if high else None, low_reported,
             report["counts"]["entropy_passed"],
             report["counts"]["long_strings_examined"]),
          sorted(entropy_hits))

    shown = run(_args_for(file=[bundle_path], show_secrets=True))
    full = {s["sha256_8"]: s["value_preview"] for s in shown["secret_candidates"]}
    check("a long value is truncated by default and printed whole with --show-secrets",
          high is not None and high["value_preview"].endswith("...[+14]")
          and len(high["value_preview"]) == 40 + len("...[+14]")
          and full.get(fp(PLANTED_HIGH_ENTROPY)) == PLANTED_HIGH_ENTROPY,
          "default preview=%r | --show-secrets returns the %d-char value=%s"
          % (high["value_preview"] if high else None, len(PLANTED_HIGH_ENTROPY),
             full.get(fp(PLANTED_HIGH_ENTROPY)) == PLANTED_HIGH_ENTROPY),
          {"default": high["value_preview"] if high else None})

    # The AWS-shaped key is inside sourcesContent, so finding it also proves the
    # recovered source is mined, not just written.
    shapes = {s["rule"] for s in report["secret_candidates"]}
    check("shape rules fire on the recovered source and on the bundle",
          "aws-access-key-id" in shapes and "named-key-assignment" in shapes,
          "shapes=%s" % sorted(shapes), report["secret_candidates"])

    methods = {e["path"]: e["methods"] for e in report["endpoints"]}
    check("methods are paired with the paths that showed one",
          methods.get("/api/v1/session") == ["POST"]
          and methods.get("/api/v1/keys") == ["DELETE"]
          and methods.get("/api/v1/profile") == ["GET"]
          and methods.get("/api/v1/admin/flag") == ["POST"],
          "session=%s keys=%s profile=%s admin/flag=%s"
          % (methods.get("/api/v1/session"), methods.get("/api/v1/keys"),
             methods.get("/api/v1/profile"), methods.get("/api/v1/admin/flag")),
          methods)

    # fetch(b+"/api/v1/users") in the fixture: the path is a fragment joined to b,
    # and the inventory has to say so rather than offering an unrequestable path.
    joined = {e["path"]: e["joined_to_bases"] for e in report["endpoints"]
              if e["joined_to_bases"]}
    check("a concatenated fetch path is marked with the base it is joined to",
          joined.get("/api/v1/users") == ["b+"]
          and "/api/v1/session" not in joined,
          "joined=%s (a literal first arg stays unmarked)" % joined, joined)

    routes = {r["path"] for r in report["routes"]}
    check("the client route table is recovered",
          {"/admin/panel", "/login", "/admin/secrets"} <= routes,
          "routes=%s" % sorted(routes), report["routes"])

    flags = set(report["feature_flag_candidates"])
    check("minified !0/!1 feature flags are decoded, plain config is not flagged",
          {"enableAdminPanel", "debugMode", "isStaff"} <= flags
          and "retries" not in flags and "maxUsers" not in flags,
          "flag-shaped=%s of %d boolean keys"
          % (sorted(flags), report["counts"]["boolean_config_keys"]),
          report["boolean_config_keys"])

    env = {e["name"] for e in report["env_refs"]}
    check("process.env and import.meta.env variables are named",
          {"REACT_APP_API_BASE", "VITE_API_BASE"} <= env,
          "env=%s" % sorted(env), report["env_refs"])

    check("static asset paths stay out of the endpoint inventory",
          "/static/js/main.4f2a.js" not in paths,
          "asset excluded=%s" % ("/static/js/main.4f2a.js" not in paths),
          sorted(paths))

    # --- the case that matters: a hostile sources array ---------------------- #
    evil_dir = os.path.join(tmp, "evil-target")
    os.makedirs(evil_dir, exist_ok=True)
    evil_map = os.path.join(tmp, "hostile.js.map")
    with open(evil_map, "w", encoding="utf-8") as handle:
        handle.write(_fixture_map(
            ["../evil-target/pwned.js", "src/clean.js"],
            ["OWNED\n", "export const ok = 1;\n"], file_name="hostile.js"))
    out2 = os.path.join(tmp, "out2")
    evil_report = run(_args_for(map=[evil_map], out=out2))
    entry = evil_report["sourcemaps"][0]
    escaped = os.path.exists(os.path.join(evil_dir, "pwned.js"))
    outside = [item for item in _listing(tmp, 500)["files"]
               if not item["relpath"].startswith(("out1" + os.sep,
                                                  "out2" + os.sep))
               and item["relpath"] not in ("bundle.js", "bundle.js.map",
                                           "hostile.js.map")]
    check("a traversal source writes nothing outside --out and counts 1 rejection",
          entry["rejected_count"] == 1 and not escaped and not outside
          and entry["written_count"] == 1
          and os.path.exists(os.path.join(out2, "src", "clean.js")),
          "rejected=%d reason=%s escaped_file=%s stray_files=%s clean_written=%s"
          % (entry["rejected_count"],
             entry["rejected"][0]["reason"] if entry["rejected"] else None,
             escaped, [i["relpath"] for i in outside],
             os.path.exists(os.path.join(out2, "src", "clean.js"))),
          entry)

    check("the rejection is counted in the report's negatives line",
          any("1 source paths were rejected" in line
              for line in evil_report["negatives"]),
          # the line by content, not by index: the negatives list has grown since
          # this case was written and [-1] is no longer the rejection line
          "; ".join(line for line in evil_report["negatives"]
                    if "source paths were rejected" in line) or "<no such line>",
          evil_report["negatives"])

    # absolute path, drive letter, and a real URL scheme under the strict policy
    hostile2 = os.path.join(tmp, "hostile2.js.map")
    with open(hostile2, "w", encoding="utf-8") as handle:
        handle.write(_fixture_map(
            ["/etc/cron.d/pwn", "C:\\windows\\pwn.js", "http://evil/x.js",
             "webpack:///../../../../../../etc/cron.d/pwn2", "\x00/nul.js",
             "webpack:///./src/keep.js"],
            ["a\n", "b\n", "c\n", "d\n", "e\n", "keep\n"]))
    out3 = os.path.join(tmp, "out3")
    rep3 = run(_args_for(map=[hostile2], out=out3))
    reasons3 = [r["reason"] for r in rep3["sourcemaps"][0]["rejected"]]
    check("each escape form is rejected by name and only the safe source lands",
          rep3["sourcemaps"][0]["rejected_count"] == 5
          and "absolute-path" in reasons3
          and "windows-drive-letter" in reasons3
          and "url-scheme:http" in reasons3
          and "traversal-above-out-dir" in reasons3
          and "control-characters-in-path" in reasons3
          and rep3["sourcemaps"][0]["written_count"] == 1
          and rep3["sourcemaps"][0]["written"][0]["relpath"]
              == os.path.join("src", "keep.js")
          and not os.path.exists("/etc/cron.d/pwn")
          and not os.path.exists("/etc/cron.d/pwn2")
          and _listing(out3, 50)["total"] == 1,
          "rejected=%d reasons=%s written=%d files_in_out=%d"
          % (rep3["sourcemaps"][0]["rejected_count"], reasons3,
             rep3["sourcemaps"][0]["written_count"],
             _listing(out3, 50)["total"]),
          rep3["sourcemaps"][0])

    out3b = os.path.join(tmp, "out3b")
    rep3b = run(_args_for(map=[hostile2], out=out3b, source_scheme="reject"))
    reasons3b = [r["reason"] for r in rep3b["sourcemaps"][0]["rejected"]]
    check("--source-scheme reject refuses the webpack:// path too, writing nothing",
          reasons3b.count("url-scheme:webpack") == 2
          and "url-scheme:http" in reasons3b
          and rep3b["sourcemaps"][0]["written_count"] == 0
          and _listing(out3b, 50)["total"] == 0,
          "reasons=%s written=%d"
          % (reasons3b, rep3b["sourcemaps"][0]["written_count"]),
          rep3b["sourcemaps"][0])

    # --- the other three discovery methods ---------------------------------- #
    old_dir = os.path.join(tmp, "old")
    os.makedirs(old_dir, exist_ok=True)
    old_bundle = os.path.join(old_dir, "app.js")
    with open(old_bundle, "w", encoding="utf-8") as handle:
        handle.write(_fixture_bundle(True, comment_form="//@",
                                     map_ref="app.js.map"))
    with open(old_bundle + ".map", "w", encoding="utf-8") as handle:
        handle.write(_fixture_map(["src/old.js"], ["const p = '/api/v1/old';\n"],
                                  file_name="app.js"))
    rep_old = run(_args_for(file=[old_bundle], out=os.path.join(tmp, "out4")))
    check("the older //@ sourceMappingURL form is found",
          rep_old["sourcemaps"] and
          rep_old["sourcemaps"][0]["method"] == "sourceMappingURL-comment"
          and "/api/v1/old" in {e["path"] for e in rep_old["endpoints"]},
          "method=%s old endpoint=%s"
          % (rep_old["sourcemaps"][0]["method"] if rep_old["sourcemaps"] else None,
             "/api/v1/old" in {e["path"] for e in rep_old["endpoints"]}),
          rep_old["bundles"][0]["sourcemap"])

    sib_dir = os.path.join(tmp, "sib")
    os.makedirs(sib_dir, exist_ok=True)
    sib_bundle = os.path.join(sib_dir, "chunk.js")
    with open(sib_bundle, "w", encoding="utf-8") as handle:
        handle.write(_fixture_bundle(False))           # no comment at all
    with open(sib_bundle + ".map", "w", encoding="utf-8") as handle:
        handle.write(_fixture_map(["src/sib.js"], ["const s='/api/v1/sib';\n"],
                                  file_name="chunk.js"))
    rep_sib = run(_args_for(file=[sib_bundle], out=os.path.join(tmp, "out5")))
    check("a .map sibling is found with no comment present",
          rep_sib["sourcemaps"] and
          rep_sib["sourcemaps"][0]["method"] == "sibling-guess"
          and "/api/v1/sib" in {e["path"] for e in rep_sib["endpoints"]},
          "method=%s" % (rep_sib["sourcemaps"][0]["method"]
                         if rep_sib["sourcemaps"] else None),
          rep_sib["bundles"][0]["sourcemap"])

    inline_dir = os.path.join(tmp, "inline")
    os.makedirs(inline_dir, exist_ok=True)
    inline_map = _fixture_map(["src/inline.js"], ["const i='/api/v1/inline';\n"],
                              file_name="inline.js")
    data_uri = "data:application/json;base64," + base64.b64encode(
        inline_map.encode("utf-8")).decode("ascii")
    inline_bundle = os.path.join(inline_dir, "inline.js")
    with open(inline_bundle, "w", encoding="utf-8") as handle:
        handle.write(_fixture_bundle(True, map_ref=data_uri))
    rep_inline = run(_args_for(file=[inline_bundle],
                               out=os.path.join(tmp, "out6")))
    check("an inline base64 data: map is decoded",
          rep_inline["sourcemaps"] and
          rep_inline["sourcemaps"][0]["method"] == "inline-data-uri"
          and "/api/v1/inline" in {e["path"] for e in rep_inline["endpoints"]},
          "method=%s" % (rep_inline["sourcemaps"][0]["method"]
                         if rep_inline["sourcemaps"] else None),
          rep_inline["bundles"][0]["sourcemap"])

    # a .map request that returns HTML is a catch-all, not a map
    catch_dir = os.path.join(tmp, "catchall")
    os.makedirs(catch_dir, exist_ok=True)
    catch_bundle = os.path.join(catch_dir, "c.js")
    with open(catch_bundle, "w", encoding="utf-8") as handle:
        handle.write(_fixture_bundle(True, map_ref="c.js.map"))
    with open(catch_bundle + ".map", "w", encoding="utf-8") as handle:
        handle.write("<!doctype html><html><body>not found</body></html>")
    rep_catch = run(_args_for(file=[catch_bundle],
                              out=os.path.join(tmp, "out7")))
    notes = [a["note"] for a in rep_catch["bundles"][0]["sourcemap"]["attempts"]]
    check("HTML served for a .map is refused, and the refusal is recorded",
          not rep_catch["bundles"][0]["sourcemap"]["found"]
          and any("not JSON" in str(n) for n in notes)
          and "0 of 1 units carried a source map" in rep_catch["negatives"][0],
          "attempts=%s | %s" % (notes, rep_catch["negatives"][0]),
          rep_catch["bundles"][0]["sourcemap"])

    # --- --url: entry page, one level of <script src>, both HTML parsers ---- #
    served = {
        "/": ("text/html",
              "<!doctype html><html><head>"
              "<link rel=\"modulepreload\" href=\"/assets/pre.js\">"
              "<script src=\"/assets/app.js\"></script>"
              "<script>window.CFG={url:\"/api/v1/inline-cfg\"};</script>"
              "</head><body></body></html>"),
        "/assets/app.js": ("application/javascript",
                           _fixture_bundle(True, map_ref="app.js.map")),
        "/assets/app.js.map": ("application/json",
                               _fixture_map(["src/web.js"],
                                            ["const w='/api/v1/web';\n"],
                                            file_name="app.js")),
        "/assets/pre.js": ("application/javascript",
                           "fetch('/api/v1/preloaded');"),
    }

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def do_GET(self):
            path = urllib.parse.urlparse(self.path).path
            if path not in served:
                body = b"no route"
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            ctype, text = served[path]
            body = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    base = "http://127.0.0.1:%d/" % server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        web = run(_args_for(url=base, out=os.path.join(tmp, "out8")))
        web_regex = run(_args_for(url=base, out=os.path.join(tmp, "out9"),
                                  html_parser="regex"))
        web_cap = run(_args_for(url=base, out=os.path.join(tmp, "outC"),
                                max_scripts=1))
    finally:
        server.shutdown()
        server.server_close()

    web_paths = {e["path"] for e in web["endpoints"]}
    check("--url crawls one level of <script src> and mines the map it finds",
          {"/api/v1/users", "/api/v1/web", "/api/v1/preloaded",
           "/api/v1/inline-cfg"} <= web_paths
          and web["html_parser"].startswith("bs4"),
          "parser=%s paths=%d web/preloaded/inline present=%s"
          % (web["html_parser"], len(web_paths),
             sorted(web_paths & {"/api/v1/web", "/api/v1/preloaded",
                                 "/api/v1/inline-cfg"})),
          sorted(web_paths))

    regex_paths = {e["path"] for e in web_regex["endpoints"]}
    check("the regex HTML fallback finds the same scripts as bs4",
          web_regex["html_parser"] == "regex-fallback"
          and regex_paths == web_paths,
          "parser=%s equal=%s bs4_only=%s regex_only=%s"
          % (web_regex["html_parser"], regex_paths == web_paths,
             sorted(web_paths - regex_paths), sorted(regex_paths - web_paths)),
          {"bs4": sorted(web_paths), "regex": sorted(regex_paths)})

    dead = run(_args_for(url="http://127.0.0.1:9/", out=os.path.join(tmp, "outA")))
    check("a dead target is a recorded transport failure, not an exception",
          dead["counts"]["endpoints"] == 0
          and any("transport failure" in str(e["note"])
                  for e in dead["fetch_log"]),
          "; ".join(str(e["note"]) for e in dead["fetch_log"]), dead["fetch_log"])

    # no --out: still an inventory, and still nothing written
    nomap_out = run(_args_for(file=[bundle_path]))
    check("without --out the sources are mined in memory and nothing is written",
          "/api/v1/admin/flag" in {e["path"] for e in nomap_out["endpoints"]}
          and nomap_out["sourcemaps"][0]["written_count"] == 0,
          "endpoints=%d written=%d"
          % (nomap_out["counts"]["endpoints"],
             nomap_out["sourcemaps"][0]["written_count"]),
          nomap_out["sourcemaps"][0])


    # --- a cap or a dead input must never quietly shorten the inventory ----- #
    # --max-scripts drops a script the entry page named. The inventory is then a
    # floor, and the report has to say which cap made it one.
    cap_paths = {e["path"] for e in web_cap["endpoints"]}
    check("a --max-scripts cap is counted, named, and marks the verdict PARTIAL",
          web_cap["counts"]["inputs_skipped"] == 1
          and "/api/v1/preloaded" not in cap_paths
          and "/api/v1/preloaded" in web_paths
          and "1 were skipped by --max-scripts 1" in web_cap["negatives"][-1]
          and "PARTIAL" in web_cap["verdict_line"]
          and any(e.get("kind") == "skip" for e in web_cap["fetch_log"]),
          "skipped=%d preloaded_dropped=%s | %s"
          % (web_cap["counts"]["inputs_skipped"],
             "/api/v1/preloaded" not in cap_paths, web_cap["negatives"][-1]),
          web_cap["fetch_log"])

    # The uncapped run is the other direction: nothing skipped, nothing truncated,
    # nothing failed, so the verdict must NOT be marked PARTIAL.
    check("a run whose every input landed whole is not marked PARTIAL",
          "PARTIAL" not in web["verdict_line"]
          and web["counts"]["inputs_failed"] == 0
          and web["counts"]["inputs_truncated"] == 0
          and web["counts"]["inputs_skipped"] == 0
          and "0 were skipped" in web["negatives"][-1],
          "verdict=%s | %s" % (web["verdict_line"][:60], web["negatives"][-1]),
          web["counts"])

    # --- D1: a dead --url must not discard the --file bundles beside it ----- #
    dead_mix_file = os.path.join(tmp, "still-on-disk.js")
    with open(dead_mix_file, "w", encoding="utf-8") as handle:
        handle.write('fetch("/api/v1/fromfile");')
    dead_mix = run(_args_for(url="http://127.0.0.1:9/", file=[dead_mix_file],
                             no_sourcemap=True))
    dead_mix_paths = {e["path"] for e in dead_mix["endpoints"]}
    check("a dead --url is recorded but does not discard the --file bundle with it",
          "/api/v1/fromfile" in dead_mix_paths
          and dead_mix["counts"]["inputs_failed"] == 1
          and dead_mix["counts"]["inputs_read"] == 2
          and any(e.get("kind") == "read" and not e["ok"]
                  and "transport failure" in str(e["note"])
                  for e in dead_mix["fetch_log"])
          and "PARTIAL" in dead_mix["verdict_line"],
          "file endpoint kept=%s inputs_read=%d failed=%d"
          % ("/api/v1/fromfile" in dead_mix_paths,
             dead_mix["counts"]["inputs_read"],
             dead_mix["counts"]["inputs_failed"]),
          dead_mix["fetch_log"])

    # --- D3: --max-bytes truncation, in both directions --------------------- #
    two_paths = os.path.join(tmp, "two-paths.js")
    with open(two_paths, "w", encoding="utf-8") as handle:
        handle.write('var a="/api/v1/early";var z="/api/v1/late";')
    cut = run(_args_for(file=[two_paths], no_sourcemap=True, max_bytes=30))
    whole = run(_args_for(file=[two_paths], no_sourcemap=True))
    cut_paths = {e["path"] for e in cut["endpoints"]}
    whole_paths = {e["path"] for e in whole["endpoints"]}
    cut_read = [e for e in cut["fetch_log"] if e.get("kind") == "read"]
    check("a file cut at --max-bytes says TRUNCATED; the same file read whole does not",
          cut_paths == {"/api/v1/early"}
          and whole_paths == {"/api/v1/early", "/api/v1/late"}
          and cut_read and cut_read[0]["truncated"] is True
          and "TRUNCATED at --max-bytes 30" in cut_read[0]["note"]
          and cut["counts"]["inputs_truncated"] == 1
          and "1 were TRUNCATED" in cut["negatives"][-1]
          and "PARTIAL" in cut["verdict_line"]
          and whole["counts"]["inputs_truncated"] == 0
          and "PARTIAL" not in whole["verdict_line"],
          "cut=%s whole=%s note=%r"
          % (sorted(cut_paths), sorted(whole_paths),
             cut_read[0]["note"] if cut_read else None),
          {"cut": cut["negatives"][-1], "whole": whole["negatives"][-1]})

    # --- D2: the call-site line is a ratio of call sites, not of endpoints --- #
    # Three fetch() calls to ONE path, plus a call site that yields nothing, plus
    # three .open( calls that are not request sites at all. The numerator must be
    # 4 of 5 whatever --max-hits is, and --max-hits must still cap the listing:
    # that pair is what separates a real count from a display artefact.
    call_sites_js = os.path.join(tmp, "call-sites.js")
    with open(call_sites_js, "w", encoding="utf-8") as handle:
        handle.write('fetch("/api/v1/same");fetch("/api/v1/same");'
                     'fetch("/api/v1/same");'
                     'window.open();modal.open("x");db.open("readwrite");'
                     'x.open("DELETE","/api/v1/xhr");'
                     'var q="?";fetch(q);')
    cs_low = run(_args_for(file=[call_sites_js], no_sourcemap=True, max_hits=1))
    cs_high = run(_args_for(file=[call_sites_js], no_sourcemap=True, max_hits=10))
    same_low = [e for e in cs_low["endpoints"] if e["path"] == "/api/v1/same"][0]
    same_high = [e for e in cs_high["endpoints"] if e["path"] == "/api/v1/same"][0]
    check("the call-site ratio counts call sites and is unmoved by --max-hits",
          cs_low["negatives"][2] == cs_high["negatives"][2]
          and cs_low["negatives"][2].startswith(
              "4 of 5 fetch/axios/XHR call sites yielded a path")
          and cs_low["counts"]["call_sites_yielding_path"] == 4
          and cs_low["counts"]["call_sites"] == 5
          and cs_low["counts"]["open_calls_not_xhr"] == 3
          # the cap really is in force, and still does not reach the line
          and same_low["hit_count"] == 6 and len(same_low["hits"]) == 1
          and same_high["hit_count"] == 6 and len(same_high["hits"]) == 6,
          "max-hits 1: %s | max-hits 10: %s | hits listed 1/%d vs 10/%d"
          % (cs_low["negatives"][2], cs_high["negatives"][2],
             len(same_low["hits"]), len(same_high["hits"])),
          cs_low["counts"])

    check("a non-HTTP .open( is not counted as a request call site",
          cs_low["counts"]["call_sites_xhr_open"] == 1
          and cs_low["counts"]["open_calls_not_xhr"] == 3
          and "3 further .open( call(s) were not request sites"
              in cs_low["negatives"][2],
          "xhr_open=%d not_request=%d"
          % (cs_low["counts"]["call_sites_xhr_open"],
             cs_low["counts"]["open_calls_not_xhr"]),
          cs_low["negatives"][2])

    # --- D4: the realpath containment check, the only layer a symlink hits -- #
    # Every other rejection fires on the spelling of the path. A symlink planted
    # inside --out is legal spelling, so only resolving the target catches it.
    sym_out = os.path.join(tmp, "outSym")
    escape_target = os.path.join(tmp, "outSym-escape-target")
    os.makedirs(sym_out, exist_ok=True)
    os.makedirs(escape_target, exist_ok=True)
    os.symlink(escape_target, os.path.join(sym_out, "esc"))
    os.symlink(sym_out, os.path.join(sym_out, "selfl"))
    sym_map = os.path.join(tmp, "symlink.js.map")
    with open(sym_map, "w", encoding="utf-8") as handle:
        handle.write(_fixture_map(["esc/pwned.js", "selfl", "src/clean.js"],
                                  ["OWNED\n", "OWNED-SELF\n",
                                   "export const ok = 1;\n"],
                                  file_name="symlink.js"))
    rep_sym = run(_args_for(map=[sym_map], out=sym_out))
    sym_entry = rep_sym["sourcemaps"][0]
    sym_reasons = [r["reason"] for r in sym_entry["rejected"]]
    check("a symlink inside --out is caught by resolving the path, not its spelling",
          sym_entry["rejected_count"] == 2
          and "resolves-outside-out-dir" in sym_reasons
          and "resolves-to-out-dir-itself" in sym_reasons
          and not os.path.exists(os.path.join(escape_target, "pwned.js"))
          and os.listdir(escape_target) == []
          and sym_entry["written_count"] == 1
          and os.path.exists(os.path.join(sym_out, "src", "clean.js")),
          "rejected=%d reasons=%s escape_dir=%s written=%d"
          % (sym_entry["rejected_count"], sym_reasons,
             os.listdir(escape_target), sym_entry["written_count"]),
          sym_entry)

    # --- D5: valid JSON that is not a source map --------------------------- #
    # The HTML catch-all above dies in json.loads and never reaches this guard.
    # A 200 of well-formed JSON with no sources array does.
    nosrc_dir = os.path.join(tmp, "nosources")
    os.makedirs(nosrc_dir, exist_ok=True)
    nosrc_bundle = os.path.join(nosrc_dir, "n.js")
    with open(nosrc_bundle, "w", encoding="utf-8") as handle:
        handle.write(_fixture_bundle(True, map_ref="n.js.map"))
    with open(nosrc_bundle + ".map", "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"version": 3, "file": "n.js",
                                 "mappings": "AAAA", "names": []}))
    rep_nosrc = run(_args_for(file=[nosrc_bundle],
                              out=os.path.join(tmp, "outNS")))
    nosrc_notes = [a["note"] for a
                   in rep_nosrc["bundles"][0]["sourcemap"]["attempts"]]
    check("valid JSON with no sources array is refused as a map, by name",
          not rep_nosrc["bundles"][0]["sourcemap"]["found"]
          and any("no sources array (version=3)" in str(n) for n in nosrc_notes)
          and rep_nosrc["sourcemaps"] == []
          and "0 of 1 units carried a source map" in rep_nosrc["negatives"][0],
          "found=%s notes=%s"
          % (rep_nosrc["bundles"][0]["sourcemap"]["found"], nosrc_notes),
          rep_nosrc["bundles"][0]["sourcemap"])

    arr_map = os.path.join(tmp, "array.js.map")
    with open(arr_map, "w", encoding="utf-8") as handle:
        handle.write('[1, 2, 3]')
    rep_arr = run(_args_for(map=[arr_map]))
    check("a JSON array served as a map is refused, not indexed as an object",
          rep_arr["sourcemaps"] == []
          and any("JSON is a list, not an object" in str(e["note"])
                  for e in rep_arr["fetch_log"]),
          "; ".join(str(e["note"]) for e in rep_arr["fetch_log"]),
          rep_arr["fetch_log"])

    # --- D6: the documented exit code, asserted through main() -------------- #
    def main_exit(argv):
        """main() with stdout and stderr captured. -> (code, text)"""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            try:
                code = main(argv)
            except SystemExit as exc:                 # argparse.error
                code = exc.code
        return code, buf.getvalue()

    barren = os.path.join(tmp, "barren.js")
    with open(barren, "w", encoding="utf-8") as handle:
        handle.write("var a=1;var b=2;")
    code_full, text_full = main_exit(["--file", bundle_path, "--no-sourcemap",
                                      "--compact"])
    code_empty, text_empty = main_exit(["--file", barren, "--no-sourcemap",
                                        "--compact"])
    code_noargs, _ = main_exit([])
    try:
        parsed_full = json.loads(text_full)
        parsed_empty = json.loads(text_empty)
    except ValueError:
        parsed_full = parsed_empty = None
    check("main() exits 0 on a non-empty inventory, 1 on nothing, 2 with no input",
          code_full == 0 and code_empty == 1 and code_noargs == 2
          and parsed_full is not None
          and parsed_full["counts"]["endpoints"] > 0
          and parsed_empty["counts"]["endpoints"] == 0,
          "exit codes: inventory=%s empty=%s no-input=%s; endpoints %s vs %s"
          % (code_full, code_empty, code_noargs,
             parsed_full["counts"]["endpoints"] if parsed_full else None,
             parsed_empty["counts"]["endpoints"] if parsed_empty else None),
          {"stdout_is_json": parsed_full is not None})

    failures = [c["case"] for c in checks if not c["pass"]]
    # The fixture goes away unless it is wanted: this runs from the aggregate
    # offline test, and a temp tree left behind on every run is litter. A failure
    # keeps it, because that is when there is something to look at.
    kept = keep_fixture or bool(failures)
    if not kept:
        shutil.rmtree(tmp, ignore_errors=True)
    return {"mode": "bundle-miner-selftest",
            "tmpdir": tmp if kept else None,
            "fixture_kept": kept,
            "checks": checks, "total": len(checks), "failures": len(failures),
            "failed": failures,
            "verdict": "PASS" if not failures else "FAIL"}


# --------------------------------------------------------------------------- #
def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    src = parser.add_argument_group("input (at least one, or --selftest)")
    src.add_argument("--url", help="entry page; one level of <script src> is crawled")
    src.add_argument("--file", action="append", metavar="PATH",
                     help="a bundle already on disk (repeatable)")
    src.add_argument("--map", action="append", metavar="PATH",
                     help="a source map already on disk or at a URL (repeatable)")
    src.add_argument("-H", "--header", action="append", default=[],
                     metavar="K: V", help="extra request header")
    src.add_argument("--timeout", type=float, default=15.0)
    src.add_argument("--max-bytes", type=int, default=32 << 20)
    src.add_argument("--max-scripts", type=int, default=25,
                     help="cap on scripts fetched from --url (default 25)")
    src.add_argument("--html-parser", default="auto",
                     choices=("auto", "bs4", "regex"),
                     help="auto uses bs4 when importable, regex otherwise")

    out = parser.add_argument_group("source reconstruction")
    out.add_argument("--out", metavar="DIR",
                     help="write sourcesContent here; omit to mine in memory only")
    out.add_argument("--source-scheme", default="normalise",
                     choices=("normalise", "reject"),
                     help="normalise strips a bundler scheme (webpack://...) and "
                          "relies on the containment check; reject refuses any "
                          "scheme outright (default normalise)")
    out.add_argument("--skip-node-modules", action="store_true",
                     help="do not write or mine node_modules sources")
    out.add_argument("--no-sourcemap", action="store_true",
                     help="do not look for a map at all")
    out.add_argument("--no-sibling-guess", action="store_true",
                     help="only trust a sourceMappingURL comment")

    ext = parser.add_argument_group("extraction")
    ext.add_argument("--include-assets", action="store_true",
                     help="keep .js/.css/image paths in the endpoint inventory")
    ext.add_argument("--min-secret-len", type=int, default=24,
                     help="shortest string considered for the entropy rule")
    ext.add_argument("--min-entropy", type=float, default=3.6,
                     metavar="BITS", help="bits per character (default 3.6)")
    ext.add_argument("--show-secrets", action="store_true",
                     help="print candidate values in full instead of a preview")
    ext.add_argument("--secret-preview", type=int, default=40)
    ext.add_argument("--max-hits", type=int, default=3,
                     help="locations listed per finding; hit_count stays exact")
    ext.add_argument("--max-listed", type=int, default=60)
    ext.add_argument("--context", type=int, default=40,
                     help="characters of surrounding code kept with a hit")
    ext.add_argument("--lookahead", type=int, default=200,
                     help="characters searched after a call site for its method")

    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--verbose", action="store_true",
                        help="selftest: include each check's own output")
    parser.add_argument("--keep-fixture", action="store_true",
                        help="selftest: keep the temp fixture tree (a failing "
                             "run keeps it anyway)")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.selftest:
        out = selftest(verbose=args.verbose, keep_fixture=args.keep_fixture)
        httpkit.jprint(out, args.compact)
        return 0 if out["verdict"] == "PASS" else 1

    if not (args.url or args.file or args.map):
        parser.error("give --url, --file or --map (or --selftest)")
    if args.out:
        try:
            os.makedirs(args.out, exist_ok=True)
        except OSError as exc:
            parser.error("--out %s: %s" % (args.out, exc))

    report = run(args)
    httpkit.jprint(report, args.compact)
    # 0 when the inventory is non-empty, 1 when the run produced nothing: a
    # bundle with no readable strings and no map is the documented falsifier for
    # this route, and the exit code should say so.
    return 0 if report["counts"]["endpoints"] else 1


if __name__ == "__main__":
    sys.exit(main())
