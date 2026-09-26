#!/usr/bin/env python3
"""Differential grammar sweep against a sanitizer, a parser pair, or a live endpoint.

The question this answers is always the same: *can any encoding of a forbidden
byte survive this filter?* And, just as important, *if none can, how many cases
proved it?* A sweep that finds nothing is only worth recording when it can be
written down as "0 of N", so the case count is a first-class output.

Targets
  --callable  module:function or path/to/file.py:function   (a local sanitizer)
  --url       a live endpoint, with --template carrying {payload}
  --diff      a second callable; every output difference is reported

Grammar families, all generated deterministically - nothing here calls random:
  raw          the forbidden item itself, the control case
  entity       decimal / hex / padded / semicolon-less / double-encoded refs,
               named refs, percent- and backslash-escapes, whole item and one
               character at a time
  splice       nested-token splices that reassemble the filtered word after one
               removal pass, plus filler and tag splices
  unicode      case folding, Turkish dotless i, fullwidth and other NFKC
               compatibility lookalikes, homoglyphs
  zerowidth    zero-width, bidi and control characters spliced between bytes
  wrapper      each of the above placed inside a tag, comment, CDATA section,
               processing instruction, doctype, raw-text element, foreign-content
               element or attribute value; --nest 2 wraps twice

Verdict
  bypass-found  at least one output still holds a forbidden item
  clean         0 of N - a recordable negative result
  divergent     the two callables disagree

A clean verdict is evidence about THIS grammar, not a proof of safety. Feed the
`record_as` line to tools/hooks.py post-probe; a clean sweep is `inconclusive`
for the class, never a confirm.

CLI:
    python3 tools/web/sanitizer_fuzz.py --selftest
    python3 tools/web/sanitizer_fuzz.py --callable app/filters.py:clean \
        --forbidden script --forbidden '<' --diff app/filters.py:escape
    python3 tools/web/sanitizer_fuzz.py --url http://host/preview \
        --method POST --template 'html={payload}' --forbidden '<script' \
        --max-cases 200 --delay 0.05
"""
import argparse
import html as html_mod
import importlib
import importlib.util
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse

try:
    from . import httpkit
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import httpkit

FAMILIES = ("raw", "entity", "splice", "unicode", "zerowidth", "wrapper")
LIVE_DEFAULT_MAX = 300


# --------------------------------------------------------------------------- #
# grammar: character-level encodings
# --------------------------------------------------------------------------- #
ENTITY_SCHEMES = (
    ("dec", lambda o: "&#%d;" % o),
    ("dec-nosemi", lambda o: "&#%d" % o),
    ("dec-pad", lambda o: "&#%07d;" % o),
    ("hex-lower", lambda o: "&#x%x;" % o),
    ("hex-upper", lambda o: "&#X%X;" % o),
    ("hex-nosemi", lambda o: "&#x%x" % o),
    ("hex-pad", lambda o: "&#x%08x;" % o),
    ("dec-double", lambda o: "&amp;#%d;" % o),
    ("hex-double", lambda o: "&amp;#x%x;" % o),
    ("dec-via-amp", lambda o: "&#38;#%d;" % o),
    ("pct", lambda o: "%%%02X" % o if o < 0x100 else "%%u%04X" % o),
    ("pct-double", lambda o: "%%25%02X" % o if o < 0x100 else None),
    ("pct-overlong", lambda o: "%%C0%%%02X" % (0x80 | (o & 0x3F)) if o < 0x80 else None),
    ("js-unicode", lambda o: "\\u%04x" % o),
    ("js-unicode-brace", lambda o: "\\u{%x}" % o),
    ("js-hex", lambda o: "\\x%02x" % o if o < 0x100 else None),
    ("css-hex", lambda o: "\\%x " % o),
    ("octal", lambda o: "\\%o" % o),
    ("xml-hex-ncr", lambda o: "&#x%02X;" % o),
)

