#!/usr/bin/env python3
"""Triage a capture: who talked to whom, how much left, and is it periodic.

The exfiltration question is a QUANTITY before it is a name -- which peer received
the most bytes outbound -- and that is the one thing a hand-written tshark run
usually gets wrong, because `-z conv,ip` prints two directional column pairs and
they are easy to read backwards. This parses that table rather than eyeballing it,
and labels each direction explicitly.

Four traps this exists to remove:

1. NAME RESOLUTION. `tshark` without `-n` issues live DNS lookups for every
   address in someone else's incident. That leaks the investigation and fills the
   output with hostnames the capture never contained. `-n` is passed on every
   invocation here and is not optional.
2. DIRECTION. In `conv,ip` the two middle column pairs are `<-` then `->`,
   relative to the FIRST named host. Reported as one "bytes" number, an inbound
   download reads as an outbound upload. Every row here carries
   a_to_b and b_to_a separately, plus which side sent more.
3. "NOT PRESENT" versus "NOT DISSECTED". A protocol on a non-standard port is not
   dissected as that protocol, so a display filter returns nothing while the
   traffic is plainly there. The protocol hierarchy is always collected, so an
   empty filter result can be separated from an absent protocol.
4. A BEACON IS A VARIANCE, NOT A GAP. One regular-looking interval proves nothing.
   Periodicity is reported as median AND population stdev over the inter-arrival
   times, with the sample count, so "low stdev relative to the median" is a number
   the reader can check rather than an impression.

The capture is never modified and nothing in it is executed. An object carved out
of a capture may be live malware: this tool reports what tshark says was
transferred and does not export it.

tshark presence is checked at run time; when it is absent the result is
`parser_ok: false` with the install command, and fkit.downgrade() makes a
confirmation impossible -- a missing parser is evidence about this box, never
about the capture.

    python3 tools/forensics/pcap_triage.py --input <capture> --challenge <sherlock>-q1
    python3 tools/forensics/pcap_triage.py --input <capture> --challenge x --beacon-peer 203.0.113.9
    python3 tools/forensics/pcap_triage.py --input <capture> --challenge x --names
"""
import argparse
import os
import re
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkit  # noqa: E402

TSHARK = "tshark"
CAPINFOS = "capinfos"
INSTALL = "sudo apt install tshark"
# tshark writes cfilters parse warnings to stderr on this box; they are noise and
# must not be mistaken for a failure, so stderr is kept but never parsed for truth.
# Byte counts are printed with THOUSANDS SEPARATORS once they pass 999 --
# `4 5,016 bytes` -- so a \d+ group silently fails on exactly the big
# conversations an exfiltration question is about. Measured on this box while
# writing this tool: the largest of three rows was the one that did not parse,
# and the output looked complete. Hence [\d,]+ plus _num() below, and hence
# `conversation_rows_unparsed` is reported rather than swallowed.
CONV_ROW = re.compile(
    r"^(?P<a>[0-9a-fA-F.:]+)(?::(?P<ap>\d+))?\s+<->\s+"
    r"(?P<b>[0-9a-fA-F.:]+)(?::(?P<bp>\d+))?\s+"
    r"(?P<fba>[\d,]+)\s+(?P<bba>[\d,]+)\s+(?:bytes\s+)?"
    r"(?P<fab>[\d,]+)\s+(?P<bab>[\d,]+)\s+(?:bytes\s+)?"
    r"(?P<ft>[\d,]+)\s+(?P<bt>[\d,]+)\s+(?:bytes\s+)?"
    r"(?P<start>[\d.]+)\s+(?P<dur>[\d.]+)")


def _num(text):
    """An integer tshark may have printed with thousands separators."""
    return int(str(text).replace(",", "").replace(" ", ""))


def have(binary):
    return shutil.which(binary) is not None


def run(argv, timeout=180):
    """(ok, stdout, stderr). A non-zero exit is data, not an exception."""
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, "", "%s: %s" % (type(exc).__name__, exc)
    return proc.returncode == 0, proc.stdout, proc.stderr


def capinfos(path):
    if not have(CAPINFOS):
        return {"available": False}
    ok, out, _err = run([CAPINFOS, path])
    if not ok:
        return {"available": True, "ok": False}
    want = {"Number of packets": "packets", "First packet time": "first_packet",
            "Last packet time": "last_packet", "File size": "file_size",
            "Capture duration": "duration"}
    info = {"available": True, "ok": True}
    for line in out.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        label = want.get(key.strip())
        if label:
            info[label] = val.strip()
    return info


