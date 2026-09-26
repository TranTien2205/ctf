#!/usr/bin/env python3
"""Send one probe and emit it in the exact shape tools/hooks.py post-probe wants.

The write gate refuses a verdict whose evidence was not a verbatim excerpt of the
response. Copying that excerpt by hand is where a probe result gets rounded up
into a confirmation, so this tool holds the request and the response together and
produces the argv for the gate from what actually came back:

    --request        the request line it sent, one string
    --result         status, length and elapsed
    --evidence       a verbatim substring of the response body, chosen by
                     --evidence-regex or --evidence-contains; never invented
    --verdict        confirms only when the evidence selector actually matched
                     AND --on-match confirms was asked for; otherwise
                     inconclusive, and never confirms on a transport failure
    --evidence-kind  class or impact, as you declare it
    --class / --hypothesis-id / --chain-card  passed straight through

Nothing is written to state here. It prints the command, and with --emit runs
`tools/hooks.py pre-probe` before the request and `post-probe` after it.

    # dry: see the gate command this response justifies
    python3 tools/web/http_probe.py --url 'http://t/?q={{7*7}}' \\
        --challenge mychal --class web-ssti --hypothesis-id h1 \\
        --evidence-regex '\\b49\\b' --on-match confirms --evidence-kind class

    # run the gate too
    python3 tools/web/http_probe.py ... --emit
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, HERE)
import httpkit  # noqa: E402

HOOKS = os.path.join(TOOLS, "hooks.py")
# hooks.py refuses these as confirmations; mirror the rule locally so a probe is
# never even proposed as a confirm on a dead connection.
NEVER_CONFIRMATIONS = re.compile(
    r"time.?out|timed?\s*out|connection\s*(reset|refused)|no\s+response|"
    r"empty\s+response|http[_ ]?000", re.I)
EVIDENCE_KINDS = ("surface", "class", "impact", "transport")
VERDICTS = ("confirms", "falsifies", "inconclusive")


def request_line(args):
    """One stable string for the probe identity the gate de-duplicates on."""
    parts = ["%s %s" % (args.method.upper(), args.url)]
    for item in args.header:
        parts.append("-H %s" % shlex.quote(item))
    if args.body:
        parts.append("-d %s" % shlex.quote(args.body[:200]))
    return " ".join(parts)


def header_blob(resp):
    return "\n".join("%s: %s" % kv for kv in resp.get("headers", {}).items())


def pick_evidence(resp, args):
    """-> (excerpt, selector, matched). The excerpt is ALWAYS a real substring."""
    body = resp.get("body", "")
    haystacks = [("body", body)]
    if args.search_headers:
        haystacks.append(("headers", header_blob(resp)))
    for where, text in haystacks:
        if args.evidence_regex:
            try:
                rx = re.compile(args.evidence_regex, re.S)
            except re.error as exc:
                return "", "bad --evidence-regex: %s" % exc, False
            match = rx.search(text)
            if match:
                start = max(0, match.start() - args.context)
                end = min(len(text), match.end() + args.context)
                return text[start:end], "regex in %s" % where, True
        if args.evidence_contains:
            index = text.find(args.evidence_contains)
            if index >= 0:
                start = max(0, index - args.context)
                end = min(len(text), index + len(args.evidence_contains) + args.context)
                return text[start:end], "literal in %s" % where, True
    if args.evidence_regex or args.evidence_contains:
        return body[: args.excerpt], "selector did not match; head of body", False
    return body[: args.excerpt], "no selector; head of body", False


def build_argv(hook, args, request, result=None, evidence=None, verdict=None,
               evidence_kind=None):
    argv = ["python3", HOOKS, hook, args.challenge, "--request", request]
    if hook == "pre-probe":
        if args.hypothesis_id:
            argv += ["--hypothesis-id", args.hypothesis_id]
        if args.probe_class:
            argv += ["--class", args.probe_class]
        if args.write_ack:
            argv += ["--write-ack"]
        if args.allow_repeat:
            argv += ["--allow-repeat"]
        return argv
    argv += ["--verdict", verdict]
    if result:
        argv += ["--result", result]
    if evidence:
        argv += ["--evidence", evidence]
    if evidence_kind:
        argv += ["--evidence-kind", evidence_kind]
    if args.probe_class:
        argv += ["--class", args.probe_class]
    if args.hypothesis_id:
        argv += ["--hypothesis-id", args.hypothesis_id]
    if args.chain_card:
        argv += ["--chain-card", args.chain_card]
    return argv


def run_hook(argv):
    proc = subprocess.run(argv, capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout)
    except ValueError:
        payload = {"stdout": proc.stdout.strip(), "stderr": proc.stderr.strip()}
    return {"exit": proc.returncode, "hook_output": payload}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--method", default="GET")
    parser.add_argument("--header", action="append", default=[], metavar="K: V")
    parser.add_argument("--body")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--no-follow", action="store_true")

    gate = parser.add_argument_group("hooks.py post-probe fields")
    gate.add_argument("--challenge", required=True,
                      help="challenge name, as tools/state.py knows it")
    gate.add_argument("--class", dest="probe_class",
                      help="bug class; must equal the hypothesis bug_class")
    gate.add_argument("--hypothesis-id", dest="hypothesis_id")
    gate.add_argument("--chain-card")
    gate.add_argument("--evidence-kind", choices=EVIDENCE_KINDS,
                      help="class or impact are the only kinds that can confirm")
    gate.add_argument("--on-match", default="inconclusive", choices=VERDICTS,
                      help="verdict to propose WHEN the evidence selector matches "
                           "(default inconclusive)")
    gate.add_argument("--on-miss", default="inconclusive", choices=VERDICTS,
                      help="verdict when it does not match (default inconclusive)")
    gate.add_argument("--write-ack", action="store_true",
                      help="pass through to pre-probe for a write-shaped request")
    gate.add_argument("--allow-repeat", action="store_true")

    ev = parser.add_argument_group("evidence selection")
    ev.add_argument("--evidence-regex", metavar="REGEX")
    ev.add_argument("--evidence-contains", metavar="LITERAL")
    ev.add_argument("--search-headers", action="store_true",
                    help="also look for the evidence in response headers")
    ev.add_argument("--context", type=int, default=60,
                    help="characters of surrounding response kept with the match")
    ev.add_argument("--excerpt", type=int, default=300)

    parser.add_argument("--emit", action="store_true",
                        help="actually run hooks.py pre-probe then post-probe")
    parser.add_argument("--body-chars", type=int, default=1200)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    request = request_line(args)
    headers = httpkit.parse_headers(args.header)

    pre = None
    if args.emit:
        pre = run_hook(build_argv("pre-probe", args, request))
        if pre["exit"] != 0:
            httpkit.jprint({"mode": "http-probe", "ok": False,
                            "phase": "pre-probe refused", "request": request,
                            "pre_probe": pre,
                            "note": "the gate blocked this probe; nothing was sent"},
                           args.compact)
            return 2

    resp = httpkit.request(args.url, args.method, headers, args.body,
                           timeout=args.timeout, follow=not args.no_follow)

    if resp["ok"]:
        result = "HTTP %s, %d bytes, %.3fs" % (resp["status"], resp["length"],
                                               resp["elapsed"])
    else:
        result = "transport failure: %s (%.3fs)" % (resp.get("error"),
                                                    resp["elapsed"])

    evidence, selector, matched = pick_evidence(resp, args)
    verdict = args.on_match if matched else args.on_miss
    downgrades = []
    if not resp["ok"] and verdict == "confirms":
        verdict = "inconclusive"
        downgrades.append("transport failure can never confirm")
    if verdict == "confirms" and NEVER_CONFIRMATIONS.search(evidence or ""):
        verdict = "inconclusive"
        downgrades.append("the excerpt reads as a timeout or a dead connection")
    if verdict == "confirms" and not (evidence or "").strip():
        verdict = "inconclusive"
        downgrades.append("no verbatim excerpt to quote")
    kind = args.evidence_kind
    if verdict == "confirms" and kind not in ("class", "impact"):
        verdict = "inconclusive"
        downgrades.append("verdict=confirms needs --evidence-kind class or impact")
    if not resp["ok"] and kind != "transport":
        # hooks.py records the kind verbatim; a dead connection is evidence
        # about availability, so it must not be filed as class or impact.
        downgrades.append("transport failure: evidence-kind forced to transport")
        kind = "transport"
    if not kind:
        kind = "class" if matched else "surface"

    post_argv = build_argv("post-probe", args, request, result, evidence, verdict,
                           kind)

    report = {
        "mode": "http-probe", "ok": True,
        "probe": {
            "request": request,
            "result": result,
            "status": resp.get("status"),
            "length": resp.get("length"),
            "elapsed": resp.get("elapsed"),
            "headers": resp.get("headers", {}),
            "body_head": resp.get("body", "")[: args.body_chars],
            "body_truncated": len(resp.get("body", "")) > args.body_chars,
        },
        "evidence": {"excerpt": evidence, "selector": selector,
                     "matched": matched, "kind": kind,
                     # an excerpt taken from --search-headers is verbatim too, so
                     # the check covers the header block, not the body alone
                     "is_verbatim_substring": bool(evidence) and
                                              (evidence in resp.get("body", "") or
                                               evidence in header_blob(resp))},
        "verdict": verdict,
        "verdict_downgrades": downgrades,
        "post_probe_command": " ".join(shlex.quote(part) for part in post_argv),
        "post_probe_argv": post_argv,
        "gate": "tools/hooks.py post-probe is the only write path for this verdict",
    }
    if pre:
        report["pre_probe"] = pre
    if args.emit:
        report["post_probe"] = run_hook(post_argv)
    else:
        report["next_action"] = ("review the excerpt, then run post_probe_command "
                                "(or re-run with --emit)")
    httpkit.jprint(report, args.compact)
    return 0 if resp["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
