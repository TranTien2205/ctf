#!/usr/bin/env python3
"""Small CTF web probe: measure endpoint behavior without broad scanning."""
import argparse
import json
import time
import urllib.parse
import urllib.request
import urllib.error
import re
import hashlib
import html


def probe(url, timeout):
    started = time.monotonic()
    request = urllib.request.Request(url, headers={"User-Agent": "ctf-web-probe/1.0"})
    try:
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            body = response.read(65536)
            content_type = response.headers.get("Content-Type", "")
            text = body.decode("utf-8", "replace")
            endpoints = sorted(set(re.findall(r"(?:fetch|location\.href)\s*\(?[\"']([^\"']+)", text, re.I)))
            forms = []
            for form in re.findall(r"<form\b([^>]*)>(.*?)</form>", text, re.I | re.S):
                attrs, form_body = form
                action = re.search(r"\baction\s*=\s*[\"']([^\"']*)", attrs, re.I)
                method = re.search(r"\bmethod\s*=\s*[\"']([^\"']*)", attrs, re.I)
                names = sorted(set(re.findall(r"\bname\s*=\s*[\"']([^\"']+)", form_body, re.I)))
                forms.append({"action": html.unescape(action.group(1)) if action else "", "method": (method.group(1).upper() if method else "GET"), "parameters": names})
            action_ids = sorted(set(re.findall(r'name=["\'](\$ACTION_ID_[^"\']+)', text, re.I)))
            endpoints.extend(sorted(set(re.findall(r"(?:fetch|axios\.(?:get|post)|XMLHttpRequest)[^\"']{0,120}[\"']([^\"']+)", text, re.I))))
            params = sorted(set(re.findall(r"name=[\"']([^\"']+)|[?&]([A-Za-z][A-Za-z0-9_-]{1,32})=", text, re.I)))
            params = sorted({a or b for a, b in params if a or b})
            signals = []
            if "X-Powered-By" in response.headers and "Next.js" in response.headers.get("X-Powered-By", ""):
                signals.append("nextjs")
            if action_ids:
                signals.append("react-server-action")
            if forms:
                signals.append("html-form")
            return {"status": response.status, "content_type": content_type,
                    "headers": dict(response.headers.items()), "final_url": response.geturl(),
                    "length_sample": len(body), "sha256_sample": hashlib.sha256(body).hexdigest(),
                    "elapsed": round(time.monotonic() - started, 3), "result": "response",
                    "endpoints": sorted(set(endpoints))[:30], "forms": forms[:30],
                    "action_ids": action_ids[:30], "parameters": params[:50], "signals": signals,
                    "artifact": "pdf" if body.startswith(b"%PDF") or "pdf" in content_type.lower() else "html" if "html" in content_type.lower() else "other"}
    except Exception as exc:
        return {"elapsed": round(time.monotonic() - started, 3), "result": "error", "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Minimal authorized CTF web behavior probe")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--param", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--save", help="save JSON observation to a file")
    args = parser.parse_args()
    query = dict(item.split("=", 1) for item in args.param if "=" in item)
    target = args.url
    if query:
        target += ("&" if "?" in target else "?") + urllib.parse.urlencode(query)
    output = {"url": target, "probe": probe(target, args.timeout)}
    rendered = json.dumps(output, ensure_ascii=False)
    print(rendered)
    if args.save:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(args.save)), exist_ok=True)
        with open(args.save, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")


if __name__ == "__main__":
    main()
