#!/usr/bin/env python3
"""Offline regression gate for the CTF solver system.

Run before accepting any change to this toolkit. Every check is offline: no
network, no live target, no challenge artifact is executed. The suite answers one
question — does the system still do what it did before the change?

Groups:
  A. structure     registry, index and router paths agree with what is on disk
  B. contract      PROMPT.md, CLAUDE.md and the control plane keep their shape
  C. routing       black-box and white-box classification golden cases
  D. dispatch      one router, no premature depth skill
  E. chain reuse   solved chains still match the evidence that produced them
  F. ledger        a parked hypothesis survives; a revived one comes back
  G. capability    counts never regress below test/baseline.json
"""
import contextlib
import io
import os
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ctf  # noqa: E402
from tools import state  # noqa: E402
from tools import chain_match, skill_select  # noqa: E402
from tools import classify as classifier  # noqa: E402
from tools import classify_solve  # noqa: E402
from tools import decide as decide_mod  # noqa: E402
from tools import hooks as hooks_mod  # noqa: E402
from tools import skill_audit  # noqa: E402
from tools import learning_report  # noqa: E402

CASES = ROOT / "test" / "cases"
BASELINE = ROOT / "test" / "baseline.json"
CONTROL_PLANE = [
    "CLAUDE.md", "PROMPT.md", "SKILL_GUIDE.md", "HYPOTHESIS_PROTOCOL.md",
    "EVIDENCE_POLICY.md", "README.md", "VERSIONING.md", "LEARNING_LOOP.md",
    "EXTERNAL_SOURCES.md",
    "skills/INDEX.md", "skills/LOOP_DISCIPLINE.md",
]
TAXONOMY = ROOT / "knowledge" / "bug-classes.json"
ENTRY_STATUS = re.compile(r"^- status: (?P<status>\w[\w-]*)\s*$", re.M)
ENTRY_HEAD = re.compile(r"^## (?P<anchor>\S+) · (?P<name>.+?) · (?P<status>\w[\w-]*)\s*$", re.M)
ROUTER_SKILLS = [
    "skills/ctf-playbook/SKILL.md", "skills/web-triage/SKILL.md",
    "skills/pwn-binary-triage/SKILL.md", "skills/rev-triage/SKILL.md",
    "skills/crypto-triage/SKILL.md", "skills/forensics-triage/SKILL.md",
    "skills/osint-triage/SKILL.md", "skills/ai-iot-triage/SKILL.md",
]
# Language detectors. The character classes are built from integer codepoints on
# purpose: this file is itself scanned by the whole-tree language check below, so
# it must stay pure ASCII. A literal character class here would make the detector
# trip over its own definition.
def _charclass(*spans):
    parts = []
    for span in spans:
        lo, hi = span if isinstance(span, tuple) else (span, span)
        parts.append(chr(lo) if lo == hi else "%s-%s" % (chr(lo), chr(hi)))
    return "[" + "".join(parts) + "]"


# Codepoints that essentially only Vietnamese uses: the six letter pairs it adds
# to the Latin alphabet (A-breve, D-stroke, I-tilde, U-tilde, O-horn, U-horn),
# the combining tone marks for decomposed text, and the whole Latin Extended
# Additional block, which carries every tone-marked Vietnamese vowel.
VN_ONLY = (0x0102, 0x0103, 0x0110, 0x0111, 0x0128, 0x0129, 0x0168, 0x0169,
           0x01A0, 0x01A1, 0x01AF, 0x01B0,
           (0x0300, 0x0303), 0x0309, 0x0323, (0x1EA0, 0x1EF9))
# Accented Latin vowels Vietnamese shares with Spanish, Portuguese and French.
# They are NOT in VN_ONLY: a Spanish search string inside an OSINT skill is data,
# not instruction, and must not fail the whole-tree check.
SHARED_ACCENTS = ((0x00C0, 0x00C3), (0x00C8, 0x00CA), 0x00CC, 0x00CD,
                  (0x00D2, 0x00D5), 0x00D9, 0x00DA, 0x00DD,
                  (0x00E0, 0x00E3), (0x00E8, 0x00EA), 0x00EC, 0x00ED,
                  (0x00F2, 0x00F5), 0x00F9, 0x00FA, 0x00FD)
VIETNAMESE_ONLY = re.compile(_charclass(*VN_ONLY))
# The control plane and the routers are held to the stricter bar: any accented
# Latin vowel in an instruction file means the English conversion is unfinished.
VIETNAMESE = re.compile(_charclass(*(SHARED_ACCENTS + VN_ONLY)))
# Cyrillic, Kana, CJK and Hangul. Their presence is either corrupted text or a
# deliberate data sample; a deliberate one must be declared in the allow list at
# test/gate-exemptions.json, with a reason.
FOREIGN_SCRIPT = re.compile(_charclass((0x0400, 0x04FF), (0x3040, 0x30FF),
                                       (0x4E00, 0x9FFF), (0xAC00, 0xD7AF)))
EXEMPTIONS = ROOT / "test" / "gate-exemptions.json"
# Tools and skills that were referenced in documentation but never existed.
PHANTOM = re.compile(r"solver/recognize\.py|credential-hygiene|external-recon/")
PROMPT_SECTIONS = ["## Context", "## Role", "## Goal", "## Instructions",
                   "## Constraints", "## Output Format", "## Examples"]



def exemptions():
    return json.loads(EXEMPTIONS.read_text(encoding="utf-8"))


def authored_files():
    """Every text file this repository authors, as pathlib paths.

    Handout source and test fixtures are excluded by prefix: they are inputs the
    system is measured against, not instructions it writes. The exclusion list
    lives in test/gate-exemptions.json so that widening it is a visible change.
    """
    rules = exemptions()
    suffixes = {s.lower() for s in rules["scan_suffixes"]}
    skipped = tuple(rules["skipped_prefixes"])
    found = []
    for root in rules["scan_roots"] + ["."]:
        base = (ROOT / root).resolve()
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*") if root != "." else base.glob("*")):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith(skipped) or "__pycache__" in rel or "/.git" in rel:
                continue
            found.append(path)
    return sorted(set(found))


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def load_cases(name):
    return json.loads((CASES / name).read_text(encoding="utf-8"))


def registry():
    return json.loads(read("skills/registry.json"))


