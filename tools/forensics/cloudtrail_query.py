#!/usr/bin/env python3
"""Query an AWS CloudTrail delivery, and never mistake a failed call for an action.

CloudTrail is the one DFIR artifact family that needs no parser at all -- it is
JSON -- which is exactly why it gets answered by hand with `jq` and why the same
four mistakes keep producing confident wrong answers. Each one is a real
property of the format, not a style preference:

1. THE DELIVERY IS GZIPPED, AND NESTED. Real CloudTrail arrives as
   `AWSLogs/<acct>/CloudTrail/<region>/<y>/<m>/<d>/*.json.gz`, one object per
   file, each `{"Records":[...]}`. A tool that globs `*.json` finds nothing and
   reports an empty trail, which reads identically to a quiet account. This walks
   a tree, reads `.gz` transparently, and COUNTS the files it skipped and why.
2. `CloudTrail-Digest` FILES ARE NOT EVENTS. They are integrity digests that sit
   in the same tree and carry no `eventName`. Merged in, they inflate every count.
   They are identified and excluded, and the exclusion is reported.
3. `errorCode` MEANS THE CALL FAILED. `AccessDenied` on `CreateUser` is an
   attempt, not a created user, and answering "the attacker created svc-report"
   off such a record is wrong. Failed calls are kept (a wall of AccessDenied is
   itself the finding) but counted separately, and --summary reports the first
   SUCCEEDED non-read action, not the first record.
4. THE PRINCIPAL IS OFTEN NOT `userIdentity.arn`. For a role session that field
   is the session's own arn; the identity that assumed it is
   `userIdentity.sessionContext.sessionIssuer.arn`, and for a federated or
   instance-profile call the useful name may only be in `principalId` or
   `userIdentity.type`. All of them are extracted into one `principal` block, each
   labelled with the path it came from, so an answer names a field rather than a
   guess.

`readOnly` is advisory and is absent on some older records; absence is reported as
unknown rather than treated as a write. eventTime is ISO 8601 UTC with a trailing
Z, so unlike auth.log this family has no timezone ambiguity -- the timestamps are
answerable as written.

    python3 tools/forensics/cloudtrail_query.py --input <dir-or-file> --summary \\
        --challenge <sherlock>-q1
    python3 tools/forensics/cloudtrail_query.py --input <dir> --event-name CreateUser \\
        --succeeded-only --challenge <sherlock>-q2 --answer requestParameters.userName
    python3 tools/forensics/cloudtrail_query.py --input <dir> \\
        --principal-contains attacker --challenge <sherlock>-q3 --answer sourceIPAddress
"""
import argparse
import gzip
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkit  # noqa: E402

DATA_EXT = (".json", ".jsonl", ".json.gz", ".jsonl.gz", ".gz")
# Read-event names that carry no mutation whatever readOnly says. Used only to
# ANNOTATE, never to filter: the authority is the readOnly field when present.
READ_PREFIXES = ("Describe", "Get", "List", "Lookup", "Head", "BatchGet",
                 "Search", "Query", "Scan", "Select", "Preview", "Estimate")


def open_maybe_gz(path):
    if path.endswith(".gz"):
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8",
                               errors="replace")
    return open(path, encoding="utf-8", errors="replace")


def load_file(path):
    """Records from one file, plus why it yielded none.

    Accepts the three shapes a delivery actually takes: {"Records":[...]},
    a bare JSON array, and newline-delimited objects.
    """
    try:
        with open_maybe_gz(path) as fh:
            text = fh.read()
    except (OSError, EOFError, gzip.BadGzipFile) as exc:
        return [], "unreadable: %s" % exc
    stripped = text.lstrip()
    if not stripped:
        return [], "empty file"
    if stripped[0] in "{[":
        try:
            doc = json.loads(stripped)
        except ValueError:
            # not one document: try newline-delimited before giving up
            recs, bad = [], 0
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    recs.append(json.loads(line))
                except ValueError:
                    bad += 1
            if recs:
                return recs, ("%d line(s) were not JSON" % bad) if bad else None
            return [], "not valid JSON and not newline-delimited JSON"
        if isinstance(doc, dict):
            if "Records" in doc and isinstance(doc["Records"], list):
                return doc["Records"], None
            if "digestPublicKeyFingerprint" in doc or "digestS3Object" in doc:
                return [], "digest file, not an event file"
            if "eventName" in doc or "eventTime" in doc:
                return [doc], None
            return [], "JSON object with no Records array and no eventName"
        if isinstance(doc, list):
            return doc, None
        return [], "JSON was neither an object nor an array"
    return [], "does not begin with { or ["


