#!/usr/bin/env python3
"""har_dump.py -- HAR (HTTP archive) request/response inventory.

Browser devtools export `.har` when a challenge says "here's the
traffic" without shipping a pcap, and OSINT/DFIR bundles carry them
too. It is JSON, but 400 entries deep the useful questions are
mechanical: distinct hosts, every request URL+method+status,
secrets in headers/cookies/postData, and flag-shaped tokens in
response bodies. This emits that inventory with entry indexes so
`jq` can pull any one entry back out.

  python3 tools/forensics/har_dump.py capture.har
  python3 tools/forensics/har_dump.py capture.har --bodies
  python3 tools/forensics/har_dump.py --selftest
"""
import argparse
import json
import re

SECRET_KEYS = re.compile(
    r"(authorization|cookie|set-cookie|token|secret|api[-_]?key"
    r"|session|password|passwd|credential)", re.I)
FLAG_RX = re.compile(r"\b[A-Za-z0-9_]{2,20}\{[^\x00-\x20}]{4,80}\}")


def _pairs(lst):
    return {e.get("name", ""): e.get("value", "") for e in lst or []}


def parse(data):
    try:
        har = json.loads(data)
    except (TypeError, ValueError):
        return {"error": "not JSON; a .har is a JSON archive"}
    log = har.get("log", {})
    entries = log.get("entries", [])
    out = {"version": log.get("version"),
           "creator": (log.get("creator") or {}).get("name"),
           "entries": []}
    secrets, flags, hosts = [], [], set()
    for i, e in enumerate(entries):
        req = e.get("request", {})
        res = e.get("response", {})
        url = req.get("url", "")
        host = re.sub(r"^https?://", "", url).split("/")[0]
        hosts.add(host)
        row = {"i": i, "method": req.get("method"), "url": url,
               "status": res.get("status"),
               "mime": (res.get("content") or {}).get("mimeType")}
        out["entries"].append(row)
        for src, hdrs in (("req", _pairs(req.get("headers"))),
                          ("res", _pairs(res.get("headers")))):
            for k, v in hdrs.items():
                if SECRET_KEYS.search(k):
                    secrets.append({"entry": i, "dir": src,
                                    "name": k, "value": v[:120]})
        for c in req.get("cookies") or []:
            secrets.append({"entry": i, "dir": "cookie",
                            "name": c.get("name", ""),
                            "value": str(c.get("value", ""))[:120]})
        pd = (req.get("postData") or {}).get("text") or ""
        for m in SECRET_KEYS.finditer(pd):
            secrets.append({"entry": i, "dir": "postData",
                            "name": "field", "value": pd[:200]})
            break
        body = (res.get("content") or {}).get("text") or ""
        if (res.get("content") or {}).get("encoding") == "base64":
            import base64
            try:
                body = base64.b64decode(body, validate=False).decode(
                    "utf-8", "replace")
            except Exception:
                body = ""
        for m in FLAG_RX.finditer(body):
            flags.append({"entry": i, "flag": m.group(0)})
        if pd:
            for m in FLAG_RX.finditer(pd):
                flags.append({"entry": i, "flag": m.group(0),
                              "where": "postData"})
    out["hosts"] = sorted(hosts)
    out["secrets"] = secrets[:200]
    out["flag_candidates"] = flags[:100]
    return out


def _selftest():
    har = {"log": {"version": "1.2", "creator": {"name": "devtools"},
                   "entries": [
                       {"request": {"method": "GET",
                                    "url": "https://a.ctf.local/x",
                                    "headers": [{"name": "Cookie",
                                                 "value": "s=sekrit"}],
                                    "cookies": [{"name": "s",
                                                 "value": "sekrit"}]},
                        "response": {"status": 200, "headers": [],
                                     "content": {"mimeType": "text/plain",
                                                 "text": "ok flag{har_ok}"}}},
                       {"request": {"method": "POST",
                                    "url": "https://b.ctf.local/api",
                                    "postData": {"text": "user=a&password=p"}},
                        "response": {"status": 403, "headers": [],
                                     "content": {"text": "denied"}}}]}}
    out = parse(json.dumps(har))
    assert len(out["entries"]) == 2
    assert out["hosts"] == ["a.ctf.local", "b.ctf.local"]
    assert any(s["value"] == "s=sekrit" for s in out["secrets"]), out
    assert any(f["flag"] == "flag{har_ok}" for f in
               out["flag_candidates"]), out
    assert parse(b"not json")["error"]
    assert parse(json.dumps({"log": {"entries": []}}))["entries"] == []
    print("har_dump selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="HAR archive inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--bodies", action="store_true",
                    help="also print response body text (truncated)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    out = parse(open(a.path, "rb").read())
    if a.bodies:
        har = json.loads(open(a.path, "rb").read())
        for i, e in enumerate(har.get("log", {}).get("entries", [])):
            out["entries"][i]["body"] = (
                (e.get("response") or {}).get("content") or {}
            ).get("text", "")[:500]
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