def taxonomy():
    return json.loads(TAXONOMY.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- A
class StructureTests(unittest.TestCase):
    def test_router_skill_paths_in_ctf_py_exist(self):
        for path in ctf.SKILLS.values():
            self.assertTrue((ROOT / path).is_file(), path)

    def test_every_registry_path_exists(self):
        for skill in registry()["skills"]:
            self.assertTrue((ROOT / skill["path"]).is_file(),
                            "registry names a missing file: " + skill["path"])

    def test_every_skill_on_disk_is_registered(self):
        on_disk = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        registered = {s["id"] for s in registry()["skills"]}
        missing = sorted(on_disk - registered)
        self.assertEqual(missing, [], "skills on disk but absent from registry.json: %s" % missing)

    def test_registry_ids_unique_and_routes_resolve(self):
        skills = registry()["skills"]
        ids = [s["id"] for s in skills]
        self.assertEqual(len(ids), len(set(ids)), "duplicate skill id in registry")
        known = set(ids)
        for skill in skills:
            for target in skill.get("routes_to", []):
                self.assertIn(target, known,
                              "%s routes to unknown skill %s" % (skill["id"], target))

    def test_ctf_py_categories_have_a_router(self):
        routers = {}
        for skill in registry()["skills"]:
            if skill["layer"] == "router":
                for category in skill["categories"]:
                    routers[category] = skill["id"]
        for category in ctf.SKILLS:
            resolved = skill_select.CATEGORY_ALIAS.get(category, category)
            self.assertIn(resolved, routers,
                          "ctf.py routes category %r but no router declares it" % category)

    def test_index_only_names_paths_that_exist(self):
        text = read("skills/INDEX.md")
        for match in re.findall(r"`(skills/[A-Za-z0-9_./-]+\.md)`", text):
            self.assertTrue((ROOT / match).is_file(), "INDEX.md names a missing file: " + match)

    def test_load_policy_caps_are_present(self):
        policy = registry()["load_policy"]["max_open_at_once"]
        self.assertEqual(policy["router"], 1)
        self.assertEqual(policy["depth"], 1)


# --------------------------------------------------------------------------- B
class ContractTests(unittest.TestCase):
    def test_prompt_has_all_seven_sections(self):
        text = read("PROMPT.md")
        for section in PROMPT_SECTIONS:
            self.assertIn(section, text, "PROMPT.md lost the section " + section)

    def test_prompt_states_the_no_invention_rule(self):
        text = read("PROMPT.md").lower()
        self.assertIn("never invent", text)
        self.assertIn("unknown", text)

    def test_control_plane_and_routers_are_english(self):
        for rel in CONTROL_PLANE + ROUTER_SKILLS:
            text = read(rel)
            hits = VIETNAMESE.findall(text)
            self.assertEqual(hits, [], "%s still contains Vietnamese text: %r" % (rel, hits[:8]))

    def test_no_corrupted_foreign_script_anywhere_in_control_plane(self):
        for rel in CONTROL_PLANE + ROUTER_SKILLS:
            hits = FOREIGN_SCRIPT.findall(read(rel))
            self.assertEqual(hits, [], "%s contains characters from an unrelated script: %r"
                             % (rel, hits[:8]))

    def test_no_vietnamese_anywhere_in_the_authored_tree(self):
        """The whole tree, not only the control plane.

        A depth reference or a solved note in a second language is the same
        defect as a bilingual router: the agent reads it as instruction.
        """
        offenders = []
        for path in authored_files():
            hits = VIETNAMESE_ONLY.findall(path.read_text(encoding="utf-8"))
            if hits:
                offenders.append("%s %s" % (path.relative_to(ROOT).as_posix(),
                                            sorted(set(hits))[:6]))
        self.assertEqual(offenders, [], "Vietnamese text is still present in: %s" % offenders)

    def test_foreign_script_is_absent_or_declared_with_a_reason(self):
        declared = {}
        for entry in exemptions()["foreign_script"]:
            self.assertTrue((ROOT / entry["path"]).is_file(),
                            "the exemption list names a missing file: " + entry["path"])
            self.assertTrue(entry.get("reason", "").strip(),
                            "%s is exempted with no reason given" % entry["path"])
            declared[entry["path"]] = entry
        undeclared, unused = [], set(declared)
        for path in authored_files():
            rel = path.relative_to(ROOT).as_posix()
            if not FOREIGN_SCRIPT.search(path.read_text(encoding="utf-8")):
                continue
            unused.discard(rel)
            if rel not in declared:
                undeclared.append(rel)
        self.assertEqual(undeclared, [],
                         "Cyrillic, CJK, Kana or Hangul text that nothing declares: %s. "
                         "Remove it, or add an entry with a reason to "
                         "test/gate-exemptions.json." % undeclared)
        self.assertEqual(sorted(unused), [],
                         "test/gate-exemptions.json exempts files that no longer need it: %s"
                         % sorted(unused))

    def test_every_reference_a_skill_names_resolves(self):
        """A SKILL.md that names a file which is not there sends the agent nowhere.

        This is the check that would have caught the 155 reference files that
        were named by skills but absent from the tree.
        """
        exempt = set()
        for entry in exemptions()["reference_links"]:
            self.assertTrue(entry.get("reason", "").strip(),
                            "%s is exempted with no reason given" % entry["path"])
            exempt.add((entry["path"], entry["target"]))
        link = re.compile(r"`([A-Za-z0-9_./-]+\.md)`")
        broken = []
        for skill in sorted((ROOT / "skills").rglob("*.md")):
            rel = skill.relative_to(ROOT).as_posix()
            for target in link.findall(skill.read_text(encoding="utf-8")):
                if (rel, target) in exempt:
                    continue
                candidates = [skill.parent / target, ROOT / target]
                if not any(c.is_file() for c in candidates):
                    broken.append("%s -> %s" % (rel, target))
        self.assertEqual(broken, [],
                         "a skill names a reference file that does not exist: %s" % broken)

    def test_no_command_hardcodes_a_tree_root(self):
        """The tree has to work wherever it is checked out.

        Ninety-nine commands used to name a home-relative tree root that was not
        where this tree actually sat. An agent that copies such a line runs a
        different tree, or nothing at all. The literal pattern is not spelled out
        here, for the same reason the language classes above are not: this file is
        scanned by its own check. Paths under the challenges directory are exempt,
        being historical records of where handout source sat at solve time.
        """
        rooted = re.compile(r"~/ctf(?:-v[0-9]+)?/(?!challenges/)[A-Za-z0-9_./-]*")
        allowed = {}
        for entry in exemptions()["tree_root_mentions"]:
            self.assertTrue(entry.get("reason", "").strip(),
                            "%s is exempted with no reason given" % entry["path"])
            allowed[entry["path"]] = entry
        offenders = []
        for path in authored_files():
            rel = path.relative_to(ROOT).as_posix()
            if rel in allowed:
                continue
            hits = rooted.findall(path.read_text(encoding="utf-8"))
            if hits:
                offenders.append("%s %s" % (rel, sorted(set(hits))[:4]))
        self.assertEqual(offenders, [],
                         "a hardcoded tree root would break this tree anywhere else: %s"
                         % offenders)

    def test_scope_boundary_holds(self):
        """No machine, Active Directory or cross-toolkit methodology in this tree.

        tools/check_boundary.py existed for this and was wired into nothing, so it
        sat failing: an Active Directory tooling section had reached the entry
        skill's own reference file. It is a required gate step now, and this test
        means a change cannot pass by quietly unwiring it.
        """
        import subprocess
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "check_boundary.py")],
                                cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout[-800:])

    def test_no_phantom_tool_references(self):
        for path in list((ROOT / "skills").rglob("*.md")) + [ROOT / rel for rel in CONTROL_PLANE]:
            hits = PHANTOM.findall(path.read_text(encoding="utf-8"))
            self.assertEqual(hits, [], "%s references a tool that does not exist: %r"
                             % (path.relative_to(ROOT), hits[:4]))

    def test_every_tool_is_named_somewhere(self):
        """The reverse of the check below: no tool may sit in tools/ unreferenced.

        Five did. Two of them mattered - the generator behind every chain card, and
        the rebuild half of a two-part index whose query half was documented - and
        one was challenge scratch carrying a hardcoded lab token.
        """
        docs = []
        for path in authored_files():
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith("tools/"):
                continue
            docs.append(path.read_text(encoding="utf-8"))
        blob = "\n".join(docs)
        orphans = []
        for tool in sorted((ROOT / "tools").glob("*.py")):
            if tool.name == "__init__.py":
                continue
            stem = tool.stem
            if tool.name in blob or ("tools." + stem) in blob or ("import " + stem) in blob:
                continue
            # a tool may still be reached only by another tool; that counts
            siblings = "\n".join(p.read_text(encoding="utf-8")
                                  for p in (ROOT / "tools").glob("*.py") if p != tool)
            if tool.name in siblings:
                continue
            orphans.append(tool.name)
        self.assertEqual(orphans, [],
                         "tools that no document, test or other tool names: %s. "
                         "Document it, wire it in, or delete it." % orphans)

    def test_claude_code_wiring_is_intact(self):
        """One tree, two agents.

        Claude Code discovers skills only under .claude/skills and reads only
        CLAUDE.md; opencode reads AGENTS.md and the plain skills directory. The
        wiring that serves both is three pieces, and losing any one of them makes
        every skill invisible from Claude Code with no error message.
        """
        link = ROOT / ".claude" / "skills"
        self.assertTrue(link.is_symlink(),
                        ".claude/skills must be a symlink, not a copy: a copy drifts")
        self.assertEqual(os.readlink(str(link)), "../skills",
                         "the symlink must stay relative so the tree can move")
        self.assertTrue(link.is_dir(), ".claude/skills is a broken symlink")

        on_disk = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        via_link = {p.parent.name for p in link.glob("*/SKILL.md")}
        self.assertEqual(on_disk, via_link,
                         "skills not reachable from Claude Code: %s" % sorted(on_disk - via_link))

        self.assertIn("@AGENTS.md", read("CLAUDE.md"),
                      "CLAUDE.md must import AGENTS.md: Claude Code never reads AGENTS.md itself")

    def test_every_skill_declares_a_name_and_description(self):
        """Claude Code decides whether to load a skill from its description."""
        bad = []
        for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
            text = skill.read_text(encoding="utf-8")
            if not text.startswith("---"):
                bad.append("%s: no frontmatter" % skill.parent.name)
                continue
            front = text.split("---", 2)[1]
            for key in ("name:", "description:"):
                if not re.search(r"^%s" % re.escape(key), front, re.M):
                    bad.append("%s: missing %s" % (skill.parent.name, key))
        self.assertEqual(bad, [], "skills Claude Code cannot route to: %s" % bad)

    def test_slash_commands_only_name_real_tools(self):
        """A command that names a missing tool fails in front of the user."""
        commands = sorted((ROOT / ".claude" / "commands").glob("*.md"))
        self.assertTrue(commands, ".claude/commands is empty")
        broken = []
        for command in commands:
            text = command.read_text(encoding="utf-8")
            for target in re.findall(r"\b((?:tools|test|scripts|build)/[a-z_]+\.(?:py|sh))", text):
                if not (ROOT / target).is_file():
                    broken.append("%s -> %s" % (command.name, target))
            for target in re.findall(r"\b(selfcheck\.py|ctf\.py)\b", text):
                if not (ROOT / target).is_file():
                    broken.append("%s -> %s" % (command.name, target))
        self.assertEqual(broken, [], "slash commands naming missing files: %s" % broken)

    def test_documented_tools_exist(self):
        for rel in CONTROL_PLANE:
            for match in re.findall(r"`?(tools/[a-z_]+\.py)`?", read(rel)):
                self.assertTrue((ROOT / match).is_file(), "%s names a missing tool: %s" % (rel, match))

    def test_claude_md_and_prompt_agree_on_scope(self):
        claude = read("CLAUDE.md").lower()
        self.assertIn("security-toolkit", claude, "CLAUDE.md must restate the scope boundary")
        self.assertIn("hypothesis_protocol.md", claude)
        self.assertIn("prompt.md", claude)

    def test_low_reliability_agent_protocol_is_documented(self):
        agents = read("AGENTS.md")
        prompt = read("PROMPT.md")
        for marker in ("Low-reliability agent protocol", "read its complete JSON output",
                       "run `tools/decide.py` after every", "post-probe", "stop_report"):
            self.assertIn(marker, agents, "AGENTS.md lost reliability marker: " + marker)
        for marker in ("Reliable execution mode", "classify -> dispatch -> chain_match",
                       "recorded as `inconclusive`"):
            self.assertIn(marker, prompt, "PROMPT.md lost reliability marker: " + marker)

    def test_ai_role_and_checkpoint_discipline_is_documented(self):
        agents = read("AGENTS.md")
        training = read("TRAINING.md")
        for marker in ("AI role discipline", "reader", "writer", "hypothesizer",
                       "the agent proposes; the machine verifies", "After four tool calls"):
            self.assertIn(marker, agents, "AGENTS.md lost AI discipline marker: " + marker)
        for marker in ("Tool layers and permissions", "Harness and replay validation",
                       "Preserve it verbatim", "After four tool calls"):
            self.assertIn(marker, training, "TRAINING.md lost training marker: " + marker)


