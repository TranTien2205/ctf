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

CASES = ROOT / "test" / "cases"
BASELINE = ROOT / "test" / "baseline.json"
CONTROL_PLANE = [
    "CLAUDE.md", "PROMPT.md", "SKILL_GUIDE.md", "HYPOTHESIS_PROTOCOL.md",
    "EVIDENCE_POLICY.md", "README.md", "VERSIONING.md",
    "skills/INDEX.md", "skills/LOOP_DISCIPLINE.md",
]
ROUTER_SKILLS = [
    "skills/ctf-playbook/SKILL.md", "skills/web-triage/SKILL.md",
    "skills/pwn-binary-triage/SKILL.md", "skills/rev-triage/SKILL.md",
    "skills/crypto-triage/SKILL.md", "skills/forensics-triage/SKILL.md",
    "skills/osint-triage/SKILL.md", "skills/ai-iot-triage/SKILL.md",
]
# Latin letters carrying Vietnamese tone or vowel marks. The control plane and the
# routers must be English so an agent never receives two languages of instruction.
VIETNAMESE = re.compile(
    "[àáảãạăằắẳẵặ"
    "âầấẩẫậèéẻẽẹ"
    "êềếểễệìíỉĩị"
    "òóỏõọôồốổỗộ"
    "ơờớởỡợùúủũụ"
    "ưừứửữựỳýỷỹỵđ]")
# Scripts that have no business in this tree; their presence means corrupted text.
FOREIGN_SCRIPT = re.compile("[Ѐ-ӿ一-鿿぀-ヿ가-힯]")
# Tools and skills that were referenced in documentation but never existed.
PHANTOM = re.compile(r"solver/recognize\.py|mcp-agent-security/|credential-hygiene")
PROMPT_SECTIONS = ["## Context", "## Role", "## Goal", "## Instructions",
                   "## Constraints", "## Output Format", "## Examples"]


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def load_cases(name):
    return json.loads((CASES / name).read_text(encoding="utf-8"))


def registry():
    return json.loads(read("skills/registry.json"))


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

    def test_no_phantom_tool_references(self):
        for path in list((ROOT / "skills").rglob("*.md")) + [ROOT / rel for rel in CONTROL_PLANE]:
            hits = PHANTOM.findall(path.read_text(encoding="utf-8"))
            self.assertEqual(hits, [], "%s references a tool that does not exist: %r"
                             % (path.relative_to(ROOT), hits[:4]))

    def test_documented_tools_exist(self):
        for rel in CONTROL_PLANE:
            for match in re.findall(r"`?(tools/[a-z_]+\.py)`?", read(rel)):
                self.assertTrue((ROOT / match).is_file(), "%s names a missing tool: %s" % (rel, match))

    def test_claude_md_and_prompt_agree_on_scope(self):
        claude = read("CLAUDE.md").lower()
        self.assertIn("security-toolkit", claude, "CLAUDE.md must restate the scope boundary")
        self.assertIn("hypothesis_protocol.md", claude)
        self.assertIn("prompt.md", claude)


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
            self.ledger(root, "sample", "--hypothesis", "old path")
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
            self.ledger(root, "sample", "--hypothesis", "parked path")
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


# --------------------------------------------------------------------------- G
class CapabilityTests(unittest.TestCase):
    @staticmethod
    def measure():
        reg = registry()
        routing = load_cases("routing.json")["cases"]
        correct = sum(1 for case in routing
                      if (ctf.observation_route(case["text"]).get("route") or {}).get("category")
                      == case["category"])
        return {
            "skills_registered": len(reg["skills"]),
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

    def test_routing_cases_all_pass(self):
        current = self.measure()
        self.assertEqual(current["routing_correct"], current["routing_cases"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
