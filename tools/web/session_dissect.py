#!/usr/bin/env python3
"""Name a session token's format, decode what opens without the key, and name the standard weakness with its next command.

`web-auth-session` is verified in this tree by three chain cards, and every one
of them opened with the same twenty minutes of hand work: base64 the first part,
squint at it, remember whether itsdangerous puts the timestamp before or after
the payload, count the signature bytes against the declared alg, look up which
salt Flask uses. The locktalk card has "decode the ticket" as a literal numbered
step. That is the twenty minutes this replaces -- one command that says what the
token is, what evidence decided it, what decodes without the key, and which
standard weakness the shape admits, each with the exact next command.

BOUNDARY, deliberate and not configurable: this tool ANALYSES. It never forges a
token and it never sends one. The only request it may make is a single GET with
--url, to read a fresh Set-Cookie; everything after that is local computation
over bytes you already hold, and --try-keys is offline HMAC over a wordlist with
no requests at all. The forge is a separate step you run yourself, and the report
hands you the command for it -- so that the decision to send a forged token is
always yours and always recorded through tools/hooks.py.

Every construction below was verified against the installed library on this box
before it was written down, not recalled: Flask's salt/derivation/digest out of
flask.sessions.SecureCookieSessionInterface, Django's out of
django.core.signing.dumps and django.utils.crypto.salted_hmac, Fernet's framing
out of cryptography.fernet, the express base64 detail cross-checked against node's
own crypto. What could NOT be verified here is labelled as unverified rather than
asserted, and Rails key recovery is refused outright with the reason.

    python3 tools/web/session_dissect.py --selftest
    python3 tools/web/session_dissect.py --token eyJhbGciOiJIUzI1NiJ9.eyJhIjoxfQ.xxx
    python3 tools/web/session_dissect.py --cookie 'session=.eJwr...; csrf=abc'
    python3 tools/web/session_dissect.py --url http://target/login
    python3 tools/web/session_dissect.py --token "$T" --try-keys \
        --wordlist /home/kali/wordlists/SecLists/Passwords/Common-Credentials/10k-most-common.txt
"""
import argparse
import base64
import binascii
import calendar
import datetime
import hashlib
import hmac
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.parse
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import httpkit  # noqa: E402

# PyJWT is present on this box but the decode path must not depend on it: a
# challenge container is not this box. It is used when importable and the report
# always says which path actually ran, so a claim can be traced to a decoder.
try:
    import jwt as pyjwt
except ImportError:                                   # pragma: no cover - guarded
    pyjwt = None

EPOCH_2010 = calendar.timegm((2010, 1, 1, 0, 0, 0))   # floor for "plausible epoch"
B64URL_RE = re.compile(r"^[A-Za-z0-9_-]*={0,2}$")
HEX_RE = re.compile(r"^(?:[0-9a-fA-F]{2})+$")
COOKIE_NAME_RE = re.compile(r"^[A-Za-z0-9!#$%&'*+\-.^_`|~]{1,64}$")
# RFC 6265 attribute names, so a Set-Cookie's own attributes are never dissected
# as if they were sibling cookies.
COOKIE_ATTRS = {"expires", "max-age", "domain", "path", "secure", "httponly",
                "samesite", "priority", "partitioned"}

# Signature sizes are fixed by the algorithm for everything except RSA, where the
# signature is exactly the modulus. That asymmetry is the point of the check: a
# 32-byte signature under a declared RS256 is not a long-key mistake, it is a
# different algorithm wearing RS256's name.
ALG_SIG_BYTES = {"none": 0, "HS256": 32, "HS384": 48, "HS512": 64,
                 "ES256": 64, "ES384": 96, "ES512": 132, "EdDSA": 64}
RSA_ALGS = ("RS256", "RS384", "RS512", "PS256", "PS384", "PS512")
HMAC_ALGS = {"HS256": hashlib.sha256, "HS384": hashlib.sha384,
             "HS512": hashlib.sha512}
DIGEST_BY_LEN = {16: "md5", 20: "sha1", 28: "sha224", 32: "sha256",
                 48: "sha384", 64: "sha512"}
# Header parameters that tell the verifier where to FETCH a key. Each one is an
# input to the signature check, which is why they are listed separately from the
# claims: RFC 7515 sections 4.1.2 (jku), 4.1.3 (jwk), 4.1.4 (kid), 4.1.5 (x5u).
KEY_SOURCING_HEADERS = ("kid", "jku", "jwk", "x5u", "x5c", "x5t")
PRIVILEGE_CLAIMS = ("role", "roles", "admin", "is_admin", "isAdmin", "isadmin",
                    "group", "groups", "scope", "scopes", "permissions", "perms",
                    "type", "user_type", "level", "priv", "is_staff", "acct_type")
IDENTITY_CLAIMS = ("sub", "user", "username", "user_id", "uid", "id", "email",
                   "name", "account", "login")
TIME_CLAIMS = ("exp", "nbf", "iat", "auth_time", "updated_at")

# Salts measured out of the installed Django: django.core.signing.dumps defaults
# to "django.core.signing", the signed_cookies session backend passes its own.
DJANGO_SALTS = ("django.core.signing",
                "django.contrib.sessions.backends.signed_cookies",
                "django.core.signing.TimestampSigner",
                "django.core.signing.Signer")
DJANGO_B62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
# itsdangerous supports four derivations; Flask selects "hmac", a bare
# URLSafeTimedSerializer defaults to "django-concat". Both are tried.
ITSDANGEROUS_DERIVATIONS = ("hmac", "django-concat", "concat", "none")
FLASK_SALT = "cookie-session"
MAX_KEYS_DEFAULT = 200000


def b64url_decode(text):
    """Padding-tolerant base64url. Returns None rather than raising."""
    if text is None or not B64URL_RE.match(text):
        return None
    try:
        return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    except (binascii.Error, ValueError):
        return None


def b64_decode_any(text):
    """base64url first, then the standard alphabet. None on failure."""
    raw = b64url_decode(text)
    if raw is not None:
        return raw
    try:
        return base64.b64decode(text + "=" * (-len(text) % 4), validate=True)
    except (binascii.Error, ValueError):
        return None


def json_object(raw):
    """-> dict for a JSON object, else None. Only an object counts as a payload."""
    if raw is None:
        return None
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def maybe_inflate(raw):
    """itsdangerous and Django both mark a zlib payload by prefixing a dot."""
    try:
        return zlib.decompress(raw), True
    except zlib.error:
        return raw, False