# --------------------------------------------------------------------------- C
WEATHER = ROOT / "challenges/Weather App/web_weather_app/challenge"


@unittest.skipUnless(WEATHER.is_dir(),
                     "white-box fixture absent; force-add it with: git add -f 'challenges/Weather App'")
class WhiteboxFixtureTests(unittest.TestCase):
    def test_whitebox_source_scan_finds_sinks_and_flag(self):
        result = ctf.source_route(str(WEATHER))
        self.assertEqual(result["mode"], "whitebox")
        signals = {item["signal"] for item in result["findings"]}
        self.assertIn("SSRF candidate", signals)
        self.assertIn("SQL injection", signals)
        self.assertTrue(any(item["value"].startswith("HTB{") for item in result["flags"]))

    def test_weather_chain_source_contract(self):
        routes = (WEATHER / "routes/index.js").read_text()
        self.assertRegex(routes, r"/register")
        self.assertIn("remoteAddress", routes)
        self.assertIn("/api/weather", routes)
        self.assertIn("http://${endpoint}", (WEATHER / "helpers/WeatherHelper.js").read_text())
        self.assertIn("INSERT INTO users", (WEATHER / "database.js").read_text())
        self.assertIn("ON CONFLICT", read("solved/weather_app.md"))


class RoutingTests(unittest.TestCase):
    def test_golden_routing_cases(self):
        for case in load_cases("routing.json")["cases"]:
            with self.subTest(text=case["text"]):
                route = ctf.observation_route(case["text"]).get("route") or {}
                self.assertEqual(route.get("category"), case["category"],
                                 "origin: " + case.get("origin", "unknown"))



