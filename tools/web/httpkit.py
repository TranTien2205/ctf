#!/usr/bin/env python3
"""Minimal shared HTTP layer for tools/web/.

stdlib urllib only, so nothing here can fail on a missing dependency. Returns a
plain dict for every outcome, including transport failures: a timeout is a
recorded result, never an exception that loses the evidence.
"""
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "ctf-v2-web/1.0"
_UNVERIFIED = ssl.create_default_context()
_UNVERIFIED.check_hostname = False
_UNVERIFIED.verify_mode = ssl.CERT_NONE


def parse_headers(pairs):
    """['X-A: b', 'Cookie=c'] -> {'X-A': 'b', 'Cookie': 'c'}"""
    out = {}
    for item in pairs or []:
        if ":" in item:
            key, value = item.split(":", 1)
        elif "=" in item:
            key, value = item.split("=", 1)
        else:
            continue
        out[key.strip()] = value.strip()
    return out


def request(url, method="GET", headers=None, body=None, timeout=10,
            max_bytes=1 << 20, insecure=True, follow=True):
    """One request. Never raises for a transport problem."""
    if isinstance(body, str):
        body = body.encode("utf-8", "surrogateescape")
    hdrs = {"User-Agent": UA}
    hdrs.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=hdrs,
                                 method=method.upper())
    opener_args = {"context": _UNVERIFIED} if insecure and url.startswith("https") else {}
    started = time.monotonic()
    try:
        handlers = [] if follow else [_NoRedirect()]
        opener = urllib.request.build_opener(*handlers)
        try:
            resp = opener.open(req, timeout=timeout, **opener_args)
        except urllib.error.HTTPError as exc:
            resp = exc
        with resp:
            raw = resp.read(max_bytes)
            return {
                "ok": True, "url": url, "method": method.upper(),
                "status": getattr(resp, "status", None) or resp.getcode(),
                "headers": dict(resp.headers.items()),
                "final_url": resp.geturl(),
                "length": len(raw),
                "body": raw.decode("utf-8", "replace"),
                "body_bytes": raw,
                "elapsed": round(time.monotonic() - started, 4),
            }
    except Exception as exc:                       # transport, DNS, TLS, timeout
        return {"ok": False, "url": url, "method": method.upper(),
                "status": None, "headers": {}, "body": "", "body_bytes": b"",
                "length": 0, "error": "%s: %s" % (type(exc).__name__, exc),
                "elapsed": round(time.monotonic() - started, 4)}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **kw):
        return None


def fill(template, **values):
    """Substitute {name} placeholders without touching other braces."""
    out = template
    for key, value in values.items():
        out = out.replace("{%s}" % key, str(value))
    return out


def body_signature(text, buckets=64):
    """Coarse fingerprint: length bucket + first matched marker set."""
    markers = sorted(set(re.findall(r"(?i)\b(error|denied|forbidden|not\s?found|"
                                    r"exist|invalid|unauthorized|success|ok)\b", text)))
    return {"length_bucket": len(text) // max(1, buckets),
            "markers": [m.lower() for m in markers][:6]}


def jprint(payload, compact=False):
    print(json.dumps(payload, ensure_ascii=False,
                     indent=None if compact else 2, default=str))
