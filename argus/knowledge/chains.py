"""Chain cards: what worked on a stack, written down so the second run is cheaper.

A card is derived from a confirmed finding and the probes that reached it. It
records the stack the finding was made on, where the input was, which ladder
steps actually fired, which probe first discriminated, the shape of proof that
settled it, the preconditions in plain language, and the blast radius of reusing
it on something shared.

It records none of the things that would make it a shortcut past proof: no
hostname, no address, no credential, no extracted row, no flag, no nonce, no
proof output, and not even the payload that worked. That omission is the whole
design. A card makes a hypothesis cheap to form and — through the markers it
needs that the target has not been seen to have — cheap to kill. It cannot make
a finding, because nothing in it is evidence about the target in front of you.

Four refusals are worth naming, because each is a mistake that is easy to make
and expensive to notice:

* **A class the matrix refuses to prove gets no card.** `dos` is in the matrix
  precisely so that asking for it returns a reason rather than a scan, and the
  corpus is a checked-in directory that any clone reads. A card is the one place
  a refused class could re-enter the system as a ranked suggestion, so a card
  whose class the matrix refuses is refused here too, with the matrix's own
  reason.
* **`validate` refuses; it never redacts.** A quietly redacted card still looks
  complete, and the next agent reads it as if the missing half had never been
  there. A refusal names the field and the reason, and the operator decides.
* **A card with no stack marker is refused.** It could never be ranked against a
  target, so it would only ever be read by accident — and a card read by
  accident is an anchor on the next hypothesis with nothing behind it.
* **A candidate finding gets no card.** A candidate is a chain whose last check
  is missing. Writing it down as experience records the part that did not work.

`match` is a ranking over shared markers and says so in every result. The useful
half of its answer is `unobserved`: the markers the card needs that this target
has not been observed to have. Each one is a single request that kills the
candidate if it is absent, which is what makes a candidate cheap rather than a
direction to spend an afternoon on.
"""
from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from urllib.parse import urlsplit

from .. import config
from ..util import (bound, check_slug, now_iso, read_json, redact, sha256_text,
                    write_json)

SCHEMA = 1
SCHEMA_PATH = Path(__file__).resolve().parent / "chain-schema.json"

# The system's own corpus, as opposed to the optional external one
# `knowledge.chain_match` reads at `config.CTF_V2`. Cards written here are
# checked in: they are knowledge about shapes, not engagement output.
CHAINS_DIR = config.ROOT / "knowledge" / "chains"

# Bounds. Bounded collection is a rule about what gets written down as well as
# about what gets read: a card is a paragraph, and a field long enough to hold a
# dumped row is a field that will eventually hold one.
MAX_FIELD_CHARS = 500
MAX_CARD_CHARS = 12_000
MAX_STEPS = 40

REUSE_CAVEAT = ("A match is a candidate. The preconditions here are plain language and nothing "
                "checks them for you, and the class's proof requirement is exactly what it was "
                "before this card existed.")


class CardRefused(ValueError):
    """A card may not be built or written, and the reason is the message.

    A refusal carries the card it refused so a caller can look at what it tried
    to write, and the reasons separately so `harvest` can report them per
    finding rather than as one string.
    """

    def __init__(self, reasons, card: dict | None = None):
        self.reasons = tuple(reasons)
        self.card = card
        super().__init__("; ".join(self.reasons))

    @property
    def reason(self) -> str:
        return "; ".join(self.reasons)


@dataclass(frozen=True)
class CardVerdict:
    ok: bool
    reasons: tuple[str, ...] = ()
    checked: int = 0

    def __bool__(self) -> bool:
        return self.ok

    @property
    def reason(self) -> str:
        return "; ".join(self.reasons) or "no refusal"

    def to_dict(self) -> dict:
        return {"ok": self.ok, "reasons": list(self.reasons), "fields_checked": self.checked}


# --- the schema file is the allowed-key list ---------------------------------

def schema() -> dict:
    """The card shape, read from `chain-schema.json` rather than restated here.

    The property list in that file is what `validate` enforces, so a field added
    to a card without being documented in the schema is refused. The alternative
    — a Python list beside a JSON file — drifts, and the half that drifts is
    always the documentation.
    """
    return read_json(SCHEMA_PATH, {}) or {}


def _allowed(node: dict) -> dict:
    return dict(node.get("properties") or {})


def _node(card: dict, key: str) -> dict:
    """A card's sub-object, or an empty one when it is the wrong type.

    `validate` has to survive any shape, including the shapes a hand-edited file
    produces. A validator that raises on malformed input fails open from the
    caller's side: the caller sees an exception where it expected a refusal, and
    the easiest way to make that go away is a bare `except`.
    """
    value = card.get(key)
    return value if isinstance(value, dict) else {}


def _forbidden_names() -> set[str]:
    return {str(name).lower() for name in (schema().get("x-forbidden-field-names") or [])}


# --- content that may not appear in a card -----------------------------------

