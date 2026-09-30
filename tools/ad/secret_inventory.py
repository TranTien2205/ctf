#!/usr/bin/env python3
"""Find where each credential lives, and in what order to rotate them.

Every team booted the same image, so every default credential in it is public and
all of them have to rotate. The loss does not come from rotating: it comes from the
ORDER. Rotate a value a running service still reads and the service goes down, and
availability is scored continuously.

So this answers one question before anything changes: which files share a value,
and which value has the most consumers.

    python3 tools/ad/secret_inventory.py --root /etc/myapp --root /srv/app
    python3 tools/ad/secret_inventory.py --root . --json

It groups by VALUE FINGERPRINT, not by file, because the same password in four
files is ONE rotation with four edits -- and missing the fourth is what takes the
service down twenty minutes later. `rotation_order` puts the group with the MOST
consumers LAST: that group is the most likely to break something, and it should be
rotated while there is still time to fix it, not at the end when there is not.

Three hard properties, in order of how much they matter:

  * **It never prints more than four characters of a value.** A tool that prints
    secrets creates a new artifact holding every secret on the box, which is worse
    than the exposure it was run to measure. What it prints is a truncated hash.
  * **No full-filesystem walk.** Roots are explicit, the defaults are checked for
    existence first, and depth, file count and file size are all capped. A walk of
    `/` on a contest box is minutes you do not have.
  * **It never calls `df` or `statvfs`.** Measured on this box: a hung hard NFS
    mount makes `df` block forever (`timeout 3 df` exits 124). Network filesystems
    are pruned by reading `/proc/mounts`.

Read only. It opens files and never writes one.
"""
import argparse
import hashlib
import json
import os
import re
import sys

# Candidate locations, each checked for existence before it is walked. Deliberately
# short: a long default list becomes a full-filesystem walk by accident.
DEFAULT_ROOTS = ("/etc", "/srv", "/opt", "/var/www")
MAX_DEPTH = 4
MAX_FILES = 4000
MAX_BYTES = 262144
SHOWN_CHARS = 4

NETWORK_FSTYPES = ("nfs", "nfs4", "cifs", "smb3", "smbfs", "fuse.sshfs", "afs",
                   "9p", "ceph", "glusterfs")
SKIP_DIRS = frozenset((".git", "node_modules", "__pycache__", "venv", ".venv",
                       "site-packages", "dist-packages", "proc", "sys", "dev"))
SKIP_SUFFIXES = (".pyc", ".so", ".o", ".a", ".zip", ".gz", ".xz", ".bz2", ".png",
                 ".jpg", ".jpeg", ".gif", ".pdf", ".ttf", ".woff", ".woff2", ".ico",
                 ".mo", ".db", ".sqlite", ".sqlite3", ".pcap", ".bin", ".img")

# A name that says "this is a credential", then a value on the same line. The name
# is what makes this precise: a bare high-entropy string matches a minified bundle,
# a hash in a lockfile and a UUID in a comment, and a finding the operator has to
# dismiss forty times is a finding they stop reading.
# `pw` is a real key name in compose files and short configs. The negative
# lookahead keeps it from matching `pwd`, which is a directory and not a secret.
NAME = (r"(?:pass(?:wd|word)?|pw(?!d)|secret|token|api[_-]?key|apikey|auth|credential|"
        r"private[_-]?key|access[_-]?key|client[_-]?secret|db[_-]?pass|"
        r"mysql[_-]?root[_-]?password|postgres[_-]?password|jwt[_-]?secret|"
        r"session[_-]?secret|flag[_-]?token)")
ASSIGN = re.compile(
    NAME + r"""\s*[:=]\s*(?P<q>['"]?)(?P<value>[^\s'"#,;]{6,200})(?P=q)""",
    re.IGNORECASE)
URL_CRED = re.compile(r"[a-z][a-z0-9+.\-]*://[^:/\s]+:(?P<value>[^@/\s]{4,200})@",
                      re.IGNORECASE)
PEM = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")

# Values that are placeholders, not credentials. Reporting these is how the real
# ones get skimmed past.
PLACEHOLDER = frozenset((
    "changeme", "change_me", "password", "passwd", "secret", "your_password",
    "yourpassword", "xxxxxxxx", "placeholder", "example", "none", "null", "true",
    "false", "undefined", "todo", "fixme", "<password>", "redacted",
))


def fingerprint(value):
    """A stable id for a value that does not reveal it."""
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:12]


def shown(value):
    """At most four characters, ever."""
    return value[:SHOWN_CHARS] + ("..." if len(value) > SHOWN_CHARS else "")