NAMED_REFS = {
    "<": ("&lt;", "&LT;", "&lt", "&Lt;", "&amp;lt;"),
    ">": ("&gt;", "&GT;", "&gt", "&amp;gt;"),
    "&": ("&amp;", "&AMP;", "&amp", "&amp;amp;"),
    '"': ("&quot;", "&QUOT;", "&quot", "&ldquo;"),
    "'": ("&apos;", "&#39;", "&apos", "&sbquo;"),
    " ": ("&nbsp;", "&#32;", "&Tab;", "&NewLine;"),
    "/": ("&sol;", "&#47;"),
    "=": ("&equals;", "&#61;"),
    ":": ("&colon;", "&#58;"),
}

# Every non-ASCII character in this file is written as a codepoint, not as the
# character itself: a homoglyph table written literally is unreadable in a diff,
# indistinguishable from the ASCII it imitates, and trips the repository's
# foreign-script gate in test/regression.py.
ZERO_WIDTH_POINTS = (
    ("zwsp", 0x200B), ("zwnj", 0x200C), ("zwj", 0x200D),
    ("bom", 0xFEFF), ("shy", 0x00AD), ("lrm", 0x200E),
    ("rlo", 0x202E), ("wordjoiner", 0x2060), ("mongolian-vs", 0x180E),
    ("nul", 0x00), ("soh", 0x01), ("tab", 0x09), ("lf", 0x0A),
    ("vt", 0x0B), ("ff", 0x0C), ("cr", 0x0D), ("sub", 0x1A),
    ("esc", 0x1B), ("del", 0x7F),
)
ZERO_WIDTH = tuple((name, chr(point)) for name, point in ZERO_WIDTH_POINTS)

# Lookalikes that survive a naive filter but collapse under casefold() or NFKC
# normalisation - the two operations a framework is most likely to apply after
# the filter has already run. A tuple of points is one multi-codepoint sequence.
LOOKALIKE_POINTS = {
    "s": (0x017F, 0x0455),              # long s casefolds to s; cyrillic dze
    "k": (0x212A,),                     # kelvin sign, NFKC -> K
    "i": (0x0131, 0x0130, 0x2170, (0x0069, 0x0307)),   # dotless i, dotted I,
    "a": (0x0430, 0x0251),              # roman numeral one, i + combining dot
    "e": (0x0435, 0x212F),
    "o": (0x043E, 0x2134),
    "c": (0x0441, 0x217D),
    "p": (0x0440,),
    "x": (0x0445, 0x2179),
    "l": (0x217C, 0x2113),
    "n": (0x0578,),
    "t": (0x0442,),
    "r": (0x0433,),
    "g": (0x0261,),
    "<": (0x2039, 0x276E, 0x3008),
    ">": (0x203A, 0x276F, 0x3009),
    "/": (0x2215, 0x29F8),
    '"': (0x201C, 0x2033),
    "'": (0x2018, 0x02B9),
}


def _points_to_text(points):
    if isinstance(points, int):
        points = (points,)
    return "".join(chr(point) for point in points)


EXTRA_LOOKALIKE = {ch: tuple(_points_to_text(entry) for entry in entries)
                   for ch, entries in LOOKALIKE_POINTS.items()}

FILLERS = ("", "\x00", "%00", "&#0;", "/*/*/", "<>", "\\", "\t", "\n",
           "&NewLine;", "</>", "<!---->", chr(0x200B))