# --------------------------------------------------------------------------- D
class DispatchTests(unittest.TestCase):
    def run_select(self, case):
        reg = registry()
        if "source" in case:
            target = str(ROOT / case["source"])
            text = skill_select.collect_text(target)
            routed = ctf.source_route(target)
            counts = {}
            for finding in routed["findings"]:
                counts[finding["category"]] = counts.get(finding["category"], 0) + 1
            category = max(counts, key=counts.get) if counts else "unknown"
            return skill_select.select(text, category, reg, True)
        text = case["observation"]
        raw = (ctf.observation_route(text).get("route") or {}).get("category")
        category = skill_select.CATEGORY_ALIAS.get(raw, raw) or "unknown"
        return skill_select.select(text, category, reg, False)

    def test_exactly_one_router_and_the_expected_one(self):
        for case in load_cases("dispatch.json")["skill_select"]:
            with self.subTest(case=case.get("observation") or case.get("source")):
                result = self.run_select(case)
                self.assertEqual(result["problems"], [])
                routers = [item for item in result["open_now"] if item["layer"] == "router"]
                self.assertEqual(len(routers), 1, "a dispatch must open exactly one router")
                self.assertEqual(routers[0]["id"], case["expect_router"],
                                 "origin: " + case.get("origin", "unknown"))

    def test_forbidden_skills_are_never_opened(self):
        for case in load_cases("dispatch.json")["skill_select"]:
            with self.subTest(case=case.get("observation") or case.get("source")):
                result = self.run_select(case)
                opened = {item["id"] for item in result["open_now"]}
                if result["depth_candidate"]:
                    opened.add(result["depth_candidate"]["id"])
                for forbidden in case["forbid_open"]:
                    self.assertNotIn(forbidden, opened,
                                     "%s must not be opened for this input" % forbidden)

    def test_entry_skill_is_always_offered(self):
        result = self.run_select({"observation": "something entirely unclassifiable"})
        self.assertEqual(result["open_now"][0]["id"], "ctf-playbook")

    def test_unclassified_input_is_reported_not_guessed(self):
        result = self.run_select({"observation": "zzzz qqqq"})
        self.assertFalse(result["classified"])
        self.assertIsNone(result["depth_candidate"])

    def test_large_depth_skills_stay_behind_a_manual_gate(self):
        reg = registry()
        for skill in reg["skills"]:
            if skill["id"].startswith("ctf-") and skill["layer"] == "depth":
                self.assertIn("manual_gate", skill,
                              "%s is a large corpus and needs a manual gate" % skill["id"])


# --------------------------------------------------------------------------- E
class ChainReuseTests(unittest.TestCase):
    def test_every_chain_card_is_well_formed(self):
        cards = chain_match.load_chains()
        self.assertTrue(cards, "no chain cards found")
        for card in cards:
            self.assertNotIn("_error", card, "unparseable chain card: %s" % card.get("_path"))
            for field in ("id", "source_note", "challenge", "preconditions", "signals",
                          "chain", "first_confirming_probe", "blast_radius", "verification"):
                self.assertIn(field, card, "%s is missing %s" % (card.get("id"), field))
            self.assertTrue((ROOT / card["source_note"]).is_file(),
                            "%s points at a missing note" % card["id"])
            self.assertTrue(card["signals"], "%s has no signals to match on" % card["id"])
            self.assertIn(card["verification"]["status"],
                          ("verified_live", "writeup-claimed", "unverified"))

    def test_chain_cards_carry_no_flags(self):
        for card in chain_match.load_chains():
            blob = json.dumps(card, ensure_ascii=False)
            self.assertIsNone(card.get("flag"), "%s must not store a flag" % card["id"])
            self.assertNotRegex(blob, r"[A-Za-z][A-Za-z0-9_-]{1,32}\{[^\r\n}]{6,}\}",
                                "%s contains a flag-shaped string" % card["id"])

    def test_golden_chain_matches(self):
        for case in load_cases("dispatch.json")["chain_match"]:
            label = case.get("observation") or case.get("source")
            with self.subTest(case=label):
                if "source" in case:
                    text = chain_match.read_source(str(ROOT / case["source"]))
                else:
                    text = case["observation"]
                lowered = text.lower()
                scored = []
                for card in chain_match.load_chains():
                    result = chain_match.score_card(card, text, lowered)
                    if result and result["signal_coverage"] >= 0.15:
                        scored.append(result)
                scored.sort(key=lambda item: (-item["match_confidence"], item["id"]))
                top = scored[0]["id"] if scored else None
                self.assertEqual(top, case["expect_chain"], "origin: " + case.get("origin", ""))

    def test_a_match_is_never_reported_as_proof(self):
        for card in chain_match.load_chains():
            text = " ".join(card["signals"])
            result = chain_match.score_card(card, text, text.lower())
            self.assertEqual(result["status"], "candidate")
            self.assertLessEqual(result["match_confidence"], 0.95)
            self.assertIn("preconditions_to_confirm", result)