def conversations(path):
    """Parsed `-z conv,ip` rows, each with both directions named separately."""
    ok, out, err = run([TSHARK, "-r", path, "-n", "-q", "-z", "conv,ip"])
    rows, unparsed = [], 0
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith(("=", "IPv", "Filter", "|")) or "<->" not in line:
            continue
        m = CONV_ROW.match(line)
        if not m:
            unparsed += 1
            continue
        g = m.groupdict()
        a_to_b, b_to_a = _num(g["bab"]), _num(g["bba"])
        smaller = min(a_to_b, b_to_a)
        rows.append({
            "peer_a": g["a"], "peer_b": g["b"],
            "frames_a_to_b": _num(g["fab"]), "bytes_a_to_b": a_to_b,
            "frames_b_to_a": _num(g["fba"]), "bytes_b_to_a": b_to_a,
            "bytes_total": _num(g["bt"]),
            "rel_start": float(g["start"]), "duration": float(g["dur"]),
            "larger_direction": ("a_to_b" if a_to_b > b_to_a
                                 else ("b_to_a" if b_to_a > a_to_b else "equal")),
            # null rather than a number divided by one: a one-sided conversation
            # has no ratio, and printing 564.0 for 564/0 invents a measurement
            "ratio_larger_to_smaller": (round(max(a_to_b, b_to_a) / smaller, 2)
                                        if smaller else None),
            "one_sided": not smaller,
            "row": line,
        })
    rows.sort(key=lambda r: -max(r["bytes_a_to_b"], r["bytes_b_to_a"]))
    return rows, unparsed, ok, err


def hierarchy(path):
    ok, out, _err = run([TSHARK, "-r", path, "-n", "-q", "-z", "io,phs"])
    protos, lines = {}, []
    for line in out.splitlines():
        m = re.match(r"^(\s*)(\S+)\s+frames:(\d+)\s+bytes:(\d+)", line)
        if not m:
            continue
        lines.append(line.rstrip())
        protos[m.group(2)] = {"frames": int(m.group(3)), "bytes": int(m.group(4)),
                              "depth": len(m.group(1)) // 2}
    return protos, lines, ok


def field_rows(path, display_filter, fields, limit=200):
    """(rows, ok, reason). An invalid field name must never look like no data.

    Measured on this box: `-e frame.time_utc` is not a valid field in this tshark
    build, and tshark then exits 1 having printed NOTHING. A caller that only
    looked at the row list reported "no DNS names" for a capture whose DNS query
    tshark dissects perfectly. So the exit status and the reason are returned, and
    every caller records them.
    """
    argv = [TSHARK, "-r", path, "-n"]
    if display_filter:
        argv += ["-Y", display_filter]
    argv += ["-T", "fields"]
    for f in fields:
        argv += ["-e", f]
    ok, out, err = run(argv)
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        rows.append(dict(zip(fields, line.split("\t"))))
        if len(rows) >= limit:
            break
    reason = None
    if not ok:
        bad = re.search(r"Some fields aren't valid:\s*(.+)", err, re.S)
        reason = ("tshark rejected the field list: %s"
                  % " ".join(bad.group(1).split())[:160]) if bad else (
                      "tshark exited non-zero: %s" % " ".join(err.split())[:160])
    return rows, ok, reason


# frame.time_utc does NOT exist in this tshark build, and frame.time renders LOCAL
# time (EDT was observed here), which is the timezone trap this whole category
# warns about. frame.time_epoch is verified present and unambiguous, so it is what
# is requested and the UTC rendering is done here.
TIME_FIELD = "frame.time_epoch"


def as_utc(epoch_text):
    try:
        secs = float(epoch_text)
    except (TypeError, ValueError):
        return None
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(secs))


def with_utc(rows):
    """Add a UTC string beside the epoch every row already carries."""
    for row in rows:
        row["time_utc"] = as_utc(row.get(TIME_FIELD))
    return rows