WRAPPERS = (
    ("tag-b", "<b>%s</b>"),
    ("tag-span", "<span>%s</span>"),
    ("tag-a", "<a href=x>%s</a>"),
    ("tag-unclosed", "<b %s"),
    ("tag-bogus", "<%s>"),
    ("comment", "<!--%s-->"),
    ("comment-spaced", "<!-- %s -->"),
    ("comment-conditional", "<!--[if IE]>%s<![endif]-->"),
    ("comment-bogus", "<!%s>"),
    ("cdata", "<![CDATA[%s]]>"),
    ("cdata-svg", "<svg><![CDATA[%s]]></svg>"),
    ("pi-xml", "<?xml %s ?>"),
    ("pi-php", "<?php %s ?>"),
    ("pi-bare", "<?%s>"),
    ("doctype", "<!DOCTYPE %s>"),
    ("entity-decl", "<!ENTITY x \"%s\">"),
    ("rawtext-textarea", "<textarea>%s</textarea>"),
    ("rawtext-title", "<title>%s</title>"),
    ("rawtext-style", "<style>%s</style>"),
    ("rawtext-script", "<script>%s</script>"),
    ("rawtext-noscript", "<noscript>%s</noscript>"),
    ("rawtext-xmp", "<xmp>%s</xmp>"),
    ("rawtext-noembed", "<noembed>%s</noembed>"),
    ("rawtext-iframe", "<iframe>%s</iframe>"),
    ("rawtext-plaintext", "<plaintext>%s"),
    ("foreign-svg", "<svg>%s</svg>"),
    ("foreign-svg-desc", "<svg><desc>%s</desc></svg>"),
    ("foreign-math", "<math><mtext>%s</mtext></math>"),
    ("foreign-svg-foreignobject", "<svg><foreignObject>%s</foreignObject></svg>"),
    ("attr-double", "<img src=x alt=\"%s\">"),
    ("attr-single", "<div data-x='%s'>"),
    ("attr-bare", "<div data-x=%s>"),
    ("table-misnest", "<table><td>%s</td></table>"),
    ("select-misnest", "<select><option>%s</option></select>"),
)
# second wrapping layer: the parser-confusion pairs, kept small so the sweep
# does not explode into a number nobody will wait for
NEST_WRAPPERS = ("comment", "cdata", "rawtext-textarea", "rawtext-title",
                 "foreign-svg", "attr-double", "pi-xml", "doctype")


def _fullwidth(ch):
    point = ord(ch)
    if 0x21 <= point <= 0x7E:
        return chr(0xFF00 + point - 0x20)
    if ch == " ":
        return chr(0x3000)               # ideographic space
    return None


def entity_variants(item):
    """Every character-reference / escape encoding, whole item and per position."""
    for name, fn in ENTITY_SCHEMES:
        whole = []
        for ch in item:
            piece = fn(ord(ch))
            if piece is None:
                whole = None
                break
            whole.append(piece)
        if whole is not None:
            yield "entity:%s:all" % name, "".join(whole)
        for index, ch in enumerate(item):
            piece = fn(ord(ch))
            if piece is None:
                continue
            yield ("entity:%s:pos%d" % (name, index),
                   item[:index] + piece + item[index + 1:])
    for index, ch in enumerate(item):
        for ref in NAMED_REFS.get(ch, ()):
            yield ("entity:named:pos%d" % index,
                   item[:index] + ref + item[index + 1:])
    # every character named at once, when every character has a name
    if item and all(ch in NAMED_REFS for ch in item):
        yield "entity:named:all", "".join(NAMED_REFS[ch][0] for ch in item)


def splice_variants(item):
    """Tokens that reassemble `item` after exactly one removal pass."""
    if len(item) >= 2:
        for cut in range(1, len(item)):
            # remove the inner copy once and item is back
            yield "splice:reassemble:%d" % cut, item[:cut] + item + item[cut:]
            # the tag form: <scr<script>ipt>
            yield ("splice:tag-reassemble:%d" % cut,
                   "<" + item[:cut] + "<" + item + ">" + item[cut:] + ">")
            for filler in FILLERS:
                yield ("splice:filler:%d:%r" % (cut, filler),
                       item[:cut] + filler + item[cut:])
    yield "splice:double", item + item
    yield "splice:overlap", item + item[:-1] if len(item) > 1 else item + item
    yield "splice:reversed-pair", item[::-1] + item
    yield "splice:nested-brackets", "<" + item + "<" + item + ">"
    yield "splice:trailing-slash", item + "/" + item


