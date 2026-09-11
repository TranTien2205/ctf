#!/usr/bin/env python3
"""Validate the local card schema and additional evidence/secret hygiene."""
import argparse
import json
import re
import sys
from pathlib import Path

SECRET = re.compile(r"(?:AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]+PRIVATE KEY-----|(?:token|password|secret)\s*[:=]\s*['\"][^'\"]{8,})", re.I)


def validate(data):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError:
        return ["jsonschema is required; validation failed closed"]
    with (Path(__file__).resolve().parents[1] / "knowledge/schema.json").open() as handle:
        schema = json.load(handle)
    errors = [f"{error.json_path}: {error.message}" for error in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data)]
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
    try:
        rendered = json.dumps(data, ensure_ascii=False, allow_nan=False)
    except ValueError:
        errors.append("nonfinite numbers are not JSON")
    else:
        if SECRET.search(rendered):
            errors.append("possible secret/token/private key; redact before indexing")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card")
    args = ap.parse_args()
    try:
        with open(args.card, encoding="utf-8") as handle:
            errors = validate(json.load(handle))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({"valid": not errors, "errors": errors}))
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
