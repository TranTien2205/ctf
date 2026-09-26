#!/usr/bin/env python3
"""Recall a dependency gadget this toolkit has already measured.

Hard CTF chains are usually version-dependent, and classify.py has no notion of a
version at all -- it SKIPs node_modules and never reads a lockfile. This closes
that gap: point it at a handout's lockfile and it answers the one question that
makes a long chain tractable, "have we measured this exact dependency before?"

    python3 tools/gadget_lookup.py --list
    python3 tools/gadget_lookup.py --package jsreport
    python3 tools/gadget_lookup.py --lockfile CSCV2026/diemthi/package-lock.json

Output is JSON on stdout, like every other tool here. A hit is a LEAD with a
stated precondition, never a finding: run the precondition check before believing
it, exactly as a chain card's first_confirming_probe must be run.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(ROOT, "knowledge", "gadgets")


def load():
    out = {}
    if not os.path.isdir(STORE):
        return out
    for name in sorted(os.listdir(STORE)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(STORE, name), encoding="utf-8") as fh:
            doc = json.load(fh)
        out[doc.get("package", name[:-5])] = doc
    return out


def aliases(pkg):
    """A store key may cover several spellings: '@scope/name', 'keras / tensorflow'."""
    parts = re.split(r"[\s/,]+", pkg.lower())
    names = {pkg.lower()}
    names.update(p for p in parts if len(p) > 2)
    names.add(pkg.lower().lstrip("@").replace("/", "-"))
    return names


def deps_from_lockfile(path):
    """Return {name: version} from a package-lock, package.json or requirements.txt."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    base = os.path.basename(path)
    found = {}
    if base.endswith(".json"):
        doc = json.loads(text)
        for key in ("packages", "dependencies"):
            for name, meta in (doc.get(key) or {}).items():
                clean = name.split("node_modules/")[-1] or name
                if not clean:
                    continue
                ver = meta.get("version") if isinstance(meta, dict) else meta
                found.setdefault(clean, ver)
        for key in ("dependencies", "devDependencies"):
            for name, ver in (doc.get(key) or {}).items():
                found.setdefault(name, ver)
    else:
        for line in text.splitlines():
            line = line.split("#")[0].strip()
            m = re.match(r"^([A-Za-z0-9._-]+)\s*(?:[=<>~!]=*\s*([0-9][^\s;]*))?", line)
            if m and m.group(1):
                found.setdefault(m.group(1), m.group(2))
    return found


def match(store, deps):
    hits = []
    for pkg, doc in store.items():
        names = aliases(pkg)
        for dep, ver in deps.items():
            if dep.lower() in names or dep.lower().lstrip("@").replace("/", "-") in names:
                hits.append({"package": pkg, "installed_as": dep, "version": ver,
                             "gadgets": doc["gadgets"]})
                break
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="every package in the store")
    ap.add_argument("--package", help="one package by name")
    ap.add_argument("--lockfile", help="package-lock.json, package.json or requirements.txt")
    ap.add_argument("--json", action="store_true", help="compact JSON on one line")
    args = ap.parse_args()

    store = load()
    if not (args.list or args.package or args.lockfile):
        ap.error("give --list, --package or --lockfile")

    payload = {"mode": "gadget-lookup", "store": STORE, "packages_known": len(store),
               "gadgets_known": sum(len(d["gadgets"]) for d in store.values())}

    if args.list:
        payload["packages"] = [
            {"package": p, "gadgets": [g["sink"][:90] for g in d["gadgets"]]}
            for p, d in sorted(store.items())]
    if args.package:
        want = args.package.lower()
        hit = next((d for p, d in store.items()
                    if want in aliases(p) or want == p.lower()), None)
        payload["query"] = args.package
        payload["found"] = bool(hit)
        if hit:
            payload["result"] = hit
        else:
            payload["known"] = sorted(store)
    if args.lockfile:
        if not os.path.isfile(args.lockfile):
            payload["error"] = "no such file: %s" % args.lockfile
            print(json.dumps(payload, indent=None if args.json else 2))
            return 2
        deps = deps_from_lockfile(args.lockfile)
        hits = match(store, deps)
        payload["lockfile"] = args.lockfile
        payload["dependencies_read"] = len(deps)
        payload["matches"] = hits
        payload["next_action"] = (
            "run each gadget's stated precondition before believing it; a hit is a lead, not a finding"
            if hits else "no measured gadget for anything in this lockfile -- classify first")

    print(json.dumps(payload, indent=None if args.json else 2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
