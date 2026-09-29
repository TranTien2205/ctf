#!/usr/bin/env python3
"""Independent fast router for CTF challenges.

Modes are intentionally limited to CTF work: source scan, observation route,
and public writeup search. This file must not import the red-team toolkit.
"""
import argparse
import html
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLS = {
    "web": "skills/web-triage/SKILL.md", "web-ssrf": "skills/web-ssrf/SKILL.md",
    "pwn": "skills/pwn-binary-triage/SKILL.md",
    "crypto": "skills/crypto-triage/SKILL.md", "rev": "skills/rev-triage/SKILL.md",
    "forensics": "skills/forensics-triage/SKILL.md", "osint": "skills/osint-triage/SKILL.md",
    "dfir": "skills/dfir-sherlock-triage/SKILL.md",
    "misc": "skills/ctf-misc/SKILL.md", "ai": "skills/ai-iot-triage/SKILL.md",
}
SIGNALS = (
    ("web-ssrf", r"ssrf|server-side fetch|url fetch|fetch|url parameter|pdf generator|pdf fetch|webhook|admin bot|headless|render url"),
    ("web", r"react server action|next\.js|server action|rsc|\$action_id"),
    ("web", r"web challenge|https?|endpoint|login|cookie|xss|sqli|sql injection|ssti|upload|idor|jwt"),
    # Stack and datastore names observed in real challenge banners and source.
    ("web", r"express|mongoose|mongodb|nosql|flask|django|laravel|rails|spring|tornado|fastapi|nest|graphql|php|nginx|apache|csrf|cors|session|prototype pollution|class pollution|deserialization|template injection|request smuggling|cache poisoning"),
    ("pwn", r"elf|buffer overflow|format string|rop|heap|shellcode|checksec|got|plt|libc|canary|use-after-free|double free"),
    ("crypto", r"rsa|aes|ecc|cipher|encrypted|modulus|ciphertext|lattice|prng|hash|nonce|oracle padding|padding oracle|diffie|elgamal"),
    ("rev", r"rev|reverse engineering|decompil\w*|disassembl\w*|packed|firmware|bytecode|ghidra|ida pro|crackme|obfuscated binary"),
    ("forensics", r"pcap|memory dump|disk image|stego|steganography|forensics|wireshark|event log|volatility|carving|exiftool"),
    # DFIR / investigation bundles (HTB Sherlocks). Every token here is one the
    # forensics row does not claim: that row owns the carrier words (pcap, stego,
    # "event log"), this one owns the artifact and investigation words.
    ("dfir", r"sherlock|evtx|sysmon|prefetch|amcache|shimcache|usnjrnl|usn journal|\$mft|\$j\b|registry hive|ntuser\.dat|usrclass|cloudtrail|dfir|incident response|triage collection|kape|logon type|4624|4625|4688|4104|7045|scheduled task|script block|threat hunt|blue team"),
    ("osint", r"osint|geolocation|reverse image|whois|social media"),
    ("ai", r"llm|prompt injection|machine learning|model weights|iot|firmware|system prompt|pickle model|mqtt|coap|modbus"),
    # Misc is scored last in practice because it is the residual category, but
    # the score is a hit count, not an order, so every term here is one that
    # no other row claims. Eight keywords used to leave "brainfuck", "QR code"
    # and "base64 chain" classified as unknown, which returned the entry skill
    # and nothing else.
    ("misc", r"pyjail|bashjail|jail|sandbox escape|sandbox|encoding|encoded|esolang|"
             r"esoteric|brainfuck|malbolge|piet|whitespace language|base32|base64|"
             r"base85|base65536|rot13|rot-?n|qr ?code|barcode|morse|z3|sat solver|"
             r"constraint solver|emulator|wasm|webassembly|save file|game vm|game state|"
             r"ctfd|scoreboard|sdr|radio|programming"),
)
SOURCE_RULES = (
    (r"pickle\.loads|yaml\.load\s*\(|unserialize|ObjectInputStream|readObject", "web", "deserialization"),
    (r"render_template_string|Template\s*\(|\{\{[^\n}]{1,80}\}\}", "web", "SSTI"),
    (r"os\.system|subprocess\.(?:run|call|Popen)|shell_exec|passthru|eval\s*\(", "web", "command execution"),
    (r"f[\"'][^\n]*\bSELECT\b[^\n]*\{|SELECT[\s\S]{0,160}(?:\+|%|\.format)|(?:execute|run)\s*\([^\n]*(?:%|format|\+|\$\{)|(?:INSERT|UPDATE|SELECT|DELETE)[^\n]*\$\{", "web", "SQL injection"),
    (r"requests\.(?:get|post)|urlopen\s*\(|\bhttp\.(?:get|request)\s*\(|\bfetch\s*\(", "web", "SSRF candidate"),
    (r"file_get_contents|readfile\s*\(|include\s*\(|require\s*\(|\.\./", "web", "file read/traversal"),
    (r"innerHTML|document\.write|mark_safe|\|safe|dangerouslySetInnerHTML", "web", "XSS"),
    (r"__proto__|Object\.assign|\.merge\s*\(", "web", "prototype pollution"),
    (r"\$rename|\$ne\b|\$gt\b|\$where\b|findOne\s*\(\s*req\.|mongoose\.model", "web", "NoSQL injection"),
    (r"jwt\.(?:decode|verify|sign)|jsonwebtoken|create_signed_value|cookie_secret|APP_KEY|SECRET_KEY", "web", "auth/session secret"),
    (r"multer|\.save\s*\(\s*(?:path|filename)|move_uploaded_file|request\.files", "web", "file upload"),
    (r"gets\s*\(|strcpy\s*\(|sprintf\s*\(|printf\s*\([^\"\n]", "pwn", "memory/format string"),
    (r"RSA|Crypto\.PublicKey|modulus|ciphertext|pow\s*\(", "crypto", "RSA/custom crypto"),
    (r"pcap|tshark|wireshark|steghide|exiftool", "forensics", "forensics/stego"),
    (r"__import__|input\s*\(|sandbox|jail", "misc", "jail/sandbox"),
)
FLAG = re.compile(r"\b[A-Za-z][A-Za-z0-9_-]{1,32}\{[^\r\n}]{1,200}\}")
SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


