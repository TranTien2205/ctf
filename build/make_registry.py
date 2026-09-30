#!/usr/bin/env python3
"""Regenerate skills/registry.json from the real tree and the bug-class taxonomy.

Hand-written routing prose for the skills that predate the taxonomy is preserved
from the current registry. Bug-class skills get their routing text derived from
knowledge/bug-classes.json, so a class and the skill it routes to cannot drift.

Token counts are recomputed from real file sizes every run.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "skills", "registry.json")
TAXONOMY = os.path.join(ROOT, "knowledge", "bug-classes.json")

# Skills that are not bug classes and keep their hand-written routing text.
PORTED = {
    "web-chromedriver": {
        "layer": "depth", "categories": ["web"],
        "use_when": ["a challenge has an admin bot and a client-side payload needs debugging",
                     "the challenge itself exposes a WebDriver or Selenium endpoint"],
        "do_not_use_when": ["the payload is already confirmed: fire it, do not rebuild the bot",
                            "there is no viewer at all, so no client-side path to the flag"],
        "routes_to": ["web-xss", "web-csrf", "file-read-primitives"],
        "unlock_signals": r"chromedriver|webdriver|selenium|headless|puppeteer|playwright|admin bot|bot visits|9515|4444",
    },
    "web-parallel-sweep": {
        "layer": "reference", "categories": ["web"],
        "use_when": ["a web target with recon done and no strong chain match, so several "
                     "bug-class families each need their own bounded measurement",
                     "a web challenge is being worked one hypothesis at a time and the "
                     "clock is the blocker"],
        "do_not_use_when": ["chain_match.py returns a candidate: run that card's probe first",
                            "no recon exists yet: run ctf-web-recon and ctf-web-bundle first",
                            "one endpoint and one sink, so there is nothing to fan out"],
        "routes_to": ["web-triage", "parallel-layer-sweep", "white-box-intended-path"],
        "unlock_signals": r"ctf-web-|fan.?out|parallel (?:web )?sweep|subagent_fanout|ten families",
    },
    "parallel-layer-sweep": {
        "layer": "reference", "categories": ["*"],
        "use_when": ["a multi-layer white-box handout and no strong chain match, so several "
                     "independent mechanism layers each need their own falsifier",
                     "a session is walking layers one at a time and the clock is the blocker"],
        "do_not_use_when": ["chain_match.py returns a candidate: run that card's probe first",
                            "one endpoint and one sink, so there is nothing to fan out",
                            "the only way to measure the layer is a write-shaped probe"],
        "routes_to": ["white-box-intended-path", "white-box-dependency-measurement",
                      "ctf-playbook"],
        "unlock_signals": r"subagent|fan.?out|parallel layer|layer sweep|novel_plan|several layers",
    },
    "mcp-agent-security": {
        "layer": "depth", "categories": ["ai"],
        "use_when": ["the challenge target is an LLM, an agent, or a tool server",
                     "an external skill or MCP bundle is being reviewed before install"],
        "do_not_use_when": ["the artifact is a serialised model file: use web-deserialization",
                            "the target is a third-party server nobody here operates"],
        "routes_to": ["web-deserialization", "file-read-primitives"],
        "unlock_signals": r"\bmcp\b|agent|llm|chatbot|system prompt|prompt injection|tool call|function calling",
    },
    "security-skill-evaluation": {
        "layer": "reference", "categories": ["*"],
        "use_when": ["a skill is being added, promoted, or considered for deletion",
                     "a field note is being reviewed, or a class raised from catalogue"],
        "do_not_use_when": ["a challenge is in progress: this skill solves nothing"],
        "routes_to": [],
        "unlock_signals": None,
    },
    "web-websocket": {
        "layer": "depth", "categories": ["web"],
        "use_when": ["the target opens a ws:// or wss:// channel, or uses Socket.IO or SockJS",
                     "a live feature carries the flag path and the cookie is HttpOnly"],
        "do_not_use_when": ["there is no realtime channel: use the matching HTTP class",
                            "the channel is already confirmed hijackable: fire one probe, do not rebuild"],
        "routes_to": ["web-csrf", "web-auth-session", "web-xss"],
        "unlock_signals": r"websocket|ws://|wss://|socket\.io|sockjs|upgrade:\s*websocket|101 switching|realtime|live update",
    },
    "web-source-map": {
        "layer": "depth", "categories": ["web"],
        "use_when": ["the front-end is a bundled SPA and the only available source",
                     "a sourceMappingURL or /_next/static/ or /static/js/ bundle is present"],
        "do_not_use_when": ["source is already supplied: read it directly",
                            "the bundle is a single inline script with no build step"],
        "routes_to": ["file-read-primitives", "web-auth-session"],
        "unlock_signals": r"sourceMappingURL|\.js\.map|_next/static|/static/js/|webpack|vite|/_buildManifest|/_ssgManifest",
    },
    "web-xs-leaks": {
        "layer": "depth", "categories": ["web"],
        "use_when": ["an admin bot visits attacker pages and the cookie is HttpOnly",
                     "the goal is to learn a fact about the victim's authenticated state"],
        "do_not_use_when": ["the response is readable cross-origin: use the ordinary web class",
                            "no bot or viewer exists to carry the victim session"],
        "routes_to": ["web-xss", "web-cache-poisoning", "web-csrf"],
        "unlock_signals": r"xs-?leak|cross-?site leak|admin bot|bot visits|onerror|onload|cache prob|iframe timing|same-?site",
    },
    "web-info-disclosure": {
        "layer": "depth", "categories": ["web"],
        "use_when": ["the flag or the next step may sit in an exposed file or debug endpoint",
                     "a 403, verbose error, debug header, or a shipped .git or archive is observed"],
        "do_not_use_when": ["the finding is a real sink: use the matching injection class",
                            "the target is a shared host and only a wide scan is available"],
        "routes_to": ["file-read-primitives", "web-auth-session", "web-source-map"],
        "unlock_signals": r"\.git/|\.env|\.ds_store|backup\.zip|actuator|swagger|debug|stack trace|server-status|source leak",
    },
    # Method skills. They do not name a bug class; they say how to establish a
    # fact about one. Both were written from CSCV 2026 sessions: the first from
    # three chains it produced, the second from the one that was lost.
    "white-box-dependency-measurement": {
        "layer": "depth", "categories": ["web"],
        "use_when": ["a chain turns on what a pinned, vendored or containerised dependency actually does",
                     "a negative result has to be recordable as a measured boundary, not an opinion"],
        "do_not_use_when": ["no source or container is available: there is nothing to measure",
                            "published documentation already settles it and nothing is pinned"],
        "routes_to": ["white-box-intended-path", "file-read-primitives"],
        "unlock_signals": (r"package-lock|yarn\.lock|requirements\.txt|poetry\.lock|go\.sum|Gemfile\.lock|"
                           r"Dockerfile|docker-compose|node_modules|vendor/|haproxy|gunicorn|uwsgi|"
                           r"nginx\.conf|varnish|alpine|==\d+\.\d+|@\d+\.\d+\.\d+"),
    },
    "white-box-intended-path": {
        "layer": "depth", "categories": ["web"],
        "use_when": ["a high-value, low-solve white-box challenge whose author-deliberate oddities are unexplained",
                     "one mechanism budget is spent with no impact and no anomaly newly explained"],
        "do_not_use_when": ["a chain already reaches impact: finish it",
                            "the challenge is black-box, so there is no handout to diff against stock"],
        "routes_to": ["white-box-dependency-measurement"],
        "unlock_signals": (r"handout|stock app|upstream diff|anomaly|unused (route|field|parameter)|"
                           r"dead code|custom fork|patched vendor|why is this here"),
    },
    # --- attack-defense. A different game from jeopardy: the flag rotates every
    # --- tick, you are also the target, and availability is scored continuously.
    "ad-service-triage": {
        "layer": "router", "categories": ["*"],
        "use_when": ["an attack-defense contest starts and a service needs triage",
                     "every team runs an identical copy of the service you are defending"],
        "do_not_use_when": ["a single jeopardy target with one flag: use ctf-playbook",
                            "the service is currently red: restore availability first"],
        "routes_to": ["ad-traffic-mining", "ad-patch-without-breaking-sla",
                      "ad-planted-backdoor-hunt", "ir-live-estate-triage",
                      "web-triage", "white-box-intended-path"],
        "unlock_signals": (r"attack.?defen[cs]e|attack-defense|scoreboard|tick|"
                           r"other teams|team host|flag rotat|availability|sla|uptime"),
    },
    "ad-traffic-mining": {
        "layer": "depth", "categories": ["*"],
        "use_when": ["another team is already attacking your service and the capture holds their payload",
                     "source reading has produced no hypothesis and the clock is the blocker"],
        "do_not_use_when": ["no baseline capture exists, so nothing can be ranked against normal",
                            "a candidate has already replayed against your own box and returned nothing"],
        "routes_to": ["ad-patch-without-breaking-sla", "web-triage"],
        "unlock_signals": (r"capture|pcap|dumpcap|tcpdump|tshark|replay|their exploit|"
                           r"inbound (request|traffic)|steal (the )?exploit"),
    },
    "ad-patch-without-breaking-sla": {
        "layer": "depth", "categories": ["*"],
        "use_when": ["a bug is understood and a patch is about to go onto a live scored service",
                     "a patch has just been applied and nothing has verified the feature still works"],
        "do_not_use_when": ["no green baseline was saved, so there is nothing to compare against",
                            "the service is already red: this is recovery, not patching"],
        "routes_to": ["ad-service-triage", "ad-planted-backdoor-hunt"],
        "unlock_signals": (r"patch|hotfix|mitigat|rollback|revert|health check|"
                           r"availability|sla|regression|checker"),
    },
    "ad-planted-backdoor-hunt": {
        "layer": "depth", "categories": ["*"],
        "use_when": ["every team booted an identical image and it may carry a planted foothold",
                     "credentials have just been rotated and the first thirty minutes are free"],
        "do_not_use_when": ["the task is reconstructing what an attacker did: use ir-live-estate-triage",
                            "the sweep has not been bounded to hosts the event assigned you"],
        "routes_to": ["ad-patch-without-breaking-sla", "dfir-persistence-trace",
                      "ir-live-estate-triage"],
        "unlock_signals": (r"backdoor|planted|starting image|authorized_keys|systemd (unit|timer)|"
                           r"cron|suid|ld\.so\.preload|web shell|persistence"),
    },
    "ir-live-estate-triage": {
        "layer": "router", "categories": ["dfir"],
        "use_when": ["a live estate has already been hit and both recovery and investigation are scored",
                     "services are down, files are encrypted, and a clock is running"],
        "do_not_use_when": ["the input is a closed artifact bundle with a numbered question list: "
                            "use dfir-sherlock-triage",
                            "nothing is scored for availability, so the intake need not be bounded"],
        "routes_to": ["dfir-authentication-trace", "dfir-execution-trace",
                      "dfir-persistence-trace", "dfir-filesystem-timeline",
                      "dfir-network-exfil-trace", "dfir-cloud-audit-trace",
                      "dfir-antiforensics-trace", "ad-planted-backdoor-hunt"],
        "unlock_signals": (r"ransom|encrypted files|ransom note|restore|recovery|incident response|"
                           r"post.?incident|live host|estate|root cause"),
    },
}


def tokens(path):
    full = os.path.join(ROOT, path)
    return round(os.path.getsize(full) / 4) if os.path.isfile(full) else 0


def dir_tokens(skill_dir):
    base = os.path.join(ROOT, "skills", skill_dir)
    total, count = 0, 0
    for name in os.listdir(base):
        sub = os.path.join(base, name)
        if os.path.isdir(sub):
            for ref in os.listdir(sub):
                path = os.path.join(sub, ref)
                if os.path.isfile(path):
                    total += os.path.getsize(path)
                    count += 1
        elif name not in ("SKILL.md",) and os.path.isfile(sub):
            total += os.path.getsize(sub)
            count += 1
    return count, round(total / 4)


def class_entry(cls):
    verified = cls["evidence_level"] == "verified"
    files, depth = dir_tokens(cls["skill_dir"])
    use_when = ["a probe or source read produced this class's signal: " + cls["first_probe"]]
    if verified:
        use_when.append("a chain card already proves this class here: "
                        + ", ".join(cls["verified_by"]))
    do_not = ["the falsifier has been observed: " + cls["falsifier"]]
    if cls.get("confusable_with"):
        do_not.append("the evidence fits one of these better: "
                      + ", ".join(cls["confusable_with"]))
    if not verified:
        do_not.append("do not present its content as local experience: this class is catalogue, "
                      "never solved in this toolkit")
    signals = cls.get("observation_signals", []) + cls.get("source_signals", [])
    return {
        "id": cls["id"], "path": cls["skill"], "layer": "depth",
        "categories": [cls["category"]],
        "evidence_level": cls["evidence_level"],
        "verified_by": cls["verified_by"],
        "skill_tokens": tokens(cls["skill"]),
        "depth_files": files, "depth_tokens": depth,
        "use_when": use_when, "do_not_use_when": do_not,
        "routes_to": [c for c in cls.get("confusable_with", [])],
        "unlock_signals": "|".join("(?:%s)" % s for s in signals) if signals else None,
        "bug_class": True,
    }


def main():
    with open(REGISTRY, encoding="utf-8") as handle:
        current = json.load(handle)
    with open(TAXONOMY, encoding="utf-8") as handle:
        taxonomy = json.load(handle)

    previous = {entry["id"]: entry for entry in current["skills"]}
    class_ids = {cls["id"] for cls in taxonomy["classes"]}
    skills = []

    # 1. keep every non-class, non-ported skill exactly as written, refreshing sizes
    for entry in current["skills"]:
        if entry["id"] in class_ids or entry["id"] in PORTED:
            continue
        entry["skill_tokens"] = tokens(entry["path"])
        files, depth = dir_tokens(os.path.basename(os.path.dirname(entry["path"])))
        entry["depth_files"], entry["depth_tokens"] = files, depth
        skills.append(entry)

    # 2. one entry per bug class, derived from the taxonomy
    for cls in taxonomy["classes"]:
        entry = class_entry(cls)
        old = previous.get(cls["id"])
        if old and old.get("manual_gate"):
            entry["manual_gate"] = old["manual_gate"]
        skills.append(entry)

    # 3. the ported skills
    for skill_id, spec in PORTED.items():
        # A formerly standalone web skill may later become a taxonomy bug class.
        # Taxonomy owns the canonical registry entry in that case; emitting both
        # creates duplicate IDs and makes routing ambiguous.
        if skill_id in class_ids:
            continue
        path = "skills/%s/SKILL.md" % skill_id
        if not os.path.isfile(os.path.join(ROOT, path)):
            continue
        files, depth = dir_tokens(skill_id)
        entry = {"id": skill_id, "path": path, "layer": spec["layer"],
                 "categories": spec["categories"],
                 "skill_tokens": tokens(path), "depth_files": files, "depth_tokens": depth,
                 "use_when": spec["use_when"], "do_not_use_when": spec["do_not_use_when"],
                 "routes_to": spec["routes_to"]}
        if spec.get("unlock_signals"):
            entry["unlock_signals"] = spec["unlock_signals"]
        skills.append(entry)

    # 4. the web router routes to every web bug class plus the web-only ported skills
    web_targets = sorted(cls["id"] for cls in taxonomy["classes"] if cls["category"] == "web")
    web_targets += ["web-chromedriver", "ctf-web",
                    "web-websocket", "web-source-map", "web-xs-leaks", "web-info-disclosure",
                    "white-box-dependency-measurement", "white-box-intended-path"]
    by_id = {entry["id"]: entry for entry in skills}
    for entry in skills:
        if entry["id"] == "web-triage":
            entry["routes_to"] = [t for t in dict.fromkeys(web_targets) if t in by_id]
        if entry["id"] == "ai-iot-triage":
            entry["routes_to"] = [t for t in ["ctf-ai-ml", "mcp-agent-security",
                                              "web-deserialization", "rev-triage"] if t in by_id]
        if entry["id"] == "ctf-playbook":
            entry["routes_to"] = [t for t in entry["routes_to"] if t in by_id]

    skills.sort(key=lambda e: ({"entry": 0, "router": 1, "depth": 2, "reference": 3}[e["layer"]],
                               e["id"]))
    current["skills"] = skills
    current["generated_from"] = ("build/make_registry.py over the real skills/ tree and "
                                 "knowledge/bug-classes.json")
    current["layers"]["depth"] = ("A bug class, or a large technique corpus. A bug-class skill "
                                  "is short and carries evidence_level; a corpus is gated.")
    with open(REGISTRY, "w", encoding="utf-8") as handle:
        json.dump(current, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    counts = {}
    for entry in skills:
        counts[entry["layer"]] = counts.get(entry["layer"], 0) + 1
    print(json.dumps({"skills": len(skills), "by_layer": counts,
                      "bug_classes": sum(1 for e in skills if e.get("bug_class")),
                      "web_router_targets": len(by_id["web-triage"]["routes_to"])},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
