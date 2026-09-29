#!/usr/bin/env python3
"""Merge several artifact exports into one UTC-ordered timeline, honestly.

A multi-part investigation question -- "what happened between the first failed
logon and the service install" -- is answered from ONE timeline, not from four
tools read side by side. The merge is where the answer is normally lost:

  - four exports carry four clocks. One column is ISO with a +02:00 offset, one
    is epoch seconds, one is a Windows FILETIME, one has no timezone at all.
    Merged as text, 10:00 sorts before 09:00, and a local-time row lands an hour
    away from the UTC row that caused it. Done by hand in a dataframe, one mixed
    column silently degrades to object dtype and the sort is lexical from then
    on, with nothing in the output saying so.
  - a row whose timestamp will not parse gets dropped by most ad-hoc merges.
    The dropped row is often the interesting one: a zeroed or malformed
    timestamp is itself a finding, and a silent drop also hides truncation.
  - the gap between consecutive rows is what locates a cleared-log window, and
    no gap is visible until every source is on one axis.

So every source is normalised to UTC, every assumption that had to be made is
stated with the number of rows it affected, unparsed rows are COUNTED and
sampled rather than discarded, and --gap surfaces the largest holes.

A timeline is a view, not a finding. The verdict proposed to tools/hooks.py is
inconclusive with evidence-kind surface unless --contains actually matched a
merged record, and then the excerpt is that record verbatim, so no excerpt is
ever hand-copied. fkit.downgrade has the last word: nothing parsed or nothing
matched can never be proposed as a confirmation.

    python3 tools/forensics/timeline_merge.py \\
        --source tools/forensics/fixtures/timeline/auth_events.csv:timestamp:auth \\
        --source tools/forensics/fixtures/timeline/proc_events.tsv:epoch:proc \\
        --source tools/forensics/fixtures/timeline/edr_alerts.jsonl:event.observed_utc:edr \\
        --challenge demo --gap 600

    # numbers that are 100ns ticks since 1601 need to say so
    ... --source tools/forensics/fixtures/timeline/mft_filetime.csv:created_filetime:mft --filetime

--format and --filetime attach to the --source they follow, so several sources
with different shapes can be given in one run.
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkit  # noqa: E402

UTC = timezone.utc
FILETIME_EPOCH = datetime(1601, 1, 1, tzinfo=UTC)
# 1e11 seconds is the year 5138; 1e11 milliseconds is 1973. Anything at or above
# the threshold is therefore milliseconds, and the count of each reading is
# reported so the choice is auditable instead of implicit.
MS_THRESHOLD = 10 ** 11
SAMPLE_CAP = 3                 # unparsed rows kept per source, as evidence samples
PLAUSIBLE_LOW = datetime(1970, 1, 1, tzinfo=UTC)
PLAUSIBLE_HIGH = datetime(2200, 1, 1, tzinfo=UTC)

HINT = ("if this is a Windows FILETIME the source needs --filetime")
OUT_OF_RANGE = "%s is not a time any epoch reading can represent; " + HINT

NUMERIC = re.compile(r"^[+-]?\d+(?:\.\d+)?$")
LONG_FRACTION = re.compile(r"^(.*\.\d{6})\d+(.*)$")

# Only formats that are exercised by the fixtures are listed here.
STRPTIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%m/%d/%Y %H:%M:%S",
    "%d/%b/%Y:%H:%M:%S %z",
)

FORMAT_BY_EXTENSION = {
    ".csv": "csv",
    ".tsv": "tsv",
    ".tab": "tsv",
    ".jsonl": "jsonl",
    ".ndjson": "jsonl",
    ".jsonlines": "jsonl",
}
DELIMITER = {"csv": ",", "tsv": "\t"}

ASSUMPTIONS = {
    "naive_utc": "a timestamp carrying no timezone was read as UTC",
    "offset_to_utc": "a timestamp carrying an explicit offset was converted to UTC",
    "epoch_seconds": "a bare number below 1e11 was read as epoch seconds",
    "epoch_milliseconds": "a bare number at or above 1e11 was read as epoch milliseconds",
    "filetime": "a number on a --filetime source was read as 100ns ticks since 1601-01-01 UTC",
}


class SourceAction(argparse.Action):
    """Append one source, so later per-source flags know which one they mean."""

    def __call__(self, parser, namespace, values, option_string=None):
        sources = getattr(namespace, "sources", None) or []
        sources.append(parse_source_spec(values, parser))
        namespace.sources = sources


class SourceOptionAction(argparse.Action):
    """A flag that modifies the most recent --source rather than the whole run."""

    def __call__(self, parser, namespace, values, option_string=None):
        sources = getattr(namespace, "sources", None) or []
        if not sources:
            parser.error("%s has to follow a --source" % option_string)
        sources[-1][self.dest] = True if self.nargs == 0 else values


def parse_source_spec(spec, parser):
    """PATH:TIMECOL[:LABEL] -> dict. The last fields win, so a path may hold ':'."""
    parts = spec.split(":")
    if len(parts) < 2:
        parser.error("--source wants PATH:TIMECOL[:LABEL], got %r" % spec)
    if len(parts) == 2:
        path, timecol, label = parts[0], parts[1], ""
    else:
        path, timecol, label = ":".join(parts[:-2]), parts[-2], parts[-1]
    if not path or not timecol:
        parser.error("--source wants PATH:TIMECOL[:LABEL], got %r" % spec)
    return {"path": path, "timecol": timecol,
            "label": label or os.path.basename(path),
            "format": None, "filetime": False}


def resolve_format(source, parser):
    if source["format"]:
        fmt = source["format"].lower()
        if fmt not in ("csv", "tsv", "jsonl"):
            parser.error("--format wants csv, tsv or jsonl, got %r" % source["format"])
        return fmt
    ext = os.path.splitext(source["path"])[1].lower()
    fmt = FORMAT_BY_EXTENSION.get(ext)
    if not fmt:
        parser.error("cannot tell the format of %s from its extension; "
                     "pass --format csv|tsv|jsonl after that --source"
                     % source["path"])
    return fmt


def from_filetime(text):
    ticks = int(float(text))
    if ticks <= 0:
        raise ValueError("FILETIME is zero or negative")
    return in_range(lambda: FILETIME_EPOCH + timedelta(microseconds=ticks / 10.0),
                    text), "filetime"


def from_numeric(text):
    value = float(text)
    if abs(value) >= MS_THRESHOLD:
        return in_range(lambda: datetime.fromtimestamp(value / 1000.0, UTC),
                        text), "epoch_milliseconds"
    return in_range(lambda: datetime.fromtimestamp(value, UTC), text), "epoch_seconds"


def in_range(make, text):
    """Keep the one useful message. A raw 'year must be in 1..9999' says nothing
    about what to do; 'this looks like a FILETIME' names the missing flag."""
    try:
        moment = make()
    except (ValueError, OSError, OverflowError):
        raise ValueError(OUT_OF_RANGE % text)
    if not (PLAUSIBLE_LOW <= moment < PLAUSIBLE_HIGH):
        raise ValueError("%s reads as %s, outside 1970..2200; %s"
                         % (text, moment.isoformat(), HINT))
    return moment


def from_text(text):
    candidate = text
    if candidate[-1:] in ("Z", "z"):
        candidate = candidate[:-1] + "+00:00"
    trimmed = LONG_FRACTION.match(candidate)
    if trimmed:                     # 100ns ISO strings: keep microseconds
        candidate = trimmed.group(1) + trimmed.group(2)
    moment = None
    try:
        moment = datetime.fromisoformat(candidate)
    except ValueError:
        for fmt in STRPTIME_FORMATS:
            try:
                moment = datetime.strptime(candidate, fmt)
                break
            except ValueError:
                continue
    if moment is None:
        raise ValueError("no known timestamp format matched")
    if moment.tzinfo is None:
        return in_range(lambda: moment.replace(tzinfo=UTC), text), "naive_utc"
    return in_range(lambda: moment.astimezone(UTC), text), "offset_to_utc"


def parse_timestamp(raw, filetime=False):
    """-> (aware UTC datetime, assumption key). Raises ValueError with a reason."""
    if raw is None:
        raise ValueError("time column is absent from this record")
    text = raw if isinstance(raw, str) else str(raw)
    text = text.strip()
    if not text:
        raise ValueError("time column is empty")
    if filetime:
        return from_filetime(text) if NUMERIC.match(text) else from_text(text)
    if NUMERIC.match(text):
        return from_numeric(text)
    return from_text(text)


class LineTap:
    """Hand csv.reader its lines while keeping the physical text of each record.

    csv.reader does not expose the raw line, and a reconstructed line is not
    verbatim -- which would break the one rule the gate cares about. Tapping the
    iterator keeps the real bytes, including a quoted field that spans lines.
    """

    def __init__(self, handle):
        self.handle = handle
        self.pending = []

    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.handle)
        self.pending.append(line)
        return line

    def take(self):
        raw = "".join(self.pending)
        self.pending = []
        return raw


def dotted_get(record, path):
    """'event.observed_utc' -> record['event']['observed_utc']; digits index lists."""
    current = record
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        elif isinstance(current, list) and part.isdigit() and int(part) < len(current):
            current = current[int(part)]
        else:
            return None
    return current


def column_value(fields, header, timecol):
    if timecol in fields:
        return fields[timecol]
    if timecol.isdigit() and int(timecol) < len(header):
        return fields.get(header[int(timecol)])
    return None


def load_delimited(source, fmt, rows, report):
    delimiter = DELIMITER[fmt]
    with open(source["path"], "r", encoding="utf-8", errors="replace",
              newline="") as handle:
        tap = LineTap(handle)
        reader = csv.reader(tap, delimiter=delimiter)
        header = []
        try:
            header = next(reader)
        except StopIteration:
            report["note"] = "file is empty"
            return
        report["header"] = header
        # Physical line of each record's FIRST line, so a quoted field spanning
        # lines does not silently shift every line number after it.
        line_number = max(1, tap.take().count("\n"))
        for values in reader:
            raw = tap.take()
            start_line = line_number + 1
            line_number += max(1, raw.count("\n"))
            if not values or (len(values) == 1 and not values[0].strip()):
                continue
            report["rows_read"] += 1
            fields = dict(zip(header, values))
            if len(values) > len(header):
                fields["_extra"] = values[len(header):]
            ingest(source, rows, report, fields, raw, start_line,
                   column_value(fields, header, source["timecol"]))


def load_jsonl(source, rows, report):
    with open(source["path"], "r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw in enumerate(handle, 1):
            if not raw.strip():
                continue
            report["rows_read"] += 1
            try:
                record = json.loads(raw)
            except ValueError as exc:
                record_unparsed(report, line_number, raw, "not valid JSON: %s" % exc)
                continue
            value = dotted_get(record, source["timecol"]) \
                if isinstance(record, (dict, list)) else None
            ingest(source, rows, report, record, raw, line_number, value)


def ingest(source, rows, report, fields, raw, line_number, value):
    try:
        moment, assumption = parse_timestamp(value, source["filetime"])
    except ValueError as exc:
        record_unparsed(report, line_number, raw, str(exc), value)
        return
    report["parsed"] += 1
    report["assumptions"][assumption] = report["assumptions"].get(assumption, 0) + 1
    rows.append({"epoch": moment.timestamp(), "ts": moment.isoformat(),
                 "source": source["label"], "line": line_number,
                 "assumption": assumption, "fields": fields, "raw": raw})


def record_unparsed(report, line_number, raw, reason, value=None):
    report["unparsed"] += 1
    if len(report["samples"]) < SAMPLE_CAP:
        report["samples"].append({
            "source": report["label"], "line": line_number, "reason": reason,
            "time_value": None if value is None else fkit.excerpt(value, 120),
            "raw": fkit.excerpt(raw.rstrip("\r\n"), 200)})


def load_source(source, fmt):
    report = {"label": source["label"], "path": source["path"], "format": fmt,
              "timecol": source["timecol"], "filetime": source["filetime"],
              "rows_read": 0, "parsed": 0, "unparsed": 0,
              "assumptions": {}, "samples": []}
    rows = []
    if not os.path.exists(source["path"]):
        report["error"] = "no such file"
        return rows, report
    if not os.path.isfile(source["path"]):
        # A directory or a FIFO here is a mistyped --source, not an empty
        # artifact, and it is never opened: a FIFO would block forever.
        report["error"] = "not a regular file"
        return rows, report
    try:
        if fmt == "jsonl":
            load_jsonl(source, rows, report)
        else:
            load_delimited(source, fmt, rows, report)
    except OSError as exc:
        report["error"] = "%s: %s" % (type(exc).__name__, exc)
    except csv.Error as exc:
        # csv's own limit, not ours: a single field over csv.field_size_limit()
        # raises mid-iteration. Keep the rows already read and say where it
        # stopped rather than tracebacking out of a merge.
        report["error"] = ("csv.Error after %d rows read: %s (csv field-size "
                           "limit is %d characters; this tool does not raise it)"
                           % (report["rows_read"], exc, csv.field_size_limit()))
    if rows:
        report["window"] = {"first": min(r["ts"] for r in rows),
                            "last": max(r["ts"] for r in rows)}
    return rows, report


def window_of(rows):
    if not rows:
        return {"first": None, "last": None, "span_seconds": None}
    return {"first": rows[0]["ts"], "last": rows[-1]["ts"],
            "span_seconds": round(rows[-1]["epoch"] - rows[0]["epoch"], 3)}


def largest_gaps(rows, threshold, top):
    gaps = []
    for index in range(1, len(rows)):
        seconds = rows[index]["epoch"] - rows[index - 1]["epoch"]
        if seconds >= threshold:
            gaps.append({"seconds": round(seconds, 3),
                         "after": rows[index - 1]["ts"],
                         "after_source": rows[index - 1]["source"],
                         "before": rows[index]["ts"],
                         "before_source": rows[index]["source"],
                         "row_index": index})
    gaps.sort(key=lambda g: g["seconds"], reverse=True)
    return gaps[:top]


def find_contains(rows, needle, context):
    for index, row in enumerate(rows):
        position = row["raw"].find(needle)
        if position >= 0:
            start = max(0, position - context)
            end = position + len(needle) + context
            return index, row, row["raw"][start:end].strip("\r\n")
    return -1, None, ""


def shown(row, raw_chars):
    out = dict(row)
    out["raw"] = fkit.excerpt(row["raw"].rstrip("\r\n"), raw_chars)
    return out


def build_parser():
    parser = argparse.ArgumentParser(
        prog="timeline_merge.py",
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--source", action=SourceAction, metavar="PATH:TIMECOL[:LABEL]",
                        help="repeatable. TIMECOL is a column name, a 0-based column "
                             "index, or for JSONL a dotted path")
    parser.add_argument("--format", dest="format", action=SourceOptionAction,
                        choices=("csv", "tsv", "jsonl"),
                        help="override the extension for the preceding --source")
    parser.add_argument("--filetime", dest="filetime", action=SourceOptionAction,
                        nargs=0,
                        help="the preceding --source holds Windows FILETIME ticks")
    parser.add_argument("--since", metavar="TIME",
                        help="drop rows before this time (any supported format)")
    parser.add_argument("--until", metavar="TIME", help="drop rows at or after this time")
    parser.add_argument("--limit", type=int, default=200,
                        help="rows printed, 0 for all (default 200)")
    parser.add_argument("--gap", type=float, metavar="SECONDS",
                        help="report merged gaps of at least this many seconds")
    parser.add_argument("--gap-top", type=int, default=5,
                        help="how many of the largest gaps to report (default 5)")
    parser.add_argument("--raw-chars", type=int, default=300,
                        help="characters of each record kept in the printed rows")

    gate = parser.add_argument_group("hooks.py post-probe fields")
    gate.add_argument("--challenge", required=True,
                      help="challenge name, as tools/state.py knows it")
    gate.add_argument("--contains", metavar="SUBSTRING",
                      help="the only thing a timeline may confirm on: a merged "
                           "record holding this literal")
    gate.add_argument("--on-match", default="inconclusive", choices=fkit.VERDICTS,
                      help="verdict proposed when --contains matches "
                           "(default inconclusive)")
    gate.add_argument("--evidence-kind", choices=fkit.EVIDENCE_KINDS,
                      help="class or impact are the only kinds that can confirm")
    gate.add_argument("--class", dest="bug_class")
    gate.add_argument("--hypothesis-id", dest="hypothesis_id")
    gate.add_argument("--chain-card")
    gate.add_argument("--answer", metavar="VALUE",
                      help="an answer read off the merged timeline; the pre-flag "
                           "argv is emitted only if --contains actually matched")
    gate.add_argument("--context", type=int, default=80,
                      help="characters kept either side of the --contains match")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    sources = getattr(args, "sources", None) or []
    if not sources:
        parser.error("at least one --source PATH:TIMECOL[:LABEL] is required")
    if args.on_match == "confirms" and not args.contains:
        parser.error("--on-match confirms needs --contains SUBSTRING: a timeline "
                     "is a view, so only a matched record can confirm anything")
    seen = {}
    for source in sources:
        label = source["label"]
        seen[label] = seen.get(label, 0) + 1
        if seen[label] > 1:
            source["label"] = "%s#%d" % (label, seen[label])

    bounds = {}
    for name in ("since", "until"):
        text = getattr(args, name)
        if text:
            try:
                bounds[name] = parse_timestamp(text)[0]
            except ValueError as exc:
                parser.error("--%s %r did not parse: %s" % (name, text, exc))

    rows, reports, assumptions = [], [], {}
    for index, source in enumerate(sources):
        fmt = resolve_format(source, parser)
        got, report = load_source(source, fmt)
        for row in got:
            row["_order"] = (row["epoch"], index, row["line"])
        rows.extend(got)
        reports.append(report)
        for key, count in report["assumptions"].items():
            bucket = assumptions.setdefault(key, {"assumption": ASSUMPTIONS[key],
                                                  "rows": 0, "sources": []})
            bucket["rows"] += count
            bucket["sources"].append(report["label"])

    rows.sort(key=lambda r: r["_order"])
    for row in rows:
        row.pop("_order", None)
    all_window = window_of(rows)

    selected = rows
    if "since" in bounds:
        floor = bounds["since"].timestamp()
        selected = [r for r in selected if r["epoch"] >= floor]
    if "until" in bounds:
        ceiling = bounds["until"].timestamp()
        selected = [r for r in selected if r["epoch"] < ceiling]

    parser_ok = bool(rows)
    matched = False
    contains = None
    evidence = ""
    if args.contains:
        index, row, excerpt = find_contains(selected, args.contains, args.context)
        matched = index >= 0
        evidence = fkit.excerpt(excerpt, 400) if matched else ""
        contains = {"needle": args.contains, "searched_rows": len(selected),
                    "matched": matched,
                    "row_index": index if matched else None,
                    "source": row["source"] if matched else None,
                    "ts": row["ts"] if matched else None,
                    "excerpt": evidence,
                    "is_verbatim_substring": (evidence in row["raw"]) if matched else False}

    verdict = args.on_match if matched else "inconclusive"
    kind = args.evidence_kind or ("class" if matched else "surface")
    verdict, forced_kind, reasons = fkit.downgrade(verdict, matched, parser_ok)
    if not args.contains:
        reasons.insert(0, "no --contains was given, so this run is a view only "
                          "and cannot propose a confirmation at all")
    if forced_kind:
        kind = forced_kind
    if verdict == "confirms" and kind not in ("class", "impact"):
        verdict = "inconclusive"
        reasons.append("verdict=confirms needs --evidence-kind class or impact")
    if verdict != "confirms" and not matched:
        kind = "surface"
    if not parser_ok and kind != "transport":
        # Same rule tools/web/http_probe.py applies to a dead connection: no
        # record was produced, so this is evidence about availability.
        reasons.append("no source produced a parsed record: evidence-kind "
                       "forced to transport")
        kind = "transport"

    emitted = selected if args.limit <= 0 else selected[: args.limit]
    request = "timeline-merge %s" % " + ".join(
        "%s:%s" % (r["label"], r["timecol"]) for r in reports)
    if bounds:
        request += " [%s..%s]" % (args.since or "", args.until or "")
    if args.contains:
        request += " contains=%s" % args.contains
    result = "%d rows merged from %d sources, %d selected, %d unparsed, window %s..%s" % (
        len(rows), len(reports), len(selected),
        sum(r["unparsed"] for r in reports), all_window["first"], all_window["last"])

    post_argv = fkit.post_probe_argv(
        args.challenge, verdict, evidence if matched else "", kind, request, result,
        bug_class=args.bug_class, hypothesis_id=args.hypothesis_id,
        chain_card=args.chain_card)

    report = fkit.envelope(
        "timeline-merge", ok=True,
        sources=[{k: v for k, v in r.items() if k != "samples"} for r in reports],
        assumptions=sorted(assumptions.values(), key=lambda a: -a["rows"]),
        merged={"rows_total": len(rows), "rows_selected": len(selected),
                "rows_emitted": len(emitted), "limit": args.limit,
                "window_all": all_window, "window_selected": window_of(selected),
                "sort": "ascending by UTC epoch, then source order, then line"},
        window_filter={"since": args.since, "until": args.until,
                       "since_utc": bounds["since"].isoformat() if "since" in bounds else None,
                       "until_utc": bounds["until"].isoformat() if "until" in bounds else None},
        unparsed={"total": sum(r["unparsed"] for r in reports),
                  "by_source": {r["label"]: r["unparsed"] for r in reports},
                  "samples": [s for r in reports for s in r["samples"]],
                  "policy": "counted and sampled, never dropped silently"},
        rows=[shown(row, args.raw_chars) for row in emitted],
        verdict=verdict, verdict_downgrades=reasons,
        evidence={"excerpt": evidence, "kind": kind, "matched": matched},
        post_probe_command=fkit.as_command(post_argv),
        post_probe_argv=post_argv,
        gate="tools/hooks.py post-probe is the only write path for this verdict")
    if args.gap is not None:
        report["gaps"] = {"threshold_seconds": args.gap, "top": args.gap_top,
                          "found": largest_gaps(selected, args.gap, args.gap_top),
                          "why": "a hole in a merged timeline is where a cleared "
                                 "log window or a stopped agent shows up"}
    if contains is not None:
        report["contains"] = contains
    if args.answer:
        if matched:
            flag_argv = fkit.pre_flag_argv(args.challenge, args.answer, evidence)
            report["pre_flag_command"] = fkit.as_command(flag_argv)
            report["pre_flag_argv"] = flag_argv
        else:
            report["pre_flag_withheld"] = (
                "--answer was given but no merged record matched --contains, so "
                "there is no verbatim excerpt to file it with")
    fkit.jprint(report, args.compact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
