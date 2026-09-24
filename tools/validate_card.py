#!/usr/bin/env python3
"""Validate a card against the schema that matches its shape.

Two card shapes live in this tree and they are not interchangeable:

  chain card    knowledge/chains/*.json   -> knowledge/chain-schema.json
  writeup card  knowledge/cards/*.json    -> knowledge/schema.json

Dispatching on the shape is what makes `tools/validate_card.py <card>` correct
for both, which is what AGENTS.md section 5 step 3 tells the agent to run after
writing a chain card. Validating a chain card against the writeup schema fails
every time with "'classification' is a required property", which reads like a
broken card rather than the wrong schema.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(r"(?:AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]+PRIVATE KEY-----|(?:token|password|secret)\s*[:=]\s*['\"][^'\"]{8,})", re.I)
FLAGISH = re.compile(r"(?:HTB|csawctf|flag)\{([^}]{2,})\}", re.I)


def _looks_like_a_real_flag(text):
    """`HTB{...}` is how these cards redact; only flag real-looking content.

    The pattern alone treated the redaction placeholder as a leak, which made a
    correctly redacted card fail validation.
    """
    for inner in FLAGISH.findall(text):
        body = inner.strip()
        if body in {"...", "…"} or set(body) <= {".", "x", "X", "*", "_", "-"}:
            continue
        if body.upper() in {"REDACTED", "FLAG", "SNIP", "OMITTED"}:
            continue
        if sum(c.isalnum() for c in body) >= 2:
            return True
    return False


def _schema_errors(data, schema_name):
    from jsonschema import Draft202012Validator, FormatChecker
    with (ROOT / "knowledge" / schema_name).open() as handle:
        schema = json.load(handle)
    return [f"{e.json_path}: {e.message}"
            for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data)]


def is_chain_card(data):
    """A chain card carries a chain and the probe that decides whether to reuse it."""
    return isinstance(data, dict) and "chain" in data and "first_confirming_probe" in data


def _common_hygiene(data):
    try:
        rendered = json.dumps(data, ensure_ascii=False, allow_nan=False)
    except ValueError:
        return ["nonfinite numbers are not JSON"]
    if SECRET.search(rendered):
        return ["possible secret/token/private key; redact before indexing"]
    return []


SIGNAL_STATS = ROOT / "knowledge" / "signal-stats.json"
SIGNAL_DF_LIMIT = 0.5
SIGNAL_MIN_SPECIFIC = 4


def _count_live(signals):
    """Document frequency for signals the stored table does not cover yet."""
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import chain_match
    except ImportError:
        return {}
    base = ROOT / "challenges"
    corpus = []
    if base.is_dir():
        for entry in sorted(base.iterdir()):
            if not entry.is_dir():
                continue
            names = {c.name for c in entry.iterdir()}
            if names & {"solve.py", "state.json"}:
                continue               # this toolkit's scratch dir, not a handout
            if sum(len(files) for _, _, files in os.walk(entry)) < 3:
                continue
            corpus.append(chain_match.read_source(str(entry)).lower())
    return {s: sum(1 for t in corpus if s.lower() in t) for s in signals}


def _signal_hygiene(data):
    """Reject signals so common they can only produce false candidates.

    chain_match ranks by how rare a matched signal is, so a signal present in
    half the known handouts contributes almost nothing to the right card while
    still putting the wrong one on the candidate list. Measured over the cards
    whose handout is on disk, stripping these took wrong-cards-above-the-right-one
    from 1.91 per query to 0.82. Rebuild the counts with
    `python3 tools/chain_match.py --rebuild-stats`.
    """
    try:
        with SIGNAL_STATS.open(encoding="utf-8") as handle:
            stats = json.load(handle)
        corpus = int(stats["corpus"])
        df = stats["df"]
    except (OSError, ValueError, KeyError, TypeError):
        return []                      # no counts on disk: nothing to compare against
    if corpus < 5:
        return []
    signals = data.get("signals", [])
    if not signals:
        return []      # whether signals are required at all is the schema's call
    unknown = [s for s in signals if s not in df]
    if unknown:
        # a brand new card names signals the stored table has never seen, and
        # those are exactly the ones worth checking, so count them now
        df = dict(df)
        df.update(_count_live(unknown))
    noisy, specific = [], []
    for signal in signals:
        seen = int(df.get(signal, 0))
        if seen / corpus >= SIGNAL_DF_LIMIT:
            noisy.append("%s (in %d/%d handouts)" % (signal, seen, corpus))
        else:
            specific.append(signal)
    # A common signal alongside plenty of specific ones is harmless: the matcher
    # weights by rarity, so it contributes almost nothing. What breaks retrieval
    # is a card that cannot be told apart WITHOUT them, which is the same
    # threshold the signal cleanup uses, so the two rules agree.
    if len(specific) >= SIGNAL_MIN_SPECIFIC:
        return []
    return ["only %d of %d signals are specific enough to identify this chain "
            "(need %d). Common ones here: %s"
            % (len(specific), len(signals), SIGNAL_MIN_SPECIFIC,
               ", ".join(noisy) or "none")]


def validate_chain(data):
    errors = _schema_errors(data, "chain-schema.json")
    if errors:
        return errors
    errors += _signal_hygiene(data)
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,160}", data["id"]):
        errors.append("unsafe card ID")
    if not (ROOT / data["source_note"]).is_file():
        errors.append("source_note does not exist on disk: %s" % data["source_note"])
    if data.get("flag") is not None:
        errors.append("flag must be null; a card never carries a flag")
    if _looks_like_a_real_flag(json.dumps(data, ensure_ascii=False)):
        errors.append("a flag-shaped string appears in the card; redact it")
    if data["verification"]["status"] == "verified_live" and not data["verification"].get("evidence"):
        errors.append("verified_live requires verification.evidence")
    return errors + _common_hygiene(data)


def validate_writeup(data):
    errors = _schema_errors(data, "schema.json")
    if errors:
        return errors
    # a writeup card feeds recognition, so its signals face the same
    # specificity bar as a chain card's
    errors += _signal_hygiene(data)
    if (data.get("quality") or {}).get("verified_live") is True:
        errors.append("a writeup card is hearsay and cannot claim verified_live; "
                      "solve it here and write a chain card instead")
    url = ((data.get("source") or {}).get("url") or "")
    if url.startswith("local://"):
        errors.append("source.url must point at the original writeup, not at this "
                      "repository")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,160}", data["id"]):
        errors.append("unsafe card ID")
    if not data["challenge"]["name"] or not data["challenge"]["category"] or not data["classification"]["primary"]:
        errors.append("name, category and primary must be nonempty")
    if not data["source"]["evidence_spans"]:
        errors.append("source.evidence_spans must be nonempty")
    if data["quality"]["verified_live"] is True and not (data.get("verification") or {}).get("proof"):
        errors.append("verified_live=true requires verification.proof")
    return errors + _common_hygiene(data)


def validate(data):
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        return ["jsonschema is required; validation failed closed"]
    return validate_chain(data) if is_chain_card(data) else validate_writeup(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", help="path to a chain card or a writeup card")
    args = ap.parse_args()
    try:
        with open(args.card, encoding="utf-8") as handle:
            data = json.load(handle)
        kind = "chain" if is_chain_card(data) else "writeup"
        errors = validate(data)
    except (OSError, ValueError) as exc:
        kind, errors = "unknown", [str(exc)]
    print(json.dumps({"valid": not errors, "kind": kind, "errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