def files(path):
    if os.path.isfile(path):
        return [path]
    output = []
    for base, dirs, names in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP]
        output.extend(os.path.join(base, n) for n in names)
    return output


def source_route(path):
    findings = []
    flags = []
    count = 0
    for filename in files(path):
        try:
            if os.path.getsize(filename) > 2 * 1024 * 1024:
                continue
            with open(filename, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except (OSError, UnicodeError):
            continue
        count += 1
        for match in FLAG.finditer(text):
            flags.append({"file": filename, "line": text.count("\n", 0, match.start()) + 1,
                          "value": match.group(0)})
        for pattern, category, label in SOURCE_RULES:
            match = re.search(pattern, text, re.I)
            if match:
                findings.append({"category": category, "skill": SKILLS[category],
                                 "signal": label, "file": filename,
                                 "line": text.count("\n", 0, match.start()) + 1})
    dataflow = []
    for item in findings:
        if item["category"] == "web":
            dataflow.append({"file": item["file"], "line": item["line"],
                             "hint": "locate request input reaching %s sink" % item["signal"]})
    return {"mode": "whitebox", "path": path, "files": count,
            "flags": flags, "findings": findings[:30], "dataflow_hints": dataflow[:20]}


def observation_route(text):
    ranked = []
    for category, pattern in SIGNALS:
        hits = re.findall(r"(?<!\w)(?:" + pattern + r")(?!\w)", text, re.I)
        if hits:
            existing = next((item for item in ranked if item["category"] == category), None)
            if existing:
                existing["score"] += len(hits)
            else:
                ranked.append({"category": category, "score": len(hits), "skill": SKILLS[category]})
    ranked.sort(key=lambda item: -item["score"])
    probes = {"web-ssrf": "baseline first; then test a controlled URL you own and compare PDF/response timing",
              "web": "identify endpoint/input reflection and send the cheapest benign probe",
              "pwn": "checksec, identify input boundary, then find the crash offset",
              "crypto": "identify primitive/parameters and run the smallest deterministic attack",
              "rev": "identify binary format, strings, symbols, and the validation path",
              "forensics": "identify artifact type and run metadata/strings before deep parsing",
              "misc": "normalize/decode the input and test the simplest constraint",
              "osint": "extract unique identifiers and pivot one source at a time",
              "ai": "map input to model/tool sink and test a harmless boundary case"}
    return {"mode": "blackbox", "route": ranked[0] if ranked else None,
            "alternates": ranked[1:3],
            "next": probes.get(ranked[0]["category"] if ranked else "", "classify category manually"),
            "related_cards": related_cards(text)}


def fts_query(text):
    tokens = re.findall(r"[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*", text.lower())
    return " OR ".join('"' + token + '"' for token in dict.fromkeys(tokens[:10]))


def related_cards(text, limit=3):
    """Retrieve only compact reviewed cards; the router never loads full writeups."""
    path = os.path.join(ROOT, "knowledge", "ctf.sqlite3")
    if not os.path.exists(path):
        return []
    query = fts_query(text)
    if not query:
        return []
    db = None
    try:
        from pathlib import Path
        db = sqlite3.connect(Path(path).as_uri() + "?mode=ro", uri=True)
        rows = db.execute(
            "SELECT id, name, event, category, technique, first_probe, source_url "
            "FROM cards WHERE cards MATCH ? LIMIT ?", (query, limit)).fetchall()
    except sqlite3.Error:
        return []
    finally:
        if db is not None:
            db.close()
    return [dict(zip(("id", "name", "event", "category", "technique", "first_probe", "source_url"), row))
            for row in rows]


def web_search(name):
    cache_dir = os.path.join(ROOT, "cache")
    cache_file = os.path.join(cache_dir, re.sub(r"[^a-zA-Z0-9_.-]+", "_", name.lower())[:120] + ".json")
    try:
        if os.path.getmtime(cache_file) > time.time() - 86400:
            return json.load(open(cache_file, encoding="utf-8"))
    except (OSError, ValueError):
        pass
    query = urllib.parse.quote('"%s" CTF writeup' % name)
    request = urllib.request.Request("https://html.duckduckgo.com/html/?q=" + query,
                                     headers={"User-Agent": "ctf-toolkit/1.0"})
    try:
        document = urllib.request.urlopen(request, timeout=12).read().decode("utf-8", "replace")
    except Exception as exc:
        return {"mode": "web", "query": name, "error": str(exc), "results": []}
    results = []
    for match in re.finditer(r'class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', document, re.I | re.S):
        href = html.unescape(match.group(1))
        href = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("uddg", [href])[0]
        title = re.sub(r"<[^>]+>", "", html.unescape(match.group(2))).strip()
        results.append({"title": title, "url": href})
    # Add GitHub repository search as a second source without requiring a token.
    try:
        api_url = "https://api.github.com/search/repositories?q=" + urllib.parse.quote(name + " CTF writeup") + "&per_page=5"
        api_request = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json", "User-Agent": "ctf-toolkit/1.0"})
        github = json.loads(urllib.request.urlopen(api_request, timeout=8).read().decode("utf-8", "replace"))
        for item in github.get("items", []):
            results.append({"title": item.get("full_name", ""), "url": item.get("html_url", ""), "source": "github"})
    except Exception:
        pass
    unique = []
    seen = set()
    for item in results:
        if item.get("url") and item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    output = {"mode": "web", "query": name, "results": unique[:12]}
    try:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as handle:
            json.dump(output, handle, ensure_ascii=False)
    except OSError:
        pass
    return output


def main():
    parser = argparse.ArgumentParser(description="Independent CTF router")
    parser.add_argument("input", nargs="?")
    parser.add_argument("--web", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.input:
        parser.error("provide source path, observation, or --web challenge name")
    result = web_search(args.input) if args.web else source_route(args.input) if os.path.exists(args.input) else observation_route(args.input)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