def discover(paths):
    """Every candidate event file under the given paths, with the skips counted."""
    files, skipped = [], []
    for root in paths:
        if os.path.isfile(root):
            files.append(root)
            continue
        if not os.path.isdir(root):
            skipped.append({"path": root, "why": "neither a file nor a directory"})
            continue
        for base, dirs, names in os.walk(root):
            dirs.sort()
            for name in sorted(names):
                full = os.path.join(base, name)
                if "CloudTrail-Digest" in full or name.startswith("."):
                    skipped.append({"path": full, "why": "digest or hidden file"})
                    continue
                if not name.endswith(DATA_EXT):
                    skipped.append({"path": full, "why": "extension is not JSON"})
                    continue
                files.append(full)
    return files, skipped


def dotted(obj, path):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


def principal_of(rec):
    """Every identity field present, each labelled with where it was read.

    Nothing is collapsed into a single "user" string: a role session has two
    identities and which one answers the question depends on the question.
    """
    ident = rec.get("userIdentity") or {}
    out = {}
    for label, path in (
            ("type", "type"),
            ("arn", "arn"),
            ("userName", "userName"),
            ("principalId", "principalId"),
            ("accountId", "accountId"),
            ("invokedBy", "invokedBy"),
            ("sessionIssuer.arn", "sessionContext.sessionIssuer.arn"),
            ("sessionIssuer.userName", "sessionContext.sessionIssuer.userName"),
            ("sessionIssuer.type", "sessionContext.sessionIssuer.type"),
            ("mfaAuthenticated", "sessionContext.attributes.mfaAuthenticated")):
        val = dotted(ident, path)
        if val is not None:
            out[label] = val
    return out


