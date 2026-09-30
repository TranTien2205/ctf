#!/usr/bin/env python3
"""Offline self-test for tools/forensics/: every primitive against real fixtures.

No network, no challenge instance, no optional dependency. The fixtures beside
this file are real bytes on disk - EVTX and registry magic read off artifacts
produced on this box, a JSONL of Windows event records in the shape converters
actually emit, and five timeline sources spanning three file formats and all
four epoch widths - so a case here fails when a tool's behaviour changes, not
when a mock drifts. The microsecond values in journal_sample.jsonl were read off
this box's own journal; the two rows labelled SYNTHETIC in that file were not.

The case that matters most is the last group: a primitive that ran no parser, or
whose filter matched nothing, must never be able to propose verdict=confirms.
That is the forensics analogue of tools/web/selftest.py case 8, and it is the
property the whole write gate rests on.

    python3 tools/forensics/selftest.py           # JSON verdict, exit 0 on PASS
    python3 tools/forensics/selftest.py --verbose # include each tool's output
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkit  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
EVTX = os.path.join(FIX, "evtx", "sherlock_sample.jsonl")
DAMAGED = os.path.join(FIX, "evtx", "damaged.jsonl")
BUNDLE = os.path.join(FIX, "bundle")
TL = os.path.join(FIX, "timeline")
JOURNAL = os.path.join(TL, "journal_sample.jsonl")
UNPLACEABLE = os.path.join(TL, "epoch_unplaceable.csv")
CASES = []


def run(tool, argv):
    proc = subprocess.run([sys.executable, os.path.join(HERE, tool)] + argv,
                          capture_output=True, text=True, timeout=120)
    try:
        return proc.returncode, json.loads(proc.stdout), proc.stderr
    except ValueError:
        return proc.returncode, None, (proc.stderr or proc.stdout)[:400]


def case(name, tool, argv, check, verbose=False):
    entry = {"name": name, "tool": tool}
    try:
        code, out, err = run(tool, argv)
    except subprocess.TimeoutExpired:
        entry.update(pass_=False, detail="TIMED OUT - a primitive must never hang")
        CASES.append({"name": name, "tool": tool, "pass": False,
                      "detail": "timed out"})
        return
    if out is None:
        CASES.append({"name": name, "tool": tool, "pass": False,
                      "detail": "no JSON on stdout (exit %d): %s" % (code, err)})
        return
    try:
        ok, detail = check(out, code)
    except Exception as exc:                       # a KeyError here IS a failure
        ok, detail = False, "%s: %s" % (type(exc).__name__, exc)
    entry = {"name": name, "tool": tool, "pass": bool(ok), "detail": detail,
             "exit": code}
    if verbose:
        entry["output"] = out
    CASES.append(entry)


def tiers(out, label):
    """The per-source assumption counts of one source, keyed by tier name.

    Read from sources[], not from the merged assumptions[] list: the merged list
    is ordered by first appearance, so indexing it would pin an ordering the tool
    never promised.
    """
    for src in out.get("sources") or []:
        if src["label"] == label:
            return src["assumptions"]
    return {}


def ts_of(out, time_value, timecol="__REALTIME_TIMESTAMP"):
    """The merged UTC timestamp of the row whose time column held this text."""
    for row in out.get("rows") or []:
        if row["fields"].get(timecol) == time_value:
            return row["ts"]
    return None


def no_confirm(out, _code):
    """The invariant: this run must not have proposed a confirmation."""
    argv = out.get("post_probe_argv") or []
    in_argv = "confirms" in argv
    return (out.get("verdict") != "confirms" and not in_argv,
            "verdict=%s argv_has_confirms=%s downgrades=%s"
            % (out.get("verdict"), in_argv,
               "; ".join(out.get("verdict_downgrades") or []) or "none"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--compact", action="store_true")
    args = ap.parse_args()
    v = args.verbose

    missing = [p for p in (EVTX, DAMAGED, BUNDLE, TL, JOURNAL, UNPLACEABLE)
               if not os.path.exists(p)]
    if missing:
        fkit.jprint({"mode": "tools-forensics-selftest", "verdict": "FAIL",
                     "total": 0, "failures": 1,
                     "cases": [{"name": "fixtures present", "pass": False,
                                "detail": "missing: %s" % missing}]}, args.compact)
        return 1

    # ---- artifact_inventory -------------------------------------------------
    case("inventory: classifies the bundle and names one route",
         "artifact_inventory.py", ["--path", BUNDLE, "--challenge", "st"],
         lambda o, c: (o["ok"] and o["scanned"]["files"] > 20
                       and o["route"]["exists"] is True
                       and o["route"]["open_first"].startswith("skills/dfir-sherlock-triage/"),
                       "files=%s route=%s" % (o["scanned"]["files"],
                                              o["route"]["open_first"])), v)

    case("inventory: recognises every major artifact family",
         "artifact_inventory.py", ["--path", BUNDLE, "--challenge", "st"],
         lambda o, c: (all(f in o["families"] for f in
                           ("evtx-security", "evtx-sysmon", "registry-hive",
                            "prefetch", "mft", "capture", "cloudtrail-json")),
                       "families=%s" % sorted(o["families"])), v)

    case("inventory: a url-encoded drive path is NOT a KAPE marker",
         "artifact_inventory.py",
         ["--path", os.path.join(FIX, "urlencoded"), "--challenge", "st"],
         lambda o, c: (o["kape_shape"]["is_kape"] is False
                       and bool(o["kape_shape"].get("rejected_signals")),
                       "is_kape=%s rejected=%s"
                       % (o["kape_shape"]["is_kape"],
                          len(o["kape_shape"].get("rejected_signals") or []))), v)

    case("inventory: a real KAPE zip comment IS a marker",
         "artifact_inventory.py",
         ["--path", os.path.join(FIX, "kape-comment.zip"), "--challenge", "st"],
         lambda o, c: (o["kape_shape"]["is_kape"] is True,
                       "marker=%s" % o["kape_shape"].get("markers")), v)

    # ---- evtx_query ---------------------------------------------------------
    case("evtx: event-id filter finds the Sysmon process create",
         "evtx_query.py", ["--input", EVTX, "--event-id", "1", "--challenge", "st"],
         lambda o, c: (o["parser_ok"] and o["records"]["matched"] == 1,
                       "matched=%s" % o["records"]["matched"]), v)

    case("evtx: ProcessGuid joins Sysmon 1 to Sysmon 3 (the method.md pivot)",
         "evtx_query.py", ["--input", EVTX, "--field-contains",
                           "ProcessGuid=a1b2c3d4", "--challenge", "st"],
         lambda o, c: (o["records"]["matched"] == 2
                       and {m["event_id"] for m in o["matches"]} == {"1", "3"},
                       "matched=%s ids=%s" % (o["records"]["matched"],
                                              sorted(m["event_id"] for m in o["matches"]))), v)

    case("evtx: out-of-order input is sorted, not trusted",
         "evtx_query.py", ["--input", EVTX, "--order", "asc", "--challenge", "st"],
         lambda o, c: (o["input_was_chronological"] is False
                       and [m["timestamp"] for m in o["matches"]]
                       == sorted(m["timestamp"] for m in o["matches"]),
                       "input_chronological=%s first=%s"
                       % (o["input_was_chronological"],
                          o["matches"][0]["timestamp"] if o["matches"] else None)), v)

    case("evtx: --answer extracts one field and emits a pre-flag argv",
         "evtx_query.py", ["--input", EVTX, "--event-id", "1",
                           "--challenge", "st", "--answer", "CommandLine"],
         lambda o, c: (o["answer"]["found"] and "-enc SQBFAFgA" in o["answer"]["value"]
                       and o["answer"]["pre_flag_argv"][2] == "pre-flag"
                       and "artifact" in o["answer"]["pre_flag_argv"],
                       "value=%r" % o["answer"]["value"][-24:]), v)

    case("evtx: a missing field yields no flag argv rather than a guess",
         "evtx_query.py", ["--input", EVTX, "--event-id", "1",
                           "--challenge", "st", "--answer", "NoSuchField"],
         lambda o, c: (o["answer"]["found"] is False
                       and "pre_flag_argv" not in o["answer"],
                       "found=%s keys=%s" % (o["answer"]["found"],
                                             sorted(o["answer"]))), v)

    case("evtx: a BOM does not eat the first record, a bad line is recorded",
         "evtx_query.py", ["--input", DAMAGED, "--challenge", "st"],
         lambda o, c: (o["records"]["read"] == 2 and o["read_error_count"] == 1
                       and c == 0,
                       "read=%s errors=%s" % (o["records"]["read"],
                                              o["read_error_count"])), v)

    # ---- timeline_merge -----------------------------------------------------
    tl_sources = ["--source", os.path.join(TL, "auth_events.csv") + ":when:auth",
                  "--source", os.path.join(TL, "proc_events.tsv") + ":epoch:proc",
                  "--source", os.path.join(TL, "edr_alerts.jsonl") + ":alert.time:edr"]

    case("timeline: merges csv+tsv+jsonl across three time formats",
         "timeline_merge.py", tl_sources + ["--challenge", "st"],
         lambda o, c: (o["merged"]["rows_total"] == 8
                       and {s["format"] for s in o["sources"]} == {"csv", "tsv", "jsonl"},
                       "rows=%s formats=%s" % (o["merged"]["rows_total"],
                                               sorted(s["format"] for s in o["sources"]))), v)

    case("timeline: a +02:00 offset is normalised to UTC, not truncated",
         "timeline_merge.py",
         ["--source", os.path.join(TL, "auth_events.csv") + ":when:auth",
          "--challenge", "st"],
         lambda o, c: (any(r["ts"].startswith("2026-09-27T10:59:41")
                           and r["fields"]["when"].startswith("2026-09-27T12:59:41")
                           for r in o["rows"]),
                       "first=%s from=%s" % (o["rows"][0]["ts"],
                                             o["rows"][0]["fields"]["when"])), v)

    case("timeline: an unparseable row is counted and sampled, never dropped",
         "timeline_merge.py",
         ["--source", os.path.join(TL, "auth_events.csv") + ":when:auth",
          "--challenge", "st"],
         lambda o, c: (o["unparsed"]["total"] == 1
                       and o["unparsed"]["samples"][0]["time_value"] == "not-a-timestamp",
                       "unparsed=%s" % o["unparsed"]["total"]), v)

    case("timeline: --gap locates the largest hole in the merged timeline",
         "timeline_merge.py", tl_sources + ["--challenge", "st", "--gap", "120"],
         lambda o, c: (bool(o["gaps"]["found"])
                       and o["gaps"]["found"][0]["seconds"] >= 120,
                       "largest=%ss" % o["gaps"]["found"][0]["seconds"]), v)

    # journald is the one log source guaranteed to exist on a systemd host, and
    # __REALTIME_TIMESTAMP is microseconds. With two tiers the whole file was
    # unparsed: measured on this box, 20 of 20 records, parsed 0.
    case("timeline: a journald microsecond epoch parses, none left unparsed",
         "timeline_merge.py",
         ["--source", JOURNAL + ":__REALTIME_TIMESTAMP:journal",
          "--challenge", "st"],
         lambda o, c: (o["unparsed"]["total"] == 0
                       and o["merged"]["rows_total"] == 6
                       and tiers(o, "journal").get("epoch_microseconds") == 4
                       and ts_of(o, "1790688901511836")
                       == "2026-09-29T13:35:01.511836+00:00",
                       "unparsed=%s tiers=%s us_row=%s"
                       % (o["unparsed"]["total"], tiers(o, "journal"),
                          ts_of(o, "1790688901511836"))), v)

    case("timeline: a nanosecond epoch lands on the same instant as the "
         "microsecond one",
         "timeline_merge.py",
         ["--source", JOURNAL + ":__REALTIME_TIMESTAMP:journal",
          "--challenge", "st"],
         lambda o, c: (tiers(o, "journal").get("epoch_nanoseconds") == 1
                       and ts_of(o, "1790688901511836000")
                       == ts_of(o, "1790688901511836"),
                       "ns=%s us=%s" % (ts_of(o, "1790688901511836000"),
                                        ts_of(o, "1790688901511836"))), v)

    # The regression pin. Two tiers were added underneath the old two, so the
    # question this asks is whether seconds and milliseconds still read exactly
    # as they did: same tier name, same resolved timestamp.
    case("timeline: seconds and milliseconds still read as they did before the "
         "microsecond and nanosecond tiers existed",
         "timeline_merge.py",
         ["--source", os.path.join(TL, "proc_events.tsv") + ":epoch:proc",
          "--source", JOURNAL + ":__REALTIME_TIMESTAMP:journal",
          "--challenge", "st"],
         lambda o, c: (tiers(o, "proc") == {"epoch_seconds": 2}
                       and tiers(o, "journal").get("epoch_milliseconds") == 1
                       and ts_of(o, "1790507038", "epoch")
                       == "2026-09-27T11:03:58+00:00"
                       and ts_of(o, "1790688901511")
                       == "2026-09-29T13:35:01.511000+00:00",
                       "proc=%s ms_row=%s s_row=%s"
                       % (tiers(o, "proc"), ts_of(o, "1790688901511"),
                          ts_of(o, "1790507038", "epoch"))), v)

    # The four tiers widen what a bare number may mean, so the 1970..2200 window
    # is the only thing left refusing one. If this case ever passes by parsing
    # all three rows, a wrong tier is succeeding silently.
    case("timeline: a number no tier can place inside 1970..2200 is still "
         "refused, one beside it still parses",
         "timeline_merge.py",
         ["--source", UNPLACEABLE + ":epoch:bad", "--challenge", "st"],
         lambda o, c: (o["merged"]["rows_total"] == 1
                       and o["unparsed"]["total"] == 2
                       and all("outside 1970..2200" in smp["reason"]
                               for smp in o["unparsed"]["samples"]),
                       "parsed=%s unparsed=%s reasons=%s"
                       % (o["merged"]["rows_total"], o["unparsed"]["total"],
                          [smp["time_value"] for smp in o["unparsed"]["samples"]])), v)

    # ---- the invariant the write gate rests on ------------------------------
    case("GATE: inventory refuses to confirm (it ran no parser)",
         "artifact_inventory.py",
         ["--path", BUNDLE, "--challenge", "st", "--verdict", "confirms"],
         no_confirm, v)

    case("GATE: evtx refuses to confirm when the filter matched nothing",
         "evtx_query.py",
         ["--input", EVTX, "--event-id", "99999", "--challenge", "st",
          "--on-match", "confirms", "--on-miss", "confirms",
          "--evidence-kind", "impact"],
         no_confirm, v)

    case("GATE: evtx refuses to confirm when no parser is available",
         "evtx_query.py",
         ["--input", os.path.join(FIX, "evtx-only", "Security.evtx"),
          "--challenge", "st", "--on-match", "confirms",
          "--on-miss", "confirms", "--evidence-kind", "impact"],
         lambda o, c: (o["verdict"] != "confirms"
                       and "confirms" not in (o.get("post_probe_argv") or [])
                       and o.get("parser_ok") is False and c == 0,
                       "parser_ok=%s verdict=%s exit=%s"
                       % (o.get("parser_ok"), o.get("verdict"), c)), v)

    case("GATE: timeline refuses to confirm on a needle that matched nothing",
         "timeline_merge.py", tl_sources + ["--challenge", "st", "--contains",
                                            "no-such-string-anywhere",
                                            "--on-match", "confirms",
                                            "--evidence-kind", "impact"],
         no_confirm, v)

    failures = [c for c in CASES if not c["pass"]]
    report = {"mode": "tools-forensics-selftest", "fixtures": FIX,
              "total": len(CASES), "failures": len(failures),
              "verdict": "PASS" if not failures else "FAIL", "cases": CASES}
    fkit.jprint(report, args.compact)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