def beacon(path, peer, limit=5000):
    """Inter-arrival statistics toward one peer. A variance, not a gap."""
    rows, ok, why = field_rows(path, "ip.dst==%s" % peer, [TIME_FIELD], limit)
    times = []
    for r in rows:
        try:
            times.append(float(r[TIME_FIELD]))
        except (TypeError, ValueError):
            continue
    times.sort()
    gaps = [round(b - a, 4) for a, b in zip(times, times[1:])]
    out = {"peer": peer, "parser_ok": ok, "field_error": why,
           "samples": len(times),
           "intervals": len(gaps), "first_gaps": gaps[:20]}
    if len(gaps) >= 3:
        med = statistics.median(gaps)
        sd = statistics.pstdev(gaps)
        out.update(median_gap_seconds=round(med, 4),
                   stdev_seconds=round(sd, 4),
                   stdev_over_median=round(sd / med, 4) if med else None,
                   reading="a LOW stdev relative to the median is the beacon "
                           "signal; this tool reports the numbers and does not "
                           "decide a threshold")
    else:
        out["reading"] = ("fewer than 3 intervals: periodicity is not measurable, "
                          "which is not the same as not periodic")
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="Every tshark invocation passes -n: no name is ever resolved, so a "
               "hostname in this output came from the capture itself.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, metavar="PATH", help="the capture")
    ap.add_argument("--top", type=int, default=10,
                    help="conversations reported (default 10)")
    ap.add_argument("--names", action="store_true",
                    help="also collect DNS query names, HTTP hosts and TLS SNI")
    ap.add_argument("--beacon-peer", metavar="ADDR",
                    help="inter-arrival median and stdev toward this address")
    ap.add_argument("--display-filter", metavar="EXPR",
                    help="an extra -Y expression, reported with its row count")

    h = ap.add_argument_group("hooks.py argv")
    h.add_argument("--challenge", required=True)
    h.add_argument("--class", dest="bug_class", metavar="BUG_CLASS")
    h.add_argument("--hypothesis-id")
    h.add_argument("--chain-card")
    h.add_argument("--evidence-kind", choices=fkit.EVIDENCE_KINDS, default="class")
    h.add_argument("--contains", metavar="SUBSTRING",
                   help="the only thing this may confirm on: a collected row "
                        "holding this literal")
    h.add_argument("--on-match", choices=fkit.VERDICTS, default="inconclusive")
    h.add_argument("--on-miss", choices=fkit.VERDICTS, default="inconclusive")
    h.add_argument("--excerpt", type=int, default=400)
    ap.add_argument("--compact", action="store_true")
    a = ap.parse_args()

    if not have(TSHARK):
        out = fkit.envelope(
            "pcap-triage", ok=True, challenge=a.challenge, parser_ok=False,
            parser="tshark", install_needed=INSTALL,
            note="a missing parser is evidence about this box, never about the "
                 "capture, so no verdict here can be a confirmation")
        verdict, kind, reasons = fkit.downgrade(a.on_miss, False, False)
        out.update(verdict=verdict, evidence_kind=kind or "transport",
                   evidence="", verdict_downgrades=reasons)
        argv = fkit.post_probe_argv(a.challenge, verdict, "", kind or "transport",
                                    "pcap_triage.py --input %s" % a.input,
                                    "tshark absent", a.bug_class, a.hypothesis_id,
                                    a.chain_card)
        out["post_probe_argv"] = argv
        out["post_probe_command"] = fkit.as_command(argv)
        fkit.jprint(out, a.compact)
        return 0

    if not os.path.isfile(a.input):
        out = fkit.envelope("pcap-triage", ok=True, challenge=a.challenge,
                            parser_ok=False, parser="tshark",
                            error="not a file: %s" % a.input)
        verdict, kind, reasons = fkit.downgrade(a.on_miss, False, False)
        out.update(verdict=verdict, evidence_kind=kind or "transport",
                   evidence="", verdict_downgrades=reasons)
        argv = fkit.post_probe_argv(a.challenge, verdict, "", kind or "transport",
                                    "pcap_triage.py --input %s" % a.input,
                                    "capture missing", a.bug_class,
                                    a.hypothesis_id, a.chain_card)
        out["post_probe_argv"] = argv
        out["post_probe_command"] = fkit.as_command(argv)
        fkit.jprint(out, a.compact)
        return 0

    info = capinfos(a.input)
    protos, phs_lines, phs_ok = hierarchy(a.input)
    convs, unparsed, conv_ok, conv_err = conversations(a.input)
    parsed_any = bool(convs or protos)

    collected = []           # every row that --contains may match against
    for c in convs:
        collected.append(c["row"])
    collected += phs_lines

    names = {}
    if a.names:
        # `dns` rather than `dns.flags.response==0`: measured on this box, the
        # response-flag filter returned nothing on a capture whose DNS query
        # tshark dissected perfectly, so it would have reported "no DNS names" on
        # a capture full of them. Plain `dns` matches queries AND responses, which
        # is harmless here because empty names are dropped and the set is deduped.
        dns, dns_ok, dns_why = field_rows(
            a.input, "dns", [TIME_FIELD, "ip.src", "dns.qry.name"])
        dns = with_utc([r for r in dns if r.get("dns.qry.name")])
        http, http_ok, http_why = field_rows(
            a.input, "http.request", [TIME_FIELD, "http.host", "http.request.uri"])
        http = with_utc(http)
        sni, sni_ok, sni_why = field_rows(
            a.input, "tls.handshake.extensions_server_name",
            [TIME_FIELD, "tls.handshake.extensions_server_name"])
        sni = with_utc(sni)
        names = {
            "dns_queries": dns[:60],
            "http_requests": http[:60],
            "tls_sni": sni[:60],
            "distinct_dns_names": sorted({r.get("dns.qry.name") for r in dns
                                          if r.get("dns.qry.name")})[:60],
            "note": "-n was passed, so every name here was carried in the capture. "
                    "dns rows include responses as well as queries",
            "field_queries_ok": {"dns": dns_ok, "http": http_ok, "tls": sni_ok},
            "field_errors": [w for w in (dns_why, http_why, sni_why) if w],
        }
        for group in ("dns_queries", "http_requests", "tls_sni"):
            collected += ["\t".join(str(v) for v in row.values())
                          for row in names[group]]

    extra = None
    if a.display_filter:
        rows, ok, why = field_rows(a.input, a.display_filter,
                                   [TIME_FIELD, "ip.src", "ip.dst"])
        rows = with_utc(rows)
        extra = {"filter": a.display_filter, "rows": len(rows),
                 "parser_ok": ok, "field_error": why, "samples": rows[:10],
                 "empty_means": "an empty result may be 'not present' OR 'not "
                                "dissected as that protocol on this port' -- "
                                "compare against protocol_hierarchy before "
                                "concluding absence"}
        collected += ["\t".join(str(v) for v in r.values()) for r in rows[:200]]

    matched_row = None
    if a.contains:
        for row in collected:
            if a.contains.lower() in row.lower():
                matched_row = row
                break

    matched = bool(matched_row) if a.contains else bool(convs)
    evidence = fkit.excerpt(matched_row if a.contains else
                            (convs[0]["row"] if convs else ""), a.excerpt)
    verdict, forced_kind, reasons = fkit.downgrade(
        a.on_match if matched else a.on_miss, matched, parsed_any)
    kind = forced_kind or a.evidence_kind

    request = "pcap_triage.py --input %s%s%s" % (
        a.input,
        " --contains %s" % a.contains if a.contains else "",
        " --beacon-peer %s" % a.beacon_peer if a.beacon_peer else "")
    result = "%d conversation(s), %d protocol(s)%s" % (
        len(convs), len(protos),
        "; --contains %s" % ("matched" if matched_row else "did not match")
        if a.contains else "")

    out = fkit.envelope(
        "pcap-triage", ok=True, challenge=a.challenge,
        parser="tshark (-n on every invocation: no name is resolved)",
        parser_ok=parsed_any,
        capture=info,
        protocol_hierarchy=protos,
        protocol_hierarchy_lines=phs_lines[:40],
        conversations=convs[:a.top],
        conversations_total=len(convs),
        conversation_rows_unparsed=unparsed,
        direction_note="bytes_a_to_b and bytes_b_to_a are reported separately "
                       "because tshark's conv table prints <- before ->, and one "
                       "collapsed 'bytes' number turns a download into an upload",
        proved_negative=(a.contains is not None and not matched_row and parsed_any),
        verdict=verdict, evidence_kind=kind, evidence=evidence,
        verdict_downgrades=reasons,
        tshark_stderr_ignored=bool(conv_err.strip()),
    )
    if names:
        out["names"] = names
    if extra:
        out["display_filter"] = extra
    if a.beacon_peer:
        out["beacon"] = beacon(a.input, a.beacon_peer)
    argv = fkit.post_probe_argv(a.challenge, verdict, evidence, kind, request,
                                result, a.bug_class, a.hypothesis_id, a.chain_card)
    out["post_probe_argv"] = argv
    out["post_probe_command"] = fkit.as_command(argv)
    fkit.jprint(out, a.compact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