def unicode_variants(item):
    """Case folding and NFKC compatibility lookalikes."""
    for name, fn in (("upper", str.upper), ("lower", str.lower),
                     ("title", str.title), ("swapcase", str.swapcase),
                     ("casefold", str.casefold)):
        out = fn(item)
        if out != item:
            yield "unicode:case:%s" % name, out
    # alternating case, both phases - deterministic, no random
    for phase in (0, 1):
        out = "".join(ch.upper() if (index % 2 == phase) else ch.lower()
                      for index, ch in enumerate(item))
        if out != item:
            yield "unicode:case:alternating%d" % phase, out
    for form in ("NFD", "NFKD", "NFC", "NFKC"):
        out = unicodedata.normalize(form, item)
        if out != item:
            yield "unicode:normalize:%s" % form, out
    full = [_fullwidth(ch) for ch in item]
    if all(full):
        yield "unicode:fullwidth:all", "".join(full)
    for index, ch in enumerate(item):
        wide = _fullwidth(ch)
        if wide:
            yield "unicode:fullwidth:pos%d" % index, item[:index] + wide + item[index + 1:]
        for alt in EXTRA_LOOKALIKE.get(ch.lower(), ()):
            yield ("unicode:lookalike:pos%d" % index,
                   item[:index] + alt + item[index + 1:])
    # every character replaced by its first lookalike, when all have one
    alts = [EXTRA_LOOKALIKE.get(ch.lower(), (None,))[0] for ch in item]
    if all(alts):
        yield "unicode:lookalike:all", "".join(alts)


def zerowidth_variants(item):
    """Zero-width, bidi and control characters spliced between the bytes."""
    for name, char in ZERO_WIDTH:
        for index in range(len(item) + 1):
            yield ("zerowidth:%s:pos%d" % (name, index),
                   item[:index] + char + item[index:])
        if len(item) > 1:
            yield "zerowidth:%s:every" % name, char.join(item)


CORE_GENERATORS = {"entity": entity_variants, "splice": splice_variants,
                   "unicode": unicode_variants, "zerowidth": zerowidth_variants}


def generate_cases(items, families=FAMILIES, nest=1):
    """Deterministic, de-duplicated list of (family, case) for the whole grammar."""
    seen = {}
    order = []

    def add(family, text):
        if text in seen:
            return
        seen[text] = family
        order.append((family, text))

    core = []
    for item in items:
        if "raw" in families:
            add("raw", item)
            core.append(("raw", item))
        for name, generator in CORE_GENERATORS.items():
            if name not in families:
                continue
            for family, text in generator(item):
                add(family, text)
                core.append((family, text))
    if "wrapper" in families:
        wrappers = list(WRAPPERS)
        for family, text in core:
            for wname, pattern in wrappers:
                add("wrapper:%s+%s" % (wname, family), pattern % text)
        if nest >= 2:
            inner = [(w, p) for w, p in wrappers if w in NEST_WRAPPERS]
            for family, text in core:
                for w1, p1 in inner:
                    once = p1 % text
                    for w2, p2 in inner:
                        if w2 == w1:
                            continue
                        add("wrapper:%s+%s+%s" % (w2, w1, family), p2 % once)
    return order


# --------------------------------------------------------------------------- #
# forbidden-item detection
# --------------------------------------------------------------------------- #
def check_output(text, items, decoded=False):
    """Return the list of hits: [{'item','check','index'}]. Empty means clean."""
    hits = []
    if text is None:
        return hits
    lowered = text.lower()
    variants = [("raw", text)]
    if decoded:
        try:
            unescaped = html_mod.unescape(text)
        except Exception:
            unescaped = text
        variants.append(("entity-decoded", unescaped))
        variants.append(("nfkc", unicodedata.normalize("NFKC", text)))
        variants.append(("casefold", text.casefold()))
        variants.append(("unquoted", urllib.parse.unquote(text)))
    for item in items:
        index = text.find(item)
        if index >= 0:
            hits.append({"item": item, "check": "raw", "index": index})
            continue
        index = lowered.find(item.lower())
        if index >= 0:
            hits.append({"item": item, "check": "case-insensitive", "index": index})
            continue
        for label, candidate in variants[1:]:
            index = candidate.lower().find(item.lower())
            if index >= 0:
                hits.append({"item": item, "check": label, "index": index})
                break
    return hits