_IPV4_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
_IPV6_RE = re.compile(r"\b(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f]{1,4}\b")
_URL_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9+.\-]*://\S+")
_FLAG_RE = re.compile(r"(?i)\b(?:flag|ctf|htb|thm|picoctf|hackthebox|key|secret|root|user)"
                      r"\{[^}\n]{1,200}\}")
_BRACED_RE = re.compile(r"\b[A-Za-z0-9_]{2,16}\{[A-Za-z0-9_@!?+/=.\-]{6,200}\}")
_CREDENTIAL_RE = re.compile(r"(?i)\b(?:password|passwd|pwd|api[_-]?key|apikey|secret[_-]?key|"
                            r"access[_-]?key|bearer|authorization)\s*[:=]\s*\S{4,}")


def _ip_literals(text: str) -> list[str]:
    """Only strings that really parse as addresses.

    A four-component version string — `10.0.19041.1` — looks like an address and
    is not one, and refusing it would make a card impossible to write for half
    the Windows stacks there are. The reverse false positive survives: a version
    whose four components are all under 256 is read as an address. The refusal
    names the field, and the fix is to write the version as a range.
    """
    out = []
    for candidate in _IPV4_RE.findall(text) + _IPV6_RE.findall(text):
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            continue
        out.append(candidate)
    return out


def _proof_output(text: str) -> list[str]:
    """Patterns the proof matrix itself reads as evidence.

    Imported from the matrix rather than copied: if `verify_command_output`
    learns a new identity shape, a card carrying that shape starts being refused
    on the same day, with no second list to remember.
    """
    from ..ledger.proof import NONCE_PREFIX, PASSWD_RE, PRIVKEY_RE, UID_RE, WINID_RE
    hits = []
    for label, pattern in (("an identity line", UID_RE), ("a windows identity", WINID_RE),
                           ("an /etc/passwd row", PASSWD_RE), ("a private key", PRIVKEY_RE)):
        if pattern.search(text):
            hits.append(label)
    if re.search(rf"\b{re.escape(NONCE_PREFIX)}[a-z0-9]{{8,}}\b", text):
        hits.append("a probe nonce")
    return hits


def _engagement_names(engagement: str) -> set[str]:
    """Hostnames this engagement has named, plus the engagement's own name.

    The engagement name is in here because operators name engagements after
    clients. A card that carries `acme-prod` is a card that names who was
    tested, which is the one thing a shared corpus must never do.
    """
    from ..ledger.scope import parse_target
    from ..ledger.state import State
    names = {engagement.strip().lower()} if engagement else set()
    try:
        state = State.load(engagement)
    except (FileNotFoundError, ValueError, OSError):
        return {n for n in names if n}
    raw = list(state.data.get("targets") or {})
    for entry in (state.data.get("targets") or {}).values():
        raw.extend(entry.get("urls") or [])
    scope = read_json(state.paths.scope, {}) or {}
    for key in ("in_scope", "out_of_scope"):
        raw.extend(str(rule) for rule in (scope.get(key) or []))
    for item in raw:
        try:
            names.add(parse_target(str(item).lstrip("*.")).host)
        except (ValueError, AttributeError):
            continue
    return {n for n in names if n}


