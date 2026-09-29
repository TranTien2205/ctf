#!/usr/bin/env python3
"""Shared helpers for tools/forensics/: the JSON envelope and the hooks argv.

Stdlib only, by design. The DFIR parsers this box needs (volatility3, regipy,
python-evtx) are installed per artifact family and several are absent at any
given time, so a primitive that imports one at module load is a primitive that
cannot run. Every tool here degrades to an honest "parser_missing" result rather
than raising, because `tools/hooks.py` treats a missing parser exactly as it
treats a timeout: evidence about availability, never about the artifact.
"""
import json
import os
import shlex

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(TOOLS)
HOOKS = os.path.join(TOOLS, "hooks.py")

EVIDENCE_KINDS = ("surface", "class", "impact", "transport")
VERDICTS = ("confirms", "falsifies", "inconclusive")
# A DFIR answer is read from a supplied artifact, never from a live response.
FLAG_SOURCE = "artifact"


def jprint(obj, compact=False):
    if compact:
        print(json.dumps(obj, separators=(",", ":"), default=str))
    else:
        print(json.dumps(obj, indent=2, default=str))


def excerpt(text, limit=400):
    """A verbatim slice. Never reformatted: the gate compares it to the source."""
    if text is None:
        return ""
    text = text if isinstance(text, str) else str(text)
    return text[:limit]


def post_probe_argv(challenge, verdict, evidence, kind, request, result,
                    bug_class=None, hypothesis_id=None, chain_card=None):
    """The exact argv tools/hooks.py post-probe wants, as a list."""
    argv = ["python3", HOOKS, "post-probe", challenge,
            "--verdict", verdict, "--request", request, "--result", result]
    if evidence:
        argv += ["--evidence", evidence, "--evidence-kind", kind]
    if bug_class:
        argv += ["--class", bug_class]
    if hypothesis_id:
        argv += ["--hypothesis-id", hypothesis_id]
    if chain_card:
        argv += ["--chain-card", chain_card]
    return argv


def pre_flag_argv(challenge, value, evidence):
    return ["python3", HOOKS, "pre-flag", challenge,
            "--value", value, "--source", FLAG_SOURCE, "--evidence", evidence]


def as_command(argv):
    return " ".join(shlex.quote(a) for a in argv)


def downgrade(verdict, matched, parser_ok):
    """Mirror the gate's rule locally so a confirm is never even proposed.

    A parser that did not run, or a filter that matched nothing, cannot confirm.
    This is the forensics analogue of tools/web/http_probe.py refusing to propose
    a confirmation on a dead connection.
    """
    reasons = []
    if not parser_ok:
        reasons.append("no parser produced a record; this is availability "
                       "evidence, not evidence about the artifact")
    if not matched:
        reasons.append("the filter matched no record, so there is no verbatim "
                       "excerpt to confirm with")
    if reasons and verdict == "confirms":
        return "inconclusive", ("transport" if not parser_ok else "surface"), reasons
    return verdict, None, reasons


def envelope(mode, **fields):
    out = {"mode": mode}
    out.update(fields)
    return out
