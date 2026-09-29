#!/usr/bin/env python3
"""Query converted Windows event log records, and stay honest when nothing parsed.

EVTX answers most Sherlock questions, and this box has no EVTX parser: evtx_dump,
chainsaw, hayabusa and the python Evtx module are all absent today. So the real
pipeline is convert once, query many times - one converter run produces JSONL,
and every question after that is a filter over that JSONL. This tool owns the
query half, because that is the half that must work with nothing installed. It
touches a converter only when one is actually on the box, and when none is, it
says so with the install command instead of guessing.

Three traps this exists to remove:

1. ORDER. evtx_dump defaults to MULTITHREADED output, whose records are complete
   but OUT OF ORDER. Any "what happened first" answer read off the top of such a
   file is silently wrong. Pass `-t 1` when converting, and note that this tool
   never trusts input order either: it parses every timestamp and sorts
   explicitly, and reports `input_was_chronological` so a multithreaded dump is
   visible rather than assumed away.
2. SHAPE. Converters disagree about where a field lives. One normaliser walks a
   dotted path and also tries the shapes listed in FIELD_SHAPES below, so
   `--field DestinationIp=1.2.3.4` works whether the record came from evtx_dump,
   from an xmltodict-style JSON, or from a flattened row.
3. EVIDENCE. A Sherlock answer has to be quotable. Every run prints the verbatim
   source text of the FIRST matched record plus the exact tools/hooks.py argv, so
   the excerpt is never retyped by hand, and `--answer FIELD` prints the pre-flag
   argv for that one field.

Reading is not a write-shaped probe, so no --write-ack is involved. A filter that
matched nothing, or a converter that never ran, is downgraded by fkit.downgrade
and can never be proposed as verdict=confirms.

What is proven and what is not, on this box, today: the .jsonl, .json and .xml
modes and the missing-converter path all ran against the fixtures beside this
file. The two converter branches did NOT run, because evtx_dump is not on PATH
and the Evtx module does not import - that is precisely why this tool exists. The
Evtx branch feeds its per-record XML through the same xml_to_record() that the
proven .xml mode uses, so only the module handle itself is unexercised. Re-verify
`evtx_dump -o jsonl -t 1` against `evtx_dump --help` after installing it, per
this tree's rule against trusting an unrun tool flag.

    # what ran, chronologically, and the command line of the first process
    python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 1 \
        --order asc --challenge sherlock-x --answer CommandLine

    # the ProcessGuid join: Sysmon 1 gives the guid, Sysmon 3 gives the peer
    python3 tools/forensics/evtx_query.py --input sysmon.jsonl --event-id 3 \
        --field ProcessGuid='{...}' --answer DestinationIp --challenge sherlock-x
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fkit  # noqa: E402

# Record shapes the one normaliser handles. Emitted in the output so the operator
# can see what was tried before believing a "field not found".
FIELD_SHAPES = (
    "dotted walk: Event.System.EventID",
    "attribute container flattened by evtx_dump: Event.System.TimeCreated"
    "_attributes.SystemTime, reached by the path Event.System.TimeCreated.SystemTime",
    "attribute container as xmltodict writes it: {'#attributes': {...}}, and an "
    "'@' prefixed attribute key such as TimeCreated['@SystemTime']",
    "text node wrapped beside attributes: EventID = {'#text': '4624', "
    "'@Qualifiers': '0'}",
    "EventData rendered as a list of Data elements: "
    "[{'@Name': 'IpAddress', '#text': '10.0.0.1'}, ...]",
    "flat record with no Event envelope: {'EventID': 4688, 'NewProcessName': ...}",
    "bare field name searched breadth-first anywhere in the record, so "
    "--field DestinationIp=... needs no path",
    "case-insensitive key fallback at each step",
)

EVENT_ID_FIELDS = ("Event.System.EventID", "System.EventID", "EventID", "event_id")
# Ordered by how specific the path is. The bare names at the end are the flat and
# the Sysmon-EventData cases; UtcTime is Sysmon's own field and is already UTC.
TIME_FIELDS = (
    "Event.System.TimeCreated.SystemTime",
    "Event.System.TimeCreated_attributes.SystemTime",
    "Event.EventData.UtcTime",
    "SystemTime",
    "TimeCreated",
    "UtcTime",
    "timestamp",
    "@timestamp",
    "EventTime",
)

# Real install routes for the converter half. Both were read off this tree's
# skills/dfir-sherlock-triage/toolchain.md; neither binary is present here, so
# neither could be re-verified in this run.
INSTALL_ROUTES = (
    "sudo apt install --no-install-recommends python3-evtx libevtx-utils",
    "download the static evtx_dump binary from the omerbenamram/evtx GitHub "
    "releases into ~/.local/bin, then: evtx_dump -o jsonl -t 1 FILE.evtx > FILE.jsonl",
)
EVTX_MAGIC = b"ElfFile\x00"
_TS = re.compile(
    r"^\s*(\d{4})-(\d{2})-(\d{2})"
    r"(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?(?:[.,](\d+))?)?"
    r"\s*(Z|z|[+-]\d{2}:?\d{2})?\s*$")
_EVENT_BLOCK = re.compile(r"<Event\b.*?</Event\s*>", re.S)


# --------------------------------------------------------------------------- #
# field access
# --------------------------------------------------------------------------- #
def _candidates(node, key):
    """Every value in `node` that could reasonably answer to `key`."""
    out = []
    if isinstance(node, dict):
        for name in (key, key + "_attributes", "@" + key, "#" + key):
            if name in node:
                out.append(node[name])
        for holder in ("#attributes", "@attributes", "attributes"):
            sub = node.get(holder)
            if isinstance(sub, dict) and key in sub:
                out.append(sub[key])
        if not out:
            low = key.lower()
            for name, value in node.items():
                if isinstance(name, str) and name.lower() == low:
                    out.append(value)
    elif isinstance(node, list):
        # EventData as a list of <Data Name="..."> elements.
        for item in node:
            if not isinstance(item, dict):
                continue
            name = item.get("@Name") or item.get("Name") or item.get("#name")
            if name == key:
                out.append(item.get("#text", item.get("text", item)))
    return out


def _dig(node, key, last):
    """One step of the walk. Mid-walk, a container beats a scalar of the same name."""
    found = _candidates(node, key)
    if not found:
        return None, False
    if last:
        return found[0], True
    for value in found:
        if isinstance(value, (dict, list)):
            return value, True
    return found[0], True


def _unwrap(value):
    """Leaf value: a text node stored beside its attributes is still a scalar."""
    if isinstance(value, dict) and "#text" in value:
        return value["#text"]
    return value


def _search(record, key):
    """Breadth-first hunt for a bare field name, so shallower wins."""
    queue = [record]
    seen = 0
    while queue and seen < 4000:
        node = queue.pop(0)
        seen += 1
        hit = _candidates(node, key)
        if hit:
            return _unwrap(hit[0]), True
        if isinstance(node, dict):
            queue.extend(v for v in node.values() if isinstance(v, (dict, list)))
        elif isinstance(node, list):
            queue.extend(v for v in node if isinstance(v, (dict, list)))
    return None, False


def field_value(record, name):
    """-> (value, found). Walks a dotted path, then falls back to a bare search.

    The shapes covered are listed in FIELD_SHAPES and are all real converter
    output, not guesses about a format.
    """
    parts = [p for p in str(name).split(".") if p != ""]
    if not parts:
        return None, False
    node, ok = record, True
    for index, part in enumerate(parts):
        node, ok = _dig(node, part, index == len(parts) - 1)
        if not ok:
            break
    if ok:
        return _unwrap(node), True
    return _search(record, parts[-1])


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, default=str)
    return str(value)


def normalise_id(value):
    text = as_text(_unwrap(value)).strip()
    try:
        return str(int(text, 10))
    except (TypeError, ValueError):
        return text


def event_id_of(record):
    for path in EVENT_ID_FIELDS:
        value, found = field_value(record, path)
        if found and as_text(value).strip() != "":
            return normalise_id(value)
    return None


# --------------------------------------------------------------------------- #
# time
# --------------------------------------------------------------------------- #
def parse_time(text):
    """ISO 8601 with or without Z, with any fraction length, normalised to UTC.

    Also accepts a bare date (treated as 00:00:00Z) so --since can be a day, and
    a space instead of T because Sysmon's own UtcTime field writes it that way.
    A numeric offset is subtracted rather than stored, so every comparison in
    this tool happens in UTC.
    """
    if not isinstance(text, str):
        return None
    match = _TS.match(text)
    if not match:
        return None
    year, month, day, hour, minute, second, frac, zone = match.groups()
    micros = 0
    if frac:
        micros = int((frac + "000000")[:6])
    try:
        stamp = datetime(int(year), int(month), int(day), int(hour or 0),
                         int(minute or 0), int(second or 0), micros,
                         tzinfo=timezone.utc)
    except ValueError:
        return None
    if zone and zone not in ("Z", "z"):
        sign = 1 if zone[0] == "+" else -1
        digits = zone[1:].replace(":", "")
        stamp -= sign * timedelta(hours=int(digits[:2]), minutes=int(digits[2:4]))
    return stamp


def time_of(record):
    """-> (datetime|None, raw_string). The first candidate that actually parses."""
    first_raw = ""
    for path in TIME_FIELDS:
        value, found = field_value(record, path)
        if not found:
            continue
        raw = as_text(value)
        if not first_raw and raw and not isinstance(value, (dict, list)):
            first_raw = raw
        stamp = parse_time(raw)
        if stamp is not None:
            return stamp, raw
    return None, first_raw


def iso(stamp):
    return None if stamp is None else stamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# --------------------------------------------------------------------------- #
# loading
# --------------------------------------------------------------------------- #
def _row(raw, record, origin, verbatim=True):
    """verbatim=False when `raw` is this tool's own re-serialisation.

    That text is faithful to the record but does not occur in the input file, so
    it must not be advertised to the gate as a quote from the artifact.
    """
    return {"raw": raw, "record": record, "excerpt_of": origin,
            "verbatim": verbatim}


MAX_READ_ERRORS = 20


def cap_errors(errors, limit=MAX_READ_ERRORS):
    """A mislabelled file fails on every line; 200k error strings help nobody.

    The count is kept, so the suppression is stated rather than silent.
    """
    if len(errors) <= limit:
        return list(errors)
    return list(errors[:limit]) + [
        "... %d further read errors suppressed, %d in total"
        % (len(errors) - limit, len(errors))]


def load_text_records(path):
    """JSONL first, then a whole-document JSON array or object. -> (rows, errors)

    A line that does not parse is recorded and skipped, not fatal: a converter
    dump truncated mid-line still has to answer questions about the lines that
    are intact. The whole-document fallback runs only when NO line parsed.
    """
    rows, errors = [], []
    # utf-8-sig, not utf-8: PowerShell writes JSONL with a BOM, and a plain
    # utf-8 read makes json reject the FIRST record - the "what happened first"
    # answer - while every later line still parses.
    text = open(path, encoding="utf-8-sig", errors="replace").read()
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, list):
                for item in obj:
                    rows.append(_row(json.dumps(item, default=str), item,
                                     "re-serialised record (a JSON array shares "
                                     "one line, so there is no per-record line)",
                                     verbatim=False))
            else:
                rows.append(_row(line, obj, "verbatim source line"))
        except (ValueError, RecursionError, MemoryError) as exc:
            errors.append("line %d is not usable JSON, skipped: %s: %s"
                          % (number, type(exc).__name__, exc))
            continue
    if rows:
        return rows, errors
    try:
        whole = json.loads(text)
    except (ValueError, RecursionError, MemoryError) as exc:
        return [], ["not JSONL and not a JSON document: %s: %s"
                    % (type(exc).__name__, exc)]
    # The per-line errors are dropped on purpose: a pretty-printed JSON document
    # fails on every line as JSONL, and reporting that as 38 read errors would
    # describe a perfectly good file as broken.
    items = whole if isinstance(whole, list) else [whole]
    doc_errors = []
    for index, item in enumerate(items, 1):
        try:
            raw = json.dumps(item, indent=2, default=str)
        except (ValueError, RecursionError, MemoryError) as exc:
            doc_errors.append("document item %d could not be re-serialised: "
                              "%s: %s" % (index, type(exc).__name__, exc))
            continue
        rows.append(_row(raw, item,
                         "re-serialised record (input was a JSON document, not "
                         "line-delimited)", verbatim=False))
    return rows, doc_errors


def _strip_ns(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def _elem_to_obj(elem):
    """XML element -> the same dict shape evtx_dump emits, so one normaliser fits.

    Attributes land in "<Tag>_attributes"; <Data Name="X">v</Data> children land
    as X: v, which is how the EventData block reads in every converter here.
    """
    obj = {}
    for child in elem:
        tag = _strip_ns(child.tag)
        if tag == "Data" and "Name" in child.attrib:
            obj[child.attrib["Name"]] = (child.text or "")
            continue
        if child.attrib:
            obj[tag + "_attributes"] = dict(child.attrib)
        if len(child):
            obj[tag] = _elem_to_obj(child)
        else:
            obj.setdefault(tag, (child.text or "").strip())
    return obj


def xml_to_record(xml_text):
    root = ET.fromstring(xml_text)
    return {_strip_ns(root.tag): _elem_to_obj(root)}


def load_xml_records(path):
    """One or more <Event>...</Event> elements, with or without a wrapping root.

    Each block is parsed on its own, so a file that is a concatenation of records
    and therefore not a single well-formed document still reads.
    """
    rows, errors = [], []
    text = open(path, encoding="utf-8-sig", errors="replace").read()
    blocks = _EVENT_BLOCK.findall(text)
    if not blocks:
        return [], ["no <Event> element found in %s" % os.path.basename(path)]
    for index, block in enumerate(blocks, 1):
        try:
            rows.append(_row(block, xml_to_record(block),
                             "verbatim source XML element"))
        except Exception as exc:                # ParseError, RecursionError, ...
            errors.append("event block %d did not parse: %s: %s"
                          % (index, type(exc).__name__, exc))
    return rows, errors


def evtx_signature(path):
    try:
        head = open(path, "rb").read(len(EVTX_MAGIC))
    except OSError as exc:
        return {"read_error": str(exc)}
    return {"first_bytes": repr(head), "is_evtx_magic": head == EVTX_MAGIC}


def load_evtx_records(path):
    """Convert a .evtx only with a converter that is really installed.

    Order is evtx_dump on PATH, then the python Evtx module. With neither, this
    returns parser_ok false and the install routes; it never raises and never
    pretends to have read a record.
    """
    info = {"converter": None, "detected": [], "install": list(INSTALL_ROUTES),
            "signature": evtx_signature(path)}
    errors = []
    exe = shutil.which("evtx_dump")
    if exe:
        info["detected"].append("evtx_dump on PATH at %s" % exe)
        argv = [exe, "-o", "jsonl", "-t", "1", path]
        info["converter"] = " ".join(argv)
        info["converter_note"] = ("-t 1 forces single-threaded output; the "
                                  "default is multithreaded and out of order")
        try:
            proc = subprocess.run(argv, capture_output=True, text=True,
                                  errors="replace", timeout=900)
        except Exception as exc:                       # missing exec bit, timeout
            return [], info, ["evtx_dump did not run: %s: %s"
                              % (type(exc).__name__, exc)]
        if proc.returncode != 0:
            return [], info, ["evtx_dump exited %d: %s"
                              % (proc.returncode, fkit.excerpt(proc.stderr, 300))]
        rows = []
        for number, line in enumerate(proc.stdout.splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(_row(line, json.loads(line),
                                 "verbatim evtx_dump output line"))
            except ValueError:
                errors.append("converter line %d is not JSON" % number)
        return rows, info, errors
    try:
        import Evtx.Evtx as evtx_mod                   # noqa: N813
    except Exception as exc:
        info["detected"].append("no evtx_dump on PATH")
        info["detected"].append("python Evtx module not importable: %s"
                                % type(exc).__name__)
        return [], info, ["no EVTX converter is installed on this box"]
    info["detected"].append("python Evtx module imported")
    info["converter"] = "python Evtx module, records()[].xml()"
    rows = []
    try:
        with evtx_mod.Evtx(path) as log:
            for index, record in enumerate(log.records(), 1):
                try:
                    xml_text = record.xml()
                    rows.append(_row(xml_text, xml_to_record(xml_text),
                                     "verbatim record XML from the Evtx module"))
                except Exception as exc:
                    errors.append("record %d did not convert: %s: %s"
                                  % (index, type(exc).__name__, exc))
    except Exception as exc:
        return rows, info, errors + ["Evtx module failed on %s: %s: %s"
                                     % (os.path.basename(path),
                                        type(exc).__name__, exc)]
    return rows, info, errors


def load_records(path):
    """-> (rows, info). info always carries parser_ok and how it was decided."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".evtx":
        rows, conv, errors = load_evtx_records(path)
        info = {"kind": "evtx", "parser": conv, "read_errors": errors,
                "parser_ok": bool(rows)}
        return rows, info
    if ext == ".xml":
        rows, errors = load_xml_records(path)
        return rows, {"kind": "xml",
                      "parser": {"converter": "stdlib xml.etree, per <Event> block",
                                 "detected": ["no external converter needed"],
                                 "install": []},
                      "read_errors": errors, "parser_ok": bool(rows)}
    rows, errors = load_text_records(path)
    return rows, {"kind": "json-lines" if ext in (".jsonl", ".ndjson") else "json",
                  "parser": {"converter": "stdlib json, no dependency",
                             "detected": ["already-converted records"],
                             "install": []},
                  "read_errors": errors, "parser_ok": bool(rows)}