def _walk(value, path: str = "") -> Iterator[tuple[str, object]]:
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _walk(item, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk(item, f"{path}[{index}]")
    else:
        yield path, value


def _keys(value, path: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            here = f"{path}.{key}" if path else str(key)
            yield here, str(key)
            yield from _keys(item, here)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _keys(item, f"{path}[{index}]")


_JSON_TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool,
               "array": list, "object": dict}

# A required field is refused when it is empty as well as when it is absent: an
# empty field reads as "there was nothing here" rather than "this was not
# written". `steps` is the one exception, because a finding proven entirely
# through `ledger.add_evidence` — a Burp request, a browser session, a source
# read — has no broker probes at all. Refusing those would make the corpus a
# record of what the broker happened to run rather than of what was proven, and
# would silently exclude exactly the evidence route the broker exists not to be
# a cage around.
MAY_BE_EMPTY = frozenset({"steps"})


def _join(path: str, key: str) -> str:
    return f"{path}.{key}" if path else str(key)


def _structure(value, declared: dict, path: str = "") -> list[str]:
    """Check one node against its schema declaration, all the way down.

    The recursion is the point. An earlier version of this checked the card's
    top level and four named sub-objects, so an undeclared key inside a `steps`
    item — the obvious place for someone to park the payload that worked —
    passed, and the schema's own `unknown-field` refusal was a claim the
    validator did not keep. The declared properties are the allowed keys at
    every depth, declared item types are enforced per element (a marker that is
    not a string is the shape that used to make `match` raise rather than
    refuse), and a nested required key has to be present.
    """
    reasons: list[str] = []
    expected = declared.get("type")
    if expected in _JSON_TYPES and value is not None \
            and not isinstance(value, _JSON_TYPES[expected]):
        where = path or "the card"
        return [f"type: {where} must be {expected}, not {type(value).__name__}"]
    if isinstance(value, dict):
        properties = _allowed(declared)
        if not properties:
            return reasons
        for key, item in value.items():
            if key not in properties:
                reasons.append(f"unknown-field: {_join(path, key)} is not declared in "
                               f"chain-schema.json")
                continue
            reasons.extend(_structure(item, properties[key], _join(path, key)))
        # Presence only, not emptiness: a probe that named no ladder step
        # honestly records an empty step name, and refusing that would lose the
        # probe rather than record it. The top level is checked by `validate`,
        # which knows which of its fields may be empty.
        if path:
            for key in declared.get("required") or []:
                if key not in value:
                    reasons.append(f"missing-field: {_join(path, key)} is required by the schema")
    elif isinstance(value, list):
        items = declared.get("items") or {}
        if items:
            for index, item in enumerate(value):
                reasons.extend(_structure(item, items, f"{path}[{index}]"))
    return reasons


# --- validation --------------------------------------------------------------

def validate(card: dict, engagement: str | None = None) -> CardVerdict:
    """Decide whether a card may exist. The reason is the output, not a boolean.

    Structure comes from `chain-schema.json`, at every depth: the declared
    properties are the allowed keys, declared item types are enforced per
    element, `required` is enforced, and `x-forbidden-field-names` refuses a key
    by name alone — those are the names the evidence records use for the things
    a card must not carry, so `rows` or `stdout_span` appearing anywhere in a
    card is enough to stop it without looking at the value.

    A class the matrix refuses to prove is refused here as well. Without that,
    the corpus is a way for a refused class to come back as a ranked suggestion
    with steps under it, and a checked-in card outlives the engagement.

    Content checks refuse an address literal, an absolute URL, a secret shape
    (`argus.util.redact`'s own patterns, so there is one list), the matrix's own
    proof-output patterns, a flag shape, and — when an engagement is named — any
    host that engagement named or the engagement's own name.

    What this cannot catch, stated rather than implied: a password that looks
    like a word, a path segment that is a tenant's name, a server banner an
    administrator put a hostname into. The checks refuse the shapes a machine
    can recognise; a card is still something a human should read once.
    """
    reasons: list[str] = []
    if not isinstance(card, dict):
        return CardVerdict(False, (f"a card must be an object, not {type(card).__name__}",))

    spec = schema()
    required = list(spec.get("required") or [])
    forbidden = _forbidden_names()

    # --- structure
    for key in required:
        if key not in card:
            reasons.append(f"missing-field: required field {key!r} is absent")
        elif card[key] in (None, "", [], {}) and key not in MAY_BE_EMPTY:
            reasons.append(f"missing-field: required field {key!r} is empty")
    reasons.extend(_structure(card, spec))
    if card.get("schema") not in (None, SCHEMA):
        reasons.append(f"schema-version: schema {card.get('schema')!r} is not {SCHEMA}")
    for path, key in _keys(card):
        if key.lower() in forbidden:
            reasons.append(f"forbidden-field: {path} — a card does not carry {key!r}")
    if isinstance(card.get("steps"), list) and len(card["steps"]) > MAX_STEPS:
        reasons.append(f"over-long: {len(card['steps'])} steps, the bound is {MAX_STEPS}")
    if card.get("slug"):
        try:
            check_slug(str(card["slug"]), "card slug")
        except ValueError as error:
            reasons.append(f"bad-slug: {error}")

    # --- the class has to be reusable under a requirement
    from ..ledger.proof import spec_for
    matrix_spec = spec_for(str(card.get("vuln_class") or ""))
    if matrix_spec is None:
        reasons.append(f"class-not-in-matrix: {card.get('vuln_class')!r} has no proof requirement "
                       f"here, so there is nothing to reuse this card under")
    elif matrix_spec.refusal or matrix_spec.kind == "refused":
        # The corpus is the one route by which a class this system refuses to
        # prove could come back as a ranked suggestion with steps to follow, and
        # a checked-in card outlives the engagement that wrote it. `dos` is in
        # the matrix so that asking for it returns a reason; a card would turn
        # that reason back into a playbook.
        reasons.append(f"refused-class: {matrix_spec.vuln_class} may not be proven by this system, "
                       f"so there is no chain to write down. "
                       f"{matrix_spec.refusal or 'The proof would be the damage.'}")
    elif _node(card, "proof").get("kind") and matrix_spec.kind != card["proof"]["kind"]:
        reasons.append(f"class-not-in-matrix: proof.kind {card['proof']['kind']!r} is not the "
                       f"matrix shape for {matrix_spec.vuln_class} ({matrix_spec.kind})")

    # --- unmatchable
    markers = _node(card, "stack").get("markers") or []
    if not markers:
        reasons.append("unmatchable: stack.markers is empty, so this card can never be ranked "
                       "against a target and would only ever be read by accident")

    # --- content
    hosts = _engagement_names(engagement) if engagement else set()
    checked = 0
    whole = []
    for path, value in _walk(card):
        if not isinstance(value, str):
            continue
        checked += 1
        whole.append(value)
        if len(value) > MAX_FIELD_CHARS:
            reasons.append(f"over-long: {path} is {len(value)} chars, the bound is "
                           f"{MAX_FIELD_CHARS} — a field that long is holding observed output")
            continue
        if redact(value) != value:
            reasons.append(f"secret-shape: {path} holds text that argus.util.redact rewrites")
        if _CREDENTIAL_RE.search(value):
            reasons.append(f"secret-shape: {path} holds a credential-shaped assignment")
        for literal in _ip_literals(value):
            reasons.append(f"address-literal: {path} names the address {literal}")
        for url in _URL_RE.findall(value):
            reasons.append(f"address-literal: {path} holds the absolute URL "
                           f"{bound(url, 60)} — a card describes a shape, not a place")
        for label in _proof_output(value):
            reasons.append(f"proof-output: {path} holds {label}")
        if _FLAG_RE.search(value) or _BRACED_RE.search(value):
            reasons.append(f"flag-shape: {path} holds something shaped like a flag")
        lowered = value.lower()
        for host in hosts:
            if len(host) > 2 and re.search(rf"(?<![\w.\-]){re.escape(host)}(?![\w.\-])", lowered):
                reasons.append(f"engagement-hostname: {path} names {host!r}, which this "
                               f"engagement named")

    total = sum(len(text) for text in whole)
    if total > MAX_CARD_CHARS:
        reasons.append(f"over-long: the card is {total} chars of text, the bound is {MAX_CARD_CHARS}")

    # The same host in five fields is one mistake, not five.
    seen, unique = set(), []
    for reason in reasons:
        if reason not in seen:
            seen.add(reason)
            unique.append(reason)
    return CardVerdict(not unique, tuple(unique), checked)


def audit(directory: str | Path | None = None) -> list[dict]:
    """Every card on disk the write path would now refuse, with the reason.

    Cards are files, and files get hand-edited. This answers "is the corpus
    clean" without having to re-harvest it, and `match` skips exactly the cards
    this lists.
    """
    out = []
    for card in cards(directory):
        verdict = validate(card)
        if not verdict:
            out.append({"slug": card.get("slug"), "reasons": list(verdict.reasons)})
    return out


# --- markers ------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\d+(?:\.\d+)+|[A-Za-z][A-Za-z0-9+_.\-]*")
_VERSION_RE = re.compile(r"\A\d+(?:\.\d+)+\Z")
_STACK_KEYS = ("server", "powered_by", "framework", "technologies", "versions")
# Words that appear in every banner and therefore discriminate nothing. A marker
# that matches everything ranks the whole corpus equally, which is the same as
# having no corpus. `product`, `version` and `major` are in here because they are
# this module's own marker prefixes: a stack re-read out of a card must not come
# back carrying `product:product`.
_STOPWORDS = frozenset({
    "and", "application", "by", "charset", "close", "for", "generator", "gzip", "header",
    "html", "http", "https", "inc", "json", "keep", "keep-alive", "ltd", "major", "none",
    "null", "powered", "product", "server", "text", "the", "true", "false", "unknown",
    "utf", "version", "web", "with", "www", "xml",
})


def markers_of(stack) -> list[str]:
    """Normalise an observed stack into comparable markers.

    Three shapes, cheapest first: `product:<name>`, `major:<name>/<n>` and
    `version:<name>/<n.n.n>`. The major marker exists because two deployments of
    the same product rarely run the same patch level, and a scoring function that
    only knows the full version ranks a card about this product below a card
    about nothing.

    A page title and a content type are read from nothing here, deliberately:
    both change with the deployment, and matching on them ranks the wrong cards
    first. A card that was found on a service whose title mentioned widgets is
    not a card about widgets.

    A stack that already carries normalised markers — a card's own `stack`, read
    back off disk — is returned as it is rather than re-tokenised, so the
    function is idempotent on its own output.
    """
    if isinstance(stack, dict) and isinstance(stack.get("markers"), (list, tuple)):
        already = [marker.strip().lower() for marker in stack["markers"]
                   if isinstance(marker, str) and ":" in marker]
        if already:
            return list(dict.fromkeys(already))
    if isinstance(stack, dict):
        parts = []
        for key in _STACK_KEYS:
            value = stack.get(key)
            if isinstance(value, (list, tuple)):
                parts.extend(str(item) for item in value)
            elif value:
                parts.append(str(value))
        text = " ".join(parts)
    else:
        text = str(stack or "")
    out, previous = [], None
    for raw in _TOKEN_RE.findall(text):
        token = raw.strip("._-").lower()
        if not token:
            continue
        if _VERSION_RE.match(token):
            if previous:
                out.append(f"version:{previous}/{token}")
                out.append(f"major:{previous}/{token.split('.')[0]}")
            continue
        if len(token) < 3 or token in _STOPWORDS:
            previous = None
            continue
        out.append(f"product:{token}")
        previous = token
    seen, unique = set(), []
    for marker in out:
        if marker not in seen:
            seen.add(marker)
            unique.append(marker)
    return unique


def _versions_of(stack: dict) -> list[str]:
    return [marker.split(":", 1)[1] for marker in markers_of(stack)
            if marker.startswith("version:")]


# --- reading the corpus -------------------------------------------------------

def _dir(directory: str | Path | None = None) -> Path:
    return Path(directory) if directory else CHAINS_DIR


def cards(directory: str | Path | None = None) -> list[dict]:
    """Every readable card in the corpus, by slug.

    Unreadable and invalid cards are returned as they are rather than filtered:
    a card the write path would now refuse should be visible to `audit`, not
    silently absent from the only function that lists the corpus.
    """
    base = _dir(directory)
    if not base.is_dir():
        return []
    out = []
    for path in sorted(base.glob("*.json")):
        card = read_json(path)
        if isinstance(card, dict):
            card.setdefault("slug", path.stem)
            out.append(card)
    return out


def load(slug: str, directory: str | Path | None = None) -> dict | None:
    try:
        safe = check_slug(str(slug), "card slug")
    except ValueError:
        return None
    return read_json(_dir(directory) / f"{safe}.json")


# --- writing ------------------------------------------------------------------

def source_digest(engagement: str, finding_id: str) -> str:
    """A card's link back to where it came from, with no name in it.

    Whoever still has the engagement can recompute this and find the finding;
    nobody else learns the engagement's name from the card. `harvest` uses it to
    tell a finding it has already written from one it has not.
    """
    return sha256_text(f"{engagement}/{finding_id}")[:16]


def write_card(card: dict, directory: str | Path | None = None) -> Path:
    """Validate, then write `knowledge/chains/<slug>.json` atomically.

    `validate` runs here as well as in `card_from_finding`, because this is the
    only path onto disk and a hand-written card arrives through it too. A slug
    that already holds a card from a different finding is refused rather than
    overwritten: two chains that normalise to the same name are two chains, and
    losing one quietly is worse than making whoever wrote the second one look.
    """
    verdict = validate(card)
    if not verdict:
        raise CardRefused(verdict.reasons, card)
    slug = check_slug(str(card["slug"]), "card slug")
    path = _dir(directory) / f"{slug}.json"
    existing = read_json(path)
    if isinstance(existing, dict) and existing.get("source_digest") != card.get("source_digest"):
        raise CardRefused((f"slug {slug!r} already holds a card from a different finding "
                           f"({existing.get('source_digest')}); rename rather than overwrite",), card)
    write_json(path, card)
    return path


# --- building a card from a finding -------------------------------------------

# What reusing a chain of this shape can damage. Derived from the proof shape,
# not measured on the original target: the card says what the class puts in
# reach, so that the decision to go past the benign proof is taken by a human
# who has read it. The repository will not help with any of the second halves.
BLAST_RADIUS = {
    "command_output": [
        "the chain reaches a shell. The proof stops at `id; echo <nonce>`, which reads identity "
        "and changes nothing; anything past that is damage, and this system will not do it.",
        "the command runs as the service account, so every tenant's data under that account is "
        "in reach the moment someone departs from the marker command.",
    ],
    "data_extraction": [
        "the chain reads the application's data store. Five rows is a proof and a full dump is "
        "an incident, and on a shared instance those rows belong to tenants who were not asked.",
        "some extraction modes write to the target — temporary tables, session rows — so on a "
        "production instance a 'read-only' extraction is not necessarily read-only.",
    ],
    "file_read": [
        "any file the service account can read, which on a shared instance includes other "
        "tenants' uploads and the application's own configuration.",
        "a file read is also how credentials leave: reading a config file turns this chain into "
        "a credential exposure that someone then has to rotate.",
    ],
    "template_eval": [
        "an expression evaluates inside the application process. Arithmetic is the proof; the "
        "same entry point reaches the engine's object graph, which is code execution.",
    ],
    "oob": [
        "the target makes requests on your behalf. On a shared instance that reaches the "
        "internal network and the cloud metadata service, neither of which is in scope by "
        "default — and a metadata read is a credential read.",
    ],
    "differential": [
        "one identity reads or acts on another's data. On a shared instance the record belongs "
        "to a real tenant, and the read itself is the damage: there is no benign version.",
    ],
    "browser_execution": [
        "a payload executes in a visitor's session. A stored variant runs for every visitor, "
        "including people who are not part of the test and did not consent to it.",
    ],
    "state_change": [
        "the chain changes state and the change persists. On a shared instance that is "
        "somebody's order, balance or permission, and this system records no undo.",
    ],
    "token_forgery": [
        "a forged credential is accepted. Reusing it is access to real accounts, and the "
        "access is logged against whoever's identity was forged rather than against the tester.",
    ],
    "secret_leak": [
        "a live credential is exposed. Validating it touches the issuer, which is a third party "
        "outside most engagement scopes, and the credential stays live until someone rotates it.",
    ],
}

# Four classes share the `differential` verifier and do not share a blast radius.
# Keyed on the class where the kind is not specific enough, because a card that
# describes the wrong damage is worse than one that describes none: it is read by
# whoever is deciding whether to go past the benign proof, and this text is the
# last thing they read before deciding.
BLAST_RADIUS_BY_CLASS = {
    "race-condition": [
        "the chain produces a state change the application's own limit was supposed to prevent — a "
        "second order, a second withdrawal, a second redemption. On a shared instance that change "
        "is somebody's, and this system records no undo.",
        "the probe is concurrent by construction, so a wider N is load as well as a proof. The "
        "control is the serial run, not a larger burst.",
    ],
    "cache-poisoning": [
        "a poisoned entry is served to people who never sent the request. The blast radius is every "
        "client of that cache key for as long as the entry lives, which is why the proof is one "
        "unrelated requester and never a warm cache.",
        "the entry outlives the probe. A card that is reused without a plan for evicting the key "
        "leaves the target serving the tester's response after the engagement ends.",
    ],
    "open-redirect": [
        "the target sends a visitor elsewhere under its own name, so the damage lands on whoever "
        "follows the link rather than on the target. The destination must be a host the engagement "
        "controls; pointing it at a third party makes them part of a test they did not agree to.",
    ],
}


def _path_shape(raw: str) -> str:
    """The request path with identifier-shaped segments collapsed.

    `/orders/4821/items` becomes `/orders/:id/items`, because the number is this
    engagement's order and the shape is what is reusable. Named segments are
    kept — which is a limit, not a guarantee: a path that names a tenant keeps
    naming it, and that is one of the things a human should read a card for.
    """
    try:
        path = urlsplit(str(raw or "")).path or "/"
    except ValueError:
        return ""
    out = []
    for segment in path.split("/"):
        if not segment:
            continue
        if segment.isdigit() or re.fullmatch(r"[0-9a-fA-F][0-9a-fA-F-]{7,}", segment):
            out.append(":id")
        else:
            out.append(segment)
    return "/" + "/".join(out)


def _query_param(raw: str) -> str:
    query = urlsplit(str(raw or "")).query
    for pair in query.split("&"):
        name = pair.split("=", 1)[0].strip()
        if name:
            return name
    return ""


def _ladder_index(vuln_class: str) -> dict:
    from . import playbook
    return {str(step.get("step", "")).lower(): step for step in playbook.ladder(vuln_class)}


def _slug_for(vuln_class: str, entry: dict, markers: list[str], digest: str) -> str:
    product = next((m.split(":", 1)[1] for m in markers if m.startswith("product:")), "unknown")
    bits = [vuln_class, entry.get("location") or "", entry.get("param") or "", product,
            digest[:8]]
    raw = "-".join(bit for bit in bits if bit)
    slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9.-]+", "-", raw.lower())).strip("-.")
    return check_slug(slug[:100].rstrip("-."), "card slug")