# --------------------------------------------------------------------------- #
# targets
# --------------------------------------------------------------------------- #
def load_callable(spec):
    """'pkg.mod:fn' or '/path/to/file.py:fn' -> the callable. Raises ValueError."""
    if ":" not in spec:
        raise ValueError("callable spec must be module:function or path.py:function")
    where, _, funcname = spec.rpartition(":")
    if not where:
        module = sys.modules[__name__]
    elif where.endswith(".py") or os.sep in where:
        path = os.path.abspath(where)
        if not os.path.exists(path):
            raise ValueError("no such file: %s" % path)
        name = "sanfuzz_" + re.sub(r"\W", "_", path)
        loader = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(loader)
        sys.modules[name] = module
        loader.loader.exec_module(module)
    else:
        sys.path.insert(0, os.getcwd())
        module = importlib.import_module(where)
    fn = getattr(module, funcname, None)
    if not callable(fn):
        raise ValueError("%s has no callable %s" % (where or __name__, funcname))
    return fn


def run_local(fn, case):
    try:
        out = fn(case)
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)
    if isinstance(out, bytes):
        out = out.decode("utf-8", "replace")
    elif not isinstance(out, str):
        out = str(out)
    return out, None


def run_live(case, url, template=None, method="GET", headers=None, timeout=10,
             urlencode=False, field="payload"):
    value = urllib.parse.quote(case, safe="") if urlencode else case
    target = httpkit.fill(url, **{field: value})
    body = httpkit.fill(template, **{field: value}) if template else None
    hdrs = dict(headers or {})
    if body is not None and method.upper() != "GET" and "Content-Type" not in hdrs:
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    resp = httpkit.request(target, method=method, headers=hdrs, body=body,
                           timeout=timeout)
    if not resp.get("ok"):
        return None, resp.get("error") or "transport failure", resp
    return resp.get("body", ""), None, resp


