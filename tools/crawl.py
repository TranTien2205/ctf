#!/usr/bin/env python3
"""Bounded public writeup fetcher for one assigned crawl session.

It fetches explicitly supplied URLs only. Discovery remains a separate task so
one worker cannot accidentally crawl an entire site.
"""
import argparse
import hashlib
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def normalize(text, content_type):
    if "html" in content_type.lower():
        text = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", text)
        text = re.sub(r"(?i)<br\s*/?>", "\n", text)
        text = re.sub(r"(?i)</?(?:p|div|article|section|h[1-6]|li|pre|code)[^>]*>", "\n", text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&nbsp;", " ", text, flags=re.I)
        text = re.sub(r"&(?:amp|lt|gt|quot);", lambda m: {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"'}[m.group(0).lower()], text, flags=re.I)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def fetch(url, timeout, max_bytes):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("only absolute http/https URLs are allowed")
    request = urllib.request.Request(url, headers={"User-Agent": "ctf-crawler/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content = response.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise ValueError("response exceeds max-bytes")
        content_type = response.headers.get("Content-Type", "")
        return content, content_type, response.status, response.geturl()


def main():
    ap = argparse.ArgumentParser(description="Fetch explicitly assigned CTF writeup URLs")
    ap.add_argument("source_id")
    ap.add_argument("urls", nargs="+", help="explicit URLs; no site discovery is performed")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--max-bytes", type=int, default=2_000_000)
    ap.add_argument("--out", default=os.path.join(ROOT, "knowledge", "raw"))
    args = ap.parse_args()
    base = os.path.join(args.out, re.sub(r"[^a-zA-Z0-9_.-]+", "_", args.source_id))
    raw_dir = os.path.join(base, "raw")
    normalized_dir = os.path.join(base, "normalized")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(normalized_dir, exist_ok=True)
    manifest = os.path.join(base, "manifest.jsonl")
    for url in dict.fromkeys(args.urls):
        row = {"url": url, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        try:
            body, content_type, status, final_url = fetch(url, args.timeout, args.max_bytes)
            digest = hashlib.sha256(body).hexdigest()
            raw_path = os.path.join(raw_dir, digest + ".bin")
            normalized_path = os.path.join(normalized_dir, digest + ".md")
            if not os.path.exists(raw_path):
                with open(raw_path, "wb") as handle:
                    handle.write(body)
            if not os.path.exists(normalized_path):
                with open(normalized_path, "w", encoding="utf-8") as handle:
                    handle.write(normalize(body.decode("utf-8", "replace"), content_type) + "\n")
            row.update({"status": status, "final_url": final_url, "content_type": content_type,
                        "sha256": digest, "raw": raw_path, "normalized": normalized_path})
        except Exception as exc:
            row.update({"status": "error", "error": str(exc)})
        with open(manifest, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