def card_from_finding(engagement: str, finding_id: str) -> dict:
    """Build one card from a confirmed finding and the probes that reached it.

    Raises `CardRefused` with the reason when the finding cannot produce an
    honest card: it is a candidate rather than confirmed, its target was never
    fingerprinted so the card would have no marker to match on, or the assembled
    card fails validation. A refusal is a message to the operator and may name
    the target; the card it refused never reaches disk.
    """
    from ..ledger.proof import spec_for
    from ..ledger.scope import origin_of
    from ..ledger.state import State

    state = State.load(engagement)
    finding = state.finding(finding_id)
    if finding is None:
        raise KeyError(f"no finding {finding_id!r} in engagement {engagement!r}")
    if finding.get("status") != "confirmed":
        raise CardRefused((f"not-confirmed: {finding_id} is a {finding.get('status')}. A card "
                           f"records what settled, and the missing check is "
                           f"{', '.join((finding.get('proof') or {}).get('missing') or ['unnamed'])}",))

    vuln_class = str(finding.get("vuln_class") or "")
    matrix_spec = spec_for(vuln_class)
    if matrix_spec is None:
        raise CardRefused((f"class-not-in-matrix: {vuln_class!r} has no proof requirement here",))

    origin = origin_of(finding.get("target") or "")
    stack_seen = ((state.data.get("targets") or {}).get(origin) or {}).get("stack") or {}
    markers = markers_of(stack_seen)
    if not markers:
        raise CardRefused((f"unmatchable: no stack was ever fingerprinted for {origin}, so the "
                           f"card would have no marker to match on. Run recon.fingerprint "
                           f"against it and harvest again",))

    probes = [probe for probe in (state.data.get("probes") or [])
              if probe.get("hypothesis_id") == finding.get("hypothesis_id")]
    ladder = _ladder_index(vuln_class)
    steps = []
    for index, probe in enumerate(probes[:MAX_STEPS], start=1):
        name = str(probe.get("step") or "")
        steps.append({"n": index, "step": name, "tool": str(probe.get("tool") or ""),
                      "tier": str((ladder.get(name.lower()) or {}).get("tier") or ""),
                      "result": str(probe.get("result") or "")})
    discriminating = next((step for step in steps if step["result"] == "signal"), None)
    if discriminating:
        rung = ladder.get(discriminating["step"].lower()) or {}
        first = {"n": discriminating["n"], "step": discriminating["step"],
                 "tool": discriminating["tool"], "tier": discriminating["tier"],
                 "why": str(rung.get("why") or "the ladder names no reason for this step; it is "
                                               "recorded because it is what actually fired first")}
    else:
        first = {"step": "", "tool": "", "tier": "",
                 "why": "no probe on this hypothesis returned a signal: the evidence was recorded "
                        "from outside the broker, so this card cannot say what discriminated"}

    declared = finding.get("entry_point") or {}
    probe_target = next((probe.get("target") for probe in reversed(probes)
                         if urlsplit(str(probe.get("target") or "")).path not in ("", "/")), "")
    param = str(declared.get("param") or declared.get("field") or _query_param(probe_target) or "")
    location = str(declared.get("location") or "")
    if not location:
        location = "query" if param and param in urlsplit(str(probe_target)).query else "unknown"
    # The hypothesis statement is the one sentence that says where the input went,
    # which is exactly what the entry-point note is for. It is operator prose
    # carried through, screened by `validate` and by nothing else.
    hypothesis = state.hypothesis(str(finding.get("hypothesis_id") or "")) or {}
    # No probe target means no observed path, and `path_shape` is then left out
    # rather than defaulted to "/". A card that says the entry point is the root
    # when nothing was recorded about the path has invented the one field the
    # next agent would use to pick a request, and a card is read as observation.
    entry = {"location": location, "param": param,
             "path_shape": _path_shape(probe_target) if probe_target else "",
             "note": bound(str(declared.get("note") or hypothesis.get("statement") or ""), 300)}
    if declared.get("method"):
        entry["method"] = str(declared["method"])

    checks = [str(check.get("check")) for check in ((finding.get("proof") or {}).get("checks") or [])
              if check.get("ok")]
    product = next((m.split(":", 1)[1] for m in markers if m.startswith("product:")), "an unnamed stack")
    # One line per product rather than one per marker: three lines naming the
    # same product at three precisions reads as three conditions and is one.
    grouped: dict[str, list[str]] = {}
    for marker in markers:
        prefix, _, body = marker.partition(":")
        name, _, release = body.partition("/")
        grouped.setdefault(name, [])
        if prefix == "version" and release and release not in grouped[name]:
            grouped[name].append(release)
    preconditions = [
        f"the service is observed to be {name}"
        + (f", at version {', '.join(releases)} (the major version alone is a weaker match)"
           if releases else "")
        for name, releases in list(grouped.items())[:6]]
    reaches = f" reaches {entry['path_shape']}" if entry["path_shape"] else \
              " exists, on a path this card does not name because no probe recorded one"
    preconditions.append(f"a {location} input named {param!r}{reaches}" if param else
                         f"an input of some kind{reaches}")
    if first["tier"]:
        preconditions.append(f"the {first['tier']} tier is enabled for the engagement, which is "
                             f"what the first discriminating step needs")
    preconditions.append(f"the proof requirement is unchanged: {matrix_spec.requirement}")

    card = {
        "schema": SCHEMA,
        "slug": _slug_for(vuln_class, entry, markers, source_digest(engagement, finding_id)),
        "title": bound(f"{vuln_class} via a {location} input on {product}", 160),
        "vuln_class": vuln_class,
        "severity": str(finding.get("severity") or matrix_spec.severity),
        "stack": {
            "server": str(stack_seen.get("server") or "").strip(),
            "powered_by": str(stack_seen.get("powered_by") or "").strip(),
            "framework": [str(item).strip() for item in (stack_seen.get("technologies") or [])][:12],
            "versions": _versions_of(stack_seen)[:12],
            "markers": markers[:24],
        },
        "entry_point": entry,
        "steps": steps,
        "first_discriminating_probe": first,
        "proof": {"kind": matrix_spec.kind,
                  "requirement": bound(matrix_spec.requirement, 400),
                  "checks_passed": checks[:12]},
        "preconditions": [bound(line, 400) for line in preconditions],
        "blast_radius": BLAST_RADIUS_BY_CLASS.get(matrix_spec.vuln_class) or BLAST_RADIUS.get(
            matrix_spec.kind, [
                f"{matrix_spec.kind} is a proof shape with no blast radius written down yet: state "
                f"what reuse can damage before reusing this card."]),
        "reuse": REUSE_CAVEAT,
        "source_digest": source_digest(engagement, finding_id),
        "recorded": now_iso(),
    }
    card["stack"] = {key: value for key, value in card["stack"].items() if value or key == "markers"}
    card["entry_point"] = {key: value for key, value in card["entry_point"].items() if value}

    verdict = validate(card, engagement=engagement)
    if not verdict:
        raise CardRefused(verdict.reasons, card)
    return card


