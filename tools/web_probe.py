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


_DEFAULT_PORT = {"http": 80, "https": 443, "ftp": 21}


def _effective_authority(url):
    """(hostname, port) with the scheme default filled in."""
    p = urllib.parse.urlparse(url)
    scheme = (p.scheme or "http").lower()
    return (p.hostname or "").lower(), p.port or _DEFAULT_PORT.get(scheme, 0)


class _SameOriginRedirect(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only while it stays on the supplied authority.

    target-recon's crawl boundary is same-origin, supplied port only: an
    outbound Location is recorded as an observation, never followed. A 3xx
    whose target crosses host or port surfaces as the 3xx itself, with its
    Location header intact -- which is the honest thing to report.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if _effective_authority(newurl) != _effective_authority(req.full_url):
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def probe(url, timeout):
    started = time.monotonic()
    request = urllib.request.Request(url, headers={"User-Agent": "ctf-web-probe/1.0"})
    tls_note = None
    # urlopen is this tool's mockable transport seam (tests patch it). The
    # redirect policy lives in a guarded opener swapped into the process
    # global just for this call, so tests keep the seam and production gets
    # the crawl boundary.
    saved_opener = urllib.request._opener
    urllib.request._opener = urllib.request.build_opener(_SameOriginRedirect())
    try:
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            response = exc
        except urllib.error.URLError as exc:
            # A CTF target on a self-signed or broken-chain cert is still a
            # target: retry once unverified, and say so in the result so the
            # observation stays honest about what was checked.
            if "CERTIFICATE_VERIFY_FAILED" in str(exc) or "certificate verify" in str(exc):
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                tls_note = "certificate did not verify; fetched unverified"
                try:
                    insecure = urllib.request.build_opener(
                        _SameOriginRedirect(), urllib.request.HTTPSHandler(context=ctx))
                    response = insecure.open(request, timeout=timeout)
                except urllib.error.HTTPError as exc2:
                    response = exc2
            else:
                raise
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
            if "json" in content_type.lower():
                # An API response that lists its own routes: HATEOAS _links,
                # endpoint maps, directory listings. Every entry is verbatim
                # from the body; reachability is a separate question.
                endpoints.extend(sorted(set(re.findall(
                    r"[\"'](/(?:[A-Za-z0-9_~-]+/)*[A-Za-z0-9_~-]{1,64}(?:\?[A-Za-z0-9_~=&%-]{0,64})?)[\"']",
                    text))))
            params = sorted(set(re.findall(r"name=[\"']([^\"']+)|[?&]([A-Za-z][A-Za-z0-9_-]{1,32})=", text, re.I)))
            params = sorted({a or b for a, b in params if a or b})
            signals = []
            if "X-Powered-By" in response.headers and "Next.js" in response.headers.get("X-Powered-By", ""):
                signals.append("nextjs")
            if action_ids:
                signals.append("react-server-action")
            if forms:
                signals.append("html-form")
            location = response.headers.get("Location")
            return {"status": response.status, "content_type": content_type,
                    "tls": tls_note,
                    "location": location,
                    "redirect_out_of_scope": bool(
                        location and 300 <= response.status < 400
                        and _effective_authority(
                            urllib.parse.urljoin(response.geturl(), location))
                        != _effective_authority(url)),
                    "headers": dict(response.headers.items()), "final_url": response.geturl(),
                    "length_sample": len(body), "sha256_sample": hashlib.sha256(body).hexdigest(),
                    "elapsed": round(time.monotonic() - started, 3), "result": "response",
                    "endpoints": sorted(set(endpoints))[:30], "forms": forms[:30],
                    "action_ids": action_ids[:30], "parameters": params[:50], "signals": signals,
                    "artifact": "pdf" if body.startswith(b"%PDF") or "pdf" in content_type.lower() else "html" if "html" in content_type.lower() else "other"}
    except Exception as exc:
        return {"elapsed": round(time.monotonic() - started, 3), "result": "error", "error": str(exc)}
    finally:
        urllib.request._opener = saved_opener


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