# --------------------------------------------------------------------------- #
# the sweep
# --------------------------------------------------------------------------- #
def sweep(items, callable_spec=None, diff_spec=None, url=None, template=None,
          method="GET", headers=None, timeout=10, urlencode=False, field="payload",
          families=FAMILIES, nest=1, max_cases=0, delay=0.0, decoded=False,
          max_report=40, max_excerpt=240):
    """Run the whole grammar against one target. Returns a JSON-ready dict."""
    if not items:
        return {"mode": "sanitizer-fuzz", "error": "no --forbidden items given"}
    if not callable_spec and not url:
        return {"mode": "sanitizer-fuzz", "error": "give --callable or --url"}

    primary = secondary = None
    if callable_spec:
        try:
            primary = load_callable(callable_spec)
        except Exception as exc:
            return {"mode": "sanitizer-fuzz",
                    "error": "could not load --callable: %s" % exc}
    if diff_spec:
        try:
            secondary = load_callable(diff_spec)
        except Exception as exc:
            return {"mode": "sanitizer-fuzz",
                    "error": "could not load --diff: %s" % exc}

    cases = generate_cases(items, families=families, nest=nest)
    generated = len(cases)
    capped = None
    limit = max_cases
    if url and not limit:
        limit = LIVE_DEFAULT_MAX
    if limit and generated > limit:
        cases = cases[:limit]
        capped = {"generated": generated, "run": len(cases),
                  "note": "capped by --max-cases; the 0-of-N claim covers only "
                          "the cases actually run"}

    findings, divergences, errors = [], [], []
    family_stats = {}
    started = time.monotonic()
    for family, case in cases:
        bucket = family.split(":")[0]
        stat = family_stats.setdefault(bucket, {"cases": 0, "hits": 0,
                                                "divergences": 0, "errors": 0})
        stat["cases"] += 1
        extra = {}
        if primary is not None:
            out, err = run_local(primary, case)
        else:
            out, err, resp = run_live(case, url, template, method, headers,
                                      timeout, urlencode, field)
            extra = {"status": resp.get("status"), "elapsed": resp.get("elapsed")}
            if delay:
                time.sleep(delay)
        if err is not None:
            stat["errors"] += 1
            if len(errors) < max_report:
                errors.append({"family": family, "case": _clip(case, max_excerpt),
                               "error": err})
            continue
        hits = check_output(out, items, decoded=decoded)
        if hits:
            stat["hits"] += 1
            if len(findings) < max_report:
                record = {"family": family, "case": _clip(case, max_excerpt),
                          "case_repr": repr(case)[:max_excerpt],
                          "output": _clip(out, max_excerpt), "hits": hits}
                record.update(extra)
                findings.append(record)
        if secondary is not None:
            other, other_err = run_local(secondary, case)
            if other_err is not None:
                stat["errors"] += 1
            elif other != out:
                stat["divergences"] += 1
                if len(divergences) < max_report:
                    divergences.append({
                        "family": family, "case": _clip(case, max_excerpt),
                        "case_repr": repr(case)[:max_excerpt],
                        "primary": _clip(out, max_excerpt),
                        "diff": _clip(other, max_excerpt)})

    total_hits = sum(s["hits"] for s in family_stats.values())
    total_div = sum(s["divergences"] for s in family_stats.values())
    total_err = sum(s["errors"] for s in family_stats.values())
    ran = len(cases)
    verdict = "bypass-found" if total_hits else ("divergent" if total_div else "clean")
    result = {
        "mode": "sanitizer-fuzz",
        "target": ({"kind": "callable", "spec": callable_spec} if primary is not None
                   else {"kind": "live", "url": url, "method": method.upper(),
                         "template": template}),
        "diff_target": {"kind": "callable", "spec": diff_spec} if secondary else None,
        "forbidden": list(items),
        "checks": (["raw", "case-insensitive", "entity-decoded", "nfkc",
                    "casefold", "unquoted"] if decoded
                   else ["raw", "case-insensitive"]),
        "families_requested": list(families),
        "nest": nest,
        "total_cases": ran,
        "cases_generated": generated,
        "capped": capped,
        "hits": total_hits,
        "divergences": total_div,
        "errors": total_err,
        "elapsed": round(time.monotonic() - started, 3),
        "by_family": family_stats,
        "findings": findings,
        "divergent_cases": divergences,
        "error_cases": errors,
        "verdict": verdict,
        "summary": "%d of %d cases left a forbidden item in the output" % (total_hits, ran),
        "record_as": _record_as(verdict, total_hits, total_div, ran, items),
        "reporting": {"max_report": max_report,
                      "findings_truncated": total_hits > len(findings),
                      "divergences_truncated": total_div > len(divergences)},
        "discipline": [
            "A clean sweep is a negative result about THIS grammar, not a proof "
            "of safety: submit it to tools/hooks.py post-probe as inconclusive.",
            "A hit is a filter bypass, not yet impact: the class is confirmed only "
            "when the surviving item reaches a sink.",
            "--url with a write method is a write-shaped probe: clear "
            "tools/hooks.py pre-probe --write-ack first and read the chain card's "
            "blast_radius.",
            "The decoded checks (--check-decoded) flag output that a LATER decoder "
            "would turn back into the forbidden item; against a correctly escaping "
            "sanitizer they are expected false positives.",
        ],
    }
    return result


def _clip(text, limit):
    if text is None:
        return None
    return text if len(text) <= limit else text[:limit] + "...[+%d]" % (len(text) - limit)