def harvest(engagement: str, directory: str | Path | None = None) -> dict:
    """Write a card for every confirmed finding that does not have one yet.

    A finding already on file is skipped by `source_digest`, so harvesting the
    same engagement twice writes nothing the second time. A finding whose card
    validation refuses is skipped with the reason, not written in a weaker form:
    a corpus is worth reading only if everything in it passed the same gate.
    """
    from ..ledger.state import State
    state = State.load(engagement)
    on_file = {card.get("source_digest"): card.get("slug") for card in cards(directory)}
    written, skipped = [], []
    for finding in (state.data.get("findings") or []):
        finding_id = str(finding.get("id") or "")
        digest = source_digest(engagement, finding_id)
        if digest in on_file:
            skipped.append({"finding": finding_id, "vuln_class": finding.get("vuln_class"),
                            "why": f"already on file as {on_file[digest]}"})
            continue
        try:
            card = card_from_finding(engagement, finding_id)
            path = write_card(card, directory)
        except CardRefused as refusal:
            skipped.append({"finding": finding_id, "vuln_class": finding.get("vuln_class"),
                            "why": refusal.reason})
            continue
        except (KeyError, OSError, ValueError) as error:
            # One finding that cannot be read, or one corpus file that cannot be
            # written, skips that finding and reports why. Letting it propagate
            # would abort the harvest and lose the cards already written from the
            # report, which is the one thing the caller needs to know afterwards.
            skipped.append({"finding": finding_id, "vuln_class": finding.get("vuln_class"),
                            "why": f"could-not-write: {type(error).__name__}: {error}"})
            continue
        on_file[digest] = card["slug"]
        written.append({"finding": finding_id, "slug": card["slug"], "path": str(path),
                        "vuln_class": card["vuln_class"]})
    return {"corpus": str(_dir(directory)), "written": written, "skipped": skipped,
            "summary": f"{len(written)} card(s) written, {len(skipped)} skipped"}


