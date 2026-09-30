#!/usr/bin/env python3
"""Compare host snapshots and say which changes a person made.

`tools/ad/host_snapshot.sh` takes the baseline during the first thirty minutes.
This answers the question no installed tool on this box answers -- there is no
`debsums`, no `aide`, no host IDS -- namely "did anything change since then".

    python3 tools/ad/host_diff.py --before t0.json --after web1.json --after web2.json

The one inference worth the code, and it needs SEVERAL after-snapshots rather than
one: a change that appears on EVERY host is the starting image, a package upgrade,
or your own automation. A change on ONE host out of eight is a person. Nobody
does that comparison reliably by eye at minute two hundred, which is the whole
reason this is a tool and not a checklist.

So `--after` is repeatable, and every finding carries `on_all_hosts`. A finding
with `on_all_hosts: true` is ranked last on purpose: it is almost never the
intrusion, and ranking it first is how the real one gets buried.

Ordering, and the reason for it: a new way to execute code outranks a new way to
authenticate, which outranks a new listener, which outranks everything else --
because the first two are how an attacker returns after you evict them, and the
third is only how they arrived.

Output is JSON on stdout. Exit 0 always: a difference is a finding to read, not a
failure. `--fail-on-single-host` exits 1 when a change appeared on one host only,
for an operator who wants this in a loop.
"""
import argparse
import json
import os
import sys

# Highest first. A surface absent from this list is still compared, and lands after
# everything named here, because an unranked change is not an ignored one.
SURFACE_RANK = (
    ("enabled_units", "a new service starts itself after every reboot"),
    ("timers", "a new timer runs code on a schedule"),
    ("cron_files", "a new cron entry runs code on a schedule"),
    ("root_crontab", "root's own crontab changed"),
    ("ld_preload", "a loader hook runs inside every process that starts"),
    ("authorized_keys", "a new key authenticates without a password"),
    ("shell_accounts", "a new account can log in"),
    ("empty_passwords", "an account authenticates with no password at all"),
    ("sudoers", "a new sudo rule grants privilege"),
    ("setid_binaries", "a new set-id binary runs as another user"),
    ("listeners", "a new listening socket accepts connections"),
    ("package_integrity", "a packaged file no longer matches its package"),
    ("local_mounts", "a new filesystem is mounted"),
)
RANKED = {name: index for index, (name, _why) in enumerate(SURFACE_RANK)}
WHY = dict(SURFACE_RANK)


def surface_lines(snapshot, key):
    """The lines of one surface, or None when it was not collected.

    None and [] are different answers and must stay different: [] means "looked,
    found nothing", None means "did not look, or the collector timed out". Treating
    a timeout as an empty set invents a disappearance on every diff.
    """
    block = (snapshot or {}).get(key)
    if not isinstance(block, dict):
        return None
    if block.get("status") != "ok":
        return None
    lines = block.get("lines")
    return list(lines) if isinstance(lines, list) else None


def diff_snapshots(before, afters):
    """Pure. before: one dict. afters: [(label, dict), ...]. Returns the report dict."""
    labels = [label for label, _snap in afters]
    surfaces = set()
    for snap in [before] + [s for _l, s in afters]:
        surfaces.update(k for k, v in (snap or {}).items() if isinstance(v, dict))

    findings, not_compared = [], []
    for key in sorted(surfaces):
        base = surface_lines(before, key)
        if base is None:
            not_compared.append({"surface": key, "why": "not collected in the baseline, "
                                                        "or its collector timed out"})
            continue
        base_set = set(base)
        added, removed = {}, {}
        for label, snap in afters:
            now = surface_lines(snap, key)
            if now is None:
                not_compared.append({"surface": key, "host": label,
                                     "why": "not collected here, or the collector timed out"})
                continue
            now_set = set(now)
            for line in sorted(now_set - base_set):
                added.setdefault(line, []).append(label)
            for line in sorted(base_set - now_set):
                removed.setdefault(line, []).append(label)

        compared = [label for label, snap in afters if surface_lines(snap, key) is not None]
        for kind, table in (("added", added), ("removed", removed)):
            for line, hosts in table.items():
                everywhere = bool(compared) and len(hosts) == len(compared)
                findings.append({
                    "surface": key,
                    "change": kind,
                    "line": line,
                    "hosts": hosts,
                    "on_all_hosts": everywhere,
                    "reading": ("the image, a package upgrade, or your own automation: "
                                "it is on every host compared"
                                if everywhere else
                                "%d of %d hosts compared: a change on a subset is a "
                                "person, not the image" % (len(hosts), len(compared))),
                    "why_it_matters": WHY.get(key, "an unranked surface changed"),
                })

    # a new way to execute outranks a new way to authenticate outranks a listener;
    # and anything present on every host sinks to the bottom whatever its surface
    findings.sort(key=lambda f: (f["on_all_hosts"],
                                 RANKED.get(f["surface"], len(SURFACE_RANK)),
                                 f["change"] != "added",
                                 f["line"]))
    single = [f for f in findings if not f["on_all_hosts"]]
    return {
        "mode": "ad-host-diff",
        "baseline_host": (before or {}).get("host"),
        "baseline_taken_utc": (before or {}).get("taken_utc"),
        "hosts_compared": labels,
        "findings": len(findings),
        "on_one_host_only": len(single),
        "read_this_first": (single[0] if single else
                            (findings[0] if findings else None)),
        "surfaces_not_compared": not_compared,
        "results": findings,
    }


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before", required=True, help="the baseline snapshot")
    parser.add_argument("--after", action="append", required=True,
                        help="a later snapshot; repeatable, and several is the point")
    parser.add_argument("--fail-on-single-host", action="store_true",
                        help="exit 1 when a change appeared on one host only")
    args = parser.parse_args()

    try:
        before = load(args.before)
    except (OSError, ValueError) as exc:
        print(json.dumps({"error": "the baseline is unreadable", "path": args.before,
                          "detail": "%s: %s" % (type(exc).__name__, exc)}))
        return 2

    afters, unreadable = [], []
    for path in args.after:
        try:
            afters.append((os.path.basename(path), load(path)))
        except (OSError, ValueError) as exc:
            unreadable.append({"path": path, "detail": str(exc)})
    if not afters:
        print(json.dumps({"error": "no later snapshot could be read",
                          "unreadable": unreadable}))
        return 2

    report = diff_snapshots(before, afters)
    if unreadable:
        report["unreadable"] = unreadable
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if args.fail_on_single_host and report["on_one_host_only"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