def _record_as(verdict, hits, divergences, ran, items):
    if verdict == "bypass-found":
        return ("verdict=confirms candidate: %d of %d grammar cases kept a "
                "forbidden item (%s) in the output; quote one finding's output as "
                "--evidence" % (hits, ran, ", ".join(items)))
    if verdict == "divergent":
        return ("verdict=inconclusive: 0 of %d cases kept a forbidden item, but "
                "the two callables disagree on %d cases - a parser differential "
                "to chase, not yet a bypass" % (ran, divergences))
    return ("verdict=inconclusive: 0 of %d grammar cases kept a forbidden item "
            "(%s); record the count and change mechanism layer rather than "
            "inventing a %d-th payload variant" % (ran, ", ".join(items), ran + 1))


# --------------------------------------------------------------------------- #
# inline test fixtures: two deliberately different sanitizers
# --------------------------------------------------------------------------- #
def demo_strip_once(value):
    """A realistic-looking bad filter: one removal pass over a blocklist."""
    return re.sub(r"(?i)<\s*/?\s*script[^>]*>|script|javascript:|onerror", "", value)


def demo_escape(value):
    """A correct filter: escape, do not strip."""
    return html_mod.escape(value, quote=True)


def demo_normalize_then_strip(value):
    """The classic order-of-operations bug: normalise AFTER filtering."""
    return unicodedata.normalize("NFKC", demo_strip_once(value)).casefold()


