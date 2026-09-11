#!/usr/bin/env python3
"""Select a bounded Markdown-only GitHub writeup pilot at a pinned commit."""
import argparse
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def api(url):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ctf-github-pilot/1.0",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8", "replace"))


def main():
    parser = argparse.ArgumentParser(description="Bounded GitHub CTF writeup pilot")
    parser.add_argument("--repo", default="ctfs/writeups")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--out", default=os.path.join(ROOT, "knowledge", "raw"))
    args = parser.parse_args()
    meta = api("https://api.github.com/repos/" + args.repo)
    repo = meta["full_name"]
    commit = api("https://api.github.com/repos/%s/commits/%s" % (repo, meta["default_branch"]))
    sha = commit["sha"]
    tree = api("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (repo, sha))
    candidates = [item for item in tree.get("tree", [])
                  if item.get("type") == "blob" and item.get("path", "").lower().endswith((".md", ".markdown"))
                  and "/web/" in "/" + item.get("path", "").lower()]
    candidates = sorted(candidates, key=lambda item: (item.get("path", "").lower(), item.get("sha", "")))[:max(1, args.limit)]
    source_id = "github-ctfs-writeups-pilot"
    urls = ["https://raw.githubusercontent.com/%s/%s/%s" % (repo, sha, item["path"])
            for item in candidates]
    os.makedirs(os.path.join(args.out, source_id), exist_ok=True)
    manifest = {"repo": repo, "commit": sha, "default_branch": meta["default_branch"],
                "selected": len(urls), "paths": [item["path"] for item in candidates]}
    with open(os.path.join(args.out, source_id, "selection.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
    if not urls:
        print(json.dumps(manifest, ensure_ascii=False))
        return
    command = [sys.executable, os.path.join(ROOT, "tools", "crawl.py"), source_id, *urls,
               "--out", args.out]
    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    print(json.dumps(manifest, ensure_ascii=False))
    print(result.stdout, end="")
    if result.returncode:
        print(result.stderr, file=sys.stderr, end="")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