def is_read(rec):
    """(read_only, how_it_was_decided). Absence of readOnly is never a write."""
    flag = rec.get("readOnly")
    if isinstance(flag, bool):
        return flag, "readOnly field"
    name = rec.get("eventName") or ""
    if name.startswith(READ_PREFIXES):
        return True, "eventName prefix (readOnly absent)"
    return None, "unknown: readOnly absent and the name is not a read prefix"


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="eventTime is UTC with a trailing Z, so timestamps here are "
               "answerable as written. A record carrying errorCode is an ATTEMPT.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", action="append", required=True, metavar="PATH",
                    help="repeatable; a file, a .json.gz, or a directory to walk")

    f = ap.add_argument_group("filters")
    f.add_argument("--event-name", action="append", default=[], metavar="NAME",
                   help="repeatable; exact match on eventName")
    f.add_argument("--event-source", action="append", default=[], metavar="SRC",
                   help="repeatable; e.g. iam.amazonaws.com")
    f.add_argument("--principal-contains", metavar="SUBSTRING",
                   help="case-insensitive substring of ANY identity field")
    f.add_argument("--source-ip", metavar="IP", help="exact match on sourceIPAddress")
    f.add_argument("--region", metavar="REGION", help="exact match on awsRegion")
    f.add_argument("--error-code", metavar="CODE",
                   help="exact match on errorCode; use --failed-only for any error")
    f.add_argument("--since", metavar="TS", help="ISO 8601; compared as a string "
                                                 "against eventTime, which is UTC")
    f.add_argument("--until", metavar="TS")
    f.add_argument("--contains", metavar="SUBSTRING",
                   help="case-insensitive substring of the whole record JSON")
    f.add_argument("--succeeded-only", action="store_true",
                   help="drop records carrying errorCode: only calls that worked")
    f.add_argument("--failed-only", action="store_true",
                   help="keep only records carrying errorCode")
    f.add_argument("--writes-only", action="store_true",
                   help="drop records decided read-only; records whose readOnly is "
                        "absent AND whose name is not a read prefix are KEPT")
    f.add_argument("--limit", type=int, default=20,
                   help="records printed (default 20); counts are over every match")
    f.add_argument("--order", choices=("asc", "desc"), default="asc")
    f.add_argument("--summary", action="store_true",
                   help="actors, addresses, event counts and the first SUCCEEDED "
                        "non-read action")

    h = ap.add_argument_group("hooks.py argv")
    h.add_argument("--challenge", required=True)
    h.add_argument("--class", dest="bug_class", metavar="BUG_CLASS")
    h.add_argument("--hypothesis-id")
    h.add_argument("--chain-card")
    h.add_argument("--evidence-kind", choices=fkit.EVIDENCE_KINDS, default="class")
    h.add_argument("--on-match", choices=fkit.VERDICTS, default="inconclusive")
    h.add_argument("--on-miss", choices=fkit.VERDICTS, default="inconclusive")
    h.add_argument("--answer", metavar="FIELD",
                   help="dotted path in the first match, e.g. sourceIPAddress or "
                        "requestParameters.userName")
    h.add_argument("--excerpt", type=int, default=400)
    ap.add_argument("--compact", action="store_true")
    a = ap.parse_args()

    if a.succeeded_only and a.failed_only:
        ap.error("--succeeded-only and --failed-only are opposites")

    files, skipped = discover(a.input)
    records, file_reports = [], []
    for path in files:
        recs, why = load_file(path)
        file_reports.append({"path": path, "records": len(recs),
                             **({"note": why} if why else {})})
        for rec in recs:
            if isinstance(rec, dict):
                records.append(rec)
    parsed_any = bool(records)

    matched, read_unknown, failed_n = [], 0, 0
    for rec in records:
        raw = json.dumps(rec, sort_keys=True, default=str)
        name = rec.get("eventName")
        if a.event_name and name not in a.event_name:
            continue
        if a.event_source and rec.get("eventSource") not in a.event_source:
            continue
        if a.source_ip and rec.get("sourceIPAddress") != a.source_ip:
            continue
        if a.region and rec.get("awsRegion") != a.region:
            continue
        err = rec.get("errorCode")
        if a.error_code and err != a.error_code:
            continue
        if a.succeeded_only and err:
            continue
        if a.failed_only and not err:
            continue
        ro, _how = is_read(rec)
        if a.writes_only and ro is True:
            continue
        when = rec.get("eventTime") or ""
        if a.since and when and when < a.since:
            continue
        if a.until and when and when >= a.until:
            continue
        if a.principal_contains:
            blob = json.dumps(principal_of(rec), default=str).lower()
            if a.principal_contains.lower() not in blob:
                continue
        if a.contains and a.contains.lower() not in raw.lower():
            continue
        if ro is None:
            read_unknown += 1
        if err:
            failed_n += 1
        matched.append({
            "eventTime": rec.get("eventTime"),
            "eventName": name,
            "eventSource": rec.get("eventSource"),
            "awsRegion": rec.get("awsRegion"),
            "sourceIPAddress": rec.get("sourceIPAddress"),
            "userAgent": rec.get("userAgent"),
            "errorCode": err,
            "errorMessage": rec.get("errorMessage"),
            "read_only": ro,
            "principal": principal_of(rec),
            "requestParameters": rec.get("requestParameters"),
            "responseElements": rec.get("responseElements"),
            "eventID": rec.get("eventID"),
            # the verbatim record, and the only string offered as evidence
            "raw": raw,
        })

    matched.sort(key=lambda r: (r.get("eventTime") or ""),
                 reverse=(a.order == "desc"))
    first = matched[0] if matched else None
    evidence = fkit.excerpt(first["raw"] if first else "", a.excerpt)
    verdict, forced_kind, reasons = fkit.downgrade(
        a.on_match if matched else a.on_miss, bool(matched), parsed_any)
    kind = forced_kind or a.evidence_kind

    request = "cloudtrail_query.py " + " ".join(
        ["--input %s" % p for p in a.input] +
        ["--event-name %s" % n for n in a.event_name] +
        (["--principal-contains %s" % a.principal_contains] if a.principal_contains else []) +
        (["--succeeded-only"] if a.succeeded_only else []) +
        (["--writes-only"] if a.writes_only else []))
    result = "%d of %d record(s) matched across %d file(s)" % (
        len(matched), len(records), len(files))

    out = fkit.envelope(
        "cloudtrail-query",
        ok=True,
        challenge=a.challenge,
        parser="stdlib json + gzip; no boto3 and no AWS call",
        parser_ok=parsed_any,
        files_considered=len(files),
        files=file_reports[:40],
        files_skipped=len(skipped),
        skipped_examples=skipped[:10],
        records_total=len(records),
        records_matched=len(matched),
        matched_failed_calls=failed_n,
        matched_read_only_unknown=read_unknown,
        proved_negative=(not matched and parsed_any),
        records=matched[:a.limit] if a.limit else matched,
        verdict=verdict,
        evidence_kind=kind,
        evidence=evidence,
        verdict_downgrades=reasons,
        notes=[
            "a record carrying errorCode is an ATTEMPT, not a completed action",
            "readOnly absent is reported as unknown, never treated as a write",
            "for a role session the assuming identity is "
            "userIdentity.sessionContext.sessionIssuer.arn, not userIdentity.arn",
        ],
    )
    if a.summary:
        actors, ips, names, by_day = {}, {}, {}, {}
        first_write = None
        for rec in matched:
            key = (rec["principal"].get("arn")
                   or rec["principal"].get("sessionIssuer.arn")
                   or rec["principal"].get("userName")
                   or rec["principal"].get("principalId")
                   or rec["principal"].get("type") or "unknown")
            actors[key] = actors.get(key, 0) + 1
            if rec.get("sourceIPAddress"):
                ips[rec["sourceIPAddress"]] = ips.get(rec["sourceIPAddress"], 0) + 1
            if rec.get("eventName"):
                names[rec["eventName"]] = names.get(rec["eventName"], 0) + 1
            day = (rec.get("eventTime") or "")[:10]
            if day:
                by_day[day] = by_day.get(day, 0) + 1
            if (first_write is None and not rec.get("errorCode")
                    and rec.get("read_only") is not True):
                first_write = rec
        out["summary"] = {
            "actors": sorted(actors.items(), key=lambda kv: -kv[1])[:15],
            "source_addresses": sorted(ips.items(), key=lambda kv: -kv[1])[:15],
            "event_names": sorted(names.items(), key=lambda kv: -kv[1])[:25],
            "events_per_day": sorted(by_day.items()),
            "first_succeeded_non_read": first_write,
            "_how": "first_succeeded_non_read skips records with errorCode and "
                    "records decided read-only; a record whose readOnly is absent "
                    "and whose name is not a read prefix is eligible",
        }
    argv = fkit.post_probe_argv(a.challenge, verdict, evidence, kind, request,
                                result, a.bug_class, a.hypothesis_id, a.chain_card)
    out["post_probe_argv"] = argv
    out["post_probe_command"] = fkit.as_command(argv)
    if a.answer:
        if not first:
            out["answer"] = {"field": a.answer, "value": None,
                             "refused": "no record matched"}
        else:
            # answer against the ORIGINAL record shape, by dotted path
            value = dotted(first, a.answer)
            if value is None:
                value = dotted(json.loads(first["raw"]), a.answer)
            if value is None:
                out["answer"] = {"field": a.answer, "value": None,
                                 "refused": "the first matched record has no %r"
                                            % a.answer}
            elif first.get("errorCode"):
                out["answer"] = {
                    "field": a.answer, "value": str(value),
                    "refused": "the first matched record carries errorCode %r, so it "
                               "is a failed attempt. Pass --succeeded-only if the "
                               "question asks what was actually done"
                               % first["errorCode"]}
            else:
                out["answer"] = {"field": a.answer, "value": str(value)}
                out["pre_flag"] = fkit.as_command(
                    fkit.pre_flag_argv(a.challenge, str(value), evidence))
    fkit.jprint(out, a.compact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