def iso(ts):
    try:
        return datetime.datetime.fromtimestamp(
            float(ts), datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    except (OverflowError, OSError, ValueError, TypeError):
        return None


def plausible_epoch(value, now):
    """A signed timestamp is only readable if it lands in a believable window."""
    return isinstance(value, (int, float)) and EPOCH_2010 <= value <= now + 400 * 86400


def b62_decode(text):
    total = 0
    for char in text:
        index = DJANGO_B62.find(char)
        if index < 0:
            return None
        total = total * 62 + index
    return total


def clip(text, limit=400):
    if text is None:
        return None
    text = text if isinstance(text, str) else repr(text)
    return text if len(text) <= limit else text[:limit] + "...[+%d]" % (len(text) - limit)


def nonprintable_ratio(raw):
    """How much of this does not read as text. Ciphertext is mostly unprintable;
    base64 of a word is not, and 'hello-world' happens to decode to a length that
    is a multiple of 8, which is exactly how a block reading gets invented."""
    printable = sum(1 for byte in raw if 32 <= byte < 127 or byte in (9, 10, 13))
    return 1.0 - printable / len(raw)


def repeated_blocks(raw, size):
    """Identical blocks are the one ECB tell that needs no key and no request."""
    blocks = [raw[i:i + size] for i in range(0, len(raw), size)]
    return len(blocks) - len(set(blocks))


# --------------------------------------------------------------------------- #
# format probes: each returns (hit, reason, detail). Every probe runs on every
# token so a rejection can be counted; the priority order below breaks ties.
# --------------------------------------------------------------------------- #
def probe_jwe(value, ctx):
    parts = value.split(".")
    if len(parts) != 5:
        return False, "%d dot-separated parts, not the 5 a JWE has" % len(parts), {}
    header = json_object(b64url_decode(parts[0]))
    if header is None:
        return False, "5 dot parts, but part 1 is not base64url JSON", {}
    if "enc" not in header:
        return False, "5 dot parts with a JSON header, but no \"enc\" member", {}
    return True, ("5 dot-separated parts and part 1 base64url-decodes to a JSON "
                  "object carrying \"enc\"=%r (alg=%r) -- JWE compact serialization"
                  % (header.get("enc"), header.get("alg"))), {"header": header,
                                                              "parts": parts}


def probe_jwt(value, ctx):
    parts = value.split(".")
    if len(parts) != 3:
        return False, "%d dot-separated parts, not the 3 a JWS has" % len(parts), {}
    header = json_object(b64url_decode(parts[0]))
    if header is None:
        return False, "3 dot parts, but part 1 is not base64url JSON", {}
    if "alg" not in header:
        return False, ("3 dot parts and part 1 is JSON, but it has no \"alg\" member "
                       "-- a JWS header must declare alg"), {}
    return True, ("3 dot-separated parts and part 1 base64url-decodes to a JSON "
                  "object whose \"alg\" is %r -- JWS/JWT compact serialization"
                  % header.get("alg")), {"header": header, "parts": parts}


def probe_itsdangerous(value, ctx):
    """payload . timestamp . signature, with the leading dot marking compression."""
    compressed_marker = value.startswith(".")
    parts = value.split(".")
    if compressed_marker:
        if len(parts) != 4 or parts[0] != "":
            return False, ("starts with a dot but is not the 4-field compressed "
                           "itsdangerous shape"), {}
        payload_part, ts_part, sig_part = parts[1], parts[2], parts[3]
    else:
        if len(parts) != 3:
            return False, "%d dot-separated parts, not 3" % len(parts), {}
        payload_part, ts_part, sig_part = parts
    ts_raw = b64url_decode(ts_part)
    if ts_raw is None or not 1 <= len(ts_raw) <= 8:
        return False, ("part 2 does not base64url-decode to the 1-8 raw bytes "
                       "itsdangerous writes a timestamp as"), {}
    stamp = int.from_bytes(ts_raw, "big")
    if not plausible_epoch(stamp, ctx["now"]):
        return False, ("part 2 decodes to %d, which is not a plausible epoch "
                       "second -- so it is not an itsdangerous timestamp" % stamp), {}
    sig_raw = b64url_decode(sig_part)
    if sig_raw is None or len(sig_raw) not in DIGEST_BY_LEN:
        return False, ("part 3 does not decode to a known digest length "
                       "(got %s bytes)" % (len(sig_raw) if sig_raw else None)), {}
    raw = b64url_decode(payload_part)
    payload, inflated = (None, False)
    if raw is not None:
        raw2, inflated = maybe_inflate(raw)
        payload = json_object(raw2)
    return True, ("3 fields payload.timestamp.signature: part 2 decodes to %d raw "
                  "bytes reading as epoch %d (%s) and part 3 to a %d-byte %s digest"
                  "%s" % (len(ts_raw), stamp, iso(stamp), len(sig_raw),
                          DIGEST_BY_LEN[len(sig_raw)],
                          "; the leading dot marks a zlib payload"
                          if compressed_marker else "")), {
        "payload_part": payload_part, "ts_part": ts_part, "sig_part": sig_part,
        "stamp": stamp, "sig_raw": sig_raw, "payload": payload,
        "inflated": inflated, "compressed_marker": compressed_marker,
        "signed_value": value.rsplit(".", 1)[0]}


def probe_django(value, ctx):
    """payload:timestamp:signature with base62 time -- Django's signing.dumps."""
    parts = value.split(":")
    if len(parts) != 3:
        return False, "%d colon-separated parts, not the 3 Django signs" % len(parts), {}
    payload_part, ts_part, sig_part = parts
    stamp = b62_decode(ts_part)
    if stamp is None:
        return False, "part 2 %r is not Django base62" % clip(ts_part, 40), {}
    if not plausible_epoch(stamp, ctx["now"]):
        return False, ("part 2 base62-decodes to %d, not a plausible epoch second"
                       % stamp), {}
    sig_raw = b64url_decode(sig_part)
    if sig_raw is None or len(sig_raw) not in DIGEST_BY_LEN:
        return False, ("part 3 does not decode to a known digest length "
                       "(got %s bytes)" % (len(sig_raw) if sig_raw else None)), {}
    body = payload_part[1:] if payload_part.startswith(".") else payload_part
    raw = b64url_decode(body)
    payload, inflated = None, False
    if raw is not None:
        raw2, inflated = maybe_inflate(raw)
        payload = json_object(raw2)
    return True, ("3 colon-separated parts: part 2 base62-decodes to epoch %d (%s) "
                  "and part 3 to a %d-byte %s digest -- Django TimestampSigner"
                  % (stamp, iso(stamp), len(sig_raw),
                     DIGEST_BY_LEN[len(sig_raw)])), {
        "payload_part": payload_part, "ts_part": ts_part, "sig_part": sig_part,
        "stamp": stamp, "sig_raw": sig_raw, "payload": payload,
        "inflated": inflated, "signed_value": value.rsplit(":", 1)[0]}


def probe_rails(value, ctx):
    """ActiveSupport::MessageVerifier writes <base64 data>--<hex digest>."""
    if "--" not in value:
        return False, "no '--' separator", {}
    left, _, right = value.rpartition("--")
    if not HEX_RE.match(right or ""):
        return False, "text after '--' is not pure hex", {}
    if len(right) // 2 not in DIGEST_BY_LEN:
        return False, ("text after '--' is %d hex chars = %d bytes, not a known "
                       "digest length" % (len(right), len(right) // 2)), {}
    raw = b64_decode_any(left)
    inner = json_object(raw) if raw else None
    return True, ("a '--' separator with %d hex characters after it = a %d-byte %s "
                  "digest -- ActiveSupport::MessageVerifier framing"
                  % (len(right), len(right) // 2,
                     DIGEST_BY_LEN[len(right) // 2])), {
        "data_part": left, "hex_digest": right, "digest_bytes": len(right) // 2,
        "decoded": raw, "inner_json": inner}


def probe_fernet(value, ctx):
    """0x80 || 8-byte time || 16-byte IV || ct || 32-byte HMAC, base64url."""
    raw = b64url_decode(value)
    if raw is None:
        return False, "not base64url", {}
    if len(raw) < 57:
        return False, ("%d decoded bytes, below the 57 bytes of Fernet framing"
                       % len(raw)), {}
    if raw[0] != 0x80:
        return False, "first decoded byte is 0x%02x, not Fernet's 0x80" % raw[0], {}
    body = len(raw) - 57
    if body == 0 or body % 16:
        return False, ("0x80 version byte but the %d bytes between the IV and the "
                       "HMAC are not a non-zero multiple of the 16-byte AES block"
                       % body), {}
    stamp = int.from_bytes(raw[1:9], "big")
    return True, ("base64url of %d bytes starting with the 0x80 Fernet version "
                  "byte; %d bytes of ciphertext = %d AES blocks between the 16-byte "
                  "IV and the 32-byte HMAC" % (len(raw), body, body // 16)), {
        "raw": raw, "stamp": stamp, "iv": raw[9:25], "ciphertext": raw[25:-32],
        "hmac": raw[-32:], "blocks": body // 16}


def probe_express(value, ctx):
    """express-session's cookie: 's:' + sid + '.' + base64(HMAC-SHA256)."""
    if not value.startswith("s:"):
        return False, "does not start with the literal 's:' prefix", {}
    rest = value[2:]
    if "." not in rest:
        return False, "'s:' prefix but no '.' before a signature", {}
    sid, _, sig = rest.rpartition(".")
    sig_raw = b64_decode_any(sig)
    if sig_raw is None or len(sig_raw) != 32:
        return False, ("'s:' prefix but the text after the final '.' is not "
                       "base64 of 32 bytes (got %s)"
                       % (len(sig_raw) if sig_raw else None)), {}
    return True, ("the literal 's:' prefix express-session uses, and the text "
                  "after the final '.' base64-decodes to 32 bytes = one "
                  "HMAC-SHA256 digest"), {"sid": sid, "sig": sig,
                                          "sig_raw": sig_raw, "signed_value": sid}


def probe_b64_json(value, ctx):
    raw = b64_decode_any(value)
    obj = json_object(raw)
    if obj is None:
        return False, ("does not base64-decode to a JSON object"
                       if raw is not None else "not valid base64"), {}
    return True, ("base64%s of a JSON object with keys %s, and no signature field "
                  "follows it" % ("url" if b64url_decode(value) is not None else "",
                                  sorted(obj.keys())[:8])), {"payload": obj,
                                                             "raw": raw}


def probe_block_blob(value, ctx):
    """A length that is a whole number of cipher blocks, and nothing else."""
    if HEX_RE.match(value):
        # hex is already a deliberate choice to encode BYTES, so a block-multiple
        # length means something. base64 is used for text all day long, so it has
        # to clear two more bars below.
        raw, encoding = binascii.unhexlify(value), "hex"
        if len(raw) < 8:
            return False, "%d decoded bytes is under one cipher block" % len(raw), {}
    else:
        raw, encoding = b64_decode_any(value), "base64"
        if raw is None:
            return False, "neither hex nor base64", {}
        if len(raw) < 16:
            return False, ("base64 of only %d bytes: under one AES block, and a "
                           "block reading of something this short proves nothing"
                           % len(raw)), {}
        ratio = nonprintable_ratio(raw)
        if ratio < 0.25:
            return False, ("base64 of %d bytes, but %.0f%% of them are printable "
                           "ASCII -- that reads as encoded text, not ciphertext"
                           % (len(raw), 100 * (1 - ratio))), {}
    if len(raw) % 16 == 0:
        size = 16
    elif len(raw) % 8 == 0:
        size = 8
    else:
        return False, ("%d decoded bytes is a multiple of neither 8 nor 16, so it "
                       "is not a whole number of cipher blocks" % len(raw)), {}
    count = len(raw) // size
    dupes = repeated_blocks(raw, size)
    return True, ("%s of %d bytes = %d blocks of %d, a whole number of blocks for "
                  "%s%s" % (encoding, len(raw), count, size,
                            "AES/Camellia/Twofish" if size == 16
                            else "DES/3DES/Blowfish/IDEA",
                            "; %d block(s) repeat" % dupes if dupes else "")), {
        "raw": raw, "encoding": encoding, "block_size": size, "block_count": count,
        "repeated_blocks": dupes}


# Priority order: the more structure a format asserts, the earlier it is tried.
# base64-json and block-cipher-blob sit last because almost anything base64 can
# satisfy a length test, and a length test proves the least.
PROBES = (("jwe", probe_jwe), ("jwt", probe_jwt), ("fernet", probe_fernet),
          ("express-signed", probe_express), ("itsdangerous", probe_itsdangerous),
          ("django-signed", probe_django), ("rails-signed", probe_rails),
          ("base64-json", probe_b64_json), ("block-cipher-blob", probe_block_blob))


def classify(value, now):
    """-> (format, evidence, detail, rejected, also_matched). Never forces a hit."""
    ctx = {"now": now}
    hits, rejected = [], []
    for name, probe in PROBES:
        try:
            hit, reason, detail = probe(value, ctx)
        except Exception as exc:                       # a probe must never abort
            hit, reason, detail = False, "%s: %s" % (type(exc).__name__, exc), {}
        (hits if hit else rejected).append((name, reason, detail))
    if not hits:
        return ("opaque", "no structural signature matched; %d format probes were "
                "run and every one was rejected" % len(rejected), {},
                rejected, [])
    name, reason, detail = hits[0]
    return name, reason, detail, rejected, [h[0] for h in hits[1:]]


# --------------------------------------------------------------------------- #
# decoding: only what opens without a key
# --------------------------------------------------------------------------- #
def decode_jwt(detail, now, want_pyjwt=True):
    parts = detail["parts"]
    header = detail["header"]
    claims = json_object(b64url_decode(parts[1]))
    path = "builtin-base64url"
    if want_pyjwt and pyjwt is not None:
        try:
            # options disable verification on purpose: this is a reader, and the
            # key is exactly what we do not have yet.
            claims = pyjwt.decode(".".join(parts), options={
                "verify_signature": False, "verify_exp": False,
                "verify_nbf": False, "verify_aud": False, "verify_iss": False})
            path = "pyjwt %s (signature verification off)" % getattr(
                pyjwt, "__version__", "unknown")
        except Exception as exc:
            path = "builtin-base64url (pyjwt refused: %s)" % type(exc).__name__
    sig_raw = b64url_decode(parts[2])
    alg = header.get("alg")
    sig_bytes = len(sig_raw) if sig_raw is not None else None
    expected, sig_note = None, None
    if not isinstance(alg, str):
        # RFC 7515 4.1.1 makes alg a string. A JSON object or array in its place
        # is not exotic -- it is a hand-built algorithm-confusion header, exactly
        # what this tool exists to read -- and it must not cost the whole report:
        # `alg in ALG_SIG_BYTES` raises TypeError on an unhashable value, which
        # used to lose the format, the decode and every weakness at once.
        matches = None
        sig_note = ("alg is not a JSON string but %s (%s), which RFC 7515 4.1.1 "
                    "does not allow: no signature size is defined for a non-string "
                    "alg, so the size check is skipped rather than guessed"
                    % (type(alg).__name__, clip(json.dumps(alg), 80)))
    elif alg in ALG_SIG_BYTES:
        expected = ALG_SIG_BYTES[alg]
        matches = sig_bytes == expected
        sig_note = ("%s signatures are exactly %d bytes; this one is %s"
                    % (alg, expected, sig_bytes))
    elif alg in RSA_ALGS:
        matches = bool(sig_bytes) and sig_bytes % 128 == 0
        expected = "the RSA modulus size in bytes (256 for a 2048-bit key)"
        sig_note = ("%s signatures are the modulus size; %s bytes implies a %s-bit "
                    "key" % (alg, sig_bytes, sig_bytes * 8 if sig_bytes else None))
    else:
        matches = None
        sig_note = "alg %r is not one this tool has a fixed size for" % alg
    out = {
        "decoder_path": path,
        "header": header,
        "claims": claims if claims is not None else
                  {"_undecodable": clip(parts[1], 120)},
        "signature": {"b64": clip(parts[2], 120), "bytes": sig_bytes,
                      "empty": not parts[2],
                      "alg_is_a_json_string": isinstance(alg, str),
                      "expected_for_alg": expected,
                      "matches_alg": matches, "note": sig_note},
        "signing_input": clip(".".join(parts[:2]), 400),
    }
    if isinstance(claims, dict):
        present = sorted(claims.keys())
        out["claims_present"] = present
        out["claims_time"] = [c for c in TIME_CLAIMS if c in claims]
        out["claims_identity"] = [c for c in IDENTITY_CLAIMS if c in claims]
        out["claims_privilege"] = [c for c in PRIVILEGE_CLAIMS if c in claims]
        out["expiry"] = expiry_view(claims, now)
    out["key_sourcing_headers"] = {k: header[k] for k in KEY_SOURCING_HEADERS
                                   if k in header}
    return out


def expiry_view(claims, now):
    """exp/nbf/iat against a reference time the caller supplies, never now()."""
    view = {"reference_time": now, "reference_time_iso": iso(now)}
    exp = claims.get("exp")
    if isinstance(exp, (int, float)):
        view["exp"] = exp
        view["exp_iso"] = iso(exp)
        view["expired"] = exp < now
        view["seconds_remaining"] = round(exp - now, 1)
    else:
        view["exp"] = None
        view["expired"] = None
        view["note"] = ("no numeric exp claim: nothing in the token bounds its "
                        "lifetime, so a captured token stays valid")
    for name in ("nbf", "iat"):
        if isinstance(claims.get(name), (int, float)):
            view[name] = claims[name]
            view[name + "_iso"] = iso(claims[name])
    if isinstance(claims.get("nbf"), (int, float)):
        view["not_yet_valid"] = claims["nbf"] > now
    return view


def decode_itsdangerous(detail, now):
    out = {
        "payload": detail["payload"] if detail["payload"] is not None else
                   {"_undecodable": clip(detail["payload_part"], 120)},
        "zlib_compressed": detail["inflated"],
        "timestamp": detail["stamp"], "timestamp_iso": iso(detail["stamp"]),
        "age_seconds": round(now - detail["stamp"], 1),
        "signature_bytes": len(detail["sig_raw"]),
        "signature_digest_by_length": DIGEST_BY_LEN[len(detail["sig_raw"])],
        "signed_value": clip(detail["signed_value"], 400),
        "note": ("Flask's serializer tags non-JSON types as a single-key object "
                 "whose key starts with a space -- {\" b\": base64} for bytes, "
                 "{\" t\": [...]} for a tuple, {\" d\": http-date} for a datetime "
                 "(read out of flask.json.tag on this box). Those are type tags, "
                 "not application data."),
    }
    if not plausible_epoch(detail["stamp"], now):
        out["timestamp_warning"] = ("the plain reading is implausible; older "
                                    "itsdangerous releases offset the epoch, so "
                                    "check the library version before trusting it")
    return out


def decode_django(detail, now):
    return {
        "payload": detail["payload"] if detail["payload"] is not None else
                   {"_undecodable": clip(detail["payload_part"], 120)},
        "zlib_compressed": detail["inflated"],
        "timestamp": detail["stamp"], "timestamp_iso": iso(detail["stamp"]),
        "age_seconds": round(now - detail["stamp"], 1),
        "signature_bytes": len(detail["sig_raw"]),
        "signature_digest_by_length": DIGEST_BY_LEN[len(detail["sig_raw"])],
        "signed_value": clip(detail["signed_value"], 400),
        "note": ("Django signs but does not encrypt: the payload above is the "
                 "whole session. max_age is enforced by the CALLER of loads(), "
                 "not by the token, so an old token may still be accepted."),
    }


def decode_rails(detail, now):
    out = {"digest_bytes": detail["digest_bytes"],
           "digest_by_length": DIGEST_BY_LEN[detail["digest_bytes"]],
           "hex_digest": detail["hex_digest"],
           "data_base64": clip(detail["data_part"], 200)}
    raw = detail["decoded"]
    if raw is None:
        out["data_decoded"] = None
        out["data_note"] = "the part before '--' is not decodable base64"
        return out
    inner = detail["inner_json"]
    out["data_decoded"] = clip(raw.decode("utf-8", "replace"), 600)
    if isinstance(inner, dict) and {"p", "h"} <= set(inner):
        out["kind"] = "encrypted"
        out["encrypted_fields"] = sorted(inner.keys())
        out["note"] = ("an outer JSON object with p (payload) and h (headers: iv, "
                       "at) is Rails' ENCRYPTED cookie: the session is not "
                       "readable without secret_key_base")
    elif inner is not None:
        out["kind"] = "signed-json"
        out["payload"] = inner
        out["note"] = "signed only, not encrypted: the payload above is readable"
    elif raw[:2] == b"\x04\x08":
        out["kind"] = "signed-marshal"
        out["note"] = ("the data begins 04 08, Ruby's Marshal version header: the "
                       "cookie is signed only and carries a marshalled object, "
                       "which is a deserialization sink if the key is recovered")
    else:
        out["kind"] = "signed-opaque"
        out["note"] = "signed only, but the data is neither JSON nor Ruby Marshal"
    return out


def decode_fernet(detail, now):
    return {
        "version_byte": "0x80",
        "timestamp": detail["stamp"], "timestamp_iso": iso(detail["stamp"]),
        "age_seconds": round(now - detail["stamp"], 1),
        "iv_hex": detail["iv"].hex(),
        "ciphertext_bytes": len(detail["ciphertext"]),
        "ciphertext_blocks": detail["blocks"],
        "hmac_hex": detail["hmac"].hex(),
        "repeated_ciphertext_blocks": repeated_blocks(detail["ciphertext"], 16),
        "note": ("the timestamp and the IV are plaintext in every Fernet token; "
                 "the ciphertext is AES-128-CBC and the trailing 32 bytes are "
                 "HMAC-SHA256 over everything before them, keyed by the FIRST 16 "
                 "bytes of the 32-byte key (verified against cryptography.fernet "
                 "on this box). Nothing else opens without that key."),
    }


def decode_express(detail, now):
    return {"session_id": detail["sid"],
            "signature_bytes": len(detail["sig_raw"]),
            "signature_b64": detail["sig"],
            "note": ("the session id is opaque server-side state, so there is "
                     "nothing to read here -- the value of this format is that "
                     "the signature is HMAC-SHA256 over the id with the app's "
                     "secret, which a wordlist can attack offline")}


def decode_b64_json(detail, now):
    return {"payload": detail["payload"],
            "keys": sorted(detail["payload"].keys()),
            "note": ("there is no signature and no MAC in this value: whatever "
                     "the server reads back is whatever was sent")}


def decode_blob(detail, now):
    return {"encoding": detail["encoding"], "decoded_bytes": len(detail["raw"]),
            "block_size": detail["block_size"],
            "block_count": detail["block_count"],
            "repeated_blocks": detail["repeated_blocks"],
            "first_block_hex": detail["raw"][:detail["block_size"]].hex(),
            "note": ("nothing decodes: the only readable facts are the length, "
                     "the block alignment and whether any block repeats. A random "
                     "session id of this length has the same shape, so the block "
                     "reading is a candidate, not a conclusion.")}


# --------------------------------------------------------------------------- #
# weaknesses, as data, each with the command that tests it
# --------------------------------------------------------------------------- #
FORGE_NOTE = ("this tool does not build that token; construct it yourself and "
              "send it through tools/web/http_probe.py so the verdict lands in "
              "tools/hooks.py")
LOCKTALK = ("htb-locktalk-haproxy-exact-path-acl-dot-segment-bypass-"
            "python-jwt-json-serialization-role-forge")


def weakness(wid, status, standard_name, why, next_command, falsifier,
             local_precedent=None):
    return {"id": wid, "status": status, "standard_name": standard_name,
            "why_here": why, "next_command": next_command,
            "falsifier": falsifier, "local_precedent": local_precedent}


def weaknesses_jwt(decoded, token, challenge):
    header = decoded["header"]
    raw_alg = header.get("alg")
    alg = str(raw_alg)
    # str(None).lower() is "none", so testing the stringified value made a JSON
    # null alg confirm an unsecured JWS -- on a token carrying a real signature.
    # Only the literal string may say the token already declares it.
    declares_none = isinstance(raw_alg, str) and raw_alg.lower() == "none"
    sig = decoded["signature"]
    probe = ("python3 tools/web/http_probe.py --url '<protected route>' "
             "--header 'Authorization: Bearer <FORGED>' --challenge %s "
             "--class web-auth-session --hypothesis-id <h> "
             "--evidence-contains '<string only a privileged response has>' "
             "--on-match confirms --evidence-kind impact" % challenge)
    out = [
        weakness(
            "alg-none",
            "present-in-token" if declares_none else "to-test",
            "unsecured JWS (RFC 7519 section 6, \"alg\": \"none\")",
            ("the token already declares alg=none, so whatever produced it is not "
             "signing at all" if declares_none else
             "alg is %s; a verifier that reads alg from the token may also accept "
             "none, which removes the signature entirely"
             % (repr(alg) if isinstance(raw_alg, str)
                else json.dumps(raw_alg) + " (not a string)")),
            "set the header to {\"alg\":\"none\"}, keep the claims, leave the third "
            "field EMPTY but keep the trailing dot; " + FORGE_NOTE + ". " + probe,
            "the route answers 401/403 with the none token while the original is "
            "accepted -- the library rejects unsecured JWS and this is closed"),
        weakness(
            "alg-confusion",
            "to-test" if alg in RSA_ALGS or alg.startswith("ES") or alg == "EdDSA"
            else "not-applicable",
            "asymmetric-to-symmetric algorithm confusion (RS/PS/ES -> HS)",
            ("alg is %r, an asymmetric algorithm: if the verifier picks the "
             "algorithm from the token but always loads the same key material, the "
             "PUBLIC key becomes an HMAC secret" % alg) if alg in RSA_ALGS or
            alg.startswith("ES") or alg == "EdDSA" else
            "alg is %r, already symmetric: there is no public key to re-use" % alg,
            "find the public key (a /jwks.json or /.well-known/jwks.json route, an "
             "embedded PEM in the handout, or one recovered from two signatures), "
             "re-sign the claims as HS256 with that key's exact bytes, then " + probe,
            "the same claims re-signed HS256 with the public key are rejected while "
            "the untouched token is accepted -- the verifier pins the algorithm"),
        weakness(
            "empty-signature",
            "present-in-token" if sig["empty"] or sig["bytes"] == 0 else "to-test",
            "signature stripped / empty third field",
            "the third field is %s bytes" % sig["bytes"],
            "send the same header and claims with the third field removed and with "
            "it empty-but-dotted -- two separate probes, they fail differently. " +
            probe,
            "both forms are rejected; the verifier requires a signature"),
        weakness(
            "weak-shared-key",
            "to-test" if alg in HMAC_ALGS else "not-applicable",
            "brute-forceable HMAC secret",
            "alg is %s, so the signature is an offline oracle for the secret: every "
            "candidate can be checked without touching the target" % alg
            if alg in HMAC_ALGS else
            "alg %r is not HMAC, so a wordlist has nothing to verify against" % alg,
            "python3 tools/web/session_dissect.py --token '<this token>' --try-keys "
            "--wordlist /home/kali/wordlists/SecLists/Passwords/Common-Credentials/"
            "10k-most-common.txt   (local computation only, no requests)",
            "0 of N candidates verify -- record the N and stop; a longer wordlist is "
            "a bigger N, not a different mechanism"),
        weakness(
            "signature-length-mismatch",
            "present-in-token" if sig["matches_alg"] is False else "not-applicable",
            "declared algorithm does not match the signature size",
            sig["note"],
            "decide which of the two is lying before forging anything: re-read the "
            "handout's verify call, and compare a second freshly issued token",
            "a second token from the same issuer has the same mismatch -- then it is "
            "this issuer's normal output, not a bug"),
    ]
    if not isinstance(raw_alg, str):
        out.append(weakness(
            "non-string-alg",
            "present-in-token",
            "alg is not a JSON string (RFC 7515 section 4.1.1 requires one)",
            "alg is %s, a JSON %s: no library issues that, so this header was "
            "hand-built. What a verifier does with a non-string alg is a property "
            "of the verifier -- it may raise, or it may reach a comparison that "
            "was written for strings" % (clip(json.dumps(raw_alg), 80),
                                        type(raw_alg).__name__),
            "send it UNCHANGED first and read the error, before forging anything: "
            "a library raising InvalidAlgorithmError has already closed this, "
            "while a hand-written check doing alg == 'none' or alg.startswith may "
            "not. " + probe,
            "the route answers exactly the error any other malformed token gets -- "
            "the alg value never reaches a comparison"))
    sourcing = decoded.get("key_sourcing_headers") or {}
    for name, value in sourcing.items():
        value_text = value if isinstance(value, str) else json.dumps(value)
        looks_path = isinstance(value, str) and (
            "/" in value or ".." in value or value.startswith("http"))
        out.append(weakness(
            "header-%s" % name,
            "present-in-token",
            {"kid": "kid as a path, an SQL parameter or a key-selection oracle",
             "jku": "jku pointing the verifier at a JWK Set you control",
             "jwk": "jwk embedding your own public key in the token",
             "x5u": "x5u pointing the verifier at a certificate you control",
             "x5c": "x5c embedding your own certificate chain",
             "x5t": "x5t thumbprint used to select a key"}.get(
                 name, "key-sourcing header"),
            "the header carries %s=%s%s" % (name, clip(value_text, 120),
                                            ", which reads as a path or URL"
                                            if looks_path else ""),
            "vary that value alone and watch the error change: a traversal "
            "(../../dev/null with an empty-key signature), a file the app is "
            "certain to have, an injection metacharacter, then a URL you serve. "
            + FORGE_NOTE,
            "every variation returns the identical error as the untouched token -- "
            "the header is not used to select the key"))
    privilege = decoded.get("claims_privilege") or []
    if privilege:
        out.append(weakness(
            "privilege-claim-in-token",
            "present-in-token",
            "authorization carried in a client-held claim",
            "the claims carry %s -- the authorization decision travels inside the "
            "token, so forging the signature is the whole attack" % privilege,
            "read the handout for the exact accepted values before forging; "
            "guessing 'admin' when the app compares against 'administrator' wastes "
            "the probe. " + probe,
            "the route ignores the claim and re-reads the role from the database",
            local_precedent=LOCKTALK))
    expiry = decoded.get("expiry") or {}
    if expiry.get("expired"):
        out.append(weakness(
            "expiry-not-enforced",
            "to-test",
            "expired token accepted (exp present but unchecked)",
            "exp is %s (%s), %.0f seconds before the reference time" % (
                expiry.get("exp"), expiry.get("exp_iso"),
                -1 * (expiry.get("seconds_remaining") or 0)),
            "replay this token UNCHANGED -- it is the cheapest read-only probe in "
            "the whole list, because nothing is forged: " + probe,
            "the route answers 401 with an exp error -- expiry is enforced"))
    elif expiry.get("exp") is None and "claims_present" in decoded:
        out.append(weakness(
            "no-expiry-claim",
            "present-in-token",
            "token without an expiry",
            "no numeric exp claim: a captured token does not age out",
            "keep it; re-use it after the session that issued it is logged out and "
            "see whether it still works. " + probe,
            "the token stops working after logout -- the server keeps a revocation "
            "list the token cannot show you"))
    return out


def weaknesses_jwe(detail, challenge):
    header = detail.get("header", {})
    return [weakness(
        "jwe-header-only",
        "present-in-token",
        "JWE: the protected header is the only plaintext",
        "alg=%r enc=%r. There is no signature to strip: a JWE that fails to "
        "decrypt fails closed, so none-algorithm and signature-stripping do not "
        "apply here" % (header.get("alg"), header.get("enc")),
        "read the handout for where the key comes from; if alg is 'dir' the CEK is "
        "a configured secret and the whole attack is recovering that secret",
        "the header names an asymmetric alg and the key never appears in the "
        "handout -- close this layer and switch")]


def weaknesses_signed_payload(fmt, decoded, challenge, wordlist_hint):
    """itsdangerous, Django and express all reduce to: recover the key, or don't."""
    probe = ("python3 tools/web/http_probe.py --url '<protected route>' "
             "--header 'Cookie: <name>=<FORGED>' --challenge %s "
             "--class web-auth-session --hypothesis-id <h> "
             "--evidence-contains '<string only a privileged response has>' "
             "--on-match confirms --evidence-kind impact" % challenge)
    readable = fmt in ("itsdangerous", "django-signed")
    out = [
        weakness(
            "payload-is-plaintext",
            "present-in-token" if readable else "not-applicable",
            "signed but not encrypted",
            "the payload above was read with no key at all -- field names, user "
            "ids and flags in the session are already yours" if readable else
            "the value is an opaque server-side id; there is nothing to read",
            "grep the handout for every field name the payload shows; a field you "
            "can see is a field the app trusts" if readable else
            "the id is a lookup key: attack the store, not the token",
            "nothing in the payload is used for an authorization decision"),
        weakness(
            "weak-secret-key",
            "to-test",
            "brute-forceable signing secret",
            "the signature is a keyed digest over bytes you hold, so every "
            "candidate secret is checkable offline with zero requests",
            wordlist_hint,
            "0 of N candidates verify -- record the N and change mechanism layer"),
        weakness(
            "timestamp-not-enforced",
            "to-test" if fmt in ("itsdangerous", "django-signed") else
            "not-applicable",
            "signed timestamp present but max_age never passed",
            "the timestamp is inside the signature, but both libraries leave the "
            "age check to the caller: loads() without max_age accepts any age"
            if fmt in ("itsdangerous", "django-signed") else
            "this format carries no timestamp",
            "replay an old token unchanged -- read-only, nothing forged: " + probe,
            "the old token is rejected with an age error -- max_age is passed"),
    ]
    if fmt == "itsdangerous":
        out.append(weakness(
            "secret-key-leak-beats-brute-force",
            "to-test",
            "SECRET_KEY read out of the app rather than guessed",
            "a wordlist only finds a human-chosen key. Flask's key is often in the "
            "handout, in a leaked .env, in /proc/self/environ through a file read, "
            "or in a debug page",
            "python3 tools/web/read_loop.py --url '<proven file-read>' --profile "
            "container   (only once a file-read primitive is already proven; "
            "confirm its flags with --help first)",
            "no file read exists and the handout ships no key -- then the wordlist "
            "is the only route and its N is the answer"))
    return out


def weaknesses_fernet(decoded, challenge):
    return [
        weakness(
            "fernet-timestamp-readable",
            "present-in-token",
            "Fernet leaks its issue time",
            "the timestamp %s (%s) is plaintext; it dates the token and can expose "
            "a predictable issuing sequence" % (decoded["timestamp"],
                                                decoded["timestamp_iso"]),
            "compare two tokens issued seconds apart: if anything other than the "
            "timestamp, IV and ciphertext changes, the key is being derived per "
            "request",
            "the timestamps are identical across issues -- it is not a real clock"),
        weakness(
            "fernet-authenticated-no-tamper",
            "not-applicable",
            "bit-flipping and padding oracles do NOT apply",
            "the trailing 32 bytes are HMAC-SHA256 over the whole token, so any "
            "modified ciphertext is rejected before AES runs. Recording this as "
            "not-applicable is the point: it stops a padding-oracle attempt that "
            "cannot work",
            "attack the KEY instead: is it in the handout, derived from a password, "
            "or generated from a seeded PRNG?",
            "the app strips or ignores the HMAC in its own decrypt path -- read the "
            "handout's decrypt call before believing that"),
        weakness(
            "fernet-key-verifiable-offline",
            "to-test",
            "candidate key confirmed by the HMAC, without decrypting",
            "if a 32-byte key leaks anywhere, its first 16 bytes verify the HMAC "
            "locally -- so a candidate can be confirmed without one request",
            "python3 tools/web/session_dissect.py --token '<this token>' --try-keys "
            "--wordlist <file of candidate Fernet keys>   (each line a 44-char "
            "urlsafe-base64 key; a password list cannot contain one)",
            "0 of N candidate keys verify")]


def weaknesses_rails(decoded, challenge):
    kind = decoded.get("kind")
    return [
        weakness(
            "rails-cookie-kind",
            "present-in-token",
            "signed-only versus encrypted Rails cookie",
            "this one reads as %s. A signed-only cookie hands you the session; an "
            "encrypted one hands you nothing but the framing" % kind,
            "if signed-only, read the payload above and look for the field the app "
            "authorizes on; if encrypted, stop here and look for secret_key_base",
            "the payload is neither JSON nor Marshal and the digest length does not "
            "match any Rails default -- reclassify, this may not be Rails"),
        weakness(
            "rails-marshal-sink",
            "to-test" if kind == "signed-marshal" else "not-applicable",
            "Ruby Marshal deserialization once the key is known",
            "the data begins 04 08, so the app calls Marshal.load on whatever "
            "verifies -- key recovery becomes RCE, not just session forgery"
            if kind == "signed-marshal" else
            "the data is not marshalled, so there is no Marshal sink here",
            "treat it as a deserialization chain, not an auth chain: open the "
            "web-deserialization skill and read blast_radius on the matching chain "
            "card before any write",
            "the app calls JSON.parse rather than Marshal.load -- read config for "
            "cookies_serializer before assuming"),
        weakness(
            "rails-key-recovery",
            "refused",
            "PBKDF2 key derivation over secret_key_base",
            "--try-keys is deliberately NOT implemented for this format: Rails "
            "derives the verifier key with PBKDF2-HMAC over secret_key_base using "
            "a per-purpose salt string and an iteration count that differ by Rails "
            "version and configuration. Those values were not verified on this box, "
            "and guessing them would produce confident false negatives",
            "read config/initializers and config/application.rb in the handout for "
            "the serializer, the digest and the key generator settings, then write "
            "the derivation from what the source says",
            "n/a -- this is a refusal to guess, not a hypothesis")]


def weaknesses_unsigned(decoded, challenge):
    return [weakness(
        "no-integrity-at-all",
        "present-in-token",
        "unsigned client-side session",
        "the value decodes to a JSON object and carries no MAC: the server reads "
        "back exactly what was sent, so there is no key to recover and no "
        "signature to strip",
        "change ONE field, re-encode with the same padding style as the original, "
        "and send it: python3 tools/web/http_probe.py --url '<protected route>' "
        "--header 'Cookie: <name>=<edited>' --challenge %s --class web-auth-session "
        "--hypothesis-id <h> --evidence-contains '<privileged string>' "
        "--on-match confirms --evidence-kind impact" % challenge,
        "the edited cookie is rejected -- then a signature is being checked "
        "somewhere the encoding did not show, so re-read the handout")]


def weaknesses_blob(decoded, challenge):
    count = decoded["block_count"]
    size = decoded["block_size"]
    return [
        weakness(
            "padding-oracle-shape",
            "to-test" if count >= 2 else "not-applicable",
            "CBC padding oracle",
            "%d blocks of %d bytes: an attack needs at least two blocks (one to "
            "corrupt, one to observe), and this has %d" % (count, size, count)
            if count >= 2 else
            "%d block of %d bytes: with a single block there is no preceding block "
            "to corrupt unless the IV is sent separately" % (count, size),
            "find the oracle before building anything: submit the token with its "
            "LAST byte changed and compare the response to the untouched token. "
            "Three distinguishable answers (valid / bad padding / bad content) is "
            "the oracle; two is not",
            "a corrupted token gives byte-identical output to a valid one -- there "
            "is no oracle and this shape proves nothing"),
        weakness(
            "ecb-repeated-blocks",
            "present-in-token" if decoded["repeated_blocks"] else "not-applicable",
            "ECB mode revealed by identical ciphertext blocks",
            "%d block(s) repeat" % decoded["repeated_blocks"]
            if decoded["repeated_blocks"] else
            "no two blocks are identical: no ECB evidence from this token alone",
            "get a token for a long, highly repetitive input you control and count "
            "repeats again -- one sample cannot show ECB, two can",
            "a controlled repetitive input still yields all-distinct blocks -- the "
            "mode is chaining"),
        weakness(
            "first-block-is-iv",
            "to-test" if count >= 2 else "not-applicable",
            "IV prepended to the ciphertext",
            "if the first block is the IV then the remaining %d block(s) are the "
            "ciphertext, and flipping bits in the IV edits the FIRST plaintext "
            "block directly" % (count - 1) if count >= 2 else
            "a single block cannot carry both an IV and a ciphertext",
            "flip one bit in the first block and compare the error to flipping one "
            "bit in the last block: different failures mean different roles",
            "both positions produce the identical error -- the first block is not "
            "being used as an IV"),
        weakness(
            "shape-is-not-a-finding",
            "present-in-token",
            "a length is not a cipher",
            "a %d-byte random session id has exactly this shape. The block count "
            "is a candidate and nothing more" % decoded["decoded_bytes"],
            "settle it cheaply: request two tokens for the SAME input. Identical "
            "means deterministic encryption or a stored id; different means a "
            "random IV or a random id -- and a third token tells you which",
            "n/a -- this entry exists to stop the shape being recorded as a finding")]


def weaknesses_opaque(value, challenge):
    return [weakness(
        "opaque-is-a-result",
        "present-in-token",
        "no recognised structure",
        "%d characters, and every format probe was rejected with a reason. An "
        "opaque value is usually a lookup key into server-side state, so the token "
        "is not the attack surface -- the store behind it is" % len(value),
        "stop reading the token. Collect several: if they differ only in a counter "
        "or a timestamp the generator is predictable (tools/crypto_attack.py list "
        "names the PRNG attacks); if they are uniformly random, the session is "
        "server-side and the bug is elsewhere",
        "n/a -- opaque is the measurement, not a hypothesis to falsify")]


# --------------------------------------------------------------------------- #
# offline key recovery
# --------------------------------------------------------------------------- #
def read_wordlist(path, max_keys):
    """Lines as-is minus the newline: a trailing space can be part of a secret."""
    words, truncated = [], False
    with open(path, "rb") as handle:
        for line in handle:
            words.append(line.rstrip(b"\r\n"))
            if max_keys and len(words) >= max_keys:
                truncated = True
                break
    return words, truncated


def try_keys(fmt, detail, decoded, path, max_keys):
    """Offline HMAC over a wordlist. No requests, ever. Counts every attempt."""
    try:
        words, truncated = read_wordlist(path, max_keys)
    except OSError as exc:
        return {"attempted": False, "reason": "wordlist unreadable: %s" % exc}
    report = {"attempted": True, "wordlist": path, "candidates": len(words),
              "truncated_at_max_keys": truncated, "verifications": 0,
              "recovered": False, "key": None, "scheme": None}

    if fmt == "jwt":
        alg = str(detail["header"].get("alg"))
        digest = HMAC_ALGS.get(alg)
        if digest is None:
            report.update(attempted=False, reason=(
                "alg is %r; a wordlist can only verify an HMAC algorithm "
                "(HS256/384/512)" % alg))
            return report
        signing_input = ".".join(detail["parts"][:2]).encode()
        target = b64url_decode(detail["parts"][2]) or b""
        report["schemes"] = ["%s: HMAC-%s over header.payload" % (alg, alg[2:])]
        for word in words:
            report["verifications"] += 1
            if hmac.compare_digest(
                    hmac.new(word, signing_input, digest).digest(), target):
                report.update(recovered=True, key=word.decode("utf-8", "replace"),
                              scheme=report["schemes"][0])
                break

    elif fmt == "itsdangerous":
        target = detail["sig_raw"]
        value = detail["signed_value"].encode()
        digest_name = DIGEST_BY_LEN[len(target)]
        digest = getattr(hashlib, digest_name)
        salts = [s.encode() for s in ([FLASK_SALT] + list(
            detail.get("extra_salts", [])))]
        report["schemes"] = ["salt=%s derivation=%s digest=%s"
                             % (s.decode(), d, digest_name)
                             for s in salts for d in ITSDANGEROUS_DERIVATIONS]
        for word in words:
            for salt in salts:
                for derivation in ITSDANGEROUS_DERIVATIONS:
                    key = derive_itsdangerous(word, salt, derivation, digest)
                    report["verifications"] += 1
                    if hmac.compare_digest(
                            hmac.new(key, value, digest).digest(), target):
                        report.update(recovered=True,
                                      key=word.decode("utf-8", "replace"),
                                      scheme="salt=%s derivation=%s digest=%s"
                                             % (salt.decode(), derivation,
                                                digest_name))
                        break
                if report["recovered"]:
                    break
            if report["recovered"]:
                break

    elif fmt == "django-signed":
        target = detail["sig_raw"]
        value = detail["signed_value"].encode()
        digest_name = DIGEST_BY_LEN[len(target)]
        digest = getattr(hashlib, digest_name)
        report["schemes"] = ["salt=%s: sha(salt+'signer'+key) then HMAC-%s"
                             % (s, digest_name) for s in DJANGO_SALTS]
        for word in words:
            for salt in DJANGO_SALTS:
                key = digest((salt + "signer").encode() + word).digest()
                report["verifications"] += 1
                if hmac.compare_digest(
                        hmac.new(key, value, digest).digest(), target):
                    report.update(recovered=True,
                                  key=word.decode("utf-8", "replace"),
                                  scheme="salt=%s digest=%s" % (salt, digest_name))
                    break
            if report["recovered"]:
                break

    elif fmt == "express-signed":
        target = detail["sig_raw"]
        value = detail["signed_value"].encode()
        report["schemes"] = ["HMAC-SHA256 over the session id"]
        for word in words:
            report["verifications"] += 1
            if hmac.compare_digest(
                    hmac.new(word, value, hashlib.sha256).digest(), target):
                report.update(recovered=True, key=word.decode("utf-8", "replace"),
                              scheme=report["schemes"][0])
                break

    elif fmt == "fernet":
        # Each candidate must BE a Fernet key; a password list cannot hold one, so
        # the count is reported against that so a zero is not read as safety.
        raw = detail["raw"]
        report["schemes"] = ["HMAC-SHA256 over token[:-32] with key[:16]"]
        usable = 0
        for word in words:
            candidate = b64url_decode(word.decode("ascii", "ignore"))
            if candidate is None or len(candidate) != 32:
                continue
            usable += 1
            report["verifications"] += 1
            if hmac.compare_digest(
                    hmac.new(candidate[:16], raw[:-32], hashlib.sha256).digest(),
                    raw[-32:]):
                report.update(recovered=True, key=word.decode("utf-8", "replace"),
                              scheme=report["schemes"][0])
                break
        report["candidates_that_were_32_byte_keys"] = usable

    else:
        report.update(attempted=False, reason=(
            "no offline verification is implemented for format %r; see the "
            "rails-key-recovery weakness for why guessing a derivation is worse "
            "than refusing" % fmt))
        return report

    if not report["recovered"]:
        report["result"] = ("0 of %d candidates verified across %d HMAC "
                            "computations -- a recordable negative, not a safety "
                            "claim" % (report["candidates"],
                                       report["verifications"]))
    else:
        report["result"] = ("recovered after %d HMAC computations"
                            % report["verifications"])
    return report


def derive_itsdangerous(key, salt, derivation, digest):
    """The four derivations itsdangerous ships. Flask selects 'hmac'."""
    if derivation == "hmac":
        return hmac.new(key, salt, digest).digest()
    if derivation == "django-concat":
        return digest(salt + b"signer" + key).digest()
    if derivation == "concat":
        return digest(salt + key).digest()
    return key


# --------------------------------------------------------------------------- #
# one token, end to end
# --------------------------------------------------------------------------- #
def dissect(value, name=None, now=None, challenge="<challenge>", wordlist=None,
            do_try_keys=False, max_keys=MAX_KEYS_DEFAULT, extra_salts=(),
            use_pyjwt=True):
    now = time.time() if now is None else now
    raw_value = value
    unquoted = urllib.parse.unquote(value)
    # Rails and express both arrive percent-encoded through a browser; classify on
    # whichever form actually has structure, and say which one was used.
    candidates = [(value, False)] if unquoted == value else [(unquoted, True),
                                                             (value, False)]
    best = None
    for candidate, decoded_flag in candidates:
        fmt, evidence, detail, rejected, also = classify(candidate.strip(), now)
        if fmt != "opaque":
            best = (candidate, decoded_flag, fmt, evidence, detail, rejected, also)
            break
    if best is None:
        candidate, decoded_flag = candidates[0]
        fmt, evidence, detail, rejected, also = classify(candidate.strip(), now)
        best = (candidate, decoded_flag, fmt, evidence, detail, rejected, also)
    candidate, url_decoded, fmt, evidence, detail, rejected, also = best

    report = {
        "name": name, "length": len(raw_value),
        "value_preview": clip(raw_value, 160),
        "url_decoded_before_classifying": url_decoded,
        "format": fmt,
        "format_evidence": evidence,
        "formats_probed": len(PROBES),
        "formats_rejected": len(rejected),
        "also_matched": also,
        "rejections": [{"format": n, "because": r} for n, r, _ in rejected],
    }

    if fmt == "jwt":
        decoded = decode_jwt(detail, now, use_pyjwt)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_jwt(decoded, candidate, challenge)
    elif fmt == "jwe":
        report["decoded"] = {"header": detail["header"],
                             "note": "only the protected header is plaintext"}
        report["weaknesses"] = weaknesses_jwe(detail, challenge)
    elif fmt == "itsdangerous":
        detail["extra_salts"] = list(extra_salts)
        decoded = decode_itsdangerous(detail, now)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_signed_payload(
            fmt, decoded, challenge,
            "python3 tools/web/session_dissect.py --token '<this value>' --try-keys "
            "--wordlist /home/kali/wordlists/SecLists/Passwords/Common-Credentials/"
            "10k-most-common.txt   (tries salt=%s with all four itsdangerous key "
            "derivations; add --salt for a non-Flask salt)" % FLASK_SALT)
    elif fmt == "django-signed":
        decoded = decode_django(detail, now)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_signed_payload(
            fmt, decoded, challenge,
            "python3 tools/web/session_dissect.py --token '<this value>' --try-keys "
            "--wordlist <list>   (tries the %d Django salts measured out of the "
            "installed django: %s)" % (len(DJANGO_SALTS), ", ".join(DJANGO_SALTS)))
    elif fmt == "express-signed":
        decoded = decode_express(detail, now)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_signed_payload(
            fmt, decoded, challenge,
            "python3 tools/web/session_dissect.py --token '<this value>' --try-keys "
            "--wordlist <list>   (HMAC-SHA256 over the session id; the base64 "
            "detail was cross-checked against node's own crypto, but the algorithm "
            "choice is the documented cookie-signature construction and was not "
            "verified against an installed express here)")
    elif fmt == "rails-signed":
        decoded = decode_rails(detail, now)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_rails(decoded, challenge)
    elif fmt == "fernet":
        decoded = decode_fernet(detail, now)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_fernet(decoded, challenge)
    elif fmt == "base64-json":
        decoded = decode_b64_json(detail, now)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_unsigned(decoded, challenge)
    elif fmt == "block-cipher-blob":
        decoded = decode_blob(detail, now)
        report["decoded"] = decoded
        report["weaknesses"] = weaknesses_blob(decoded, challenge)
    else:
        report["decoded"] = {"note": "nothing decoded; see rejections for the "
                                     "reason each format was ruled out"}
        report["weaknesses"] = weaknesses_opaque(candidate, challenge)

    report["padding_oracle_candidate"] = padding_oracle_view(fmt, detail)
    report["weakness_counts"] = count_statuses(report["weaknesses"])

    if do_try_keys:
        if not wordlist:
            report["key_recovery"] = {
                "attempted": False,
                "reason": ("--try-keys needs --wordlist PATH. No built-in list is "
                           "shipped because the words would be a guess; SecLists "
                           "is at /home/kali/wordlists/SecLists/")}
        else:
            report["key_recovery"] = try_keys(fmt, detail, report.get("decoded"),
                                              wordlist, max_keys)
    return report


def padding_oracle_view(fmt, detail):
    """Reported for every format, so a NOT-a-candidate is recorded too."""
    if fmt == "block-cipher-blob":
        return {"candidate": detail["block_count"] >= 2,
                "block_size": detail["block_size"],
                "block_count": detail["block_count"],
                "encoding": detail["encoding"],
                "repeated_blocks": detail["repeated_blocks"],
                "statement": ("the SHAPE is a whole number of %d-byte blocks (%d of "
                              "them). That is a candidate and nothing more: no "
                              "oracle has been observed, and a random id of this "
                              "length looks identical."
                              % (detail["block_size"], detail["block_count"]))}
    if fmt == "fernet":
        return {"candidate": False, "block_size": 16,
                "block_count": detail["blocks"],
                "statement": ("the ciphertext is %d AES blocks, but Fernet appends "
                              "HMAC-SHA256 over the whole token, so modified "
                              "ciphertext is rejected before any padding check. Not "
                              "a padding-oracle candidate." % detail["blocks"])}
    return {"candidate": False, "statement": ("format %s is not a raw block-cipher "
                                              "shape" % fmt)}


def summarize(tokens):
    """The summary block. `errors` exists so a token that failed to analyse is
    counted: without it the report said ok with a format of "error" inside."""
    return {
        "tokens": len(tokens),
        "formats": {t["name"]: t["format"] for t in tokens},
        "opaque": sum(1 for t in tokens if t["format"] == "opaque"),
        "errors": [t["name"] for t in tokens if t["format"] == "error"],
        "padding_oracle_candidates": [t["name"] for t in tokens
                                      if t["padding_oracle_candidate"]["candidate"]],
        "keys_recovered": [t["name"] for t in tokens
                           if (t.get("key_recovery") or {}).get("recovered")],
        "next": ("read format_evidence first: if it does not convince you, the "
                 "classification is wrong and every weakness below it is wrong "
                 "too. Then run exactly one next_command whose status is "
                 "present-in-token, before any that says to-test."),
    }


def count_statuses(weaknesses):
    counts = {}
    for item in weaknesses:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    counts["total"] = len(weaknesses)
    return counts


# --------------------------------------------------------------------------- #
# input collection
# --------------------------------------------------------------------------- #
def split_cookie_header(text, from_set_cookie=False, dropped=None):
    """-> [(name, value)]. Set-Cookie attributes are dropped, not dissected.

    Anything else this drops is appended to `dropped` with the reason, so a jar
    with one malformed piece reports a short inventory instead of quietly
    returning one fewer token than it was given.
    """
    out = []
    for index, piece in enumerate(text.split(";")):
        piece = piece.strip()
        if not piece:
            continue
        if from_set_cookie and index > 0:
            continue                                   # attributes, not cookies
        if "=" not in piece:
            _drop(dropped, piece, "no '=' in this piece, so it names no cookie")
            continue
        name, _, value = piece.partition("=")
        name, value = name.strip(), value.strip().strip('"')
        if not COOKIE_NAME_RE.match(name):
            _drop(dropped, piece, "%r is not a legal RFC 6265 cookie name"
                                  % clip(name, 40))
            continue
        if not value:
            _drop(dropped, piece, "the value after '=' is empty")
            continue
        out.append((name, value))
    return out


def _drop(dropped, piece, reason):
    if dropped is not None:
        dropped.append({"piece": clip(piece, 120), "reason": reason})


def looks_like_cookie_header(line, now=None, explain=False):
    """-> True when the line reads as 'name=value', not as one bare token.

    '.' and '+' are legal in an RFC 6265 cookie name, so banning them silently
    turned connect.sid -- express-session's DEFAULT cookie name -- and
    .AspNetCore.Session into nameless bare tokens, and turned a padded bare
    base64 token into a cookie whose value was the pad character. The veto that
    keeps a bare JWT out is structural instead: if the WHOLE line already
    classifies as a known token format, it is that token and not a jar.

    The guess is recorded per line in the report, and --jar / --raw force either
    reading, because no heuristic can settle every line: a rails or base64 cookie
    whose own value contains the separator can satisfy both readings.
    """
    def answer(hit, because):
        return (hit, because) if explain else hit
    if "=" not in line:
        return answer(False, "no '=' in the line, so it names no cookie")
    head = line.split("=", 1)[0].strip()
    if not COOKIE_NAME_RE.match(head):
        return answer(False, "%r is not a legal RFC 6265 cookie name"
                             % clip(head, 40))
    fmt = classify(line.strip(), time.time() if now is None else now)[0]
    if fmt != "opaque":
        return answer(False, "the whole line classifies as %s, so it is one token "
                             "and not a jar" % fmt)
    return answer(True, "%r is a legal RFC 6265 cookie name and the whole line "
                        "matches no token format" % clip(head, 40))


def set_cookie_view(resp, dropped=None):
    """-> every Set-Cookie on the response, not only the last one.

    dict(resp.headers) keeps one value per header name, and Set-Cookie is
    repeated on every response that sets more than one cookie -- measured here
    against a three-cookie response, which reported one. httpkit also returns
    `set_cookies` (every value, in order) and `headers_all`; this reads those and
    names the source it used, so a short inventory is never silent. A plain
    headers dict is still accepted, and then says what it cannot see.
    """
    if isinstance(resp, dict) and ("set_cookies" in resp or "headers_all" in resp):
        found = list(resp.get("set_cookies") or
                     [v for k, v in (resp.get("headers_all") or [])
                      if k.lower() == "set-cookie"])
        source = ("httpkit set_cookies: every repeated Set-Cookie header, in the "
                  "order the server sent them")
    else:
        headers = resp.get("headers", resp) if isinstance(resp, dict) else {}
        found = [v for k, v in headers.items() if k.lower() == "set-cookie"]
        source = ("a collapsed headers dict -- this response reader supplied no "
                  "set_cookies list, so only the LAST of several Set-Cookie "
                  "headers is visible. Pass the full jar with --cookie if a cookie "
                  "is missing")
    view = {"present": bool(found), "raw": found, "header_count": len(found),
            "source": source}
    cookies, attrs = [], {}
    for raw in found:
        cookies.extend(split_cookie_header(raw, from_set_cookie=True,
                                           dropped=dropped))
        for piece in raw.split(";")[1:]:
            key, _, val = piece.strip().partition("=")
            if key.strip().lower() in COOKIE_ATTRS:
                attrs[key.strip()] = val.strip() or True
    view["cookies"] = cookies
    view["attributes"] = attrs
    view["flags_note"] = ("HttpOnly stops a JS read, Secure stops a plaintext "
                          "send, SameSite bounds CSRF -- absent flags are the "
                          "cheapest finding on this list")
    return view


def stdin_reading(line, raw, jar, now):
    """-> (read_as, because). The guess is reported, never silent."""
    if raw:
        return "bare-token", "--raw: every stdin line is treated as one token"
    if jar:
        return "cookie-header", "--jar: every stdin line is treated as a jar"
    hit, because = looks_like_cookie_header(line, now, explain=True)
    return ("cookie-header" if hit else "bare-token"), because


def collect(args, report, now=None):
    """-> [(name, value)] plus whatever the one allowed request produced."""
    pairs, dropped = [], []
    if args.token:
        for index, token in enumerate(args.token):
            pairs.append(("--token[%d]" % index if len(args.token) > 1
                          else "--token", token))
    if args.cookie:
        for blob in args.cookie:
            pairs.extend(split_cookie_header(blob, dropped=dropped))
    if args.stdin:
        readings = []
        for line in sys.stdin.read().splitlines():
            line = line.strip()
            if not line:
                continue
            read_as, because = stdin_reading(line, args.raw, args.jar, now)
            readings.append({"line_preview": clip(line, 80), "read_as": read_as,
                             "because": because})
            if read_as == "cookie-header":
                pairs.extend(split_cookie_header(line, dropped=dropped))
            else:
                pairs.append(("--stdin", line))
        report["stdin"] = {"lines": len(readings), "readings": readings,
                           "note": ("--raw forces every line to a bare token, "
                                    "--jar forces every line to a cookie header")}
    if args.url:
        resp = httpkit.request(args.url, "GET", httpkit.parse_headers(args.header),
                               None, timeout=args.timeout,
                               follow=args.follow_redirects)
        request = {"request": "GET %s" % args.url, "ok": resp["ok"],
                   "status": resp.get("status"), "elapsed": resp.get("elapsed"),
                   "followed_redirects": args.follow_redirects,
                   "note": ("one GET, to read Set-Cookie. This is the only request "
                            "this tool makes; redirects are NOT followed by default "
                            "because a 302 often carries the cookie.")}
        if not resp["ok"]:
            request["error"] = resp.get("error")
            report["request"] = request
            return pairs
        view = set_cookie_view(resp, dropped=dropped)
        request["set_cookie"] = view
        report["request"] = request
        pairs.extend(view["cookies"])
    if dropped:
        report["input_dropped"] = {
            "count": len(dropped), "pieces": dropped,
            "note": ("these pieces of the supplied jars or Set-Cookie headers "
                     "named no dissectable cookie; they are listed so the token "
                     "count below can be reconciled against what was given")}
    return pairs


# --------------------------------------------------------------------------- #
# selftest: offline, deterministic, tokens built here with stdlib only
# --------------------------------------------------------------------------- #
SELFTEST_KEY = "s3cr3t-cookie-key"
SELFTEST_NOW = 1750000000.0                            # 2025-06-15T14:26:40Z

# Ground truth, not self-construction. Every token below was emitted by the real
# library installed on this box (itsdangerous 2.2.0 configured exactly as
# flask.sessions.SecureCookieSessionInterface does, Django 4.2.19's
# signing.dumps, cryptography's Fernet, PyJWT 2.10.1) under the secret named
# here, then pasted in. A token this tool BUILT itself can only prove the tool
# agrees with itself -- these prove it agrees with the libraries, which is what a
# challenge will actually be running. FIXTURE_NOW is a fixed reference time just
# after they were minted, so no assertion below ever reads a clock.
FIXTURE_SECRET = "correct horse battery staple"
FIXTURE_NOW = 1790700000.0
FIXTURES = {
    # itsdangerous with Flask's settings: salt cookie-session, derivation hmac,
    # digest sha1. Timestamp 1790689657, 20-byte signature.
    "itsd_hmac": "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9.arvBeQ."
                 "vv24z46pIEF-Fu_TSsskMPJBzV0",
    # the same payload under itsdangerous' OWN default derivation, django-concat:
    # a different signature over identical bytes, which is why try-keys sweeps
    # all four derivations instead of assuming Flask.
    "itsd_default": "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9.arvBeQ."
                    "gxjcgsBKeIWdkYngn28ns7uKBbo",
    # compressed: the leading dot, and a zlib payload behind it
    "itsd_zlib": ".eJyrViotTi1SslJKL00tLlHSUcrLL0kFcitGwaACSrUAxFLDxg.arvBeQ."
                 "Vo-SrCNJkuaT_x-rB2S_y_a75io",
    # Django signing.dumps: salt django.core.signing, sha256, base62 timestamp
    # 1790689658 written as 1xBYBG
    "django": "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9:1xBYBG:"
              "T_h4OGZAa6hBPKgMwf48SeKpt7QgRMwriwntZuoLrKY",
    "django_zlib": ".eJyrViotTi1SslJKL00tLlHSUcrLL0kFcitHwaACSrUAANjFVg:1xBYBG:"
                   "kxZ14590ueUNYaJfkbvGNnqn1EjUXCFMYz8NjBQsX24",
    # Fernet over a key that is bytes(range(32)), so the fixture is reproducible
    "fernet_key": "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8=",
    "fernet": "gAAAAABqu8F738LgJ0L5oSm-fP7gQooonvQK-qPZQTltsfXah0rtCOQoUAfr3SVa"
              "Hu6B2SZ3IjT9aQVkK0uy84CC8HcXmSgEJ_9PpowAXR-MbJAwJ03yalA=",
    # PyJWT HS256, exp 1750003600 -- inside SELFTEST_NOW + 1h
    "pyjwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJndWVzdCIsInJvbGUi"
             "OiJndWVzdCIsImV4cCI6MTc1MDAwMzYwMH0."
             "_zHQAgGBGiU8LMLiRUFQuAZYTImKZMzhUHffwBO36Eo",
    # itsdangerous 2.2.0, Flask's salt but the "concat" derivation
    # (key = sha1(salt + secret)): the SAME salt and digest as itsd_hmac, so only
    # the derivation differs. Minted with URLSafeTimedSerializer(key_derivation=
    # "concat", digest_method=sha1) and read back by that library's own loads().
    "itsd_concat": "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9.arvPoA."
                   "toTKlHq9vvVt3P7xx4qnM-MNT5g",
    # itsdangerous 2.2.0, Flask's derivation but the salt "my-app-salt": the only
    # thing that recovers this is --salt, so it is the fixture that proves the
    # extra salts are actually swept.
    "itsd_extrasalt": "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9.arvPoA."
                      "Z-K8a5AFGOA25np7uE34mjjssv4",
}
ITSD_EXTRA_SALT = "my-app-salt"
# Django 4.2.19 signing.dumps under EACH of the four salts this tool sweeps, all
# with the same secret and the same base62 timestamp 1xBZ7i = 1790693282. Each was
# verified by signing.loads(key=FIXTURE_SECRET, salt=<its own salt>). The salt
# strings are written out here, NOT read from DJANGO_SALTS: a test that iterates
# the constant it is testing cannot notice the constant shrinking.
DJANGO_SALT_FIXTURES = {
    "django.core.signing":
        "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9:1xBZ7i:"
        "Km777AYIihWDcz3XQjoDe7UI2IgnMC-wNIxYqKjFUqw",
    "django.contrib.sessions.backends.signed_cookies":
        "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9:1xBZ7i:"
        "tadeA35ls1tZrs_KNRQuOLXNYcEtEQWfTUbs99mFAyw",
    "django.core.signing.TimestampSigner":
        "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9:1xBZ7i:"
        "pvGl0HBxVD2tYnPV4JyyEjX0XGthAf35aeqteqByml4",
    "django.core.signing.Signer":
        "eyJ1c2VyIjoiZ3Vlc3QiLCJhZG1pbiI6ZmFsc2V9:1xBZ7i:"
        "fR7CWxMquaE0-5uwSZHSwk7AR0aszrEiUq8dVIsXRLA",
}
DJANGO_SALT_FIXTURE_STAMP = 1790693282
# RFC 7515 4.1.2-4.1.6, written out for the same reason.
EXPECTED_KEY_SOURCING_HEADERS = ("kid", "jku", "jwk", "x5u", "x5c", "x5t")
FIXTURE_TIMESTAMPS = {"itsd": 1790689657, "django": 1790689658,
                      "fernet": 1790689659}


def _b64u(raw):
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _make_jwt(header, claims, key=None, digest=hashlib.sha256):
    signing_input = "%s.%s" % (_b64u(json.dumps(header, separators=(",", ":"))
                                    .encode()),
                               _b64u(json.dumps(claims, separators=(",", ":"))
                                     .encode()))
    if key is None:
        return signing_input + "."
    return "%s.%s" % (signing_input,
                      _b64u(hmac.new(key.encode(), signing_input.encode(),
                                     digest).digest()))


def _make_itsdangerous(payload, key, stamp, salt=FLASK_SALT):
    body = "%s.%s" % (_b64u(json.dumps(payload, separators=(",", ":")).encode()),
                      _b64u(stamp.to_bytes(4, "big")))
    derived = hmac.new(key.encode(), salt.encode(), hashlib.sha1).digest()
    return "%s.%s" % (body, _b64u(hmac.new(derived, body.encode(),
                                           hashlib.sha1).digest()))


def _make_fernet(stamp, blocks=2, key=None):
    """Real Fernet framing with stdlib only: the HMAC is what this tool checks."""
    body = (bytes([0x80]) + stamp.to_bytes(8, "big") + bytes(range(16))
            + bytes((i * 7) % 256 for i in range(16 * blocks)))
    signing = (b64url_decode(key)[:16] if key else b"\x00" * 16)
    return _b64u(body + hmac.new(signing, body, hashlib.sha256).digest())


def _write(path, lines):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return path


def selftest(tmpdir=None):
    """Offline and deterministic. The wordlist fixtures go in a private temp dir
    that is removed afterwards -- a fixed world-writable path is a symlink target
    and the sibling tools use tempfile, so this one does too."""
    if tmpdir:
        return _selftest(tmpdir, removed=False)
    tmpdir = tempfile.mkdtemp(prefix="session_dissect-selftest-")
    try:
        return _selftest(tmpdir, removed=True)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _selftest(tmpdir, removed):
    """Build each format here, assert the classification AND the decode."""
    checks, skipped = [], []
    os.makedirs(tmpdir, exist_ok=True)

    def check(name, got, want, extra=None):
        entry = {"name": name, "expected": want, "got": got,
                 "pass": got == want}
        if extra:
            entry.update(extra)
        checks.append(entry)
        return entry["pass"]

    def skip(name, reason):
        """A check that cannot run here is NOT counted as one that passed: the
        total drops, which is the only honest signal that it did not run."""
        skipped.append({"name": name, "reason": reason})

    # 1. HS256 JWT signed with a known key
    tok = _make_jwt({"alg": "HS256", "typ": "JWT"},
                    {"sub": "guest", "role": "guest",
                     "exp": int(SELFTEST_NOW) + 3600}, SELFTEST_KEY)
    rep = dissect(tok, now=SELFTEST_NOW)
    check("HS256 JWT classified", rep["format"], "jwt",
          {"evidence": rep["format_evidence"]})
    check("HS256 claims decoded", rep["decoded"]["claims"].get("role"), "guest")
    check("HS256 signature is 32 bytes", rep["decoded"]["signature"]["bytes"], 32)
    check("HS256 signature matches its alg",
          rep["decoded"]["signature"]["matches_alg"], True)
    check("HS256 not expired against the reference time",
          rep["decoded"]["expiry"]["expired"], False)
    check("privilege claim surfaced", rep["decoded"]["claims_privilege"], ["role"])
    check("weak-shared-key is to-test for HS256",
          [w["status"] for w in rep["weaknesses"] if w["id"] == "weak-shared-key"],
          ["to-test"])
    check("alg-confusion is not-applicable for HS256",
          [w["status"] for w in rep["weaknesses"] if w["id"] == "alg-confusion"],
          ["not-applicable"])
    check("padding oracle correctly NOT a candidate for a JWT",
          rep["padding_oracle_candidate"]["candidate"], False)

    # 2. the same token with alg none and an empty signature
    none_tok = _make_jwt({"alg": "none", "typ": "JWT"},
                         {"sub": "guest", "role": "admin"}, None)
    rep_none = dissect(none_tok, now=SELFTEST_NOW)
    check("alg=none JWT still classified as jwt", rep_none["format"], "jwt")
    check("alg=none header read", rep_none["decoded"]["header"]["alg"], "none")
    check("alg=none signature is 0 bytes",
          rep_none["decoded"]["signature"]["bytes"], 0)
    check("alg-none reported as present-in-token",
          [w["status"] for w in rep_none["weaknesses"] if w["id"] == "alg-none"],
          ["present-in-token"])
    check("empty-signature reported as present-in-token",
          [w["status"] for w in rep_none["weaknesses"]
           if w["id"] == "empty-signature"], ["present-in-token"])
    check("no-expiry-claim raised when exp is absent",
          any(w["id"] == "no-expiry-claim" for w in rep_none["weaknesses"]), True)

    # 3. expiry decided against a passed-in reference time, never now()
    old = _make_jwt({"alg": "HS256", "typ": "JWT"},
                    {"sub": "guest", "exp": int(SELFTEST_NOW) - 600},
                    SELFTEST_KEY)
    rep_old = dissect(old, now=SELFTEST_NOW)
    check("expired JWT reported expired", rep_old["decoded"]["expiry"]["expired"],
          True)
    check("seconds_remaining is negative and exact",
          rep_old["decoded"]["expiry"]["seconds_remaining"], -600.0)
    check("expiry-not-enforced raised for an expired token",
          any(w["id"] == "expiry-not-enforced" for w in rep_old["weaknesses"]),
          True)
    # the same token one hour earlier is NOT expired: proves the reference time
    # is really the input and not a hidden clock read
    check("same token is valid at an earlier reference time",
          dissect(old, now=SELFTEST_NOW - 3600)["decoded"]["expiry"]["expired"],
          False)

    # 4. Flask/itsdangerous shape, built with the derivation read off this box
    flask_tok = _make_itsdangerous({"user": "guest", "admin": False},
                                   SELFTEST_KEY, int(SELFTEST_NOW) - 30)
    rep_flask = dissect(flask_tok, now=SELFTEST_NOW)
    check("itsdangerous token classified", rep_flask["format"], "itsdangerous",
          {"evidence": rep_flask["format_evidence"]})
    check("itsdangerous payload decoded",
          rep_flask["decoded"]["payload"].get("user"), "guest")
    check("itsdangerous timestamp decoded",
          rep_flask["decoded"]["timestamp"], int(SELFTEST_NOW) - 30)
    check("itsdangerous signature read as sha1",
          rep_flask["decoded"]["signature_digest_by_length"], "sha1")
    # a JWT and a Flask cookie are both three dotted base64 fields: the classifier
    # must not confuse them in EITHER direction
    check("a JWT is not misread as itsdangerous",
          rep["format"] == "jwt" and "itsdangerous" not in rep["also_matched"],
          True)
    check("a Flask cookie is not misread as a JWT",
          "jwt" not in ([rep_flask["format"]] + rep_flask["also_matched"]), True,
          {"jwt_rejected_because": [r["because"] for r in rep_flask["rejections"]
                                    if r["format"] == "jwt"]})
    # the discriminator is the alg member, so the rejection must say so: a
    # three-field base64 token WITHOUT alg is not a JWS, however much it looks
    # like one
    check("and the JWT rejection names the missing alg member",
          any("alg" in r["because"] for r in rep_flask["rejections"]
              if r["format"] == "jwt"), True)
    # three dotted base64 fields are NOT enough: without a plausible epoch in
    # field 2 this is some other three-part token, and calling it itsdangerous
    # would attach a whole wrong weakness list and a wrong key derivation
    fake = "%s.%s.%s" % (_b64u(b'{"a":1}'), _b64u(b"\x00\x01"), _b64u(bytes(20)))
    rep_fake = dissect(fake, now=SELFTEST_NOW)
    check("a 3-field token with an implausible timestamp is not itsdangerous",
          rep_fake["format"] != "itsdangerous", True,
          {"got_format": rep_fake["format"]})
    check("and the rejection quotes the implausible value",
          any("plausible epoch" in r["because"] for r in rep_fake["rejections"]
              if r["format"] == "itsdangerous"), True)

    # 5. Fernet framing
    fern = _make_fernet(int(SELFTEST_NOW) - 5, blocks=3)
    rep_fern = dissect(fern, now=SELFTEST_NOW)
    check("Fernet token classified", rep_fern["format"], "fernet",
          {"evidence": rep_fern["format_evidence"]})
    check("Fernet timestamp decoded", rep_fern["decoded"]["timestamp"],
          int(SELFTEST_NOW) - 5)
    check("Fernet ciphertext block count", rep_fern["decoded"]["ciphertext_blocks"],
          3)
    check("Fernet is NOT a padding-oracle candidate",
          rep_fern["padding_oracle_candidate"]["candidate"], False)
    # the version byte is the whole discriminator: a blob of exactly Fernet's
    # length that does NOT start 0x80 must be rejected, or every long base64
    # session id in the world gets called Fernet
    not_fern = _b64u(bytes([0x7f]) + b64url_decode(fern)[1:])
    rep_nf = dissect(not_fern, now=SELFTEST_NOW)
    check("a Fernet-length blob with the wrong version byte is not Fernet",
          rep_nf["format"] != "fernet", True, {"got_format": rep_nf["format"]})
    check("and the rejection names the version byte",
          any("0x80" in r["because"] for r in rep_nf["rejections"]
              if r["format"] == "fernet"), True)

    # 6. bare base64 JSON: no signature at all
    plain = base64.urlsafe_b64encode(
        json.dumps({"user": "guest", "is_admin": False}).encode()).decode()
    rep_plain = dissect(plain, now=SELFTEST_NOW)
    check("base64 JSON cookie classified", rep_plain["format"], "base64-json",
          {"evidence": rep_plain["format_evidence"]})
    check("base64 JSON payload decoded",
          rep_plain["decoded"]["payload"].get("is_admin"), False)
    check("no-integrity-at-all raised",
          [w["id"] for w in rep_plain["weaknesses"]], ["no-integrity-at-all"])

    # 7. hex blobs: 32 bytes is two AES blocks, 16 bytes is one and must NOT be
    # offered as a padding-oracle candidate
    blob32 = ("%032x" % 0x1122334455667788) + ("%032x" % 0x99aabbccddeeff00)
    rep_blob = dissect(blob32, now=SELFTEST_NOW)
    check("32-byte hex blob classified", rep_blob["format"], "block-cipher-blob",
          {"evidence": rep_blob["format_evidence"]})
    check("32-byte hex blob is 32 decoded bytes",
          rep_blob["decoded"]["decoded_bytes"], 32)
    check("32-byte hex blob is 2 AES blocks",
          (rep_blob["decoded"]["block_size"], rep_blob["decoded"]["block_count"]),
          (16, 2))
    check("32-byte hex blob IS a padding-oracle candidate",
          rep_blob["padding_oracle_candidate"]["candidate"], True)
    check("single-block hex blob is NOT a padding-oracle candidate",
          dissect("%032x" % 0xdeadbeef,
                  now=SELFTEST_NOW)["padding_oracle_candidate"]["candidate"], False)
    # base64 has to clear the printability bar, or every short word with a
    # convenient length becomes a cipher block
    cipher_b64 = base64.b64encode(bytes((i * 37 + 11) % 256
                                        for i in range(32))).decode()
    rep_cb = dissect(cipher_b64, now=SELFTEST_NOW)
    check("base64 of ciphertext-shaped bytes IS a block blob",
          (rep_cb["format"], rep_cb["decoded"]["block_count"]),
          ("block-cipher-blob", 2))
    check("a short word is NOT forced into a block blob",
          dissect("hello-world", now=SELFTEST_NOW)["format"], "opaque")
    check("base64 of plain text is NOT forced into a block blob",
          dissect(base64.b64encode(b"A" * 32).decode(),
                  now=SELFTEST_NOW)["format"], "opaque")
    check("and that rejection quotes the printable percentage",
          any("printable" in r["because"]
              for r in dissect(base64.b64encode(b"A" * 32).decode(),
                               now=SELFTEST_NOW)["rejections"]
              if r["format"] == "block-cipher-blob"), True)
    ecb = "41" * 16 + "41" * 16
    check("repeated blocks counted for an ECB tell",
          dissect(ecb, now=SELFTEST_NOW)["decoded"]["repeated_blocks"], 1)

    # 8. genuinely none of the above
    rep_op = dissect("this is not a token, it is a sentence.", now=SELFTEST_NOW)
    check("a sentence comes back opaque", rep_op["format"], "opaque",
          {"evidence": rep_op["format_evidence"]})
    check("every format probe was rejected and counted",
          rep_op["formats_rejected"], len(PROBES))
    check("opaque still returns an action",
          [w["id"] for w in rep_op["weaknesses"]], ["opaque-is-a-result"])

    # 9. Django, from the real django 4.2.19 output. The base62 timestamp is the
    # assertion that matters: a wrong alphabet ordering still round-trips against
    # a token this file encoded itself, so only a library-minted one catches it.
    dj_tok = FIXTURES["django"]
    rep_dj = dissect(dj_tok, now=FIXTURE_NOW)
    check("real Django cookie classified", rep_dj["format"], "django-signed",
          {"evidence": rep_dj["format_evidence"]})
    check("real Django base62 timestamp decoded",
          rep_dj["decoded"]["timestamp"], FIXTURE_TIMESTAMPS["django"])
    check("real Django payload decoded",
          rep_dj["decoded"]["payload"], {"user": "guest", "admin": False})
    check("real Django signature read as sha256",
          rep_dj["decoded"]["signature_digest_by_length"], "sha256")
    rep_djz = dissect(FIXTURES["django_zlib"], now=FIXTURE_NOW)
    check("Django compressed payload inflated",
          (rep_djz["format"], rep_djz["decoded"]["zlib_compressed"],
           rep_djz["decoded"]["payload"].get("user")),
          ("django-signed", True, "guest"))

    # 10. Rails framing
    rails_data = base64.b64encode(b"\x04\x08somemarshal").decode()
    rails_tok = "%s--%s" % (rails_data, "ab" * 20)
    rep_rails = dissect(rails_tok, now=SELFTEST_NOW)
    check("Rails double-dash cookie classified", rep_rails["format"],
          "rails-signed", {"evidence": rep_rails["format_evidence"]})
    check("Rails Marshal header recognised", rep_rails["decoded"]["kind"],
          "signed-marshal")
    check("Rails key recovery is refused, not guessed",
          [w["status"] for w in rep_rails["weaknesses"]
           if w["id"] == "rails-key-recovery"], ["refused"])

    # 11. the real itsdangerous and Fernet tokens, decoded and key-recovered
    rep_id = dissect(FIXTURES["itsd_hmac"], now=FIXTURE_NOW)
    check("real Flask-configured itsdangerous token classified",
          rep_id["format"], "itsdangerous", {"evidence": rep_id["format_evidence"]})
    check("real itsdangerous payload decoded",
          rep_id["decoded"]["payload"], {"user": "guest", "admin": False})
    check("real itsdangerous timestamp decoded",
          rep_id["decoded"]["timestamp"], FIXTURE_TIMESTAMPS["itsd"])
    rep_idz = dissect(FIXTURES["itsd_zlib"], now=FIXTURE_NOW)
    check("itsdangerous compressed form inflated",
          (rep_idz["format"], rep_idz["decoded"]["zlib_compressed"],
           rep_idz["decoded"]["payload"].get("user")),
          ("itsdangerous", True, "guest"))
    rep_fx = dissect(FIXTURES["fernet"], now=FIXTURE_NOW)
    check("real Fernet token classified", rep_fx["format"], "fernet")
    check("real Fernet timestamp decoded", rep_fx["decoded"]["timestamp"],
          FIXTURE_TIMESTAMPS["fernet"])

    # the same secret must be found under BOTH derivations, from the signature
    # alone -- this is what proves the derivation sweep is not decoration
    fixture_list = _write(os.path.join(tmpdir, "fixture.txt"),
                          ["password", FIXTURE_SECRET, "hunter2"])
    for label, token in (("flask-hmac", FIXTURES["itsd_hmac"]),
                         ("itsdangerous-default", FIXTURES["itsd_default"])):
        got = dissect(token, now=FIXTURE_NOW, wordlist=fixture_list,
                      do_try_keys=True)["key_recovery"]
        check("real secret recovered from the %s signature" % label,
              (got["recovered"], got["key"]), (True, FIXTURE_SECRET),
              {"scheme": got.get("scheme")})
    dj_keys = dissect(FIXTURES["django"], now=FIXTURE_NOW, wordlist=fixture_list,
                      do_try_keys=True)["key_recovery"]
    check("real Django SECRET_KEY recovered from the real signature",
          (dj_keys["recovered"], dj_keys["key"]), (True, FIXTURE_SECRET),
          {"scheme": dj_keys.get("scheme")})
    fx_keys = dissect(FIXTURES["fernet"], now=FIXTURE_NOW,
                      wordlist=_write(os.path.join(tmpdir, "fkey.txt"),
                                      ["password", FIXTURES["fernet_key"]]),
                      do_try_keys=True)["key_recovery"]
    check("real Fernet key verified by its own HMAC",
          (fx_keys["recovered"], fx_keys["key"]),
          (True, FIXTURES["fernet_key"]))
    pj = dissect(FIXTURES["pyjwt"], now=SELFTEST_NOW, wordlist=fixture_list,
                 do_try_keys=True)
    check("real PyJWT token classified and its key recovered",
          (pj["format"], pj["key_recovery"]["recovered"],
           pj["key_recovery"]["key"]), ("jwt", True, FIXTURE_SECRET))
    check("real PyJWT exp read against the reference time",
          (pj["decoded"]["expiry"]["exp"], pj["decoded"]["expiry"]["expired"]),
          (1750003600, False))

    # 12. --try-keys finds the key in a token built here, and reports failure
    hit_list = _write(os.path.join(tmpdir, "hit.txt"),
                      ["password", "letmein", SELFTEST_KEY, "hunter2"])
    miss_list = _write(os.path.join(tmpdir, "miss.txt"),
                       ["password", "letmein", "hunter2"])
    jwt_hit = dissect(tok, now=SELFTEST_NOW, wordlist=hit_list, do_try_keys=True)
    check("try-keys recovers the JWT HMAC key",
          (jwt_hit["key_recovery"]["recovered"], jwt_hit["key_recovery"]["key"]),
          (True, SELFTEST_KEY))
    jwt_miss = dissect(tok, now=SELFTEST_NOW, wordlist=miss_list, do_try_keys=True)
    check("try-keys reports failure rather than a false positive",
          (jwt_miss["key_recovery"]["recovered"], jwt_miss["key_recovery"]["key"]),
          (False, None), {"result": jwt_miss["key_recovery"]["result"]})
    check("the negative is countable",
          jwt_miss["key_recovery"]["candidates"], 3)

    flask_hit = dissect(flask_tok, now=SELFTEST_NOW, wordlist=hit_list,
                        do_try_keys=True)
    check("try-keys recovers the itsdangerous key",
          (flask_hit["key_recovery"]["recovered"], flask_hit["key_recovery"]["key"]),
          (True, SELFTEST_KEY))
    check("the recovered itsdangerous scheme names Flask's derivation",
          "derivation=hmac" in (flask_hit["key_recovery"]["scheme"] or ""), True)
    flask_miss = dissect(flask_tok, now=SELFTEST_NOW, wordlist=miss_list,
                         do_try_keys=True)
    check("itsdangerous try-keys does not false-positive",
          flask_miss["key_recovery"]["recovered"], False,
          {"verifications": flask_miss["key_recovery"]["verifications"]})

    fern_key = base64.urlsafe_b64encode(bytes(range(32))).decode()
    fern_tok = _make_fernet(int(SELFTEST_NOW), blocks=1, key=fern_key)
    fern_list = _write(os.path.join(tmpdir, "fernet.txt"),
                       ["password", fern_key, "hunter2"])
    fern_hit = dissect(fern_tok, now=SELFTEST_NOW, wordlist=fern_list,
                       do_try_keys=True)
    check("try-keys verifies a Fernet key by its HMAC",
          (fern_hit["key_recovery"]["recovered"],
           fern_hit["key_recovery"]["candidates_that_were_32_byte_keys"]),
          (True, 1))

    # 13. try-keys refuses rather than guesses on Rails, and refuses with no list
    rails_try = dissect(rails_tok, now=SELFTEST_NOW, wordlist=hit_list,
                        do_try_keys=True)
    check("try-keys is not attempted for Rails",
          rails_try["key_recovery"]["attempted"], False,
          {"reason": rails_try["key_recovery"].get("reason")})
    check("try-keys without a wordlist refuses instead of inventing words",
          dissect(tok, now=SELFTEST_NOW,
                  do_try_keys=True)["key_recovery"]["attempted"], False)

    # 14. the builtin decoder must agree with pyjwt when pyjwt is present. When
    # pyjwt is NOT importable both sides of that comparison are produced by the
    # builtin decoder, so it compares a value with itself: it is skipped instead,
    # and the total drops by two rather than staying at a reassuring constant.
    builtin = dissect(tok, now=SELFTEST_NOW, use_pyjwt=False)
    check("builtin decoder path is reported",
          builtin["decoded"]["decoder_path"], "builtin-base64url")
    if pyjwt is None:
        skip("builtin and pyjwt paths agree on the claims",
             "pyjwt is not importable here, so both sides would be the builtin "
             "decoder and the comparison could not fail")
        skip("the pyjwt path really ran for that comparison",
             "pyjwt is not importable here")
    else:
        check("the pyjwt path really ran for that comparison",
              rep["decoded"]["decoder_path"].startswith("pyjwt "), True,
              {"decoder_path": rep["decoded"]["decoder_path"]})
        check("builtin and pyjwt paths agree on the claims",
              builtin["decoded"]["claims"], rep["decoded"]["claims"],
              {"pyjwt_path": rep["decoded"]["decoder_path"]})

    # 15. cookie-header splitting and the Set-Cookie attribute rule
    pairs = split_cookie_header("session=%s; csrftoken=abc123" % plain)
    check("cookie header split into both values",
          [p[0] for p in pairs], ["session", "csrftoken"])
    sc = set_cookie_view({"Set-Cookie": "session=%s; Path=/; HttpOnly; SameSite=Lax"
                                        % plain})
    check("Set-Cookie attributes are not dissected as cookies",
          [p[0] for p in sc["cookies"]], ["session"])
    check("Set-Cookie flags are captured",
          sorted(k.lower() for k in sc["attributes"]),
          ["httponly", "path", "samesite"])
    check("a bare JWT is not mistaken for a cookie header",
          looks_like_cookie_header(tok), False)
    check("name=value IS read as a cookie header",
          looks_like_cookie_header("session=" + plain), True)

    # 16. express-session. Nothing above this line ever mentioned the format, so
    # probe_express could be made to reject every value with the gate still green.
    ex_sid = "AbC-123_xyz"
    ex_sig = base64.b64encode(
        hmac.new(SELFTEST_KEY.encode(), ex_sid.encode(),
                 hashlib.sha256).digest()).decode().rstrip("=")
    ex_tok = "s:%s.%s" % (ex_sid, ex_sig)
    rep_ex = dissect(ex_tok, now=SELFTEST_NOW)
    check("express-session cookie classified", rep_ex["format"], "express-signed",
          {"evidence": rep_ex["format_evidence"]})
    check("express session id read back whole",
          rep_ex["decoded"].get("session_id"), ex_sid)
    check("express signature read as 32 bytes",
          rep_ex["decoded"].get("signature_bytes"), 32)
    # the NOT-express direction: the 's:' prefix alone cannot be enough, or every
    # cookie starting with s: inherits a key-recovery weakness list
    rep_exs = dissect("s:%s.%s" % (ex_sid, _b64u(bytes(20))), now=SELFTEST_NOW)
    check("an 's:' value whose signature is not 32 bytes is NOT express",
          rep_exs["format"] != "express-signed", True,
          {"got_format": rep_exs["format"]})
    check("and the express rejection quotes the byte count",
          any("32 bytes" in r["because"] for r in rep_exs["rejections"]
              if r["format"] == "express-signed"), True)
    check("a value without the 's:' prefix is rejected for that reason",
          any("'s:' prefix" in r["because"] for r in rep_plain["rejections"]
              if r["format"] == "express-signed"), True)
    # express key recovery: signing with md5 instead of sha256 left the gate green
    ex_hit = dissect(ex_tok, now=SELFTEST_NOW, wordlist=hit_list, do_try_keys=True)
    check("try-keys recovers the express secret over the session id",
          (ex_hit["key_recovery"]["recovered"], ex_hit["key_recovery"]["key"]),
          (True, SELFTEST_KEY), {"scheme": ex_hit["key_recovery"]["scheme"]})
    check("and the express scheme names HMAC-SHA256",
          ex_hit["key_recovery"]["scheme"], "HMAC-SHA256 over the session id")
    ex_miss = dissect(ex_tok, now=SELFTEST_NOW, wordlist=miss_list,
                      do_try_keys=True)
    check("express try-keys keeps its negative countable",
          (ex_miss["key_recovery"]["recovered"],
           ex_miss["key_recovery"]["candidates"],
           ex_miss["key_recovery"]["verifications"]), (False, 3, 3))
    # the percent-decode-before-classify step: a browser sends this cookie
    # url-encoded, and without that step it comes back opaque
    rep_exq = dissect(urllib.parse.quote(ex_tok, safe=""), now=SELFTEST_NOW)
    check("a percent-encoded express cookie is decoded before classifying",
          (rep_exq["format"], rep_exq["url_decoded_before_classifying"]),
          ("express-signed", True))
    check("and a value that needed no decoding says so",
          rep_ex["url_decoded_before_classifying"], False)

    # 17. JWE. Also absent from the gate: probe_jwe could reject everything.
    def _jwe(header):
        return ".".join([_b64u(json.dumps(header).encode()), "", _b64u(bytes(12)),
                         _b64u(bytes(32)), _b64u(bytes(16))])
    rep_jwe = dissect(_jwe({"alg": "dir", "enc": "A256GCM"}), now=SELFTEST_NOW)
    check("JWE compact serialization classified", rep_jwe["format"], "jwe",
          {"evidence": rep_jwe["format_evidence"]})
    check("JWE protected header read",
          ((rep_jwe["decoded"].get("header") or {}).get("alg"),
           (rep_jwe["decoded"].get("header") or {}).get("enc")),
          ("dir", "A256GCM"))
    check("JWE weakness says the header is the only plaintext",
          [(w["id"], w["status"]) for w in rep_jwe["weaknesses"]],
          [("jwe-header-only", "present-in-token")])
    check("a JWE is NOT offered as a padding-oracle candidate",
          rep_jwe["padding_oracle_candidate"]["candidate"], False)
    # 5 parts is not the discriminator -- "enc" is
    rep_jn = dissect(_jwe({"alg": "dir"}), now=SELFTEST_NOW)
    check("5 dotted parts without an \"enc\" member are NOT a JWE",
          rep_jn["format"] != "jwe", True, {"got_format": rep_jn["format"]})
    check("and the JWE rejection names the missing enc member",
          any("enc" in r["because"] for r in rep_jn["rejections"]
              if r["format"] == "jwe"), True)

    # 18. the RSA branch of the signature-size check. Forcing matches=True left
    # the gate green, and that is the check that tells a 32-byte "RS256" from a
    # real one -- a false True here sends a solver past the whole finding.
    rs_head = {"alg": "RS256", "typ": "JWT"}
    rep_rs = dissect(_make_jwt(rs_head, {"sub": "guest"}, None) + _b64u(bytes(32)),
                     now=SELFTEST_NOW)
    check("RS256 with a 32-byte signature does not match its alg",
          (rep_rs["decoded"].get("signature") or {}).get("matches_alg"), False,
          {"note": (rep_rs["decoded"].get("signature") or {}).get("note")})
    check("and signature-length-mismatch is raised for it",
          [w["status"] for w in rep_rs["weaknesses"]
           if w["id"] == "signature-length-mismatch"], ["present-in-token"])
    check("alg-confusion is to-test for an asymmetric alg",
          [w["status"] for w in rep_rs["weaknesses"]
           if w["id"] == "alg-confusion"], ["to-test"])
    rep_rsok = dissect(_make_jwt(rs_head, {"sub": "guest"}, None)
                       + _b64u(bytes(256)), now=SELFTEST_NOW)
    check("RS256 with a 256-byte signature DOES match its alg",
          (rep_rsok["decoded"].get("signature") or {}).get("matches_alg"), True,
          {"note": (rep_rsok["decoded"].get("signature") or {}).get("note")})
    check("and then signature-length-mismatch is not-applicable",
          [w["status"] for w in rep_rsok["weaknesses"]
           if w["id"] == "signature-length-mismatch"], ["not-applicable"])

    # 19. the key-sourcing headers, written out here rather than read from the
    # constant they test: emptying KEY_SOURCING_HEADERS left the gate green.
    ks_header = {"alg": "HS256", "kid": "../../dev/null",
                 "jku": "http://evil.example/jwks.json", "jwk": {"kty": "oct"},
                 "x5u": "http://evil.example/c.pem", "x5c": ["MIIB"], "x5t": "abc"}
    rep_ks = dissect(_make_jwt(ks_header, {"sub": "guest"}, SELFTEST_KEY),
                     now=SELFTEST_NOW)
    check("every RFC 7515 key-sourcing header is surfaced",
          sorted(rep_ks["decoded"].get("key_sourcing_headers") or {}),
          sorted(EXPECTED_KEY_SOURCING_HEADERS))
    check("and each one gets its own weakness entry",
          sorted(w["id"] for w in rep_ks["weaknesses"]
                 if w["id"].startswith("header-")),
          sorted("header-" + n for n in EXPECTED_KEY_SOURCING_HEADERS))
    check("a traversal kid is called out as a path",
          [w["why_here"] for w in rep_ks["weaknesses"] if w["id"] == "header-kid"],
          ["the header carries kid=../../dev/null, which reads as a path or URL"])
    check("a plain HS256 header surfaces no key-sourcing header at all",
          (rep["decoded"].get("key_sourcing_headers"),
           [w["id"] for w in rep["weaknesses"] if w["id"].startswith("header-")]),
          ({}, []))

    # 20. nbf. Deleting the not_yet_valid line left the gate green, and a token
    # that is not valid yet looks exactly like a working one without it.
    nbf_future = _make_jwt({"alg": "HS256"},
                           {"sub": "guest", "nbf": int(SELFTEST_NOW) + 600,
                            "exp": int(SELFTEST_NOW) + 3600}, SELFTEST_KEY)
    rep_nbf = dissect(nbf_future, now=SELFTEST_NOW)
    check("a future nbf is reported as not yet valid",
          (rep_nbf["decoded"]["expiry"].get("nbf"),
           rep_nbf["decoded"]["expiry"].get("not_yet_valid")),
          (int(SELFTEST_NOW) + 600, True),
          {"nbf_iso": rep_nbf["decoded"]["expiry"].get("nbf_iso")})
    check("nbf is listed among the time claims",
          rep_nbf["decoded"].get("claims_time"), ["exp", "nbf"])
    check("a past nbf is reported as already valid",
          dissect(_make_jwt({"alg": "HS256"},
                            {"sub": "guest", "nbf": int(SELFTEST_NOW) - 600,
                             "exp": int(SELFTEST_NOW) + 3600}, SELFTEST_KEY),
                  now=SELFTEST_NOW)["decoded"]["expiry"].get("not_yet_valid"),
          False)

    # 21. a non-string alg. `alg in ALG_SIG_BYTES` raised TypeError on an
    # unhashable value, which cost the format, the decode AND every weakness
    # while the report still said ok -- on the one header shape a hand-built
    # algorithm-confusion attempt actually has.
    for label, bad_alg in (("object", {"nested": 1}), ("array", ["HS256"]),
                           ("null", None)):
        rep_bad = dissect("%s.%s.%s" % (
            _b64u(json.dumps({"alg": bad_alg, "typ": "JWT"}).encode()),
            _b64u(b'{"sub":"guest"}'), _b64u(bytes(32))), now=SELFTEST_NOW)
        bad_sig = rep_bad["decoded"].get("signature") or {}
        check("a JWT whose alg is a JSON %s still decodes" % label,
              (rep_bad["format"],
               (rep_bad["decoded"].get("claims") or {}).get("sub"),
               bad_sig.get("alg_is_a_json_string"), bad_sig.get("matches_alg")),
              ("jwt", "guest", False, None), {"note": bad_sig.get("note")})
        check("and a non-string alg is itself reported (%s)" % label,
              [w["status"] for w in rep_bad["weaknesses"]
               if w["id"] == "non-string-alg"], ["present-in-token"])
        # only the literal string "none" may confirm an unsecured JWS: str(None)
        # is "none", so a JSON null alg used to confirm it on a signed token
        check("and a JSON %s alg does not confirm alg=none" % label,
              [w["status"] for w in rep_bad["weaknesses"]
               if w["id"] == "alg-none"], ["to-test"])
    check("the string \"none\" still DOES confirm alg-none",
          [w["status"] for w in rep_none["weaknesses"] if w["id"] == "alg-none"],
          ["present-in-token"])
    check("a normal string alg raises no non-string-alg weakness",
          any(w["id"] == "non-string-alg" for w in rep["weaknesses"]), False)
    check("and a string alg is recorded as a string",
          rep["decoded"]["signature"]["alg_is_a_json_string"], True)

    # 22. the itsdangerous derivation sweep and the extra salts, both from real
    # library output. Returning b"BROKEN" from the concat derivation and dropping
    # the extra salts each left the gate green.
    concat = dissect(FIXTURES["itsd_concat"], now=FIXTURE_NOW,
                     wordlist=fixture_list, do_try_keys=True)
    check("the real concat-derivation token is classified itsdangerous",
          concat["format"], "itsdangerous")
    check("and its secret is recovered through the concat derivation",
          (concat["key_recovery"]["recovered"], concat["key_recovery"]["key"]),
          (True, FIXTURE_SECRET))
    check("and the scheme names the derivation that actually verified",
          concat["key_recovery"]["scheme"],
          "salt=cookie-session derivation=concat digest=sha1")
    no_salt = dissect(FIXTURES["itsd_extrasalt"], now=FIXTURE_NOW,
                      wordlist=fixture_list, do_try_keys=True)
    check("a non-Flask salt is NOT recovered without --salt",
          (no_salt["key_recovery"]["recovered"],
           no_salt["key_recovery"]["candidates"]), (False, 3),
          {"result": no_salt["key_recovery"]["result"]})
    with_salt = dissect(FIXTURES["itsd_extrasalt"], now=FIXTURE_NOW,
                        wordlist=fixture_list, do_try_keys=True,
                        extra_salts=[ITSD_EXTRA_SALT])
    check("and IS recovered once --salt supplies it",
          (with_salt["key_recovery"]["recovered"], with_salt["key_recovery"]["key"],
           with_salt["key_recovery"]["scheme"]),
          (True, FIXTURE_SECRET, "salt=my-app-salt derivation=hmac digest=sha1"))
    check("and the extra salt appears in the schemes the report lists",
          any("salt=%s" % ITSD_EXTRA_SALT in s
              for s in with_salt["key_recovery"]["schemes"]), True)

    # 23. all four Django salts, each against a token real Django signed with
    # exactly that salt. Deleting three of them left the gate green.
    for salt, token in sorted(DJANGO_SALT_FIXTURES.items()):
        got = dissect(token, now=FIXTURE_NOW, wordlist=fixture_list,
                      do_try_keys=True)
        check("Django salt %s recovers its own token" % salt,
              (got["format"], got["decoded"].get("timestamp"),
               got["key_recovery"]["recovered"], got["key_recovery"]["scheme"]),
              ("django-signed", DJANGO_SALT_FIXTURE_STAMP, True,
               "salt=%s digest=sha256" % salt))
    check("and the swept salt list still holds exactly those four",
          sorted(DJANGO_SALTS), sorted(DJANGO_SALT_FIXTURES))

    # 24. --max-keys. Ignoring the cap left the gate green; worse, a run that was
    # truncated and does not say so turns "0 of N verified" into a false negative.
    long_list = _write(os.path.join(tmpdir, "capped.txt"),
                       ["w%d" % i for i in range(7)] + [SELFTEST_KEY, "x", "y"])
    capped = dissect(tok, now=SELFTEST_NOW, wordlist=long_list, do_try_keys=True,
                     max_keys=5)["key_recovery"]
    check("--max-keys really caps the candidate count and says it truncated",
          (capped["candidates"], capped["truncated_at_max_keys"],
           capped["recovered"]), (5, True, False), {"result": capped["result"]})
    uncapped = dissect(tok, now=SELFTEST_NOW, wordlist=long_list,
                       do_try_keys=True, max_keys=0)["key_recovery"]
    check("--max-keys 0 reads the whole list and finds the key past the cap",
          (uncapped["candidates"], uncapped["truncated_at_max_keys"],
           uncapped["recovered"]), (10, False, True))

    # 25. the stdin reading rule. '.' and '+' are legal in an RFC 6265 cookie
    # name, so banning them silently turned connect.sid -- express-session's
    # DEFAULT name -- into a nameless bare token that classified opaque.
    for name in ("connect.sid", ".AspNetCore.Session", "session+id"):
        check("%s=... is read as a cookie header" % name,
              looks_like_cookie_header("%s=%s" % (name, ex_tok), SELFTEST_NOW),
              True)
    check("and the jar keeps the dotted name",
          [p[0] for p in split_cookie_header("connect.sid=%s; csrf=abc" % ex_tok)],
          ["connect.sid", "csrf"])
    check("so --stdin agrees with --cookie on a dotted express cookie",
          stdin_reading("connect.sid=%s" % ex_tok, False, False, SELFTEST_NOW)[0],
          "cookie-header")
    # the NOT-a-jar direction, which is what the character ban was there for. The
    # '=' has to be real base64 padding: such a line used to be split into a
    # cookie whose name was the token and whose value was the pad character.
    padded = base64.urlsafe_b64encode(
        json.dumps({"user": "guest"}, separators=(",", ":")).encode()).decode()
    check("the padded token really carries base64 padding", padded.endswith("=="),
          True, {"value": padded})
    check("a padded bare base64 token is NOT read as a cookie header",
          looks_like_cookie_header(padded, SELFTEST_NOW), False)
    check("and the reason names the format it classified as",
          looks_like_cookie_header(padded, SELFTEST_NOW, explain=True)[1],
          "the whole line classifies as base64-json, so it is one token and not "
          "a jar")
    check("so it is dissected whole, not split on its padding",
          [(n, dissect(v, name=n, now=SELFTEST_NOW)["format"])
           for n, v in ([("--stdin", padded)]
                        if stdin_reading(padded, False, False,
                                         SELFTEST_NOW)[0] == "bare-token"
                        else split_cookie_header(padded))],
          [("--stdin", "base64-json")])
    check("--raw forces a jar-shaped line to one bare token",
          stdin_reading("connect.sid=%s" % ex_tok, True, False, SELFTEST_NOW)[0],
          "bare-token")
    check("--jar forces a token-shaped line to a cookie header",
          stdin_reading("session=%s" % rails_tok, False, True, SELFTEST_NOW)[0],
          "cookie-header")

    # 26. a jar piece this tool cannot use is counted, not silently dropped
    dropped = []
    kept = split_cookie_header("good=%s; bad name=x; empty=; nokey" % plain,
                               dropped=dropped)
    check("a malformed jar keeps only the usable pieces",
          [p[0] for p in kept], ["good"])
    check("and every dropped piece is accounted with its reason",
          [d["reason"] for d in dropped],
          ["'bad name' is not a legal RFC 6265 cookie name",
           "the value after '=' is empty",
           "no '=' in this piece, so it names no cookie"])

    # 27. every Set-Cookie, not only the last. Measured against a three-cookie
    # response, reading the collapsed headers dict reported one cookie.
    three = ["first=%s; Path=/; HttpOnly" % plain, "second=%s; Path=/" % tok,
             "third=%s; Path=/" % plain]
    resp = {"headers": {"Set-Cookie": three[-1], "Content-Type": "text/plain"},
            "headers_all": [["Set-Cookie", v] for v in three]
                           + [["Content-Type", "text/plain"]],
            "set_cookies": three}
    view = set_cookie_view(resp)
    check("all three Set-Cookie headers are read, in order",
          [p[0] for p in view["cookies"]], ["first", "second", "third"])
    check("and the header count is reported", view["header_count"], 3)
    check("and each value is dissected under its own name",
          {t["name"]: t["format"] for t in
           [dissect(v, name=n, now=SELFTEST_NOW) for n, v in view["cookies"]]},
          {"first": "base64-json", "second": "jwt", "third": "base64-json"})
    collapsed = set_cookie_view({"headers": resp["headers"]})
    check("a reader with no set_cookies list says what it cannot see",
          "only the LAST" in collapsed["source"], True)
    check("and then it really does see only the last one",
          [p[0] for p in collapsed["cookies"]], ["third"])

    # 28. a value that could not be analysed is counted, so ok and the exit code
    # stop claiming a clean run over a token whose analysis was lost
    rows = [{"name": "--token", "format": "error", "error": "TypeError: x",
             "padding_oracle_candidate": {"candidate": False}},
            {"name": "c", "format": "jwt",
             "padding_oracle_candidate": {"candidate": False}}]
    check("an unanalysable value is counted as an error, not as one more row",
          (summarize(rows)["errors"], summarize(rows)["tokens"]),
          (["--token"], 2))
    check("and a clean run reports no errors",
          summarize(rows[1:])["errors"], [])

    failures = [c["name"] for c in checks if not c["pass"]]
    return {"mode": "session-dissect-selftest",
            "reference_time": SELFTEST_NOW, "reference_time_iso": iso(SELFTEST_NOW),
            "pyjwt_present": pyjwt is not None,
            "tmpdir": tmpdir, "tmpdir_removed_after": removed,
            "checks": checks, "total": len(checks), "failures": len(failures),
            "failed": failures,
            "skipped": skipped, "skipped_count": len(skipped),
            "verdict": "PASS" if not failures else "FAIL"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    src = parser.add_argument_group("input (at least one)")
    src.add_argument("--token", action="append", default=[], metavar="VALUE",
                     help="one token value; repeatable")
    src.add_argument("--cookie", action="append", default=[], metavar="JAR",
                     help="'name=value; other=value' -- every value is dissected")
    src.add_argument("--url", metavar="URL",
                     help="ONE GET, to read Set-Cookie. The only request this "
                          "tool ever makes")
    src.add_argument("--stdin", action="store_true",
                     help="read tokens from stdin, one per line. A line is read as "
                          "a cookie header when the text before the first '=' is a "
                          "legal RFC 6265 cookie name (dots included, so "
                          "connect.sid works) AND the whole line matches no token "
                          "format; the choice made for each line is reported. "
                          "--raw and --jar force it")
    src.add_argument("--raw", action="store_true",
                     help="with --stdin, treat every line as a bare token")
    src.add_argument("--jar", action="store_true",
                     help="with --stdin, treat every line as a cookie header")

    req = parser.add_argument_group("the one allowed request")
    req.add_argument("-H", "--header", action="append", default=[], metavar="K: V")
    req.add_argument("--timeout", type=float, default=10.0)
    req.add_argument("--follow-redirects", action="store_true",
                     help="off by default: a 302 usually carries the cookie")

    keys = parser.add_argument_group("offline key recovery (no requests)")
    keys.add_argument("--try-keys", action="store_true", dest="do_try_keys",
                      help="HMAC every wordlist line against this token, locally")
    keys.add_argument("--wordlist", metavar="PATH",
                      help="required by --try-keys; SecLists is under "
                           "/home/kali/wordlists/SecLists/")
    keys.add_argument("--max-keys", type=int, default=MAX_KEYS_DEFAULT,
                      help="cap the candidate count; 0 = no cap (default %d)"
                           % MAX_KEYS_DEFAULT)
    keys.add_argument("--salt", action="append", default=[], metavar="SALT",
                      help="extra itsdangerous salt to try besides %s" % FLASK_SALT)

    parser.add_argument("--challenge", default="<challenge>",
                        help="name used in the emitted http_probe commands")
    parser.add_argument("--now", type=float, metavar="EPOCH",
                        help="reference time for every expiry decision "
                             "(default: the real clock)")
    parser.add_argument("--no-pyjwt", action="store_true",
                        help="force the builtin base64url decoder")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        out = selftest()
        httpkit.jprint(out, compact=args.compact)
        return 0 if out["verdict"] == "PASS" else 1

    if not (args.token or args.cookie or args.url or args.stdin):
        parser.error("give one of --token, --cookie, --url or --stdin")

    now = args.now if args.now is not None else time.time()
    report = {
        "mode": "session-dissect",
        "reference_time": now, "reference_time_iso": iso(now),
        "optional_deps": {"pyjwt": {"present": pyjwt is not None,
                                    "version": getattr(pyjwt, "__version__", None),
                                    "used": pyjwt is not None and not args.no_pyjwt}},
        "boundary": ("analysis only: nothing is forged and nothing is sent. "
                     "%s request was made; --try-keys is local HMAC."
                     % ("One GET" if args.url else "No")),
    }
    if args.raw and args.jar:
        parser.error("--raw and --jar are opposites; pass at most one")
    pairs = collect(args, report, now)
    if not pairs:
        report["ok"] = False
        report["tokens"] = []
        report["problem"] = ("no token value was obtained from the inputs given"
                             + (" -- the GET returned no Set-Cookie"
                                if args.url else ""))
        httpkit.jprint(report, compact=args.compact)
        return 1

    report["ok"] = True
    report["tokens"] = []
    for name, value in pairs:
        try:
            report["tokens"].append(
                dissect(value, name=name, now=now, challenge=args.challenge,
                        wordlist=args.wordlist, do_try_keys=args.do_try_keys,
                        max_keys=args.max_keys, extra_salts=args.salt,
                        use_pyjwt=not args.no_pyjwt))
        except Exception as exc:
            # one unusual value in a jar must not cost the report for the rest;
            # the failure is recorded as a value, not raised away
            report["tokens"].append(
                {"name": name, "length": len(value),
                 "value_preview": clip(value, 160), "format": "error",
                 "error": "%s: %s" % (type(exc).__name__, exc),
                 "padding_oracle_candidate": {"candidate": False,
                                              "statement": "not reached"},
                 "weaknesses": [], "weakness_counts": {"total": 0}})
    report["summary"] = summarize(report["tokens"])
    # a value that could not be analysed is a failure of this run, not one more
    # row: ok and the exit code have to say so or the report claims a clean pass
    report["ok"] = not report["summary"]["errors"]
    if report["summary"]["errors"]:
        report["problem"] = ("%d of %d values could not be analysed: %s -- read "
                             "each one's error field"
                             % (len(report["summary"]["errors"]),
                                len(report["tokens"]),
                                ", ".join(report["summary"]["errors"])))
    httpkit.jprint(report, compact=args.compact)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