def selftest(nest=1):
    """Three sweeps: a filter that must fail, one that must be clean, and a diff."""
    here = os.path.abspath(__file__)
    checks = []

    bad = sweep(["script"], callable_spec="%s:demo_strip_once" % here, nest=nest)
    checks.append({"name": "strip-once filter is bypassed",
                   "expect": "bypass-found", "got": bad["verdict"],
                   "total_cases": bad["total_cases"], "hits": bad["hits"],
                   "pass": bad["verdict"] == "bypass-found" and bad["hits"] > 0,
                   "example": bad["findings"][0] if bad["findings"] else None})

    # html.escape neutralises the metacharacters, so a sweep for them must come
    # back 0-of-N. It does NOT remove the WORD "script" - forbidding that here
    # would be a wrong expectation, not a harness failure.
    good = sweep(["<", ">", '"'], callable_spec="%s:demo_escape" % here, nest=nest)
    checks.append({"name": "html.escape leaves no raw metacharacter (0 of N)",
                   "expect": "clean", "got": good["verdict"],
                   "total_cases": good["total_cases"], "hits": good["hits"],
                   "pass": good["verdict"] == "clean" and good["hits"] == 0,
                   "summary": good["summary"], "record_as": good["record_as"]})

    # the same correct filter, swept for a blocked WORD, must report hits: a
    # filter that escapes is not a filter that removes, and the harness has to
    # say so rather than flatter it
    word = sweep(["script"], callable_spec="%s:demo_escape" % here, nest=nest)
    checks.append({"name": "escaping does not remove a blocked word",
                   "expect": "bypass-found", "got": word["verdict"],
                   "total_cases": word["total_cases"], "hits": word["hits"],
                   "pass": word["hits"] > 0})

    norm = sweep(["script"], callable_spec="%s:demo_normalize_then_strip" % here,
                 nest=nest)
    checks.append({"name": "normalise-after-filter reintroduces the word",
                   "expect": "bypass-found", "got": norm["verdict"],
                   "total_cases": norm["total_cases"], "hits": norm["hits"],
                   "pass": norm["hits"] > 0,
                   "example": norm["findings"][0] if norm["findings"] else None})

    diff = sweep(["<"], callable_spec="%s:demo_escape" % here,
                 diff_spec="%s:demo_strip_once" % here, nest=nest)
    checks.append({"name": "diff mode reports the two filters disagreeing",
                   "expect": "divergences > 0", "got": diff["divergences"],
                   "total_cases": diff["total_cases"],
                   "pass": diff["divergences"] > 0,
                   "example": diff["divergent_cases"][0] if diff["divergent_cases"] else None})

    determinism = (generate_cases(["script"]) == generate_cases(["script"]))
    checks.append({"name": "grammar generation is deterministic",
                   "expect": True, "got": determinism, "pass": determinism})

    failures = [c["name"] for c in checks if not c["pass"]]
    return {"mode": "sanitizer-fuzz-selftest", "checks": checks,
            "total": len(checks), "failures": len(failures),
            "failed": failures, "verdict": "PASS" if not failures else "FAIL"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Differential grammar sweep against a sanitizer or endpoint; "
                    "reports every surviving forbidden item and the total case "
                    "count, so a clean run is recordable as '0 of N'.")
    parser.add_argument("--forbidden", action="append", default=[], metavar="ITEM",
                        help="byte or substring that must not survive (repeatable)")
    parser.add_argument("--callable", dest="call", metavar="module:function",
                        help="local sanitizer; module:function or path.py:function")
    parser.add_argument("--diff", metavar="module:function",
                        help="second callable; every output difference is reported")
    parser.add_argument("--url", help="live endpoint; may contain {payload}")
    parser.add_argument("--template", help="request body containing {payload}")
    parser.add_argument("--method", default="GET")
    parser.add_argument("-H", "--header", action="append", default=[])
    parser.add_argument("--field", default="payload",
                        help="placeholder name in --url/--template (default payload)")
    parser.add_argument("--urlencode", action="store_true",
                        help="percent-encode each case before substitution")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--delay", type=float, default=0.0,
                        help="seconds between live requests")
    parser.add_argument("--families", default=",".join(FAMILIES),
                        help="comma-separated subset of: " + ",".join(FAMILIES))
    parser.add_argument("--nest", type=int, default=1, choices=(1, 2),
                        help="2 wraps each core variant twice (much larger sweep)")
    parser.add_argument("--max-cases", type=int, default=0,
                        help="cap the sweep; 0 = all (live mode defaults to %d)"
                             % LIVE_DEFAULT_MAX)
    parser.add_argument("--check-decoded", action="store_true",
                        help="also flag output that a later decoder would turn "
                             "back into a forbidden item")
    parser.add_argument("--max-report", type=int, default=40,
                        help="how many findings/divergences to list (counts are exact)")
    parser.add_argument("--count-only", action="store_true",
                        help="generate the grammar and report the case count only")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        out = selftest(nest=args.nest)
        httpkit.jprint(out, compact=args.compact)
        return 0 if out["verdict"] == "PASS" else 1

    families = tuple(f.strip() for f in args.families.split(",") if f.strip())
    unknown = [f for f in families if f not in FAMILIES]
    if unknown:
        parser.error("unknown families: %s (known: %s)"
                     % (", ".join(unknown), ", ".join(FAMILIES)))

    if args.count_only:
        cases = generate_cases(args.forbidden or ["script"], families=families,
                               nest=args.nest)
        buckets = {}
        for family, _ in cases:
            buckets[family.split(":")[0]] = buckets.get(family.split(":")[0], 0) + 1
        httpkit.jprint({"mode": "sanitizer-fuzz-count",
                        "forbidden": args.forbidden or ["script"],
                        "families": list(families), "nest": args.nest,
                        "total_cases": len(cases), "by_family": buckets},
                       compact=args.compact)
        return 0

    out = sweep(args.forbidden, callable_spec=args.call, diff_spec=args.diff,
                url=args.url, template=args.template, method=args.method,
                headers=httpkit.parse_headers(args.header), timeout=args.timeout,
                urlencode=args.urlencode, field=args.field, families=families,
                nest=args.nest, max_cases=args.max_cases, delay=args.delay,
                decoded=args.check_decoded, max_report=args.max_report)
    httpkit.jprint(out, compact=args.compact)
    if "error" in out:
        return 2
    return 1 if out["verdict"] == "bypass-found" else 0


if __name__ == "__main__":
    sys.exit(main())