# --------------------------------------------------------------------------- #
# filtering
# --------------------------------------------------------------------------- #
def split_pair(spec, parser, flag):
    if "=" not in spec:
        parser.error("%s wants NAME=VALUE, got %r" % (flag, spec))
    name, value = spec.split("=", 1)
    if not name.strip():
        parser.error("%s wants a field name before the '=', got %r" % (flag, spec))
    return name.strip(), value


def matches(record, wanted_ids, exact, contains, event_id):
    """-> (bool, misses). misses names the filter that rejected the record."""
    if wanted_ids and event_id not in wanted_ids:
        return False, ["event-id"]
    for name, want in exact:
        value, found = field_value(record, name)
        if not found or as_text(value) != want:
            return False, ["field %s" % name]
    for name, want in contains:
        value, found = field_value(record, name)
        # Case-insensitive on purpose: the same image path is written
        # C:\Windows in one channel and c:\windows in another, and an answer
        # lost to letter case is the commonest silent miss in this family.
        if not found or want.lower() not in as_text(value).lower():
            return False, ["field-contains %s" % name]
    return True, []


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="evtx_query.py", description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--input", required=True, metavar="PATH",
                        help=".jsonl/.json of converted records, .xml of <Event> "
                             "elements, or .evtx (needs an installed converter)")

    flt = parser.add_argument_group("filters")
    flt.add_argument("--event-id", action="append", default=[], metavar="ID",
                     help="repeatable; matches any of the ids given")
    flt.add_argument("--field", action="append", default=[], metavar="NAME=VALUE",
                     help="repeatable; exact, case-sensitive match")
    flt.add_argument("--field-contains", action="append", default=[],
                     metavar="NAME=SUBSTRING",
                     help="repeatable; substring, case-INsensitive")
    flt.add_argument("--since", metavar="TS",
                     help="ISO 8601 or a bare date; records with no parseable "
                          "timestamp are excluded when this is given")
    flt.add_argument("--until", metavar="TS")
    flt.add_argument("--limit", type=int, default=20,
                     help="cap on returned records (default 20); the counts are "
                          "over every match, not just the returned ones")
    flt.add_argument("--order", choices=("asc", "desc"), default="asc",
                     help="on the record timestamp, sorted here and never taken "
                          "from input order (default asc)")

    gate = parser.add_argument_group("hooks.py argv")
    gate.add_argument("--challenge", required=True,
                      help="challenge name, as tools/state.py knows it")
    gate.add_argument("--class", dest="bug_class")
    gate.add_argument("--hypothesis-id", dest="hypothesis_id")
    gate.add_argument("--chain-card")
    gate.add_argument("--evidence-kind", choices=fkit.EVIDENCE_KINDS,
                      help="class or impact are the only kinds that can confirm")
    gate.add_argument("--on-match", default="inconclusive", choices=fkit.VERDICTS,
                      help="verdict proposed when at least one record matched "
                           "(default inconclusive)")
    gate.add_argument("--on-miss", default="inconclusive", choices=fkit.VERDICTS)
    gate.add_argument("--answer", metavar="FIELD",
                      help="extract this field from the first match and emit the "
                           "pre-flag argv for it")
    gate.add_argument("--excerpt", type=int, default=400,
                      help="characters of the first matched record kept as evidence")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    path = os.path.abspath(os.path.expanduser(args.input))
    if not os.path.isfile(path):
        parser.error("no such file: %s" % path)
    if args.limit < 0:
        parser.error("--limit cannot be negative")
    if args.excerpt < 0:
        parser.error("--excerpt cannot be negative")
    exact = [split_pair(spec, parser, "--field") for spec in args.field]
    contains = [split_pair(spec, parser, "--field-contains")
                for spec in args.field_contains]
    wanted_ids = {normalise_id(value) for value in args.event_id}
    since = until = None
    if args.since:
        since = parse_time(args.since)
        if since is None:
            parser.error("--since is not an ISO 8601 timestamp: %r" % args.since)
    if args.until:
        until = parse_time(args.until)
        if until is None:
            parser.error("--until is not an ISO 8601 timestamp: %r" % args.until)

    rows, info = load_records(path)
    parser_ok = info["parser_ok"]

    timed, untimed, no_ts = [], [], 0
    all_ids = {}
    for index, row in enumerate(rows):
        record = row["record"]
        row["event_id"] = event_id_of(record)
        stamp, raw = time_of(record)
        row["timestamp"] = iso(stamp)
        row["timestamp_raw"] = raw
        row["_order"] = index
        key = row["event_id"] if row["event_id"] is not None else "unknown"
        all_ids[key] = all_ids.get(key, 0) + 1
        if stamp is None:
            no_ts += 1
            untimed.append((None, index, row))
        else:
            timed.append((stamp, index, row))

    # None, not True, when fewer than two records carry a timestamp: order cannot
    # be judged from one record, and a vacuous "true" would read as a measurement.
    chronological = (all(a[0] <= b[0] for a, b in zip(timed, timed[1:]))
                     if len(timed) > 1 else None)
    timed.sort(key=lambda item: (item[0], item[1]), reverse=args.order == "desc")
    # A record with no parseable timestamp cannot be placed on the timeline, so it
    # always sorts last rather than being silently dated.
    ordered = [row for _, _, row in timed] + [row for _, _, row in untimed]

    matched, rejected = [], {}
    for row in ordered:
        if since or until:
            if row["timestamp"] is None:
                rejected["no-timestamp-with-time-filter"] = \
                    rejected.get("no-timestamp-with-time-filter", 0) + 1
                continue
            stamp = parse_time(row["timestamp"])
            if since and stamp < since:
                rejected["before-since"] = rejected.get("before-since", 0) + 1
                continue
            if until and stamp > until:
                rejected["after-until"] = rejected.get("after-until", 0) + 1
                continue
        keep, misses = matches(row["record"], wanted_ids, exact, contains,
                               row["event_id"])
        if keep:
            matched.append(row)
        else:
            for miss in misses:
                rejected[miss] = rejected.get(miss, 0) + 1

    by_id = {}
    for row in matched:
        key = row["event_id"] if row["event_id"] is not None else "unknown"
        by_id[key] = by_id.get(key, 0) + 1
    stamps = [row["timestamp"] for row in matched if row["timestamp"]]

    returned = matched[: args.limit] if args.limit else []
    first = matched[0] if matched else None
    evidence = fkit.excerpt(first["raw"], args.excerpt) if first else ""

    verdict = args.on_match if matched else args.on_miss
    verdict, forced_kind, downgrades = fkit.downgrade(verdict, bool(matched),
                                                      parser_ok)
    kind = forced_kind or args.evidence_kind or ("class" if matched else "surface")
    downgrades = list(downgrades)
    if not parser_ok:
        # hooks.py records the kind verbatim, and a converter that never ran is
        # evidence about availability, exactly as a dead connection is in
        # tools/web/http_probe.py. It cannot be filed as class or impact.
        if kind != "transport":
            downgrades.append("no parser produced a record: evidence-kind forced "
                              "to transport")
        kind = "transport"
    elif kind in ("class", "impact") and not matched:
        downgrades.append("nothing matched: evidence-kind forced to surface, "
                          "because class or impact would claim a record that is "
                          "not there")
        kind = "surface"
    if verdict == "confirms" and kind not in ("class", "impact"):
        verdict = "inconclusive"
        downgrades = list(downgrades) + [
            "verdict=confirms needs --evidence-kind class or impact"]
    if verdict == "confirms" and not evidence.strip():
        verdict = "inconclusive"
        downgrades = list(downgrades) + ["no verbatim excerpt to quote"]

    if parser_ok:
        result = "%d records read, %d matched, %d returned" % (
            len(rows), len(matched), len(returned))
    else:
        result = "no parser produced a record from %s" % os.path.basename(path)
    request = "evtx_query %s%s%s%s%s" % (
        os.path.basename(path),
        "".join(" --event-id %s" % i for i in sorted(wanted_ids)),
        "".join(" --field %s=%s" % pair for pair in exact),
        "".join(" --field-contains %s=%s" % pair for pair in contains),
        (" --since %s" % args.since if args.since else "")
        + (" --until %s" % args.until if args.until else ""))

    post_argv = fkit.post_probe_argv(
        args.challenge, verdict, evidence, kind, request, result,
        bug_class=args.bug_class, hypothesis_id=args.hypothesis_id,
        chain_card=args.chain_card)

    report = fkit.envelope(
        "evtx-query",
        ok=True,
        input={"path": path, "kind": info["kind"],
               "bytes": os.path.getsize(path)},
        parser_ok=parser_ok,
        parser=info["parser"],
        read_errors=cap_errors(info["read_errors"]),
        read_error_count=len(info["read_errors"]),
        field_shapes_handled=list(FIELD_SHAPES),
        filters={"event_id": sorted(wanted_ids),
                 "field": ["%s=%s" % pair for pair in exact],
                 "field_contains": ["%s=%s" % pair for pair in contains],
                 "since": iso(since), "until": iso(until),
                 "order": args.order, "limit": args.limit},
        records={"read": len(rows), "matched": len(matched),
                 "returned": len(returned), "without_timestamp": no_ts,
                 "rejected_by": rejected},
        input_was_chronological=chronological,
        ordering_note=("timestamps were parsed and sorted here; evtx_dump's "
                       "default multithreaded output is out of order, so input "
                       "order is never trusted"),
        summary={"by_event_id": by_id, "by_event_id_all_records": all_ids,
                 "first_matched_timestamp": min(stamps) if stamps else None,
                 "last_matched_timestamp": max(stamps) if stamps else None},
        matches=[{"event_id": row["event_id"], "timestamp": row["timestamp"],
                  "timestamp_raw": row["timestamp_raw"], "record": row["record"]}
                 for row in returned],
        evidence={"excerpt": evidence,
                  "excerpt_of": first["excerpt_of"] if first else None,
                  "is_verbatim_substring": bool(evidence) and bool(first)
                  and first["verbatim"] and evidence in first["raw"],
                  "kind": kind,
                  "event_id": first["event_id"] if first else None,
                  "timestamp": first["timestamp"] if first else None},
        verdict=verdict,
        verdict_downgrades=list(downgrades),
        post_probe_argv=post_argv,
        post_probe_command=fkit.as_command(post_argv),
        gate="tools/hooks.py post-probe is the only write path for this verdict",
    )

    if args.answer:
        if first is None:
            report["answer"] = {
                "field": args.answer, "found": False,
                "note": "nothing matched, so there is no record to read a field "
                        "from; no flag argv emitted"}
        else:
            value, found = field_value(first["record"], args.answer)
            text = as_text(value)
            if not found or text == "":
                report["answer"] = {
                    "field": args.answer, "found": False,
                    "note": "the first matched record has no such field; the "
                            "shapes tried are in field_shapes_handled. No flag "
                            "argv emitted",
                    "available_top_level": sorted(first["record"].keys())
                    if isinstance(first["record"], dict) else []}
            else:
                flag_argv = fkit.pre_flag_argv(args.challenge, text, evidence)
                report["answer"] = {
                    "field": args.answer, "found": True, "value": text,
                    "from_event_id": first["event_id"],
                    "from_timestamp": first["timestamp"],
                    "pre_flag_argv": flag_argv,
                    "pre_flag_command": fkit.as_command(flag_argv)}

    if not parser_ok:
        report["next_action"] = (
            "install a converter (see parser.install), convert once, then query "
            "the JSONL with this same tool")
    fkit.jprint(report, args.compact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
