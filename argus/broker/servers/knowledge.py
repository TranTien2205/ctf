"""knowledge — the ladders, the proof matrix, the skills, and prior chains.

This server answers "what is known about this shape already", which is always
cheaper than measuring it again. It reads data files, never the network: a
research question that needs the internet goes to a browser MCP server, and its
answer comes back as evidence through `ledger.add_evidence`.
"""
from __future__ import annotations

import json

from ... import config
from ...knowledge import playbook
from ...ledger import proof as matrix
from ...util import read_json
from ..mcp import Server, ToolContext

SERVER = Server("knowledge", "probe ladders, proof requirements, skills and prior chains")


@SERVER.tool(
    "knowledge.playbook",
    "The probe ladder for a class: the cheapest discriminating step first, the proof step last, and "
    "why each step exists. Read it before probing, and depart from it deliberately rather than by "
    "accident.",
    {"properties": {"vuln_class": {"type": "string",
                                   "description": "omit to list every class with a ladder"}},
     "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def playbook_tool(context: ToolContext, vuln_class: str = "") -> dict:
    if not vuln_class:
        return {"summary": f"{len(playbook.known_classes())} class(es) with a ladder",
                "data": {"classes": playbook.known_classes(),
                         "recon_ladder": playbook.recon_ladder()}}
    steps = playbook.ladder(vuln_class)
    if not steps:
        return {"ok": False, "error": "unknown-class",
                "summary": f"no ladder for {vuln_class!r}; known: {playbook.known_classes()}"}
    return {"summary": f"{vuln_class}: {len(steps)} step(s), skill {playbook.skill_for(vuln_class)}",
            "data": {"steps": steps, "skill": playbook.skill_for(vuln_class),
                     "proof_step": playbook.proof_step(vuln_class)},
            "output": "\n".join(f"{i+1}. {s['step']} [{s['tier']}] via {s['tool']} — {s['why']}"
                                for i, s in enumerate(steps))}


@SERVER.tool(
    "knowledge.proof_matrix",
    "Every class this system can prove, with the requirement and the required checks. The classes "
    "it refuses are listed too, with the reason.",
    {"properties": {}, "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def proof_matrix(context: ToolContext) -> dict:
    rows = []
    for name in matrix.classes():
        spec = matrix.spec_for(name)
        rows.append({"vuln_class": name, "kind": spec.kind, "severity": spec.severity,
                     "requirement": spec.requirement,
                     "required_checks": list(spec.required_checks),
                     "refusal": spec.refusal})
    return {"summary": f"{len(rows)} class(es) in the proof matrix",
            "data": {"classes": rows, "candidate_only": matrix.CANDIDATE_ONLY},
            "output": "\n".join(f"{r['vuln_class']:18} {r['kind']:18} {r['requirement']}"
                                for r in rows)}


@SERVER.tool(
    "knowledge.skills",
    "List the skills installed in this repository: the deeper methodology for one class or one "
    "activity. Open at most one depth skill at a time — the corpus is large, and opening it early "
    "both burns context and anchors the next hypothesis.",
    {"properties": {"query": {"type": "string"}}, "required": []},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def skills(context: ToolContext, query: str = "") -> dict:
    registry = read_json(config.SKILLS / "registry.json", {"skills": []})
    entries = registry.get("skills", [])
    if query:
        needle = query.lower()
        entries = [e for e in entries if needle in json.dumps(e, ensure_ascii=False).lower()]
    return {"summary": f"{len(entries)} skill(s)",
            "data": {"skills": entries},
            "output": "\n".join(f"{e['name']:28} {e.get('kind','') :10} {e.get('summary','')[:70]}"
                                for e in entries)}


@SERVER.tool(
    "knowledge.skill",
    "Read one skill in full: the written-down method for a class or an activity, including the "
    "shapes that look like a finding and are not. Open at most one depth skill at a time — the "
    "corpus is large, and opening it early both burns the context window and anchors the next "
    "hypothesis before the surface is mapped.",
    {"properties": {"name": {"type": "string"}}, "required": ["name"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def skill(context: ToolContext, name: str) -> dict:
    path = config.SKILLS / name / "SKILL.md"
    if not path.is_file():
        return {"ok": False, "error": "unknown-skill",
                "summary": f"no skill {name!r} at {path}"}
    text = path.read_text(encoding="utf-8")
    return {"summary": f"{name}: {len(text)} chars", "output": text[:40_000],
            "data": {"path": str(path)}}


@SERVER.tool(
    "knowledge.cve_lookup",
    "What this installation knows locally about a CVE or a product version: a registered exploit "
    "script, a matching nuclei template, or nothing. It reads files on disk and never the network — "
    "the advisory itself has to be read, and a browser MCP server is the honest route for that. "
    "Returns the preconditions already on file, because those are what usually exclude the instance "
    "in front of you.",
    {"properties": {"cve": {"type": "string", "description": "e.g. CVE-2021-41773"},
                    "product": {"type": "string", "description": "e.g. apache httpd, tomcat"},
                    "version": {"type": "string"}},
     "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def cve_lookup(context: ToolContext, cve: str = "", product: str = "", version: str = "") -> dict:
    needle = " ".join(part for part in (cve, product, version) if part).lower()
    if not needle:
        return {"ok": False, "error": "bad-arguments",
                "message": "give at least one of cve, product, version"}
    registry = read_json(config.EXPLOITS / "registry.json", {"scripts": []})
    scripts = [entry for entry in registry.get("scripts", [])
               if any(token in json.dumps(entry, ensure_ascii=False).lower()
                      for token in needle.split())]
    templates = _nuclei_templates(cve)
    guidance = [
        "A version match is a candidate, never a finding.",
        "Read the advisory's preconditions before probing: version range, configuration flag, "
        "module, authentication state, platform. They usually exclude this instance.",
        "Prove it under the class the CVE implies, with that class's requirement — not as a CVE id.",
    ]
    return {
        "summary": (f"{len(scripts)} registered script(s) and {len(templates)} nuclei template(s) "
                    f"match {needle!r}"),
        "result": "signal" if (scripts or templates) else "no-signal",
        "data": {"scripts": scripts, "nuclei_templates": templates[:20],
                 "preconditions_on_file": [p for entry in scripts
                                           for p in (entry.get("preconditions") or [])],
                 "guidance": guidance},
        "output": "\n".join([*(f"script: {entry['id']} proves {entry.get('vuln_class')} "
                               f"(tier {entry.get('tier')})" for entry in scripts),
                             *(f"template: {path}" for path in templates[:20])])
                  or "nothing on file locally",
        "next": ("run the registered script with exploit.run_script, after checking its "
                 "preconditions" if scripts else
                 "read the advisory through a browser MCP server, record its preconditions with "
                 "ledger.add_evidence kind=source, then check them with one probe each"),
    }


def _nuclei_templates(cve: str) -> list[str]:
    if not cve:
        return []
    from pathlib import Path
    roots = [Path.home() / ".local" / "nuclei-templates", Path.home() / "nuclei-templates",
             Path("/usr/share/nuclei-templates")]
    needle = cve.lower().replace("cve-", "")
    out = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob(f"*{needle}*"):
            out.append(str(path))
            if len(out) >= 40:
                return out
    return out


# ----------------------------------------------------------------------------
# 1. knowledge.chains
# ----------------------------------------------------------------------------


@SERVER.tool(
    "knowledge.chains",
    "List this system's own chain corpus: one card per confirmed finding that has been harvested, "
    "with the class, the stack markers the card needs and the entry-point shape. A card is "
    "experience about a shape, never evidence about a target, so nothing listed here can raise a "
    "grade. Cards the write path would now refuse are reported separately rather than hidden.",
    {"properties": {"vuln_class": {"type": "string",
                                   "description": "list only the cards for this class"}},
     "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def chains_list(context: ToolContext, vuln_class: str = "") -> dict:
    from ...knowledge import chains as corpus
    every = corpus.cards()
    rows = every
    if vuln_class:
        wanted = vuln_class.strip().lower()
        rows = [card for card in rows
                if str(card.get("vuln_class") or "").lower() == wanted]
    refused = corpus.audit()
    return {
        "summary": (f"{len(rows)} of {len(every)} card(s) in the argus corpus are {vuln_class}"
                    if vuln_class else f"{len(every)} card(s) in the argus corpus")
                   + (f"; {len(refused)} card(s) on disk would be refused by the write path"
                      if refused else ""),
        "result": "signal" if rows else "no-signal",
        "data": {"cards": [{"slug": card.get("slug"), "vuln_class": card.get("vuln_class"),
                            "title": card.get("title"),
                            "markers": (card.get("stack") or {}).get("markers"),
                            "entry_point": card.get("entry_point"),
                            "first_discriminating_probe": card.get("first_discriminating_probe")}
                           for card in rows],
                 "refused": refused, "corpus": str(corpus.CHAINS_DIR)},
        "output": "\n".join(
            f"{str(card.get('slug')):50} {str(card.get('vuln_class')):14} "
            f"{','.join((card.get('stack') or {}).get('markers') or [])}" for card in rows),
        "next": ("rank them against this target with knowledge.chain_match before probing "
                 "anything novel" if rows else
                 f"nothing on file for {vuln_class}, though the corpus holds {len(every)} card(s) "
                 f"for other classes: read the class ladder instead" if vuln_class and every else
                 "the corpus is empty: knowledge.chain_write fills it once a finding is confirmed"),
    }


# ----------------------------------------------------------------------------
# 2. knowledge.chain_write
# ----------------------------------------------------------------------------


@SERVER.tool(
    "knowledge.chain_write",
    "Write a chain card for every confirmed finding in this engagement that does not have one yet. "
    "A card records the stack it was found on, the entry-point shape, the ladder steps that "
    "actually fired, the probe that first discriminated, the proof shape that settled it and the "
    "blast radius of reusing it. It refuses to carry a hostname, an address, a credential, an "
    "extracted row, a flag, a nonce or the proof output, so it cannot be read as a shortcut past "
    "the class's requirement. A candidate finding gets no card, because the card would record the "
    "chain that did not settle.",
    {"properties": {}, "required": []}, tier=config.TIER_PASSIVE, touches_target=False,
)
def chain_write(context: ToolContext) -> dict:
    from ...knowledge import chains as corpus
    if not context.engagement:
        return {"ok": False, "error": "no-engagement",
                "message": "a card is harvested from an engagement's confirmed findings: pass "
                           "engagement=<name>, or set ARGUS_ENGAGEMENT"}
    result = corpus.harvest(context.engagement)
    return {
        "summary": f"{result['summary']} -> {result['corpus']}",
        "result": "signal" if result["written"] else "no-signal",
        "data": result,
        "output": "\n".join(
            [*(f"written {row['slug']} ({row['vuln_class']})" for row in result["written"]),
             *(f"skipped {row['finding']}: {row['why']}" for row in result["skipped"])]),
        "next": ("the corpus now covers these shapes, and knowledge.chain_match will rank them "
                 "against the next target of the same kind" if result["written"] else
                 "nothing new to write. A skip reading 'not-confirmed' is a finding whose last "
                 "check is still missing; one reading 'unmatchable' means the target was never "
                 "fingerprinted, so the card would have no marker to match on"),
    }


# ----------------------------------------------------------------------------
# 3. knowledge.chain_match — replaces the existing body
# ----------------------------------------------------------------------------


def _external_chains(stack: str, limit: int) -> tuple[list[dict], str]:
    """The optional CTF-toolkit corpus, scored by shared words.

    Kept separate from the argus corpus and labelled, because the two scores are
    not the same measurement: this one counts words that appear anywhere in the
    card, the other is the share of a card's declared stack markers the target
    has been observed to have. Merging them into one ranking would put a card
    with a long description above a card about the right product.
    """
    chains_dir = config.CTF_V2 / "knowledge" / "chains"
    if not chains_dir.is_dir():
        return [], str(chains_dir)
    words = {word for word in stack.lower().replace("/", " ").split() if len(word) > 2}
    scored = []
    for path in sorted(chains_dir.glob("*.json")):
        card = read_json(path, {})
        text = json.dumps(card, ensure_ascii=False).lower()
        score = sum(1 for word in words if word in text)
        if score:
            scored.append((score, {"corpus": "external", "card": path.name,
                                   "words_matched": score,
                                   "title": card.get("title") or card.get("name"),
                                   "vuln_class": card.get("bug_class") or card.get("class"),
                                   "preconditions": card.get("preconditions"),
                                   "first_confirming_probe": card.get("first_confirming_probe"),
                                   "verification": (card.get("verification") or {}).get("status")}))
    scored.sort(key=lambda pair: -pair[0])
    return [entry for _score, entry in scored[:limit]], str(chains_dir)


@SERVER.tool(
    "knowledge.chain_match",
    "Look for a chain already verified on a stack like this one, in two corpora: the cards this "
    "system harvested from its own confirmed findings, and the optional external CTF toolkit "
    "bridge. Every result says which corpus it came from, and the two scores are not comparable — "
    "an argus card scores the share of its own stack markers this target has been observed to "
    "have, the external one counts shared words. A match is a CANDIDATE either way: the "
    "preconditions are plain language, nothing checks them for you, and the class's proof "
    "requirement is unchanged. Read `unobserved` first: those are the markers the card needs that "
    "this target has not been seen to have, and any one of them absent kills the candidate for a "
    "single request.",
    {"properties": {"stack": {"type": "string", "description": "what the target runs, in words — "
                                                               "the Server header and the framework "
                                                               "markers are enough"},
                    "vuln_class": {"type": "string",
                                   "description": "rank only the cards for this class"},
                    "limit": {"type": "integer"}},
     "required": ["stack"]}, tier=config.TIER_PASSIVE, touches_target=False,
)
def chain_match(context: ToolContext, stack: str, vuln_class: str = "", limit: int = 5) -> dict:
    from ...knowledge import chains as corpus
    bound = max(1, min(int(limit or 5), 20))
    own = corpus.match(stack, class_hint=vuln_class or None, limit=bound)
    for entry in own:
        entry["corpus"] = "argus"
    external, bridge = _external_chains(stack, bound)
    candidates = [entry for entry in own if entry["candidate"]]
    return {
        "summary": (f"{len(candidates)} of {len(own)} argus card(s) share a marker with "
                    f"{stack!r}; {len(external)} external card(s) share a word"
                    if (own or external) else
                    f"no prior chain on file for {stack!r} in either corpus"),
        "result": "signal" if (candidates or external) else "no-signal",
        "data": {"stack_markers": corpus.markers_of(stack),
                 "argus": own, "external": external,
                 "corpora": {"argus": str(corpus.CHAINS_DIR), "external": bridge}},
        "output": "\n".join(
            [*(f"argus    {entry['score']:>5}  {entry['slug']}  needs {entry['unobserved']}"
               for entry in own),
             *(f"external {entry['words_matched']:>5}w {entry['card']}" for entry in external)]),
        "next": ("run the top card's first_discriminating_probe before anything novel, and kill it "
                 "on its unobserved markers first" if candidates else
                 "nothing comparable on file: measure it. The ladder for the class is the cheaper "
                 "route than a card that shares no marker"),
    }
