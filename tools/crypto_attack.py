#!/usr/bin/env python3
"""Run one standard cryptographic attack by name, with JSON in and JSON out.

A result is a candidate until it decrypts or validates against the supplied
artifact: this tool reports what it recovered and how it verified it, and never
asserts a flag. Every attack carries its APPLICABILITY CONDITION -- the
observable that says "use me" -- printed by `list`.

    python3 tools/crypto_attack.py list
    python3 tools/crypto_attack.py describe wiener
    python3 tools/crypto_attack.py wiener --n 0x... --e 0x...
    python3 tools/crypto_attack.py hastad --pairs n1:c1,n2:c2,n3:c3 --e 3
    python3 tools/crypto_attack.py identify --file output.txt
    python3 tools/crypto_attack.py selftest

Exit status: 0 when the attack recovered its target, 1 when it did not (a
recorded negative result), 2 on a usage or input error.
"""
import argparse
import base64
import binascii
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import crypto                                                  # noqa: E402
from crypto import (numtheory as nt, rsa_attacks as rsa, dlog, lcg, lfsr,      # noqa: E402
                    hash_ext, hnp, mt19937, xor)


# ------------------------------------------------------------------ value input
def as_int(value, name="value"):
    """Accept 12345, 0xdeadbeef, 1_000, or a decimal string with whitespace."""
    if isinstance(value, int):
        return value
    if value is None:
        raise ValueError("%s is required" % name)
    text = str(value).strip().replace("_", "").replace(" ", "")
    try:
        return int(text, 16) if text.lower().startswith("0x") else int(text)
    except ValueError:
        raise ValueError("%s is not an integer: %r" % (name, value))


def as_bytes(value, name="value"):
    """Accept raw text, hex:..., b64:..., or a bare hex string."""
    if isinstance(value, bytes):
        return value
    text = str(value)
    if text.startswith("hex:"):
        return bytes.fromhex(text[4:])
    if text.startswith("b64:"):
        return base64.b64decode(text[4:])
    if re.fullmatch(r"[0-9a-fA-F]{2,}", text) and len(text) % 2 == 0:
        try:
            return bytes.fromhex(text)
        except ValueError:
            pass
    return text.encode()


def int_list(value, name="list"):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [as_int(v, name) for v in value]
    return [as_int(v, name) for v in re.split(r"[,\s]+", str(value).strip()) if v]


def load_json_input(path):
    if path in ("-", "/dev/stdin"):
        return json.load(sys.stdin)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def merged(args, keys):
    """Values from --in <json> filled in for any flag not given on the command line.

    A JSON key may be written either way: secret-len as the flag spells it, or
    secret_len as Python would. Both reach the same parameter, because guessing
    which spelling a tool wants is exactly the friction this CLI exists to remove.
    """
    data = {}
    if getattr(args, "in_file", None):
        raw = load_json_input(args.in_file)
        if not isinstance(raw, dict):
            raise ValueError("--in must contain a JSON object")
        canonical = {k.replace("-", "_"): k for k in keys}
        for given, value in raw.items():
            key = canonical.get(str(given).replace("-", "_"), given)
            data[key] = value
    for key in keys:
        val = getattr(args, key.replace("-", "_"), None)
        if val is not None:
            data[key] = val
    return data


def need(data, key, conv=as_int):
    if key not in data or data[key] is None:
        raise ValueError("missing required parameter: %s" % key)
    return conv(data[key], key) if conv else data[key]


def opt(data, key, default=None, conv=None):
    if key not in data or data[key] is None:
        return default
    return conv(data[key], key) if conv else data[key]


# ----------------------------------------------------------------- big-int JSON
def jsonable(obj, hex_threshold=1 << 64):
    """Large integers are emitted as decimal AND hex so they can be pasted anywhere."""
    if isinstance(obj, dict):
        out = {}
        for key, val in obj.items():
            out[key] = jsonable(val, hex_threshold)
            if isinstance(val, int) and abs(val) >= hex_threshold and not isinstance(val, bool):
                out[key + "_hex"] = "0x%x" % val
        return out
    if isinstance(obj, (list, tuple)):
        return [jsonable(v, hex_threshold) for v in obj]
    if isinstance(obj, bytes):
        return obj.hex()
    return obj


def emit(args, attack, result, primary_key, notes=None, next_action=None):
    ok = True
    if primary_key is not None and isinstance(result, dict):
        ok = result.get(primary_key) is not None
    elif result is None:
        ok = False
    payload = {
        "mode": "crypto-attack",
        "attack": attack,
        "status": "recovered" if ok else "not-recovered",
        "applicability": crypto.applicability(attack) if attack in crypto.ATTACKS else None,
        "lll_backend": crypto.lll.backend(),
        "result": jsonable(result),
        "notes": notes or [],
        "next_action": next_action or (
            "verify the recovered value against the artifact (decrypt, check a tag, "
            "or recompute the public key) before recording anything"
            if ok else "record this negative result and change mechanism class"),
    }
    text = json.dumps(payload, ensure_ascii=False) if args.json \
        else json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    return 0 if ok else 1