def find_secrets(text, path="<text>"):
    """Pure. Returns [{path, line, kind, name, fingerprint, shown, length}, ...]."""
    out = []
    for number, line in enumerate(text.split("\n"), 1):
        if len(line) > 4000:
            continue          # a minified bundle is not a configuration file
        if PEM.search(line):
            out.append({"path": path, "line": number, "kind": "private-key-header",
                        "name": "PRIVATE KEY", "fingerprint": fingerprint(path),
                        "shown": "-----BEGIN", "length": None})
            continue
        for match in ASSIGN.finditer(line):
            value = match.group("value")
            if value.lower() in PLACEHOLDER or value.startswith(("$", "{", "%")):
                continue      # a placeholder, or a reference to a value elsewhere
            name = match.group(0).split("=")[0].split(":")[0].strip()
            out.append({"path": path, "line": number, "kind": "assignment",
                        "name": name[:60], "fingerprint": fingerprint(value),
                        "shown": shown(value), "length": len(value)})
        for match in URL_CRED.finditer(line):
            value = match.group("value")
            if value.lower() in PLACEHOLDER:
                continue
            out.append({"path": path, "line": number, "kind": "url-credential",
                        "name": "in a connection string",
                        "fingerprint": fingerprint(value),
                        "shown": shown(value), "length": len(value)})
    return out


def group(findings):
    """Pure. One entry per distinct value, ordered by how many places share it."""
    groups = {}
    for item in findings:
        entry = groups.setdefault(item["fingerprint"], {
            "fingerprint": item["fingerprint"], "shown": item["shown"],
            "length": item["length"], "kinds": set(), "places": []})
        entry["kinds"].add(item["kind"])
        entry["places"].append({"path": item["path"], "line": item["line"],
                                "name": item["name"]})
    out = []
    for entry in groups.values():
        entry["kinds"] = sorted(entry["kinds"])
        entry["consumers"] = len(entry["places"])
        entry["places"].sort(key=lambda p: (p["path"], p["line"]))
        out.append(entry)
    out.sort(key=lambda e: (-e["consumers"], e["fingerprint"]))
    return out


def rotation_order(groups):
    """Fewest consumers first. The widely-shared value is rotated while there is
    still time to fix what it breaks, not last when there is not."""
    ordered = sorted(groups, key=lambda e: (e["consumers"], e["fingerprint"]))
    return [{"fingerprint": e["fingerprint"], "consumers": e["consumers"],
             "paths": sorted({p["path"] for p in e["places"]}),
             "note": ("one place, so rotating it is one edit"
                      if e["consumers"] == 1 else
                      "%d places share this value: ONE rotation, %d edits, and "
                      "missing one takes the service down later"
                      % (e["consumers"], e["consumers"]))}
            for e in ordered]


def network_paths():
    """Mount points on a network filesystem, read from /proc/mounts. Never df."""
    out = set()
    try:
        with open("/proc/mounts", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                parts = line.split()
                if len(parts) >= 3 and parts[2] in NETWORK_FSTYPES:
                    out.add(parts[1])
    except OSError:
        pass
    return out


def walk(roots, skip):
    """Bounded file list. Returns (paths, notes)."""
    paths, notes = [], []
    for root in roots:
        if not os.path.isdir(root):
            notes.append("%s: not a directory, skipped" % root)
            continue
        if any(root == m or root.startswith(m.rstrip("/") + "/") for m in skip):
            notes.append("%s: on a network filesystem, skipped" % root)
            continue
        base_depth = root.rstrip("/").count("/")
        for current, dirs, files in os.walk(root, topdown=True):
            if any(current == m or current.startswith(m.rstrip("/") + "/") for m in skip):
                dirs[:] = []
                continue
            if current.rstrip("/").count("/") - base_depth >= MAX_DEPTH:
                dirs[:] = []
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            for name in files:
                if name.endswith(SKIP_SUFFIXES):
                    continue
                full = os.path.join(current, name)
                try:
                    if os.path.getsize(full) > MAX_BYTES:
                        continue
                except OSError:
                    continue
                paths.append(full)
                if len(paths) >= MAX_FILES:
                    notes.append("stopped at the %d-file cap; narrow --root"
                                 % MAX_FILES)
                    return paths, notes
    return paths, notes


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", action="append", default=[],
                        help="a directory to scan; repeatable. Defaults to the short "
                             "list of configuration locations that exist")
    parser.add_argument("--json", action="store_true", help="one line instead of indented")
    args = parser.parse_args()

    roots = args.root or [r for r in DEFAULT_ROOTS if os.path.isdir(r)]
    skip = network_paths()
    paths, notes = walk(roots, skip)

    findings, unreadable = [], 0
    for path in paths:
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                text = handle.read(MAX_BYTES)
        except OSError:
            unreadable += 1
            continue
        if "\x00" in text[:2048]:
            continue          # binary that did not match a suffix
        findings.extend(find_secrets(text, path))

    groups = group(findings)
    print(json.dumps({
        "mode": "ad-secret-inventory",
        "roots": roots,
        "network_paths_skipped": sorted(skip),
        "files_scanned": len(paths),
        "files_unreadable": unreadable,
        "notes": notes,
        "distinct_values": len(groups),
        "rotation_order": rotation_order(groups),
        "groups": groups,
        "never_printed": "no more than %d characters of any value appear in this "
                         "output; the fingerprint is a truncated sha256" % SHOWN_CHARS,
    }, ensure_ascii=False, indent=None if args.json else 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
