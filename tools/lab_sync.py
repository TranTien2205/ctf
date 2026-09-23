#!/usr/bin/env python3
"""Bridge the ctf-v2 agent to a CTF practice range on another host.

The range (Amazon Science CTF-Dojo on a Windows host, or any docker-compose CTF
runner) publishes a small JSON file listing the challenges that are up:

    {
      "host": "192.168.1.20",
      "challenges": [
        {"key": "ca-event-web-task", "name": "Task", "category": "web",
         "target": "http://192.168.1.20:32768",
         "source_url": "http://192.168.1.20:8899/source/ca-event-web-task.zip",
         "flag_sha256": "..."}
      ]
    }

This tool only reads that file and prepares local state; it never probes the
target. The agent still runs the normal control loop and verifies any flag
through tools/hooks.py.

    python3 tools/lab_sync.py --targets <url|file> --list
    python3 tools/lab_sync.py --targets <url|file> --challenge <key> [--fetch-source]
    python3 tools/lab_sync.py --targets <url|file> --verify <key> <flag>
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def safe_name(key):
    name = re.sub(r"[^a-z0-9._-]+", "-", key.lower()).strip("-")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,99}", name):
        raise SystemExit(json.dumps({"error": "unsafe challenge key", "key": key}))
    return name


def load_targets(source):
    if re.match(r"^https?://", source):
        with urllib.request.urlopen(source, timeout=15) as handle:
            return json.loads(handle.read().decode("utf-8"))
    with open(source, encoding="utf-8") as handle:
        return json.load(handle)


def find_challenge(payload, key):
    for item in payload.get("challenges", []):
        if item.get("key") == key or safe_name(item.get("key", "")) == key:
            return item
    return None


def cmd_list(payload):
    rows = payload.get("challenges", [])
    if not rows:
        print(json.dumps({"challenges": 0, "note": "no challenge is up on the range"}))
        return 0
    for item in rows:
        print("%-40s %-10s %s" % (item.get("key"), item.get("category"), item.get("target")))
    print(json.dumps({"challenges": len(rows), "host": payload.get("host")}))
    return 0


def cmd_challenge(payload, key, fetch_source):
    item = find_challenge(payload, key)
    if item is None:
        raise SystemExit(json.dumps({"error": "unknown challenge key", "key": key,
                                     "available": [c.get("key") for c in payload.get("challenges", [])]}))
    name = safe_name(item["key"])
    target = item.get("target", "")
    category = item.get("category") or "misc"

    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "state.py"), name,
                    "--category", category, "--target", target], cwd=ROOT, check=False)

    source_dir = os.path.join(ROOT, "challenges", name, "source")
    fetched = None
    if fetch_source and item.get("source_url"):
        os.makedirs(source_dir, exist_ok=True)
        archive = os.path.join(ROOT, "challenges", name, "source.zip")
        with urllib.request.urlopen(item["source_url"], timeout=60) as handle, \
                open(archive, "wb") as out:
            out.write(handle.read())
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(source_dir)
        fetched = os.path.relpath(source_dir, ROOT)

    result = {
        "challenge": name,
        "category": category,
        "target": target,
        "flag_sha256": item.get("flag_sha256"),
        "source_dir": fetched,
        "next_commands": [
            "python3 tools/classify.py --source %s" % fetched if fetched else 'python3 tools/classify.py "<observation>"',
            "python3 tools/skill_select.py --source %s" % fetched if fetched else 'python3 tools/skill_select.py "<observation>"',
            "python3 tools/chain_match.py --source %s" % fetched if fetched else 'python3 tools/chain_match.py "<observation>"',
            "python3 tools/decide.py %s" % name,
        ],
        "rules": [
            "verify any flag through tools/hooks.py pre-flag with live-response or artifact evidence",
            "tear the challenge down on the range host when done",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_verify(payload, key, flag):
    item = find_challenge(payload, key)
    if item is None:
        raise SystemExit(json.dumps({"error": "unknown challenge key", "key": key}))
    expected = (item.get("flag_sha256") or "").lower()
    actual = hashlib.sha256(flag.encode("utf-8")).hexdigest()
    ok = bool(expected) and expected == actual
    print(json.dumps({"challenge": item["key"], "sha256_match": ok,
                      "expected_present": bool(expected),
                      "note": "a hash match is a second check; the flag still needs live-response or artifact evidence"}))
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(description="Bridge to a CTF practice range")
    parser.add_argument("--targets", required=True, help="URL or path of lab_targets.json")
    parser.add_argument("--list", action="store_true", help="list the challenges that are up")
    parser.add_argument("--challenge", help="prepare local state for this challenge key")
    parser.add_argument("--fetch-source", action="store_true", help="download the source archive when preparing")
    parser.add_argument("--verify", nargs=2, metavar=("KEY", "FLAG"),
                        help="compare a candidate flag against the range's sha256")
    args = parser.parse_args()

    payload = load_targets(args.targets)
    if args.list:
        return cmd_list(payload)
    if args.verify:
        return cmd_verify(payload, args.verify[0], args.verify[1])
    if args.challenge:
        return cmd_challenge(payload, args.challenge, args.fetch_source)
    parser.error("choose --list, --challenge or --verify")


if __name__ == "__main__":
    sys.exit(main())