# --------------------------------------------------------------------- identify
_PRINTABLE = set(range(32, 127)) | {9, 10, 13}
_HEXSTR = re.compile(r"[0-9a-fA-F]+\Z")
# Standard sizes, not facts about any one handout: GCM/Poly1305 tags are 16
# bytes, AEAD nonces are 8..16, and a prime-field curve coordinate is 160..528
# bits. A detector fires on the arrangement of fields, never on a field's name.
_TAG_BYTES = 16
_NONCE_BYTES = (8, 16)
_COORD_BITS = (160, 528)


def _walk_structure(parsed):
    """One pass over parsed JSON: integers, hex strings, int lists, object shapes.

    Returns (ints, hexes, hex_text, int_lists, objects) where `objects` maps an
    object's path to {field name: (kind, size)} with kind in int|hex|int-list|
    list|other, size in bits for an int and in bytes for a hex string. Every
    detector below reads only this structure.
    """
    ints, hexes, hex_text, int_lists, objects = {}, {}, {}, {}, {}

    def record(parent, name, kind, size):
        if parent is not None:
            objects.setdefault(parent, {})[name] = (kind, size)

    def walk(node, path="", parent=None, name=None):
        if isinstance(node, dict):
            objects.setdefault(path, {})
            record(parent, name, "object", len(node))
            for key, val in node.items():
                walk(val, path + "/" + str(key), path, str(key))
        elif isinstance(node, list):
            bits = [v.bit_length() for v in node
                    if isinstance(v, int) and not isinstance(v, bool)]
            if node and len(bits) == len(node):
                int_lists[path] = bits
                record(parent, name, "int-list", len(bits))
            else:
                record(parent, name, "list", len(node))
            for i, val in enumerate(node):
                walk(val, path + "/%d" % i, path, str(i))
        elif isinstance(node, bool):
            record(parent, name, "other", 0)
        elif isinstance(node, int):
            ints[path] = node
            record(parent, name, "int", node.bit_length())
        elif isinstance(node, str):
            text = node.strip()
            if re.fullmatch(r"[0-9a-fA-F]{16,}", text):
                ints[path] = int(text, 16)          # unchanged: feeds integer_fields
            if len(text) >= 8 and len(text) % 2 == 0 and _HEXSTR.match(text):
                hexes[path] = len(text) // 2
                hex_text[path] = text.lower()
                record(parent, name, "hex", len(text) // 2)
            else:
                record(parent, name, "other", len(text))
        else:
            record(parent, name, "other", 0)

    walk(parsed)
    return ints, hexes, hex_text, int_lists, objects


def _int_list_values(ints, path, count):
    """The integers of one all-integer list, in order, read back out of `ints`."""
    return [ints[path + "/%d" % i] for i in range(count)]


def _detect_lcg(ints, int_lists, objects):
    """A run of same-width integers, optionally beside a modulus-sized integer.

    Shape only: k >= 3 list entries whose bit widths agree to within max(4,
    w/8), and -- for the strong form -- a sibling scalar whose width is the
    output width or a couple of bits above it (the modulus the outputs reduce
    under). Truncated vs full state is decided by that width gap.
    """
    obs, suggest = [], []
    for path, bits in sorted(int_lists.items()):
        width = max(bits)
        if len(bits) < 3 or width < 24:
            continue
        if width - min(bits) > max(4, width // 8):
            continue                       # not one width: a mixed bag, not a stream
        parent = path.rsplit("/", 1)[0]
        mods = [(name, size) for name, (kind, size) in objects.get(parent, {}).items()
                if kind == "int" and width <= size <= width + 2]
        if mods:
            name, size = max(mods, key=lambda kv: kv[1])
            mod_path = parent + "/" + name
            mod_val = ints.get(mod_path)
            obs.append("LCG-shaped at %s: %d outputs of %d..%d bits beside a %d-bit "
                       "modulus-like sibling %r" % (path, len(bits), min(bits),
                                                    width, size, name))
            truncated = mod_val is not None and width < mod_val.bit_length() - 2
            suggest.append("lcg-recover --outputs %s --modulus %s (falsifier: the "
                           "recovered (a, c) must reproduce the outputs you did not "
                           "feed it)%s" % (path, mod_path,
                                           "; lcg-truncated -- the outputs are "
                                           "narrower than the modulus"
                                           if truncated else ""))
        elif len(bits) >= 6:
            # Structure alone is too weak here -- any list of same-width integers
            # looks like this -- so the gcd-over-differences test is run as the
            # falsifier before the shape is reported at all.
            try:
                probe = lcg.lcg_recover_modulus(_int_list_values(ints, path,
                                                                len(bits))[:12])
            except (ValueError, TypeError, ZeroDivisionError):
                probe = {"modulus": None}
            if not probe.get("modulus"):
                continue
            obs.append("%d same-width integers (%d..%d bits) at %s with no modulus "
                       "sibling, and the gcd-over-differences test on them returns a "
                       "candidate %d-bit modulus: consistent with consecutive LCG "
                       "outputs" % (len(bits), min(bits), width, path,
                                    int(probe["modulus"]).bit_length()))
            suggest.append("lcg-unknown-modulus on %s (then lcg-predict; falsifier: "
                           "the parameters must reproduce a held-back output); "
                           "mt19937-clone instead if the width is 32 and there are "
                           "624 of them" % path)
    return obs, suggest


def _on_known_curve(x, y):
    """Name the standard curve a coordinate pair satisfies, or None."""
    for name, params in sorted(crypto.ec.CURVES.items()):
        if x >= params["p"] or y >= params["p"]:
            continue         # cannot be a coordinate in this field; not a width test
        for point in ((x, y), (y, x)):
            if crypto.ec.on_curve(point, params["p"], params["a"], params["b"]):
                return name
    return None


def _detect_ecdsa(ints, int_lists, objects):
    """A curve-point-shaped pair, and/or a list of signature-shaped tuples.

    Point: an object holding exactly two integers of curve-coordinate width
    whose widths agree; confirmed for free when the pair satisfies a standard
    curve equation. Signatures: a list of >= 2 sibling objects each holding two
    or three same-width integers of that same width class, or one flat integer
    list of that width whose length divides into pairs or triples.
    """
    obs, suggest = [], []
    lo, hi = _COORD_BITS
    points, sig_lists = [], []
    for path, fields in sorted(objects.items()):
        scalars = [(name, size) for name, (kind, size) in fields.items()
                   if kind == "int"]
        if len(scalars) == len(fields) == 2:
            (n1, w1), (n2, w2) = scalars
            if abs(w1 - w2) <= 8 and lo <= max(w1, w2) <= hi:
                curve = _on_known_curve(ints[path + "/" + n1], ints[path + "/" + n2])
                points.append((path, max(w1, w2), curve))
    for path, fields in sorted(objects.items()):
        for name, (kind, size) in sorted(fields.items()):
            child = path + "/" + name
            if kind != "list" or size < 2:
                continue
            widths = []
            for i in range(size):
                shape = objects.get(child + "/%d" % i)
                if not shape:
                    widths = []
                    break
                scalars = [s for k, s in shape.values() if k == "int"]
                if len(scalars) != len(shape) or not 2 <= len(scalars) <= 3:
                    widths = []
                    break
                widths.append(max(scalars))
            if widths and lo <= max(widths) <= hi \
                    and max(widths) - min(widths) <= 16:
                sig_lists.append((child, size, max(widths)))
    for path, bits in sorted(int_lists.items()):
        if len(bits) >= 4 and lo <= max(bits) <= hi \
                and max(bits) - min(bits) <= 16 and (len(bits) % 2 == 0
                                                     or len(bits) % 3 == 0):
            sig_lists.append((path, len(bits), max(bits)))
    # An unconfirmed pair of same-width big integers is also what {n, c} looks
    # like, so it is only reported when a standard curve equation holds or a
    # signature list of the same scalar width is present to corroborate it.
    shown = [p for p in points if p[2]] or (points if sig_lists else [])
    for path, width, curve in shown:
        obs.append("curve-point-shaped pair at %s: two %d-bit coordinates%s"
                   % (path, width,
                      ", and they satisfy the %s curve equation" % curve if curve
                      else ", same width as the signature scalars (no standard "
                           "curve equation matched: custom or unknown curve)"))
    for path, count, width in sig_lists:
        obs.append("signature-shaped list at %s: %d tuples of %d-bit scalars"
                   % (path, count, width))
    points = shown
    if points and sig_lists:
        suggest.append("ecdsa-nonce-reuse first if any r repeats in the list, else "
                       "hnp-ecdsa (biased nonce, lattice); the public point is the "
                       "falsifier -- a recovered d must regenerate it")
    elif points:
        suggest.append("hnp-ecdsa / ecdsa-nonce-reuse need (r, s, z) tuples, and "
                       "none are in the clear here: the published point says to "
                       "look for the signature list inside an encrypted stage or "
                       "a separate service response")
    elif sig_lists:
        suggest.append("ecdsa-nonce-reuse if any r repeats, else hnp-ecdsa; no "
                       "public point is published, so verify a recovered key by "
                       "re-signing one listed message instead")
    return obs, suggest


def _detect_aead(hex_text, objects):
    """Nonce/ciphertext/tag triples of hex fields, and how many stages there are.

    Shape only: an object whose three fields are all hex, one exactly 16 bytes
    (tag), one 8..16 bytes (nonce), one strictly longer than 16 bytes
    (ciphertext). Several such siblings with a consistent tag width is a staged
    ladder; a repeated nonce is reported because it is a stronger finding.
    """
    obs, suggest, claimed = [], [], set()
    blobs = []
    for path, fields in sorted(objects.items()):
        hx = [(name, size) for name, (kind, size) in fields.items() if kind == "hex"]
        if len(hx) != 3 or len(fields) != 3:
            continue
        sizes = sorted(size for _, size in hx)
        ct = [name for name, size in hx if size == sizes[-1] and size > _TAG_BYTES]
        if len(ct) != 1:
            continue
        rest = [(name, size) for name, size in hx if name != ct[0]]
        tag = [name for name, size in rest if size == _TAG_BYTES]
        if not tag:
            continue
        nonce = [(name, size) for name, size in rest if name != tag[0]
                 and _NONCE_BYTES[0] <= size <= _NONCE_BYTES[1]]
        if not nonce:
            continue
        blobs.append({"path": path, "nonce": nonce[0][0], "nonce_bytes": nonce[0][1],
                      "ct": ct[0], "ct_bytes": sizes[-1], "tag": tag[0],
                      "nonce_value": hex_text.get(path + "/" + nonce[0][0])})
        claimed.update(path + "/" + name for name, _ in hx)
    if not blobs:
        return obs, suggest, claimed
    nonce_widths = sorted({b["nonce_bytes"] for b in blobs})
    ct_widths = sorted({b["ct_bytes"] for b in blobs})
    if len(blobs) == 1:
        obs.append("one AEAD-shaped blob at %s: %d-byte nonce %r, %d-byte "
                   "ciphertext %r, %d-byte tag %r"
                   % (blobs[0]["path"], blobs[0]["nonce_bytes"], blobs[0]["nonce"],
                      blobs[0]["ct_bytes"], blobs[0]["ct"], _TAG_BYTES,
                      blobs[0]["tag"]))
        suggest.append("no key is in the handout: the tag is the oracle -- derive a "
                       "candidate key from the other observations and let "
                       "decrypt_and_verify accept or reject it")
    else:
        obs.append("%d sibling AEAD-shaped blobs (%s): each is a hex triple with a "
                   "%s-byte nonce, a %d..%d-byte ciphertext and a consistently "
                   "%d-byte tag -> authenticated multi-stage ladder, no key in the "
                   "clear" % (len(blobs), ", ".join(b["path"] for b in blobs[:6])
                              + (", ..." if len(blobs) > 6 else ""),
                              "/".join(str(w) for w in nonce_widths),
                              ct_widths[0], ct_widths[-1], _TAG_BYTES))
        suggest.append("work the ladder one stage at a time: solve the ONE stage "
                       "whose own fields carry a solvable shape (see the other "
                       "observations), then read the next stage's parameters out of "
                       "the plaintext you recovered. Every stage is tag-verified, "
                       "so a wrong key fails loudly and never needs guessing")
    seen = {}
    for blob in blobs:
        if blob["nonce_value"]:
            seen.setdefault(blob["nonce_value"], []).append(blob["path"])
    reused = {value: paths for value, paths in seen.items() if len(paths) > 1}
    if reused:
        obs.append("nonce value repeats across blobs: %s"
                   % "; ".join("%s at %s" % (value[:16], ", ".join(paths))
                               for value, paths in sorted(reused.items())))
        suggest.append("same key/nonce twice in a counter-mode AEAD leaks the "
                       "keystream by XOR and, for GCM, the authentication key: "
                       "start from the XOR of the two ciphertexts")
    return obs, suggest, claimed


def cmd_identify(args):
    """Cheap triage: sizes, bit lengths, block repeats and which attack to try."""
    if args.file:
        with open(args.file, "rb") as handle:
            raw = handle.read()
    elif args.hex:
        raw = bytes.fromhex(args.hex)
    elif args.text is not None:
        raw = args.text.encode()
    else:
        raise ValueError("supply --file, --hex or --text")

    obs, suggest = [], []
    report = {"bytes": len(raw)}
    try:
        parsed = json.loads(raw.decode("utf-8", "replace"))
        report["json"] = True
        ints, hexes, hex_text, int_lists, objects = _walk_structure(parsed)
        report["integer_fields"] = {k: v.bit_length() for k, v in
                                   sorted(ints.items(), key=lambda kv: -kv[1].bit_length())[:40]}
        report["hex_fields"] = {k: v for k, v in
                               sorted(hexes.items(), key=lambda kv: -kv[1])[:40]}
        report["integer_lists"] = {k: v for k, v in sorted(int_lists.items())[:20]}
        aead_obs, aead_suggest, aead_paths = _detect_aead(hex_text, objects)
        # A field already explained as an AEAD nonce, ciphertext or tag is not an
        # RSA parameter, whatever it happens to be called: without this, a hex
        # nonce named "N" counts as a modulus and asks for batch-gcd.
        rsa_ints = {k: v for k, v in ints.items() if k not in aead_paths}
        names = {k.rsplit("/", 1)[-1].lower() for k in rsa_ints}
        if {"n", "e", "c"} & names:
            obs.append("RSA-shaped fields present")
        e_vals = [v for k, v in rsa_ints.items()
                  if k.rsplit("/", 1)[-1].lower() == "e"]
        n_vals = [v for k, v in rsa_ints.items()
                  if k.rsplit("/", 1)[-1].lower() == "n"]
        if e_vals and all(v <= 65537 for v in e_vals):
            obs.append("small public exponent(s): %s" % sorted(set(e_vals)))
            suggest.append("small-e-root; hastad if the same message appears under "
                           "several moduli")
        if e_vals and any(v.bit_length() > 64 for v in e_vals):
            obs.append("public exponent as large as the modulus")
            suggest.append("wiener, then boneh-durfee")
        if len(n_vals) >= 2:
            suggest.append("batch-gcd across the moduli")
        if {"r", "s"} <= names:
            obs.append("signature-shaped (r, s) pairs")
            suggest.append("ecdsa-nonce-reuse if any r repeats, else hnp-ecdsa")
        for detector in (_detect_lcg(ints, int_lists, objects),
                         _detect_ecdsa(ints, int_lists, objects),
                         (aead_obs, aead_suggest)):
            for line in detector[0]:
                if line not in obs:
                    obs.append(line)
            for line in detector[1]:
                if line not in suggest:
                    suggest.append(line)
    except (ValueError, UnicodeDecodeError):
        report["json"] = False

    if not report.get("json"):
        printable = sum(1 for b in raw if b in _PRINTABLE)
        report["printable_ratio"] = round(printable / max(1, len(raw)), 3)
        blob = raw
        stripped = bytes(re.sub(rb"\s", b"", raw))
        if re.fullmatch(rb"[0-9a-fA-F]+", stripped) and len(stripped) % 2 == 0:
            blob = binascii.unhexlify(stripped)
            obs.append("body is hex: %d bytes decoded" % len(blob))
        elif re.fullmatch(rb"[A-Za-z0-9+/=\s]+", raw) and len(stripped) % 4 == 0:
            try:
                blob = base64.b64decode(stripped)
                obs.append("body is base64: %d bytes decoded" % len(blob))
            except binascii.Error:
                blob = raw
        report["decoded_bytes"] = len(blob)
        for size in (8, 16):
            blocks = [blob[i:i + size] for i in range(0, len(blob) - len(blob) % size, size)]
            dup = [b.hex() for b, count in collections.Counter(blocks).items() if count > 1]
            if dup:
                obs.append("%d-byte block repeats (%d distinct) -> ECB or a reused "
                           "keystream block" % (size, len(dup)))
                suggest.append("identify ECB structure; byte-at-a-time recovery")
        if len(blob) % 16 == 0 and len(blob) >= 32:
            obs.append("length is a multiple of 16: CBC/ECB block cipher")
    report["observations"] = obs
    report["suggested_attacks"] = suggest or ["nothing matched a standard shape; "
                                              "open skills/crypto-triage"]
    payload = {"mode": "crypto-attack", "attack": "identify", "status": "reported",
               "result": report,
               "next_action": "pick ONE suggested attack and run it; do not run three"}
    print(json.dumps(payload, ensure_ascii=False,
                     **({} if args.json else {"indent": 2})))
    return 0


# ------------------------------------------------------------------- dispatchers
def cmd_list(args):
    payload = {"mode": "crypto-attack", "attack": "list",
               "lll_backend": crypto.lll.backend(),
               "optional_libs": {"fpylll": crypto.lll.HAVE_FPYLLL,
                                 "mpmath": crypto.polynomials.HAVE_MPMATH},
               "attacks": crypto.describe_all(),
               "next_action": "pick the attack whose applicability matches an "
                              "observable you have actually seen"}
    print(json.dumps(payload, ensure_ascii=False,
                     **({} if args.json else {"indent": 2})))
    return 0


def cmd_describe(args):
    name = args.name
    if name not in crypto.ATTACKS:
        raise ValueError("unknown attack %r; run `list`" % name)
    fn = crypto.ATTACKS[name][0]
    payload = {"mode": "crypto-attack", "attack": name,
               "function": fn.__module__ + "." + fn.__name__,
               "applicability": crypto.applicability(name),
               "docstring": (fn.__doc__ or "").strip()}
    print(json.dumps(payload, ensure_ascii=False,
                     **({} if args.json else {"indent": 2})))
    return 0


def cmd_selftest(args):
    from crypto import selftest
    argv = ["--json"] if args.json else []
    if args.slow:
        argv.append("--slow")
    saved = sys.argv
    sys.argv = ["selftest"] + argv
    try:
        return selftest.main()
    finally:
        sys.argv = saved


def cmd_attack(args):
    name = args.command
    data = merged(args, ARG_KEYS[name])
    fn, primary, _family = crypto.ATTACKS[name]
    notes = []

    if name == "hastad":
        pairs = data.get("pairs")
        if isinstance(pairs, str):
            pairs = [tuple(as_int(x) for x in part.split(":"))
                     for part in re.split(r"[,\s]+", pairs.strip()) if part]
        elif isinstance(pairs, list):
            pairs = [(as_int(p[0]), as_int(p[1])) for p in pairs]
        else:
            ns, cs = int_list(data.get("n"), "n"), int_list(data.get("c"), "c")
            pairs = list(zip(ns, cs))
        if not pairs:
            raise ValueError("supply --pairs n1:c1,n2:c2,... (or n= and c= lists)")
        result = fn(pairs, opt(data, "e", 3, as_int), opt(data, "bytes", None, as_int))
    elif name == "small-e-root":
        result = fn(need(data, "n"), need(data, "e"), need(data, "c"),
                    opt(data, "max-k", 1 << 16, as_int))
    elif name == "common-modulus":
        result = fn(need(data, "n"), need(data, "e1"), need(data, "c1"),
                    need(data, "e2"), need(data, "c2"))
    elif name == "wiener":
        result = fn(need(data, "n"), need(data, "e"))
    elif name == "boneh-durfee":
        result = fn(need(data, "n"), need(data, "e"), float(opt(data, "delta", 0.28)),
                    opt(data, "m", 6, as_int), opt(data, "t", None, as_int))
        notes.append("d < n**0.292 is the theoretical ceiling; escalate m if this fails")
    elif name == "boneh-durfee-escalate":
        mlist = int_list(opt(data, "m", "6,7,8"), "m") or [6, 7, 8]
        result = fn(need(data, "n"), need(data, "e"), float(opt(data, "delta", 0.28)),
                    m_list=mlist)
    elif name == "coppersmith-high-bits":
        result = fn(need(data, "n"), need(data, "known"), need(data, "bits"),
                    need(data, "p-bits"), opt(data, "m", 8, as_int),
                    opt(data, "t", None, as_int))
        notes.append("the known part must be the TOP bits of the prime; the unknown "
                     "part is centred automatically")
    elif name == "coppersmith-core":
        result = fn(need(data, "n"), need(data, "a"), need(data, "X"),
                    opt(data, "m", 8, as_int), opt(data, "t", None, as_int))
    elif name == "fermat":
        got = fn(need(data, "n"), opt(data, "max-iters", 1 << 22, as_int))
        result = {"factors": list(got) if got else None,
                  "reason": None if got else "p and q are not close"}
        primary = "factors"
    elif name == "batch-gcd":
        mods = int_list(data.get("moduli"), "moduli")
        if data.get("file"):
            with open(data["file"], encoding="utf-8") as handle:
                mods += int_list(handle.read(), "moduli")
        if len(mods) < 2:
            raise ValueError("supply at least two moduli via --moduli or --file")
        hits = fn(mods)
        result = {"shared_prime_pairs": hits, "moduli_checked": len(mods),
                  "reason": None if hits else "every pairwise gcd is 1"}
        primary = "shared_prime_pairs"
        if not hits:
            result["shared_prime_pairs"] = None
    elif name == "pollard-pm1":
        result = fn(need(data, "n"), opt(data, "b1", 100000, as_int))
    elif name == "rsa-decrypt":
        result = fn(need(data, "n"), need(data, "e"), need(data, "c"),
                    need(data, "p"), opt(data, "q", None, as_int))
    elif name == "eth-root":
        factors = int_list(need(data, "factors", None), "factors")
        roots = fn(need(data, "c"), need(data, "e"), factors)
        result = {"roots": roots or None, "count": len(roots)}
        primary = "roots"
    elif name == "factor-from-d":
        got = fn(need(data, "n"), opt(data, "e", None, as_int),
                 opt(data, "d", None, as_int), opt(data, "phi", None, as_int))
        result = {"factors": list(got) if got else None}
        primary = "factors"
    elif name == "pohlig-hellman":
        result = fn(need(data, "g"), need(data, "h"), need(data, "p"),
                    opt(data, "order", None, as_int))
    elif name == "bsgs":
        result = fn(need(data, "g"), need(data, "h"), need(data, "p"),
                    opt(data, "order", None, as_int))
    elif name == "smoothness":
        result = fn(need(data, "n"))
        primary = None
    elif name == "lcg-recover":
        result = fn(int_list(need(data, "outputs", None), "outputs"),
                    need(data, "modulus"))
    elif name == "lcg-unknown-modulus":
        result = fn(int_list(need(data, "outputs", None), "outputs"))
    elif name == "lcg-truncated":
        result = fn(int_list(need(data, "outputs", None), "outputs"),
                    need(data, "modulus"), need(data, "a"), need(data, "c"),
                    need(data, "low-bits"))
    elif name == "mt19937-clone":
        outs = int_list(data.get("outputs"), "outputs")
        if data.get("outputs-file"):
            with open(data["outputs-file"], encoding="utf-8") as handle:
                outs += int_list(handle.read(), "outputs")
        result = fn(outs, opt(data, "count", 5, as_int))
    elif name in ("lfsr-recover", "lfsr-predict"):
        bits = _bits_from(data)
        taps = int_list(need(data, "taps", None), "taps")
        width = opt(data, "width", None, as_int) or max(taps)
        result = (fn(bits, taps, width) if name == "lfsr-recover"
                  else fn(bits, taps, width, opt(data, "count", 64, as_int)))
    elif name == "berlekamp-massey":
        result = fn(_bits_from(data))
        primary = None
    elif name == "length-extension":
        result = fn(opt(data, "hash", "sha256"), str(need(data, "mac", None)),
                    need(data, "secret-len"), as_bytes(need(data, "orig", None)),
                    as_bytes(need(data, "append", None)))
        notes.append("submit new_message_hex as the message and forged_digest as the MAC")
    elif name == "hnp-ecdsa":
        sigs = _sigs_from(data)
        pub = data.get("pubkey")
        if isinstance(pub, str):
            pub = [as_int(x) for x in pub.split(",")]
        result = fn(sigs, need(data, "order"), opt(data, "nonce-bits", None, as_int),
                    opt(data, "nonce-bound", None, as_int),
                    opt(data, "curve", "secp256k1"), pub)
        notes.append("without --pubkey the key is only size-checked, not verified")
    elif name == "ecdsa-nonce-reuse":
        sigs = _sigs_from(data)
        if len(sigs) < 2:
            raise ValueError("need two signatures")
        result = fn(sigs[0], sigs[1], need(data, "order"))
    elif name == "hnp":
        result = fn(int_list(need(data, "t", None), "t"),
                    int_list(need(data, "u", None), "u"),
                    need(data, "modulus"), need(data, "bound"))
    elif name == "crib-drag":
        result = fn(as_bytes(need(data, "ct1", None)), as_bytes(need(data, "ct2", None)),
                    str(need(data, "crib", None)))
        primary = None
    elif name == "single-byte-xor":
        result = fn(as_bytes(need(data, "ct", None)))
        primary = None
    elif name == "nth-root":
        root, exact = fn(need(data, "x"), need(data, "n"))
        result = {"root": root, "exact": exact}
        primary = "root"
    elif name == "crt":
        got = fn(int_list(need(data, "residues", None), "residues"),
                 int_list(need(data, "moduli", None), "moduli"))
        result = {"x": got[0], "modulus": got[1]} if got else {"x": None,
                                                               "reason": "inconsistent"}
        primary = "x"
    else:                                                       # pragma: no cover
        raise ValueError("no dispatcher for %s" % name)
    return emit(args, name, result, primary, notes)


def _bits_from(data):
    if data.get("bits"):
        text = re.sub(r"[^01]", "", str(data["bits"]))
        return [int(ch) for ch in text]
    if data.get("keystream-hex"):
        raw = bytes.fromhex(str(data["keystream-hex"]))
        return [(byte >> (7 - i)) & 1 for byte in raw for i in range(8)]
    if data.get("bits-file"):
        with open(data["bits-file"], encoding="utf-8") as handle:
            return [int(ch) for ch in re.sub(r"[^01]", "", handle.read())]
    raise ValueError("supply --bits, --keystream-hex or --bits-file")


def _sigs_from(data):
    raw = data.get("sigs")
    if isinstance(raw, str):
        raw = load_json_input(raw)
    if raw is None:
        raise ValueError("supply --sigs FILE.json (a list of [r, s, z] or {r, s, z})")
    out = []
    for item in raw:
        if isinstance(item, dict):
            out.append((as_int(item["r"]), as_int(item["s"]),
                        as_int(item.get("z", item.get("h", item.get("m"))))))
        else:
            out.append(tuple(as_int(v) for v in item[:3]))
    return out


# Which flags each attack reads. Every one also accepts --in FILE for the same
# keys, so a challenge's parameters can be piped in as JSON.
ARG_KEYS = {
    "hastad": ["pairs", "n", "c", "e", "bytes"],
    "small-e-root": ["n", "e", "c", "max-k"],
    "common-modulus": ["n", "e1", "c1", "e2", "c2"],
    "wiener": ["n", "e"],
    "boneh-durfee": ["n", "e", "delta", "m", "t"],
    "boneh-durfee-escalate": ["n", "e", "delta", "m"],
    "coppersmith-high-bits": ["n", "known", "bits", "p-bits", "m", "t"],
    "coppersmith-core": ["n", "a", "X", "m", "t"],
    "fermat": ["n", "max-iters"],
    "batch-gcd": ["moduli", "file"],
    "pollard-pm1": ["n", "b1"],
    "rsa-decrypt": ["n", "e", "c", "p", "q"],
    "eth-root": ["c", "e", "factors"],
    "factor-from-d": ["n", "e", "d", "phi"],
    "pohlig-hellman": ["g", "h", "p", "order"],
    "bsgs": ["g", "h", "p", "order"],
    "smoothness": ["n"],
    "lcg-recover": ["outputs", "modulus"],
    "lcg-unknown-modulus": ["outputs"],
    "lcg-truncated": ["outputs", "modulus", "a", "c", "low-bits"],
    "mt19937-clone": ["outputs", "outputs-file", "count"],
    "lfsr-recover": ["bits", "keystream-hex", "bits-file", "taps", "width"],
    "lfsr-predict": ["bits", "keystream-hex", "bits-file", "taps", "width", "count"],
    "berlekamp-massey": ["bits", "keystream-hex", "bits-file"],
    "length-extension": ["hash", "mac", "secret-len", "orig", "append"],
    "hnp-ecdsa": ["sigs", "order", "nonce-bits", "nonce-bound", "curve", "pubkey"],
    "ecdsa-nonce-reuse": ["sigs", "order"],
    "hnp": ["t", "u", "modulus", "bound"],
    "crib-drag": ["ct1", "ct2", "crib"],
    "single-byte-xor": ["ct"],
    "nth-root": ["x", "n"],
    "crt": ["residues", "moduli"],
}


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="run `list` for every attack and its applicability condition")
    parser.add_argument("--json", action="store_true",
                        help="compact JSON on one line (default is indented)")
    # --json is accepted on either side of the subcommand: SUPPRESS keeps an
    # unused subparser flag from overwriting the global one with its default.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="compact JSON on one line")
    subs = parser.add_subparsers(dest="command", required=True)

    subs.add_parser("list", parents=[common],
                    help="every attack with its applicability condition")
    desc = subs.add_parser("describe", parents=[common],
                           help="one attack's full docstring")
    desc.add_argument("name")
    ident = subs.add_parser("identify", parents=[common],
                            help="triage a handout: sizes, shapes, hints")
    ident.add_argument("--file")
    ident.add_argument("--hex")
    ident.add_argument("--text")
    st = subs.add_parser("selftest", parents=[common],
                         help="run the deterministic self-test")
    st.add_argument("--slow", action="store_true")

    for name, keys in sorted(ARG_KEYS.items()):
        sub = subs.add_parser(name, parents=[common],
                              help=crypto.applicability(name)[:110])
        sub.add_argument("--in", dest="in_file", metavar="FILE",
                         help="JSON object with any of this attack's parameters "
                              "(- for stdin)")
        for key in keys:
            sub.add_argument("--" + key, dest=key.replace("-", "_"))
    return parser


def main():
    args = build_parser().parse_args()
    if not hasattr(args, "json"):
        args.json = False
    handlers = {"list": cmd_list, "describe": cmd_describe, "identify": cmd_identify,
                "selftest": cmd_selftest}
    try:
        if args.command in handlers:
            return handlers[args.command](args)
        return cmd_attack(args)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({"mode": "crypto-attack", "attack": args.command,
                          "status": "input-error", "error": str(exc)}, indent=2),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
