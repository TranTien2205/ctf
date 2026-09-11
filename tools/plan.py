#!/usr/bin/env python3
"""Generate a bounded first-principles CTF plan without web or machine corpus."""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ctf import observation_route


def main():
    ap = argparse.ArgumentParser(description="Plan first probes for an unknown CTF")
    ap.add_argument("observation")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    routed = observation_route(args.observation)
    route = routed.get("route") or {"category": "unknown", "score": 0, "skill": None}
    text = args.observation.lower()
    policy_path = os.path.join(ROOT, "knowledge", "first-probes.json")
    try:
        with open(policy_path, encoding="utf-8") as handle:
            policies = json.load(handle)
    except (OSError, ValueError):
        policies = {}
    candidates = []
    rules = {
        "web": [("ssrf-pdf-fetch", r"url|fetch|webhook|pdf|internal"), ("ssti", r"template|jinja|twig|\{\{"),
                ("sqli", r"sql|sqli|query|database|login"), ("xss-admin-bot", r"xss|reflection|admin bot"), ("jwt", r"jwt"),
                ("idor", r"idor|object|user id|authorization")],
        "web-ssrf": [("ssrf-pdf-fetch", r"url|fetch|webhook|pdf|internal")],
        "pwn": [("buffer-overflow", r"elf|buffer|heap|rop|format|checksec")],
        "crypto": [("rsa", r"rsa|modulus"), ("parameter-weakness", r"aes|nonce|key|cipher|ciphertext|hash")],
        "rev": [("validation-path", r"rev|binary|reverse|decompil\w*|disassembl\w*|packed|firmware|bytecode")],
        "forensics": [("artifact-analysis", r"pcap|memory|disk|stego|forensic")],
        "misc": [("encoding-constraint", r"jail|sandbox|encoding|vm|programming")],
    }
    for technique, pattern in rules.get(route["category"], []):
        hits = re.findall(r"(?<!\w)(?:" + pattern + r")(?!\w)", text, re.I)
        if hits:
            candidates.append({"technique": technique, "score": len(hits), "evidence": sorted(set(hits))})
    if not candidates:
        candidates = [{"technique": "category-discovery", "score": 0, "evidence": [],
                       "probe": "inspect the interface/artifact and establish a baseline"}]
    for candidate in candidates:
        policy = policies.get(candidate["technique"], {})
        candidate.setdefault("probe", policy.get("probe", "run the cheapest confirming probe for " + candidate["technique"]))
        candidate.setdefault("expected", policy.get("expected", "observable response difference"))
        candidate.setdefault("falsifier", policy.get("falsifier", "no controllable input or no distinguishing signal"))
    candidates.sort(key=lambda item: -item["score"])
    result = {"mode": "first-probe-plan", "route": route, "hypotheses": candidates[:3],
              "timebox_minutes": 15, "writeup_search": "skip unless challenge/event name is known"}
    print(json.dumps(result, ensure_ascii=False) if args.json else json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