# --------------------------------------------------------------------------- F
class LedgerTests(unittest.TestCase):
    def ledger(self, root, *args):
        with patch.object(state, "ROOT", str(root)), patch.object(sys, "argv", ["state", *args]), \
                contextlib.redirect_stdout(io.StringIO()):
            state.main()

    def test_parking_keeps_the_branch_open(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            (root / "challenges").mkdir()
            self.ledger(root, "sample", "--hypothesis", "old path", "--bug-class", "web-ssti")
            data = json.loads((root / "challenges/sample/state.json").read_text())
            hid = data["hypotheses"][0]["id"]
            self.assertEqual(data["hypotheses"][0]["priority"], state.DEFAULT_PRIORITY)
            self.ledger(root, "sample", "--hypothesis-id", hid, "--deprioritize", "operator redirect")
            data = json.loads((root / "challenges/sample/state.json").read_text())
            self.assertEqual(len(data["hypotheses"]), 1)
            self.assertEqual(data["hypotheses"][0]["priority"], 0)
            self.assertEqual(data["hypotheses"][0]["status"], "open")
            self.assertEqual(data["hypotheses"][0]["deprioritized_reason"], "operator redirect")

    def test_a_parked_branch_can_be_revived(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            (root / "challenges").mkdir()
            self.ledger(root, "sample", "--hypothesis", "parked path", "--bug-class", "web-ssti")
            path = root / "challenges/sample/state.json"
            hid = json.loads(path.read_text())["hypotheses"][0]["id"]
            self.ledger(root, "sample", "--hypothesis-id", hid, "--deprioritize", "no new signal")
            self.ledger(root, "sample", "--hypothesis-id", hid, "--revive", "new evidence appeared")
            revived = json.loads(path.read_text())["hypotheses"][0]
            self.assertEqual(revived["status"], "open")
            self.assertEqual(revived["priority"], state.REVIVE_PRIORITY)
            self.assertEqual(revived["revived_reason"], "new evidence appeared")
            self.assertNotIn("deprioritized_reason", revived)
            self.assertTrue(revived["history"], "revival must be recorded in history")

    def test_protocol_documents_the_parking_commands(self):
        text = read("HYPOTHESIS_PROTOCOL.md")
        for flag in ("--deprioritize", "--revive", "--show"):
            self.assertIn(flag, text, "HYPOTHESIS_PROTOCOL.md must document " + flag)


# --------------------------------------------------------------------------- H
class TaxonomyTests(unittest.TestCase):
    """The bug-class taxonomy, the skills it names, and the classifier that uses it."""

    def test_every_class_has_a_skill_and_field_notes(self):
        for cls in taxonomy()["classes"]:
            with self.subTest(cls=cls["id"]):
                self.assertTrue((ROOT / cls["skill"]).is_file(),
                                "class %s names a missing skill: %s" % (cls["id"], cls["skill"]))
                notes = ROOT / "skills" / cls["skill_dir"] / "field-notes.md"
                self.assertTrue(notes.is_file(),
                                "class %s has no field-notes.md" % cls["id"])

    def test_evidence_level_is_declared_and_matches_the_skill(self):
        for cls in taxonomy()["classes"]:
            with self.subTest(cls=cls["id"]):
                text = (ROOT / cls["skill"]).read_text(encoding="utf-8")
                self.assertIn("evidence_level: %s" % cls["evidence_level"], text,
                              "%s does not declare its evidence level" % cls["skill"])

    def test_verified_classes_name_chain_cards_that_exist(self):
        available = {c["id"] for c in chain_match.load_chains() if "_error" not in c}
        for cls in taxonomy()["classes"]:
            with self.subTest(cls=cls["id"]):
                if cls["evidence_level"] == "verified":
                    self.assertTrue(cls["verified_by"],
                                    "%s is verified with no chain card" % cls["id"])
                    for chain_id in cls["verified_by"]:
                        self.assertIn(chain_id, available,
                                      "%s names a chain card that does not exist: %s"
                                      % (cls["id"], chain_id))
                else:
                    self.assertEqual(cls["verified_by"], [],
                                     "%s is catalogue but names chain cards" % cls["id"])

    def test_catalogue_skills_say_they_are_catalogue(self):
        for cls in taxonomy()["classes"]:
            if cls["evidence_level"] != "catalogue":
                continue
            with self.subTest(cls=cls["id"]):
                text = (ROOT / cls["skill"]).read_text(encoding="utf-8")
                self.assertIn("Catalogue class", text,
                              "%s must state plainly that nothing here has solved one" % cls["skill"])

    def test_every_class_is_registered(self):
        registered = {entry["id"] for entry in registry()["skills"]}
        for cls in taxonomy()["classes"]:
            self.assertIn(cls["id"], registered,
                          "class %s is not in skills/registry.json" % cls["id"])

    def test_every_signal_compiles(self):
        for cls in taxonomy()["classes"]:
            for field in ("observation_signals", "source_signals"):
                for raw in cls.get(field, []):
                    with self.subTest(cls=cls["id"], signal=raw):
                        re.compile(raw, re.I)

    def test_every_class_has_a_probe_and_a_falsifier(self):
        for cls in taxonomy()["classes"]:
            with self.subTest(cls=cls["id"]):
                self.assertTrue(cls["first_probe"].strip())
                self.assertTrue(cls["falsifier"].strip())
                self.assertGreaterEqual(len(cls.get("observation_signals", [])), 1)

    def test_depth_refs_exist(self):
        for cls in taxonomy()["classes"]:
            for ref in cls.get("depth_refs", []):
                with self.subTest(cls=cls["id"], ref=ref):
                    self.assertTrue((ROOT / ref).is_file(),
                                    "%s points at a missing file: %s" % (cls["id"], ref))


# --------------------------------------------------------------------------- I
class ClassifierTests(unittest.TestCase):
    @staticmethod
    def run_case(case, classes):
        if "source" in case:
            target = str(ROOT / case["source"])
            hits = classifier.scan_source(target, classifier.compile_signals(classes, "source_signals"))
        else:
            hits = classifier.scan_text(case["observation"],
                                        classifier.compile_signals(classes, "observation_signals"))
        return classifier.rank(hits, classes)

    def test_golden_observations(self):
        classes = taxonomy()["classes"]
        for case in load_cases("classify.json")["cases"]:
            with self.subTest(case=case["observation"][:48]):
                ranked = self.run_case(case, classes)
                names = [item["class"] for item in ranked]
                if case.get("expect_top"):
                    self.assertTrue(names, "no candidate at all; origin: " + case["origin"])
                    self.assertEqual(names[0], case["expect_top"], "origin: " + case["origin"])
                if case.get("expect_within"):
                    want = case["expect_within"]
                    self.assertIn(want["class"], names[: want["n"]], "origin: " + case["origin"])

    def test_golden_sources(self):
        classes = taxonomy()["classes"]
        for case in load_cases("classify.json")["source_cases"]:
            with self.subTest(case=case["source"]):
                ranked = self.run_case(case, classes)
                names = [item["class"] for item in ranked]
                if case.get("expect_none"):
                    self.assertEqual(names, [],
                                     "a signal is too broad: %s matched an ordinary app. %s"
                                     % (names, case["origin"]))
                if case.get("expect_within"):
                    want = case["expect_within"]
                    self.assertIn(want["class"], names[: want["n"]], "origin: " + case["origin"])
                for want in case.get("also_within", []):
                    self.assertIn(want["class"], names[: want["n"]], "origin: " + case["origin"])

    def test_a_class_is_reported_as_candidate_never_finding(self):
        classes = taxonomy()["classes"]
        ranked = self.run_case({"observation": "sql union select order by sqlite"}, classes)
        self.assertTrue(ranked)
        for item in ranked:
            self.assertEqual(item["status"], "candidate")
            self.assertTrue(item["first_probe"])
            self.assertTrue(item["falsifier"])


# --------------------------------------------------------------------------- J
class LearningLoopTests(unittest.TestCase):
    def test_field_note_entries_use_only_known_statuses(self):
        for cls in taxonomy()["classes"]:
            path = ROOT / "skills" / cls["skill_dir"] / "field-notes.md"
            text = path.read_text(encoding="utf-8")
            for match in ENTRY_HEAD.finditer(text):
                with self.subTest(cls=cls["id"], anchor=match.group("anchor")):
                    self.assertIn(match.group("status"), ("proposed", "confirmed"),
                                  "unknown status in %s" % path.relative_to(ROOT))
            for match in ENTRY_STATUS.finditer(text):
                self.assertIn(match.group("status"), ("proposed", "confirmed"))

    def test_field_notes_cite_a_chain_card_that_exists(self):
        available = {c["id"] for c in chain_match.load_chains() if "_error" not in c}
        pattern = re.compile(r"- chain card: `knowledge/chains/(?P<id>[a-z0-9-]+)\.json`")
        for cls in taxonomy()["classes"]:
            path = ROOT / "skills" / cls["skill_dir"] / "field-notes.md"
            for match in pattern.finditer(path.read_text(encoding="utf-8")):
                with self.subTest(cls=cls["id"]):
                    self.assertIn(match.group("id"), available,
                                  "field note cites a chain card that does not exist")

    def test_the_loop_is_documented(self):
        text = read("LEARNING_LOOP.md")
        for token in ("classify_solve.py", "--review", "--confirm", "proposed", "confirmed",
                      "catalogue", "verified"):
            self.assertIn(token, text, "LEARNING_LOOP.md must document " + token)

    def test_classify_solve_refuses_to_guess_on_a_tie(self):
        source = (ROOT / "tools" / "classify_solve.py").read_text(encoding="utf-8")
        self.assertIn("the evidence does not decide between these classes", source,
                      "a tie must be reported, never resolved by sort order")


# --------------------------------------------------------------------------- G
class CapabilityTests(unittest.TestCase):
    @staticmethod
    def measure():
        reg = registry()
        routing = load_cases("routing.json")["cases"]
        correct = sum(1 for case in routing
                      if (ctf.observation_route(case["text"]).get("route") or {}).get("category")
                      == case["category"])
        tax = taxonomy()
        proposed = confirmed = 0
        for cls in tax["classes"]:
            notes = ROOT / "skills" / cls["skill_dir"] / "field-notes.md"
            if notes.is_file():
                text = notes.read_text(encoding="utf-8")
                proposed += len(re.findall(r"^- status: proposed$", text, re.M))
                confirmed += len(re.findall(r"^- status: confirmed$", text, re.M))
        return {
            "skills_registered": len(reg["skills"]),
            "bug_classes": len(tax["classes"]),
            "bug_classes_verified": sum(1 for c in tax["classes"]
                                        if c["evidence_level"] == "verified"),
            "field_notes_total": proposed + confirmed,
            "field_notes_confirmed": confirmed,
            "routers": sum(1 for s in reg["skills"] if s["layer"] == "router"),
            "chain_cards": len([c for c in chain_match.load_chains() if "_error" not in c]),
            "routing_cases": len(routing),
            "routing_correct": correct,
            "solved_notes": len(list((ROOT / "solved").glob("*.md"))),
        }

    def test_capability_never_regresses(self):
        if not BASELINE.is_file():
            self.skipTest("no baseline recorded yet; run test/capability_report.py --write")
        baseline = json.loads(BASELINE.read_text(encoding="utf-8"))["metrics"]
        current = self.measure()
        for key, floor in baseline.items():
            self.assertGreaterEqual(current.get(key, -1), floor,
                                    "%s regressed: %s < %s (baseline)" % (key, current.get(key), floor))

    def test_capability_report_runs_and_emits_json(self):
        """The update gate calls this script; a crash there used to be invisible.

        test/run_all.sh reported PASS while the snapshot step raised
        ModuleNotFoundError, because its exit status was never checked. Both ends
        are fixed now, and this test keeps the script itself honest.
        """
        import subprocess
        result = subprocess.run([sys.executable, str(ROOT / "test" / "capability_report.py")],
                                cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0,
                         "capability_report.py failed: %s" % result.stderr[-600:])
        payload = json.loads(result.stdout)
        self.assertIn("metrics", payload)
        self.assertIn("routing_cases", payload["metrics"])

    def test_the_gate_script_checks_every_required_step(self):
        """Every REQUIRED step in run_all.sh must set the failure flag."""
        script = read("test/run_all.sh")
        required = re.findall(r'^hr "REQUIRED:[^"]*"\n(.*)$', script, re.M)
        self.assertTrue(required, "run_all.sh declares no required steps")
        for command in required:
            self.assertIn("fail=1", command,
                          "a REQUIRED step in run_all.sh ignores its exit status: %s" % command)

    def test_system_evaluation_is_wired_into_the_gate(self):
        script = read("test/run_all.sh")
        self.assertIn("tools/system_eval.py", script)
        self.assertIn("end-to-end offline system evaluation", script)

    def test_system_evaluation_cases_are_well_formed(self):
        payload = json.loads((CASES / "system_eval.json").read_text(encoding="utf-8"))
        self.assertTrue(payload["classification"])
        self.assertTrue(payload["routing"])
        self.assertTrue(payload["decisions"])
        for case in payload["classification"]:
            for key in ("id", "observation", "expect_top"):
                self.assertIn(key, case)
        for case in payload["routing"]:
            self.assertIn("category", case)
        for case in payload["decisions"]:
            self.assertIn("state", case)
            self.assertIn("action", case)
        for case in payload.get("evidence_policy", []):
            self.assertIn(case["evidence_kind"], ("surface", "class", "impact", "transport"))
            self.assertIn(case["verdict"], ("confirms", "falsifies", "inconclusive"))

    def test_learning_report_is_read_only_and_complete(self):
        payload = learning_report.report()
        self.assertIn("summary", payload)
        self.assertIn("review_queue", payload)
        self.assertEqual(payload["summary"]["field_notes"],
                         payload["summary"]["proposed_notes"] +
                         payload["summary"]["confirmed_notes"])
        self.assertEqual(len(payload["classes"]), len(taxonomy()["classes"]))

    def test_routing_cases_all_pass(self):
        current = self.measure()
        self.assertEqual(current["routing_correct"], current["routing_cases"])


# --------------------------------------------------------------------------- I
class OrchestratorTests(unittest.TestCase):
    """decide.py and hooks.py: the external decision controller and its gates."""

    TAXONOMY = {"classes": [
        {"id": "web-ssti", "first_probe": "an arithmetic marker in the template value"},
        {"id": "web-ssrf", "first_probe": "one address you control, then an internal-only address"},
    ]}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self._tmp.name)
        (self.root / "challenges").mkdir()
        (self.root / "knowledge").mkdir()
        (self.root / "knowledge" / "bug-classes.json").write_text(
            json.dumps(self.TAXONOMY), encoding="utf-8")
        self.patchers = [
            patch.object(decide_mod, "ROOT", str(self.root)),
            patch.object(decide_mod.state_mod, "ROOT", str(self.root)),
            patch.object(hooks_mod.state_mod, "ROOT", str(self.root)),
        ]
        for patcher in self.patchers:
            patcher.start()
        for patcher in reversed(self.patchers):
            self.addCleanup(patcher.stop)

    def write_state(self, name, data):
        directory = self.root / "challenges" / name
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "state.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def read_state(self, name):
        return json.loads((self.root / "challenges" / name
                           / "state.json").read_text(encoding="utf-8"))

    def hooks(self, *argv):
        with contextlib.redirect_stdout(io.StringIO()):
            return hooks_mod.main(list(argv))

    def test_decide_requires_evidence_for_a_flag(self):
        self.write_state("t1", {"hypotheses": [], "probes": [],
                                "flag": {"value": "HTB{x}", "source": "guess"}})
        self.assertEqual(decide_mod.decide("t1")["action"], "verify_flag")
        self.write_state("t1", {"hypotheses": [], "probes": [],
                                "flag": {"value": "HTB{x}",
                                         "source": "live-response",
                                         "evidence": "response body carried the flag"}})
        self.assertEqual(decide_mod.decide("t1")["action"], "record_solve")

    def test_decide_reopens_an_unsupported_confirmation(self):
        self.write_state("t2", {"hypotheses": [
            {"id": "h1", "name": "ssti", "status": "confirmed",
             "priority": 50, "time": 1, "bug_class": "web-ssti"}],
            "probes": []})
        decision = decide_mod.decide("t2")
        self.assertEqual(decision["action"], "reopen_confirm")
        self.assertIn("--hypothesis-id h1", " ".join(decision["commands"]))

    def test_decide_switches_class_when_budget_is_exhausted(self):
        probes = [{"request": "GET /?p=%d" % i, "result": "inconclusive",
                   "time": 1000.0 + i, "verdict": "inconclusive",
                   "class": "web-ssti"} for i in range(5)]
        self.write_state("t3", {
            "hypotheses": [{"id": "h1", "name": "ssti", "status": "open", "bug_class": "web-ssti",
                            "priority": 50, "time": 1000.0}],
            "probes": probes, "classes_considered": ["web-ssti", "web-ssrf"]})
        decision = decide_mod.decide("t3", now=1000.0 + 60)
        self.assertEqual(decision["action"], "switch_class")
        self.assertTrue(any("deprioritize" in command
                            for command in decision["commands"]))
        self.assertEqual(decision["next_probe"]["class"], "web-ssrf")

    def test_decide_prefers_an_unprobed_chain_card(self):
        self.write_state("t4", {
            "hypotheses": [{"id": "h1", "name": "fresh idea", "status": "open",
                            "priority": 50, "time": 1, "bug_class": "web-ssti"}],
            "probes": [],
            "chain_candidates": [{"id": "card-1",
                                  "first_confirming_probe": "the card probe"}]})
        decision = decide_mod.decide("t4")
        self.assertEqual(decision["action"], "run_probe")
        self.assertEqual(decision["next_probe"]["chain_card"], "card-1")

    def test_decide_classifies_before_probing_an_empty_state(self):
        self.write_state("t5", {"hypotheses": [], "probes": []})
        self.assertEqual(decide_mod.decide("t5")["action"], "new_hypothesis")

    def test_hooks_reject_evidence_free_confirmations(self):
        self.write_state("t6", {"hypotheses": [{"id": "h1", "name": "ssti",
                                                  "status": "open", "bug_class": "web-ssti"}], "probes": []})
        self.assertEqual(self.hooks("post-probe", "t6", "--request", "GET /a",
                                    "--verdict", "confirms"), 2)
        self.assertEqual(self.hooks("post-probe", "t6", "--request", "GET /b",
                                    "--verdict", "confirms",
                                    "--evidence", "timed out after 30s"), 2)
        self.assertEqual(self.hooks("post-probe", "t6", "--request", "GET /c",
                                    "--verdict", "confirms",
                                    "--evidence", "49 appeared in the page",
                                    "--evidence-kind", "class",
                                    "--hypothesis-id", "h1", "--class", "web-ssti"), 0)
        recorded = self.read_state("t6")["probes"][-1]
        self.assertEqual(recorded["verdict"], "confirms")
        self.assertIn("49", recorded["evidence"])

    def test_hooks_reject_duplicate_and_write_shaped_probes(self):
        self.write_state("t7", {"hypotheses": [{"id": "h1", "name": "ssti",
                                                  "status": "open", "bug_class": "web-ssti"}], "probes": [
            {"request": "GET /a", "result": "inconclusive", "time": 1}]})
        self.assertEqual(self.hooks("pre-probe", "t7", "--request", "GET /a",
                                    "--hypothesis-id", "h1", "--class", "web-ssti"), 2)
        self.assertEqual(self.hooks("pre-probe", "t7",
                                    "--request", "POST /mass-update", "--hypothesis-id", "h1",
                                    "--class", "web-ssti"), 2)
        self.assertEqual(self.hooks("pre-probe", "t7", "--request", "GET /b",
                                    "--hypothesis-id", "h1", "--class", "web-ssti"), 0)

    def test_hooks_reject_unlinked_probes_and_mismatched_confirms(self):
        self.write_state("t7b", {"hypotheses": [{"id": "h1", "name": "ssti",
                                                   "status": "open", "bug_class": "web-ssti"}],
                                  "probes": []})
        self.assertEqual(self.hooks("pre-probe", "t7b", "--request", "GET /a"), 2)
        self.assertEqual(self.hooks("pre-probe", "t7b", "--request", "GET /a",
                                    "--hypothesis-id", "h1", "--class", "web-ssrf"), 2)
        self.assertEqual(self.hooks("post-probe", "t7b", "--request", "GET /a",
                                    "--verdict", "confirms", "--evidence", "49 rendered"), 2)

    def test_post_probe_clears_stale_next_action(self):
        self.write_state("t7c", {"next_action": "repeat the old request",
                                  "hypotheses": [{"id": "h1", "name": "ssti",
                                                   "status": "open", "bug_class": "web-ssti"}],
                                  "probes": []})
        self.assertEqual(self.hooks("post-probe", "t7c", "--request", "GET /?t=49",
                                    "--verdict", "inconclusive", "--evidence", "response was literal",
                                    "--hypothesis-id", "h1", "--class", "web-ssti"), 0)
        self.assertIsNone(self.read_state("t7c").get("next_action"))

    def test_state_hypothesis_keeps_bug_class(self):
        with patch.object(state, "ROOT", str(self.root)), patch.object(sys, "argv",
                                                                       ["state", "t7d", "--hypothesis", "ssti path",
                                                                        "--bug-class", "web-ssti"]), \
                contextlib.redirect_stdout(io.StringIO()):
            state.main()
        data = json.loads((self.root / "challenges/t7d/state.json").read_text())
        self.assertEqual(data["hypotheses"][0]["bug_class"], "web-ssti")

    def test_hooks_gate_confirmations_and_flags(self):
        self.write_state("t8", {"hypotheses": [
            {"id": "h1", "name": "ssti", "status": "open",
             "priority": 50, "time": 1, "bug_class": "web-ssti"}],
            "probes": []})
        self.assertEqual(self.hooks("pre-confirm", "t8",
                                    "--hypothesis-id", "h1"), 2)
        self.assertEqual(self.hooks("post-probe", "t8",
                                    "--request", "GET /?t=49",
                                    "--verdict", "confirms",
                                    "--evidence", "49 rendered",
                                    "--evidence-kind", "class",
                                    "--class", "web-ssti",
                                    "--hypothesis-id", "h1"), 0)
        self.assertEqual(self.hooks("pre-confirm", "t8",
                                    "--hypothesis-id", "h1"), 0)
        self.assertEqual(self.hooks("pre-flag", "t8", "--value", "HTB{x}"), 2)
        self.assertEqual(self.hooks("pre-flag", "t8", "--value", "HTB{x}",
                                    "--source", "guess",
                                    "--evidence", "looked like one"), 2)
        self.assertEqual(self.hooks("pre-flag", "t8", "--value", "HTB{x}",
                                    "--source", "live-response",
                                    "--evidence", "response: HTB{x}"), 0)
        self.assertEqual(decide_mod.decide("t8")["action"], "record_solve")

    def test_agents_md_exists_and_stays_ctf_only(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for tool in ("tools/decide.py", "tools/hooks.py", "tools/skill_audit.py"):
            self.assertIn(tool, text, "AGENTS.md must document " + tool)
            self.assertTrue((ROOT / tool).is_file(),
                            "AGENTS.md names a missing tool: " + tool)
        for marker in ("password spray", "ssh pivot", "lateral movement",
                       "root flag"):
            self.assertNotIn(marker.lower(), text.lower(),
                             "AGENTS.md must stay CTF-only, no red team: "
                             + marker)

    def test_skill_audit_report_is_written_and_consistent(self):
        report_path = ROOT / "knowledge" / "skill-audit.json"
        self.assertTrue(report_path.is_file(),
                        "run tools/skill_audit.py --apply to record the audit")
        report = skill_audit.audit()
        committed = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["summary"], committed["summary"],
                         "knowledge/skill-audit.json is stale; re-run "
                         "tools/skill_audit.py --apply")
        allowed = {"pass", "warn", "review", "thin-by-design", "reference",
                   "missing"}
        for row in report["skills"]:
            self.assertIn(row["verdict"], allowed,
                          "%s has an unknown verdict" % row["id"])
        flagged = {r["id"] for r in report["skills"]
                   if r["verdict"] == "review"}
        self.assertEqual(flagged, set(report["review"]),
                         "the review list must name exactly the review rows")


if __name__ == "__main__":
    unittest.main(verbosity=2)
