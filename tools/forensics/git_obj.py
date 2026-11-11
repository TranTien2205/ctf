#!/usr/bin/env python3
"""git_obj.py -- loose git object reader + unreachable-object scan.

'Flag in a deleted commit' is a standard hide: `git log` only shows
reachable history, and `git fsck` needs the git binary anyway. This
walks .git/objects/aa/bb... loose files (zlib, 'type size\\0body'),
resolves refs/ + packed-refs, marks everything reachable from them,
and reports the objects left over — the dangling ones.

  python3 tools/forensics/git_obj.py ./dotgit list
  python3 tools/forensics/git_obj.py ./dotgit cat <sha1>
  python3 tools/forensics/git_obj.py ./dotgit dangling
  python3 tools/forensics/git_obj.py --selftest

`cat` writes the raw object body to stdout (blob = file contents;
commit = the commit record with tree/parent lines; tree = binary
entries). Only loose objects — pack files report packed presence
but are not walked.
"""
import argparse
import json
import os
import re
import sys
import zlib


def read_obj(root, sha):
    p = os.path.join(root, "objects", sha[:2], sha[2:])
    if not os.path.exists(p):
        return None, None
    raw = zlib.decompress(open(p, "rb").read())
    head, _, body = raw.partition(b"\x00")
    typ, _, _sz = head.partition(b" ")
    return typ.decode(), body


def list_objs(root):
    out = []
    odir = os.path.join(root, "objects")
    for d in os.listdir(odir) if os.path.isdir(odir) else []:
        if len(d) != 2:
            continue
        for f in os.listdir(os.path.join(odir, d)):
            sha = d + f
            try:
                typ, body = read_obj(root, sha)
                if typ:
                    out.append({"sha": sha, "type": typ,
                                "size": len(body)})
            except zlib.error:
                continue
    return out


def refs(root):
    out = []
    rdir = os.path.join(root, "refs")
    for dp, _dn, fn in os.walk(rdir):
        for f in fn:
            v = open(os.path.join(dp, f), "rb").read().strip()
            out.append((f, v.decode("ascii", "replace")))
    pr = os.path.join(root, "packed-refs")
    if os.path.exists(pr):
        for line in open(pr, "rb"):
            line = line.strip()
            if line and not line.startswith(b"#"):
                sha, _, name = line.partition(b" ")
                out.append((name.decode(), sha.decode()))
    return out


def reach(root, start, seen=None):
    if seen is None:
        seen = set()
    todo = [start]
    while todo:
        sha = todo.pop()
        if sha in seen:
            continue
        seen.add(sha)
        typ, body = read_obj(root, sha)
        if not body:
            continue
        if typ == "commit":
            for m in re.finditer(rb"^(?:tree|parent) ([0-9a-f]{40})",
                                 body, re.M):
                todo.append(m.group(1).decode())
        elif typ == "tree":
            for i in range(len(body)):
                if body[i:i + 1] == b"\x00":
                    todo.append(body[i + 1:i + 21].hex())
    return seen


def dangling(root):
    objs = list_objs(root)
    seen = set()
    for _name, sha in refs(root):
        reach(root, sha, seen)
    return [o for o in objs if o["sha"] not in seen]


def _selftest():
    import hashlib
    import tempfile
    root = tempfile.mkdtemp()

    def put(typ, body):
        raw = typ.encode() + b" " + str(len(body)).encode() + \
            b"\x00" + body
        sha = hashlib.sha1(raw).hexdigest()
        d = os.path.join(root, "objects", sha[:2])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, sha[2:]), "wb").write(
            zlib.compress(raw))
        return sha

    blob = put("blob", b"flag{reachable_blob}")
    tree = put("tree", b"100644 f.txt\x00" + bytes.fromhex(blob))
    commit = put("commit",
                 b"tree " + tree.encode() + b"\nauthor x\n\nmsg")
    lost = put("blob", b"flag{deleted_commit_remains}")
    os.makedirs(os.path.join(root, "refs", "heads"), exist_ok=True)
    open(os.path.join(root, "refs", "heads", "main"), "w").write(
        commit)
    objs = list_objs(root)
    assert len(objs) == 4, objs
    t, b = read_obj(root, blob)
    assert t == "blob" and b"reachable_blob" in b
    dg = dangling(root)
    assert [o["sha"] for o in dg] == [lost], dg
    print("git_obj selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="loose git object reader")
    ap.add_argument("gitdir", nargs="?")
    ap.add_argument("cmd", nargs="?",
                    choices=["list", "cat", "dangling"])
    ap.add_argument("sha", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.gitdir and a.cmd):
        ap.error("gitdir and cmd required")
    if a.cmd == "list":
        print(json.dumps(list_objs(a.gitdir), indent=1))
    elif a.cmd == "dangling":
        print(json.dumps(dangling(a.gitdir), indent=1))
    else:
        if not a.sha:
            ap.error("cat needs a sha")
        typ, body = read_obj(a.gitdir, a.sha)
        if body is None:
            sys.exit("object not found")
        sys.stderr.write(f"type={typ} size={len(body)}\n")
        sys.stdout.buffer.write(body)


if __name__ == "__main__":
    raise SystemExit(main())
