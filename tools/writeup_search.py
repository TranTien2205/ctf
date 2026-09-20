#!/usr/bin/env python3
"""Search CTF writeups across public indexes; cache URLs, not untrusted prompts."""
import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache", "writeup-search")

# html.duckduckgo.com serves an anti-bot challenge page to non-browser
# User-Agents; a browser UA returns real results.
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(url, timeout=10, headers=None):
    merged = {"User-Agent": UA}
    if headers:
        merged.update(headers)
    request = urllib.request.Request(url, headers=merged)
    return urllib.request.urlopen(request, timeout=timeout).read().decode("utf-8", "replace")


def ddg(query):
    doc = get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query))
    rows = []
    for match in re.finditer(r'class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', doc, re.I | re.S):
        href = match.group(1)
        href = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("uddg", [href])[0]
        title = re.sub(r"<[^>]+>", "", match.group(2)).strip()
        rows.append({"title": title, "url": href, "source": "duckduckgo"})
    if not rows and ("anomaly" in doc or "challenge-form" in doc):
        raise RuntimeError("duckduckgo anti-bot challenge page; 0 results")
    return rows


def github(query):
    url = ("https://api.github.com/search/repositories?q="
           + urllib.parse.quote(f"{query} writeup in:name,description,readme")
           + "&per_page=10")
    data = json.loads(get(url, 10, {"Accept": "application/vnd.github+json"}))
    return [{"title": item.get("full_name", ""), "url": item.get("html_url", ""), "source": "github"}
            for item in data.get("items", [])]


def main():
    ap = argparse.ArgumentParser(description="Search public CTF writeup indexes")
    ap.add_argument("query")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    key = re.sub(r"[^a-z0-9_.-]+", "_", args.query.lower())[:120]
    path = os.path.join(CACHE, key + ".json")
    result = None
    if not args.fresh:
        try:
            if time.time() - os.path.getmtime(path) < 86400:
                cached = json.load(open(path, encoding="utf-8"))
                # Do not reuse poisoned caches: empty results with recorded errors.
                if cached.get("results") or not cached.get("errors"):
                    result = cached
        except (OSError, ValueError):
            pass
    if result is None:
        rows = []
        errors = []
        for source, fn in (("duckduckgo", ddg), ("github", github)):
            try:
                rows.extend(fn(args.query))
            except Exception as exc:
                errors.append({"source": source, "error": str(exc)})
        seen = set()
        rows = [row for row in rows if row.get("url") and not (row["url"] in seen or seen.add(row["url"]))]
        result = {"query": args.query, "results": rows[:20], "errors": errors}
        # Cache successes (or genuine empty results without errors) only.
        if rows or not errors:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False)
    print(json.dumps(result, ensure_ascii=False) if args.json else "\n".join(r["url"] for r in result["results"]))


if __name__ == "__main__":
    main()
