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
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(r"(?:AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]+PRIVATE KEY-----|(?:token|password|secret)\s*[:=]\s*['\"][^'\"]{8,})", re.I)
FLAGISH = re.compile(r"(?:HTB|csawctf|flag)\{[^}]{2,}\}", re.I)


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


def validate_chain(data):
    errors = _schema_errors(data, "chain-schema.json")
    if errors:
        return errors
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,160}", data["id"]):
        errors.append("unsafe card ID")
    if not (ROOT / data["source_note"]).is_file():
        errors.append("source_note does not exist on disk: %s" % data["source_note"])
    if data.get("flag") is not None:
        errors.append("flag must be null; a card never carries a flag")
    if FLAGISH.search(json.dumps(data, ensure_ascii=False)):
        errors.append("a flag-shaped string appears in the card; redact it")
    if data["verification"]["status"] == "verified_live" and not data["verification"].get("evidence"):
        errors.append("verified_live requires verification.evidence")
    return errors + _common_hygiene(data)


def validate_writeup(data):
    errors = _schema_errors(data, "schema.json")
    if errors:
        return errors
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