# --- matching -----------------------------------------------------------------

def match(stack, class_hint: str | None = None, limit: int = 5,
          directory: str | Path | None = None) -> list[dict]:
    """Rank cards against an observed stack. A ranking, never evidence.

    `score` is the share of the card's own markers this target has been observed
    to have — nothing more. It does not go up because a chain is common, and a
    score of 1.0 is a card about a stack that looks the same, not a finding.

    `unobserved` is the half worth reading. Those are the markers the card needs
    and this target has not been seen to have, and each one is a single request
    that kills the candidate if it comes back absent. A candidate you can kill
    in one request is cheap; a candidate you cannot is where an afternoon goes.

    Cards the write path would now refuse are skipped — `audit` lists them with
    the reason, so a hand-edited card is invisible here but not silently gone.
    """
    observed = set(markers_of(stack))
    wanted = None
    if class_hint:
        from ..ledger.proof import spec_for
        resolved = spec_for(class_hint)
        wanted = resolved.vuln_class if resolved else str(class_hint).strip().lower()
    out = []
    for card in cards(directory):
        if not validate(card):
            continue
        if wanted is not None:
            from ..ledger.proof import spec_for
            card_spec = spec_for(str(card.get("vuln_class") or ""))
            name = card_spec.vuln_class if card_spec else str(card.get("vuln_class") or "").lower()
            if name != wanted:
                continue
        # `validate` has already refused a non-string marker, so this filter is
        # belt and braces — but it is the difference between one hand-edited file
        # and a `knowledge.chain_match` that raises for the whole corpus, and a
        # ranking function that can be taken out by one bad file is a ranking
        # function the controller cannot rely on.
        needed = [marker for marker in ((card.get("stack") or {}).get("markers") or [])
                  if isinstance(marker, str)]
        matched = [marker for marker in needed if marker in observed]
        unobserved = [marker for marker in needed if marker not in observed]
        score = round(len(matched) / len(needed), 2) if needed else 0.0
        out.append({
            "slug": card.get("slug"),
            "vuln_class": card.get("vuln_class"),
            "title": card.get("title"),
            "score": score,
            "candidate": bool(matched),
            "matched": matched,
            "unobserved": unobserved,
            "cheapest_kill": (f"check {unobserved[0]} first: if the target does not have it, this "
                              f"candidate is dead for one request"
                              if unobserved else
                              "every marker this card needs has been observed; the entry point is "
                              "the next thing to check, and it is still a hypothesis"),
            "entry_point": card.get("entry_point"),
            "first_discriminating_probe": card.get("first_discriminating_probe"),
            "preconditions": card.get("preconditions"),
            "blast_radius": card.get("blast_radius"),
            "proof_still_required": (card.get("proof") or {}).get("requirement"),
            "reuse": card.get("reuse") or REUSE_CAVEAT,
            "why_ranked": (f"{len(matched)}/{len(needed)} of this card's markers are present in "
                           f"the observed stack. A shared marker is a reason to form a "
                           f"hypothesis, and it is not evidence about this target."),
        })
    out.sort(key=lambda entry: (-entry["score"], -len(entry["matched"]), str(entry["slug"])))
    return out[: max(1, min(int(limit or 5), 50))]
