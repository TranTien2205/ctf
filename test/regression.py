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
import argparse
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Trees .gitignore excludes ON PURPOSE because they hold real flags and organiser
# material: challenges/ (line 53, force-add one at a time) and CSCV2026/ (line 61,
# "carries an event writeup with a live flag").
#
# A fresh clone therefore has every card, alias, skill note and planner case that
# REFERS to those trees, but not the data. Four checks asserted the referent
# existed, so the gate passed on the machine that solved the challenge and failed
# on every clone -- measured: 121 pass here, 117 pass and 4 fail in a clean clone
# of the same commit. That is a portability bug in the gate, not a defect in the
# tree, and committing the data to silence it would break the repository's own
# rule against committing a flag.
#
# The convention already exists: tools/crypto/selftest.py reads
# CSCV2026/Crypto/solve/output_typhon.txt and SKIPS when it is absent, which
# .gitignore itself points at as the reason ignoring the tree "costs a clone
# nothing but the skip". These helpers apply that same rule to the gate: check
# the reference when the data is present, skip it when it is not, and never let
# an absent referent read as a broken one.
UNCOMMITTED_DATA_ROOTS = ("challenges/", "CSCV2026/")


def refers_to_uncommitted_data(relpath):
    """True when this path lives in a tree .gitignore excludes on purpose."""
    norm = str(relpath).replace(os.sep, "/").lstrip("./")
    return norm.startswith(UNCOMMITTED_DATA_ROOTS)


def absent_uncommitted(relpath):
    """True when the path is BOTH inside such a tree AND not on this disk.

    Deliberately two conditions. A reference into challenges/ that IS present --
    a force-added fixture -- stays fully checked, so the gate keeps catching a
    genuinely broken pairing wherever the data exists to check it against.
    """
    return refers_to_uncommitted_data(relpath) and not (ROOT / relpath).exists()
import ctf  # noqa: E402
from tools import state  # noqa: E402
from tools import chain_match, skill_select  # noqa: E402
from tools import classify as classifier  # noqa: E402
from tools import classify_solve  # noqa: E402
from tools import decide as decide_mod  # noqa: E402
from tools import hooks as hooks_mod  # noqa: E402
from tools import skill_audit  # noqa: E402
from tools import learning_report  # noqa: E402
from tools import search_facts  # noqa: E402
from tools import handout_inventory  # noqa: E402

CASES = ROOT / "test" / "cases"
BASELINE = ROOT / "test" / "baseline.json"
CONTROL_PLANE = [
    "CLAUDE.md", "PROMPT.md", "SKILL_GUIDE.md", "HYPOTHESIS_PROTOCOL.md",
    "ORCHESTRATION.md",
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
TOOL_PATH = re.compile(r"\btools/[A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)*\.py\b")
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

    def test_bug_classes_json_matches_its_generator(self):
        """knowledge/bug-classes.json is generated; regenerating must be a no-op.

        It had drifted from build/make_bug_classes.py in three places at once,
        because each fix was applied to the OUTPUT by hand and the generator was
        left stale. Regenerating then silently reverted every one of them: the
        whole web-xs-leaks class vanished, the base64 deserialization magics lost
        their \\b anchors so they fired inside any blob, and two race-condition
        signals fell back to the promiscuous "confirm" and bare "limit". Nothing
        in the gate noticed, because nothing compared the two. This does.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_mbc", ROOT / "build" / "make_bug_classes.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            module.OUT = os.path.join(tmp, "bug-classes.json")
            with contextlib.redirect_stdout(io.StringIO()):
                module.main()
            produced = json.loads(Path(module.OUT).read_text(encoding="utf-8"))
        committed = json.loads(read("knowledge/bug-classes.json"))
        self.assertEqual(
            [c["id"] for c in produced["classes"]],
            [c["id"] for c in committed["classes"]],
            "build/make_bug_classes.py and knowledge/bug-classes.json disagree on "
            "which classes exist; regenerating would add or drop a class. Fix the "
            "GENERATOR, then re-run it -- never hand-edit the output.")
        self.assertEqual(
            produced, committed,
            "knowledge/bug-classes.json is not what build/make_bug_classes.py "
            "produces. Port the change into the generator and re-run it; a "
            "hand-edited output is reverted by the next regeneration.")

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
        uncommitted = []
        for skill in sorted((ROOT / "skills").rglob("*.md")):
            rel = skill.relative_to(ROOT).as_posix()
            for target in link.findall(skill.read_text(encoding="utf-8")):
                if (rel, target) in exempt:
                    continue
                candidates = [skill.parent / target, ROOT / target]
                if any(c.is_file() for c in candidates):
                    continue
                if absent_uncommitted(target):
                    # A field note citing the handout it was written from. The
                    # handout is gitignored, so this is absent by design on a
                    # clone rather than a broken link.
                    uncommitted.append("%s -> %s" % (rel, target))
                    continue
                broken.append("%s -> %s" % (rel, target))
        self.assertEqual(broken, [],
                         "a skill names a reference file that does not exist: %s" % broken)
        if uncommitted:
            print("\n  note: %d skill reference(s) point into a gitignored data "
                  "tree and were not checked: %s" % (len(uncommitted), uncommitted))

    def test_sql_injection_has_one_canonical_owner(self):
        """SQLi references must live under web-sqli, not a second web corpus."""
        old = ROOT / "skills" / "ctf-web" / "sql-injection.md"
        canonical = ROOT / "skills" / "web-sqli"
        self.assertFalse(old.exists(), "legacy SQLi corpus still creates a second owner")
        self.assertTrue((canonical / "SKILL.md").is_file())
        self.assertTrue((canonical / "references" / "README.md").is_file())
        self.assertTrue((canonical / "references" / "extended-corpus.md").is_file())
        cls = next(c for c in taxonomy()["classes"] if c["id"] == "web-sqli")
        self.assertTrue(all(ref.startswith("skills/web-sqli/")
                            for ref in cls.get("depth_refs", [])),
                        "SQLi depth references must remain under its canonical owner")

    def test_sql_injection_deferred_sink_falsifier_is_not_premature(self):
        cls = next(c for c in taxonomy()["classes"] if c["id"] == "web-sqli")
        falsifier = cls["falsifier"].lower()
        self.assertIn("deferred", falsifier)
        self.assertIn("consumer", falsifier)
        self.assertIn("trigger", falsifier)
        self.assertIn("second-order", (ROOT / "skills/web-sqli/SKILL.md").read_text().lower())

    def test_class_depth_references_have_canonical_owners(self):
        classes = {c["id"]: c for c in taxonomy()["classes"]}
        expected = {
            "web-nosqli": "skills/web-nosqli/",
            "web-race-condition": "skills/web-race-condition/",
            "web-idor": "skills/web-idor/",
        }
        for class_id, prefix in expected.items():
            refs = classes[class_id].get("depth_refs", [])
            with self.subTest(class_id=class_id):
                self.assertTrue(refs)
                self.assertTrue(all(ref.startswith(prefix) for ref in refs),
                                "%s references must be class-owned: %s" % (class_id, refs))
        self.assertTrue((ROOT / "skills/web-idor/references/README.md").is_file())
        self.assertTrue((ROOT / "skills/web-nosqli/references/README.md").is_file())
        self.assertTrue((ROOT / "skills/web-race-condition/references/README.md").is_file())

    def test_graphql_has_one_operational_probe(self):
        text = (ROOT / "skills/web-graphql/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("## Operational probe"), 1)

    def test_generated_bug_class_skill_template_has_budget_contract(self):
        generator = (ROOT / "build/make_class_skills.py").read_text(encoding="utf-8")
        self.assertIn('"budget:"', generator)
        self.assertIn('stuck_threshold: 3', generator)
        self.assertIn('on_stuck: pivot', generator)

    def test_web_and_mcp_content_is_untrusted_and_requires_observed_effect(self):
        web = (ROOT / "skills/web-triage/SKILL.md").read_text(encoding="utf-8").lower()
        mcp = (ROOT / "skills/mcp-agent-security/SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("untrusted data", web)
        self.assertIn("raw request and response", web)
        self.assertIn("callback establishes only", web)
        self.assertIn("tool result is evidence", mcp)
        self.assertIn("third party", mcp)

    def test_large_forensic_artifact_workflow_is_bounded_and_preserves_provenance(self):
        text = (ROOT / "skills/ctf-forensics/SKILL.md").read_text(encoding="utf-8").lower()
        for phrase in ("gigabyte", "cryptographic hash", "bounded ranges", "separate evidence directory",
                       "hash of", "untrusted evidence"):
            self.assertIn(phrase, text)

    def test_novel_whitebox_plan_surfaces_chain_openers_without_claiming_a_finding(self):
        if absent_uncommitted("CSCV2026/public"):
            self.skipTest("CSCV2026/ is gitignored (it carries a live flag); the "
                          "planner's golden case needs that handout on disk")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/novel_plan.py"), "--json",
             str(ROOT / "CSCV2026/public")], capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        plan = json.loads(proc.stdout)
        ids = {row["id"] for row in plan["layers"]}
        self.assertTrue({"proxy-boundary", "internal-fetch", "upload-boundary"}.issubset(ids))
        self.assertIn("serialized-input", ids)
        self.assertIn("no proof is claimed", plan["chain_match_policy"])
        self.assertIn("source text", " ".join(plan["rules"]))

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

    def test_a_short_signal_does_not_fire_inside_a_longer_word(self):
        """`lua` must not match `evaluate`, and `lua_State` must still match.

        Plain containment had `lua` matching 9 of the 40 handouts with every hit
        inside `evaluate`, `mail` matching 16 with 13 inside `email`, and `eval`
        matching 17 with 10 inside words like `retrieval` — 61 phantom hits over
        18 signals. Because the scorer weights rare signals highest, a phantom
        hit on a rare short signal pushed the wrong card up the ranking. Only
        letters bound a signal: \\b would reject `lua_State`, which is a real hit.
        """
        should_match = [("lua", "lua_State *L"), ("lua", "redis.lua script"),
                        ("eval", "eval(userInput)"), ("mail", "mail() helper"),
                        ("curl", "curl -s http://x"), ("xss", "an XSS payload"),
                        ("template", "templates are rendered")]
        should_not = [("lua", "evaluate the archive"), ("eval", "retrieval of the key"),
                      ("mail", "the email field"), ("curl", "curlybrace syntax"),
                      ("bio", "biography"), ("latex", "translatex")]
        for signal, text in should_match:
            self.assertTrue(chain_match.found(signal, text.lower()),
                            "%r must still match %r" % (signal, text))
        for signal, text in should_not:
            self.assertFalse(chain_match.found(signal, text.lower()),
                             "%r must not fire inside %r" % (signal, text))

    def test_rarity_statistics_are_counted_with_the_real_matcher(self):
        """The IDF denominator has to be measured the way a hit is decided.

        rebuild_stats counted raw containment while scoring used found(), so
        every short signal was scored against a frequency it could never reach.
        """
        source = (ROOT / "tools" / "chain_match.py").read_text(encoding="utf-8")
        self.assertIn("found(s, t)", source,
                      "rebuild_stats must count with found(), not `s.lower() in t`")

    def test_classify_discounts_a_signal_that_matches_most_handouts(self):
        """A matched signal must be worth less when it matches everything.

        classify.py scored a plain count, so web-file-upload's
        `avatar|attachment|import|plugin|\\.tar\\b|\\.zip\\b` — which matches 95%
        of the handouts on disk — counted the same as a signal that matches one.
        Rarity modulates the count between SIGNAL_FLOOR and 1.0; it does not
        replace it, because two corroborating common signals are real evidence.
        """
        stats = classifier.load_signal_stats()
        if not stats:
            self.skipTest("knowledge/classify-signal-stats.json not built")
        total = stats["corpus"]
        broad = [k for k, v in stats["df"].items() if v / total > 0.6]
        self.assertTrue(broad, "expected some broad signals to exist to discount")
        rare_w = classifier.signal_weight("x", "a-signal-never-seen", stats)
        for key in broad[:5]:
            class_id, signal = key.split("||", 1)
            broad_w = classifier.signal_weight(class_id, signal, stats)
            self.assertLess(broad_w, rare_w,
                            "%r matches %d/%d handouts yet scores %.3f, "
                            "no less than a never-seen signal at %.3f"
                            % (signal, stats["df"][key], total, broad_w, rare_w))
            self.assertGreaterEqual(broad_w, classifier.SIGNAL_FLOOR,
                                    "a matched signal must never be worth nothing")

    def test_abstaining_writes_nothing_to_the_ledger(self):
        """Silence must reach the controller, or abstaining changes nothing.

        decide.py rule 6 runs a recorded card's probe ahead of the agent's own
        hypothesis, so grading a card weak only helps if the weak card also stops
        being recorded. Held out across 24 challenges, the index returns a card
        from the wrong mechanism family 29% of the time; without this the agent
        would spend its first probe on one of them instead of planning from
        source.
        """
        source = (ROOT / "tools" / "chain_match.py").read_text(encoding="utf-8")
        self.assertIn('c.get("status") == "candidate"', source,
                      "--record must filter weak cards out before writing the ledger")
        marker = source.index("def record_candidates")
        body = source[marker:source.index("def main()", marker)]
        self.assertIn("candidate", body,
                      "the filter belongs inside record_candidates, where the "
                      "ledger is actually written")

    def test_the_transfer_harness_does_not_invent_its_own_ground_truth(self):
        """tools/holdout_eval.py scores retrieval, so it must not grade its own work.

        Two ground truths were tried and discarded while building it. A Jaccard
        over stack and chain wording called two JWT key-confusion cards unrelated
        and reported a 4% transfer rate that meant nothing. Shared chain stages
        were worse than meaningless: recon, primitive, pivot, exfil and cleanup
        are the schema's fixed stage names, present in every card, so every pair
        looked related and the harness reported that a peer existed for 100% of
        challenges. Both numbers were published before inspection caught them.

        What replaced them comes from outside the harness: the class an operator
        reviewed through classify_solve, widened by the taxonomy's own
        confusable_with. This guards that it stays that way, because an
        improvement measured against a ground truth the improver can edit is not
        a measurement.
        """
        source = (ROOT / "tools" / "holdout_eval.py").read_text(encoding="utf-8")
        for discarded in ("def relatedness", "def vocabulary", "def mechanism_family"):
            self.assertNotIn(discarded, source,
                             "%s computed ground truth inside the harness; it must not return"
                             % discarded)

        # The filing leaked: a retriever that keys on skills/*/field-notes.md then
        # scores well for agreeing with the labels the metric is defined over. The
        # winning bake-off approach disclosed exactly that and put its leak-free
        # number at 0.083 against the 0.208 it reported. Prose may still explain
        # the history, but no code may read the filing back in.
        code = "\n".join(line for line in source.splitlines()
                         if not line.lstrip().startswith("#"))
        code = re.sub(r'"""(?:.|\n)*?"""', "", code)
        for leaked in ("field-notes.md", "confusable_with", "bug-classes.json"):
            self.assertNotIn(leaked, code,
                             "the harness must not read %r: a retriever keyed on it "
                             "would be scored against its own labelling" % leaked)

        families = json.loads((ROOT / "test" / "baselines" /
                               "mechanism_families.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(families["pairs"]), 8,
                                "too few reviewed pairs to measure transfer at all")
        chains = {p.stem for p in (ROOT / "knowledge" / "chains").glob("*.json")}
        for entry in families["pairs"]:
            self.assertEqual(len(entry["pair"]), 2)
            self.assertGreaterEqual(entry["votes"], 2,
                                    "a pair needs two of three annotators")
            for card in entry["pair"]:
                self.assertIn(card, chains,
                              "%s is not a card on disk; a typo here silently drops a "
                              "pair from the metric" % card)

    def test_the_taxonomy_can_name_what_this_library_already_solved(self):
        """A class the toolkit cannot name is a class it cannot route to.

        Three annotators described, blind, the move that opens each of the 24
        handout-backed chains. Feeding those descriptions to classify.py named a
        class for 20 of 24; two of the misses were signals that never described
        the shape of the handoff — "one front layer is the whole authorization
        story and its decision is keyed on a header the client can supply", and
        "the decoded request body is handed to the driver as the whole query
        structure". Both are now covered and the measure reads 22 of 24.

        The two that remain are structural and are recorded in the data file:
        one belongs to a registry skill that is not a bug class, and one names a
        mechanism the taxonomy has no class for.
        """
        data = json.loads((ROOT / "test" / "baselines" /
                           "mechanism_families.json").read_text(encoding="utf-8"))
        mechanisms = data.get("opening_mechanisms") or {}
        self.assertGreaterEqual(len(mechanisms), 20, "too few reviewed mechanisms to measure")
        named = 0
        for text in mechanisms.values():
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "classify.py"), "--json", str(text)[:400]],
                cwd=str(ROOT), capture_output=True, text=True)
            if json.loads(result.stdout).get("candidates"):
                named += 1
        self.assertGreaterEqual(
            named, 22,
            "classify.py named only %d of %d mechanisms this library has actually solved; "
            "a drop here means a signal was narrowed or a class removed" % (named, len(mechanisms)))

    def test_a_solve_is_filed_by_what_opened_the_chain(self):
        """AGENTS.md section 5 states the rule; this is what makes it reachable.

        classify_card scored the whole card at once — every chain stage, the
        signals, the stack and the entire solved note — so the exploit narrative
        decided the filing. Its vocabulary is the loud part (RCE, pickle,
        template) and it outvoted the quiet sentence that says where the chain
        actually starts. Measured on the library: a chain opening on "a
        recursive merge whose destination is an object" was filed under SSRF,
        one opening on "f-strings inside query construction" under SSTI. The
        --into docstring already admitted this; the fix is to rank the opening
        stages on their own first, and fall back to the full text only when they
        name no class at all.
        """
        source = (ROOT / "tools" / "classify_solve.py").read_text(encoding="utf-8")
        self.assertIn("def opening_text", source)
        marker = source.index("def classify_card")
        body = source[marker:source.index("def render_entry", marker)]
        self.assertIn("opening_text(card)", body,
                      "classify_card must rank the opening stages before anything else")

        card = {
            "id": "synthetic", "source_note": "does/not/exist.md",
            "signals": [], "stack": [],
            "chain": [
                {"stage": "recon", "action": "a recursive merge copies request keys into an "
                                             "object whose prototype is shared"},
                {"stage": "exfil", "action": "read the flag with a pickle reduce that spawns a "
                                             "template render and returns remote code execution"},
            ],
        }
        taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
        ranked = classify_solve.classify_card(card, taxonomy)
        self.assertTrue(ranked, "the opener names a mechanism, so something must rank")
        self.assertEqual(ranked[0]["class"], "web-prototype-pollution",
                         "the opening merge decides the filing, not the pickle and template "
                         "vocabulary of the final payload; got %s" % ranked[0]["class"])

    def test_a_barely_matching_chain_card_is_graded_weak(self):
        """The index must be able to say it does not know.

        tools/holdout_eval.py holds each card out and queries with its own
        handout, which is then a challenge the library has never seen. Measured
        over 24: it abstained 0 times and reported a median 0.65 confidence, up
        to 0.891, on a card that was not the answer — and decide.py rule 6 runs a
        recorded card's probe ahead of the agent's own hypothesis. The right card
        matches a median 0.89 of its own signals and a wrong one 0.27, but
        match_confidence was summed rarity and never saw that difference.
        """
        card = {"id": "probe-card", "_path": "synthetic",
                "signals": ["alpha-marker", "beta-marker", "gamma-marker",
                            "delta-marker", "epsilon-marker", "zeta-marker"],
                "stack": [], "chain": [], "preconditions": {},
                "first_confirming_probe": {"request": "x"}}
        barely = chain_match.score_card(card, "alpha-marker only", "alpha-marker only")
        self.assertIsNotNone(barely)
        self.assertEqual(barely["status"], "weak",
                         "one of six signals is a coincidence, not a lead")
        self.assertEqual(barely["suggested_priority"], 10,
                         "a weak card must not arrive with a high priority")

        text = " ".join(card["signals"][:5])
        solid = chain_match.score_card(card, text, text)
        self.assertEqual(solid["status"], "candidate",
                         "five of six signals present is a real match")
        self.assertGreater(solid["suggested_priority"], 10)

    def test_registry_unlock_signals_match_the_taxonomy(self):
        """A stale unlock_signals lets the dispatcher veto the classifier's answer.

        registry.json's unlock_signals are generated from the taxonomy's signals,
        and skill_select only ranks a skill whose unlock_signals matched. After
        the taxonomy gained proxy-config signals but the registry was not
        regenerated, web-parser-differential scored 4.50 in classify.py and was
        still locked out of dispatch with "no unlock signal observed yet". It
        looked fine on the real challenge only because that file happens to
        contain the word haproxy, which the stale pattern already carried.
        """
        taxonomy = {c["id"]: c for c in
                    json.loads(TAXONOMY.read_text(encoding="utf-8"))["classes"]}
        stale = []
        for skill in json.loads((ROOT / "skills" / "registry.json")
                                .read_text(encoding="utf-8"))["skills"]:
            entry = taxonomy.get(skill["id"])
            pattern = skill.get("unlock_signals")
            if entry is None or not pattern:
                continue
            for signal in entry.get("source_signals", []) + entry.get("observation_signals", []):
                if signal not in pattern:
                    stale.append("%s is missing %r" % (skill["id"], signal[:48]))
                    break
        self.assertEqual(stale, [],
                         "skills/registry.json is behind knowledge/bug-classes.json; "
                         "re-run python3 build/make_registry.py: %s" % stale[:4])

    def test_source_signals_read_context_not_just_substrings(self):
        """Three misreadings that sent a real challenge to the wrong skill.

        Measured on CSCV2026/public, whose chain is proxy ACL -> internal route
        -> multipart parser -> restricted unpickle. classify.py answered
        file-read-primitives, web-file-upload, web-ssrf, web-ssti: the opener and
        the sink were both absent and the winner rested on a regex bug.

        (a) `urlopen(` contains `open(`, so an outbound fetch scored as a local
            file read. (b) web-deserialization knew `pickle.loads` but not a
            subclassed `Unpickler` with `find_class`, which is the form an author
            writes when the restriction IS the challenge. (c) every
            parser-differential signal described the application reading a
            trusted header, so a proxy config stating the whole boundary matched
            nothing — a differential needs both parsers, and only one was modelled.
        """
        taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))["classes"]

        def classes_for(text):
            found = set()
            for entry in taxonomy:
                for signal in entry.get("source_signals", []):
                    try:
                        if re.search(signal, text, re.I | re.M):
                            found.add(entry["id"])
                            break
                    except re.error:
                        pass
            return found

        outbound = classes_for("with urlopen(request, timeout=3) as response:")
        self.assertNotIn("file-read-primitives", outbound,
                         "urlopen( is an outbound fetch; open( inside it is not a file read")
        self.assertIn("web-ssrf", outbound)

        self.assertIn("file-read-primitives",
                      classes_for("with open(os.path.join(BASE, request.args['n'])) as fh:"),
                      "a genuine request-controlled open() must still be found")

        self.assertIn("web-deserialization",
                      classes_for("class RestrictedUnpickler(pickle.Unpickler):\n"
                                  "    def find_class(self, module, name):"),
                      "a restricted unpickler is the deserialization sink an author writes")

        self.assertIn("web-parser-differential",
                      classes_for("  acl is_office_path path,url_dec -i -m sub office\n"
                                  "  http-request deny if is_office_path !network_office\n"
                                  "  use_backend back1 if is_office_web"),
                      "the proxy half of a parser differential must be recognisable")

    def test_dispatcher_defers_to_the_classifier(self):
        """One classifier decides which skill opens, not two that disagree.

        skill_select ranked on its own regex pass over registry unlock_signals,
        unweighted, ignoring the taxonomy. On CSCV2026/public classify.py put
        web-parser-differential first at 4.50 while the dispatcher returned
        web-file-upload — the chain's last entry point instead of the gate that
        has to be crossed first. AGENTS.md sends the agent to the dispatcher, so
        the weaker opinion was the one that got acted on.
        """
        source = ("acl is_office_path path,url_dec -i -m sub office\n"
                  "http-request deny if is_office_path !network_office\n"
                  "use_backend back1 if is_office_web\n"
                  "f = request.files['file']\n"
                  "class RestrictedUnpickler(pickle.Unpickler):\n"
                  "    def find_class(self, module, name): pass\n")
        registry = skill_select.load_registry()
        picked = skill_select.select(source, "web", registry, source_mode=True)
        top = picked.get("depth_candidate")
        self.assertIsNotNone(top, "a source naming a proxy ACL must unlock some depth skill")
        self.assertEqual(top["id"], "web-parser-differential",
                         "the dispatcher must open the chain opener, not the last "
                         "entry point; got %s" % top["id"])
        self.assertEqual(top.get("classify_rank"), 0,
                         "the dispatcher's choice must carry the classifier's rank")

    def test_every_class_is_found_by_its_own_name(self):
        """Typing the name of a class must return that class.

        classify.py is the first command AGENTS.md tells the agent to run, and
        `sqli in a login form` returned no candidate at all. Four of fifteen
        classes did not match their own name — sqli, ssti, xxe, nosqli — while
        xss, ssrf, csrf and cors did, only because those letters happened to sit
        inside an unrelated pattern. The taxonomy could recognise the evidence
        for a class without recognising what the class is called.
        """
        taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))["classes"]
        missing = []
        for entry in taxonomy:
            word = entry["id"].split("-", 1)[-1].replace("-", " ")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "classify.py"), "--json", word],
                cwd=str(ROOT), capture_output=True, text=True)
            got = [c["class"] for c in (json.loads(result.stdout).get("candidates") or [])]
            if entry["id"] not in got[:2]:
                missing.append("%s not found by %r (got %s)" % (entry["id"], word, got[:2]))
        self.assertEqual(missing, [],
                         "a class must be reachable by the name a person types: %s" % missing)

    def test_a_writeup_literal_may_not_be_an_ordinary_word(self):
        """External text may add a signal, but not a signal that matches anything.

        The one reviewed writeup card contributed six literals to SQL injection.
        Five were distinctive; the sixth was the bare word `PROFILE`, compiled
        case-insensitively and unanchored. Measured before the fix, the wholly
        benign observation "a Flask app with a user profile page and an avatar"
        returned web-sqli as its TOP candidate on that single word — a class
        this toolkit then treats as verified local experience.
        """
        for word in ["PROFILE", "profile", "admin", "SESSION", "token", "user"]:
            self.assertFalse(classifier.is_distinctive(word),
                             "%r is an ordinary word and must not become a class signal" % word)
        for literal in ["extractvalue(", "Duplicate column name", "is_ExclusiveMember",
                        "$_SESSION=$_POST", "ACCESS?action=browse"]:
            self.assertTrue(classifier.is_distinctive(literal),
                            "%r is distinctive evidence and must be kept" % literal)
        benign = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "classify.py"), "--json",
             "a Flask app with a user profile page and an avatar"],
            cwd=str(ROOT), capture_output=True, text=True)
        classes = [c["class"] for c in
                   (json.loads(benign.stdout).get("candidates") or [])]
        self.assertNotIn("web-sqli", classes[:1],
                         "a profile page alone must not make SQL injection the top "
                         "candidate; got %s" % classes[:3])

    def test_white_box_scan_excludes_this_toolkit_s_own_files(self):
        """Evidence about a target may not come from what we wrote about it.

        Measured on CSCV2026 before the fix: three of the top four candidates
        drew their evidence from `diemthi_exploit.py`, `WRITEUP.md` and
        `solve/attacks.py`. The top candidate's only evidence was the exploit
        script from diemthi — the challenge this toolkit LOST — so a failed
        attempt was being read back as an observation about the target.

        The filter must not overreach: a lockfile naming a real dependency, and
        a handout file that merely contains the substring (`resolve.py`,
        `solver_config.json`), are evidence and must be kept.
        """
        ours = ["WRITEUP.md", "writeup.md", "solve.py", "solve2.py", "solves.py",
                "exploit.py", "diemthi_exploit.py", "my_solve.py", "probe.py",
                "poc.js", "notes.md", "state.json", "anomaly_map.json"]
        theirs = ["resolve.py", "problem.py", "app.js", "routes.py", "models.py",
                  "package-lock.json", "solver_config.json", "prober.js",
                  "notesapp.py", "index.html"]
        for name in ours:
            self.assertTrue(classifier.is_self_authored(name),
                            "%s is written by this toolkit and must not be scanned" % name)
        for name in theirs:
            self.assertFalse(classifier.is_self_authored(name),
                             "%s is handout evidence and must still be scanned" % name)

    def test_taxonomy_matches_the_generator_that_produces_it(self):
        """A generated artifact must not drift from its generator.

        knowledge/bug-classes.json is written by build/make_bug_classes.py and
        read by classify.py, skill_audit.py, the registry and the index. It sat
        one class behind its generator — web-xs-leaks was defined in the
        generator and absent from the JSON — which orphaned that skill, tripped
        the capability floor, and read as a deliberate deletion rather than a
        missed regenerate. Only the generator is the source of truth.
        """
        generator = (ROOT / "build" / "make_bug_classes.py").read_text(encoding="utf-8")
        declared = set(re.findall(r'"id":\s*"([a-z0-9-]+)"', generator))
        built = {c["id"] for c in json.loads(TAXONOMY.read_text(encoding="utf-8"))["classes"]}
        missing = sorted(declared - built)
        self.assertEqual(missing, [],
                         "build/make_bug_classes.py defines these classes but "
                         "knowledge/bug-classes.json does not carry them; re-run "
                         "python3 build/make_bug_classes.py: %s" % missing)

    def test_every_state_key_the_controller_reads_has_a_writer(self):
        """A controller rule that reads a key nothing writes is a dead rule.

        decide.py rule 6 — reuse a solved chain before inventing a hypothesis,
        the cheapest win the system has — read state["chain_candidates"] while no
        tool wrote it. It fired only on a regression fixture, so for the whole
        life of the tree the controller never once offered a solved card's probe.
        Only the fixture kept it looking alive, which is exactly what this guards.
        """
        decide_src = (ROOT / "tools" / "decide.py").read_text(encoding="utf-8")
        read_keys = set(re.findall(r'current\.get\("([a-z_]+)"\)', decide_src))
        read_keys -= {"probes", "hypotheses", "flag", "name", "category", "target",
                      "next_action", "decisions", "searches", "schema_version"}
        writers = "\n".join(p.read_text(encoding="utf-8")
                            for p in sorted((ROOT / "tools").glob("*.py"))
                            if p.name != "decide.py")
        # Look for an assignment INTO a state dict, not for the name anywhere.
        # A bare name check passed `classes_considered` because classify.py
        # printed it as a count in its own stdout while never writing it to the
        # ledger, so the third dead rule survived the first version of this test.
        dead = [key for key in sorted(read_keys)
                if not re.search(r'\[\s*"%s"\s*\]\s*=' % re.escape(key), writers)]
        self.assertEqual(dead, [],
                         "tools/decide.py branches on state keys no tool writes, so "
                         "those rules can never fire outside a test fixture: %s" % dead)

    def test_documents_state_the_budget_the_controller_enforces(self):
        """One number, in one place, restated nowhere that can drift from it.

        PROMPT.md — the file the session contract tells the agent to load first —
        said "after three probes ... park that class" while decide.py enforced
        five, as did HYPOTHESIS_PROTOCOL.md, CLAUDE.md, AGENTS.md and
        LOOP_DISCIPLINE.md. An agent obeying PROMPT.md parked a live class two
        probes early while the controller was still returning run_probe.
        """
        words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                 "ten": 10, "fifteen": 15, "twenty": 20, "twenty-five": 25,
                 "thirty": 30, "forty-five": 45}

        def value(token):
            token = token.lower()
            return words.get(token, int(token) if token.isdigit() else None)

        pattern = re.compile(
            r"\b([a-z-]+|\d+) probes? (?:or|/) ([a-z-]+|\d+) (?:active )?minutes?\b",
            re.I)
        wrong = []
        for path in authored_files():
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith(("solved/", "challenges/", "test/")):
                continue
            for probes, minutes in pattern.findall(path.read_text(encoding="utf-8")):
                got_p, got_m = value(probes), value(minutes)
                if got_p is None or got_m is None:
                    continue
                pair = (got_p, got_m)
                if pair not in {(decide_mod.PROBE_BUDGET, decide_mod.MINUTE_BUDGET),
                                (decide_mod.CHALLENGE_PROBE_BUDGET,
                                 decide_mod.CHALLENGE_MINUTE_BUDGET)}:
                    wrong.append("%s says %d probes / %d minutes" % (rel, got_p, got_m))
        self.assertEqual(wrong, [],
                         "a document states a budget the controller does not enforce "
                         "(decide.py: %d/%d per class, %d/%d per challenge): %s"
                         % (decide_mod.PROBE_BUDGET, decide_mod.MINUTE_BUDGET,
                            decide_mod.CHALLENGE_PROBE_BUDGET,
                            decide_mod.CHALLENGE_MINUTE_BUDGET, wrong))

    def test_every_tool_path_named_in_prose_resolves(self):
        """PHANTOM only knew three retired names, so it could not catch a new one.

        skills/crypto-triage/SKILL.md once told every crypto session to start with
        `python3 tools/crypto_attack.py --list` while that file did not exist: the
        router's first command was a file-not-found and nothing in the gate said
        so. This resolves every tools/<name>.py written anywhere an agent reads,
        which is the check that would have caught it.
        """
        sources = (list((ROOT / "skills").rglob("*.md"))
                   + [ROOT / rel for rel in CONTROL_PLANE]
                   + [ROOT / "AGENTS.md"]
                   + sorted((ROOT / ".claude" / "commands").glob("*.md")))
        dangling = []
        for path in sources:
            if not path.is_file():
                continue
            for ref in sorted(set(TOOL_PATH.findall(path.read_text(encoding="utf-8")))):
                if not (ROOT / ref).is_file():
                    dangling.append("%s -> %s" % (path.relative_to(ROOT), ref))
        self.assertEqual(dangling, [],
                         "a document names a tool that does not exist: %s" % dangling[:6])

    def test_every_workflow_script_spawns_an_agent_that_exists(self):
        """A workflow that names an absent subagent cannot run at all.

        .claude/workflows/*.js drive the fleet through agentType, which resolves
        against .claude/agents/. A typo or an aspirational name is not a runtime
        warning -- the spawn fails mid-wave, after the earlier agents have
        already cost their 7-10 minutes each. The fleet lists are duplicated in
        the scripts (the sandbox has no filesystem, so they cannot be read from
        disk at run time), which is exactly the kind of duplication that rots, so
        it is proven here instead of trusted.
        """
        workflows = ROOT / ".claude" / "workflows"
        if not workflows.is_dir():
            self.skipTest("no .claude/workflows/ in this tree")
        agents = {p.stem for p in (ROOT / ".claude" / "agents").glob("*.md")}
        self.assertTrue(agents, "no subagents on disk to check against")

        # Quoted 'ctf-*' / 'ad-*' literals are the agent names a script can pass
        # as agentType; anything else in these files is prose.
        named = re.compile(r"['\"]((?:ctf|ad)-[a-z0-9-]+)['\"]")
        missing, checked = [], 0
        for path in sorted(workflows.glob("*.js")):
            text = path.read_text(encoding="utf-8")
            for name in sorted(set(named.findall(text))):
                checked += 1
                if name not in agents:
                    missing.append("%s -> %s" % (path.name, name))
        self.assertGreater(checked, 0,
                           "the extractor found no agent names in any workflow "
                           "script; it has stopped matching and proves nothing")
        self.assertEqual(sorted(set(missing)), [],
                         "a workflow script spawns a subagent that is not in "
                         ".claude/agents/: %s" % sorted(set(missing)))

    def test_a_workflow_return_envelope_only_reads_module_scope_variables(self):
        """The most expensive failure shape there is, and it happened.

        web-sweep.js declared `let held = []` inside the Sweep phase block and
        read it in the final `return {...}`. Every one of thirteen agents
        finished -- 1.03M tokens, 28 minutes, zero agent errors -- and the run
        then died with `ReferenceError: held is not defined` while assembling the
        result, so the whole thing was lost. `node --check` passes such a script
        because the syntax is valid; only scope is wrong.

        A variable the envelope reads is part of the envelope's scope, not the
        phase's. This checks that cheaply and offline.
        """
        workflows = ROOT / ".claude" / "workflows"
        if not workflows.is_dir():
            self.skipTest("no .claude/workflows/ in this tree")

        declared_re = re.compile(r"(?m)^(?:const|let|var)\s+([A-Za-z_$][\w$]*)")
        # `key: name` or `key: name.something(...)` where the value starts with a
        # bare identifier. A value that starts with a quote is a string literal
        # and is skipped, which is what kept `python3` out of an earlier version.
        reads_re = re.compile(r"^\s*[A-Za-z_$][\w$]*:\s*([A-Za-z_$][\w$]*)\b")
        builtins = {"true", "false", "null", "undefined", "args", "Object",
                    "Array", "JSON", "Math", "String", "Number", "Boolean"}

        checked, missing = 0, []
        for path in sorted(workflows.glob("*.js")):
            text = path.read_text(encoding="utf-8")
            declared = set(declared_re.findall(text))
            # ONLY the module-level envelopes, at column zero. An earlier
            # version matched every `return {` at any indentation and so flagged
            # returns inside helper functions, where the names it complained
            # about were parameters and locals genuinely in scope -- four false
            # positives in solver-fleet.js alone. A nested return is checked by
            # the engine's own scoping; it is the top-level one that can read a
            # block-scoped variable and die after the agents have all finished.
            for match in re.finditer(r"(?m)^return \{$", text):
                indent = ""
                tail = text[match.end():]
                end = tail.find("\n" + indent + "}")
                body = tail[:end if end >= 0 else len(tail)]
                for line in body.splitlines():
                    hit = reads_re.match(line)
                    if not hit:
                        continue
                    name = hit.group(1)
                    if name in builtins or name in declared:
                        continue
                    checked += 1
                    missing.append("%s: envelope reads %r, declared nowhere at "
                                   "module scope" % (path.name, name))
            checked += 1

        self.assertGreater(checked, 0,
                           "the extractor matched no return envelope; it has "
                           "stopped working and proves nothing")
        self.assertEqual(sorted(set(missing)), [],
                         "a workflow result would die with ReferenceError AFTER "
                         "every agent finished: %s" % sorted(set(missing))[:4])

    def test_no_workflow_script_delegates_the_ledger(self):
        """The one rule the speed rebuild must not quietly break.

        tools/decide.py enforces twenty-five probes per challenge, and ten agents
        recording probes in parallel would spend that in one round and force a
        class switch on classes nobody worked. So a workflow may COLLECT
        measurements and PRINT the commands, but it must never tell an agent to
        run the write gate itself. A script that did would look like a speed-up
        and would silently disable the controller.
        """
        workflows = ROOT / ".claude" / "workflows"
        if not workflows.is_dir():
            self.skipTest("no .claude/workflows/ in this tree")
        offenders = []
        for path in sorted(workflows.glob("*.js")):
            # Block-aware, because a line scanner cannot tell the two uses apart
            # and the first version flagged the SANCTIONED one. A command inside
            # a returned `the_main_thread_must_now` array is the whole point of
            # these workflows; the same command inside an agent() prompt is the
            # thing that would silently disable the controller. So track whether
            # we are inside an agent() argument list and only judge there.
            depth, in_agent = 0, False
            for number, line in enumerate(
                    path.read_text(encoding="utf-8").splitlines(), 1):
                lowered = line.lower()
                if not in_agent and re.search(r"\bagent\s*\(", line):
                    in_agent, depth = True, 0
                if in_agent:
                    depth += line.count("(") - line.count(")")
                    if depth <= 0 and not re.search(r"\bagent\s*\($", line.strip()):
                        # the call closed on this line; judge it, then leave
                        pass
                if "hooks.py" not in lowered and "state.py" not in lowered:
                    if in_agent and depth <= 0:
                        in_agent = False
                    continue
                if not in_agent:
                    # emitted for the main thread, not handed to an agent
                    continue
                # A comment is documentation, not a delegation. These files
                # explain at length WHY the gate is not delegated, so without
                # this the test flags its own rationale.
                if lowered.lstrip().startswith(("//", "*", "/*", "#")):
                    continue
                # Naming the gate as forbidden, or printing a command for the
                # MAIN thread to run, is the correct use and must stay allowed.
                allowed = ("never", "not run", "do not", "must now", "candidate",
                           "main thread", "forbid", "python3 tools/hooks.py "
                           "pre-flag", "# ", "gate")
                if any(token in lowered for token in allowed):
                    continue
                offenders.append("%s:%d %s" % (path.name, number, line.strip()[:90]))
        self.assertEqual(offenders, [],
                         "a workflow script appears to delegate tools/hooks.py "
                         "or tools/state.py to a subagent: %s" % offenders)

    def test_every_tool_flag_named_in_prose_exists(self):
        """The path test's sibling, one level down: the FLAGS have to be real too.

        test_every_tool_path_named_in_prose_resolves catches a document naming a
        tool that does not exist. It does not catch a document naming a flag the
        tool does not have, and that is what happened: CLAUDE.md, AGENTS.md and
        skills/crypto-triage/SKILL.md all told a crypto session to run
        `tools/crypto_attack.py --list`, while `list` is a SUBCOMMAND there --
        the documented form exits 2 with "the following arguments are required:
        command". Crypto was this toolkit's measured zero in a real contest and
        the router's first command did not run.

        Subcommand-aware on purpose: hooks.py keeps --verdict and --evidence
        under `post-probe`, so checking only top-level help reported fifteen real
        flags as missing.
        """
        sources = (list((ROOT / "skills").rglob("*.md"))
                   + [ROOT / rel for rel in CONTROL_PLANE]
                   + [ROOT / "AGENTS.md"]
                   + sorted((ROOT / ".claude" / "commands").glob("*.md"))
                   + sorted((ROOT / ".claude" / "agents").glob("*.md")))
        helpcache = {}

        def helptext(tool, sub):
            key = (tool, sub)
            if key not in helpcache:
                argv = [sys.executable, str(ROOT / tool)] + ([sub] if sub else []) + ["--help"]
                try:
                    done = subprocess.run(argv, capture_output=True, text=True,
                                          timeout=120, cwd=str(ROOT))
                    helpcache[key] = done.stdout + done.stderr
                except (OSError, subprocess.SubprocessError):
                    helpcache[key] = ""
            return helpcache[key]

        flag_re = re.compile(r"(?<![\w<-])(--[a-z][a-z0-9-]+)")
        call_re = re.compile(r"python3 (tools/[\w/]+\.py)((?:\s+\S+)*)")
        block_re = re.compile(r"```(?:bash|sh|console)?\n(.*?)```", re.S)
        bogus, checked = [], 0
        for path in sources:
            if not path.is_file():
                continue
            for block in block_re.findall(path.read_text(encoding="utf-8")):
                # join backslash continuations, or a flag on the second line is
                # attributed to no command at all and silently skipped
                for line in re.sub(r"\\\n\s*", " ", block).splitlines():
                    hit = call_re.search(line.strip())
                    if not hit or not (ROOT / hit.group(1)).is_file():
                        continue
                    tool, rest = hit.group(1), hit.group(2).split()
                    top = helptext(tool, None)
                    sub = None
                    if (rest and not rest[0].startswith("-")
                            and re.fullmatch(r"[a-z][a-z0-9-]*", rest[0])
                            and rest[0] in top):
                        sub = rest[0]
                    text = helptext(tool, sub)
                    if not text:
                        continue
                    checked += 1
                    for flag in sorted(set(flag_re.findall(line))):
                        if flag not in text:
                            bogus.append("%s -> %s%s has no %s" % (
                                path.relative_to(ROOT), tool,
                                (" " + sub) if sub else "", flag))
        self.assertGreater(checked, 40,
                           "only %d documented commands were checked; the extractor "
                           "has stopped matching and this test proves nothing" % checked)
        self.assertEqual(sorted(set(bogus)), [],
                         "a document tells an agent to pass a flag the tool does not "
                         "have: %s" % sorted(set(bogus))[:6])

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

    def test_actionable_web_skills_keep_operational_probe_contracts(self):
        required = {
            "web-csrf": ("Operational probe", "before/after state change"),
            "web-request-smuggling": ("Operational probe", "raw status lines"),
            "web-prototype-pollution": ("Operational probe", "training_marker"),
            "web-idor": ("Operational probe", "Two identities"),
            "web-cors": ("Operational probe", "Access-Control-Allow-Origin"),
            "web-open-redirect": ("Operational probe", "Location"),
            "web-xss": ("Operational probe", "XSS_PROBE_", "reflection alone is inconclusive"),
            "web-xxe": ("Operational probe", "XXE_PROBE", "malformed XML error does not prove"),
            "web-graphql": ("Operational probe", "__typename", "Schema disclosure is not an exploit"),
            "web-web3": ("Operational probe", "solved predicate", "receipt/status"),
        }
        for skill, markers in required.items():
            text = read("skills/%s/SKILL.md" % skill)
            for marker in markers:
                self.assertIn(marker, text, "%s lost actionable marker: %s" % (skill, marker))


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
            if not absent_uncommitted(card["source_note"]):
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

    def test_only_reviewed_writeup_signals_extend_classification(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Path(temp)
            (store / "reviewed.json").write_text(json.dumps({
                "classification": {"primary": "SQL injection"},
                "signals": ["vendor_magic_marker", "SELECT MAGIC_COL"],
                "quality": {"review_status": "reviewed", "verified_live": False},
                "first_probe": {"payload": "MUST_NOT_ENTER_CLASSIFIER"},
            }), encoding="utf-8")
            (store / "unreviewed.json").write_text(json.dumps({
                "classification": {"primary": "web-sqli"},
                "signals": ["unreviewed_magic_marker"],
                "quality": {"review_status": "extracted", "verified_live": False},
            }), encoding="utf-8")
            taxonomy_classes = taxonomy()["classes"]
            writeup_signals = classifier.load_writeup_signals(store, taxonomy_classes)
            merged = classifier.merge_writeup_signals(taxonomy_classes, writeup_signals)
            ranked = classifier.rank(classifier.scan_text(
                "vendor_magic_marker", classifier.compile_signals(
                    merged, "observation_signals")), merged)
            self.assertEqual(ranked[0]["class"], "web-sqli")
            self.assertEqual(writeup_signals["web-sqli"],
                             ["SELECT MAGIC_COL", "vendor_magic_marker"])
            patterns = dict((class_id, [raw for raw, _ in pats])
                            for class_id, pats in classifier.compile_signals(
                                merged, "observation_signals").items())
            self.assertFalse(any("MUST_NOT_ENTER_CLASSIFIER" in p
                                 for values in patterns.values() for p in values))
            self.assertFalse(any("unreviewed_magic_marker" in p
                                 for values in patterns.values() for p in values))


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
        # Check the whole step, not the first line of it. A step may open with a
        # comment or run a loop over several selftests, and the single-line form
        # read the comment and reported the step as unchecked.
        steps = re.split(r'^hr "', script, flags=re.M)[1:]
        required = [s for s in steps if s.startswith("REQUIRED:")]
        self.assertTrue(required, "run_all.sh declares no required steps")
        for step in required:
            title = step.split('"', 1)[0]
            self.assertIn("fail=1", step,
                          "a REQUIRED step in run_all.sh ignores its exit status: %s" % title)

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

    def test_a_resumed_challenge_is_not_born_budget_exhausted(self):
        """Parking and reviving is documented; it used to be unreachable.

        The minute budget was `now - first probe`, so a challenge parked on
        Monday and resumed on Friday returned switch_class for every class and
        state.py --revive could never be acted on. Only minutes actually worked
        are charged now: gaps longer than the idle threshold are parking.
        """
        start = 1000.0
        week = 7 * 24 * 3600
        probes = [{"request": "GET /?p=%d" % i, "result": "inconclusive",
                   "time": start + i * 120, "verdict": "inconclusive",
                   "class": "web-ssti"} for i in range(2)]
        self.write_state("resumed", {
            "hypotheses": [{"id": "h1", "name": "ssti", "status": "open",
                            "bug_class": "web-ssti", "priority": 50, "time": start}],
            "probes": probes, "classes_considered": ["web-ssti", "web-ssrf"]})
        decision = decide_mod.decide("resumed", now=start + week)
        self.assertEqual(decision["action"], "run_probe",
                         "a week-old challenge must resume, not arrive exhausted")

    def test_challenge_ceiling_stops_class_hopping(self):
        """The per-class cap is keyed on an agent-supplied string, so relabelling
        the class resets it. Twenty-five classes at five probes each is 125
        probes with nothing saying stop; CLAUDE.md stated a 45-minute ceiling
        per challenge that no code implemented. This is that ceiling."""
        start = 1000.0
        probes = [{"request": "GET /?p=%d" % i, "result": "inconclusive",
                   "time": start + i * 60, "verdict": "inconclusive",
                   "class": "made-up-class-%d" % i}
                  for i in range(decide_mod.CHALLENGE_PROBE_BUDGET)]
        self.write_state("hopper", {
            "hypotheses": [{"id": "h1", "name": "n", "status": "open",
                            "bug_class": "web-ssti", "priority": 50, "time": start}],
            "probes": probes, "classes_considered": ["web-ssti"]})
        budgets = decide_mod.compute_budget(probes, start + 60 * len(probes))
        self.assertFalse(any(b["exhausted"] for b in budgets.values()),
                         "no single class is over its own cap, which is the point")
        decision = decide_mod.decide("hopper", now=start + 60 * len(probes))
        # The ceiling still fires and still forbids a further probe. What changed
        # is what the controller does about it: a spent probe budget is not a
        # finished challenge, so it changes STRATEGY instead of reporting defeat.
        self.assertEqual(decision["action"], "escalate")
        self.assertIn("challenge budget exhausted", decision["rationale"])
        self.assertIn("no further probe is permitted", decision["rationale"])

    def test_the_escalation_ladder_ends_in_a_stop_and_not_a_loop(self):
        """Removing the stop would make the controller loop for ever.

        "Keep going until the flag" is implemented as a ladder of real
        strategies, not as an unbounded retry: each rung is offered once,
        tools/state.py --strategy-used records that it was spent, and when every
        rung is spent the controller stops and asks for the kill map. Without
        this test the ladder could silently re-offer a rung and never terminate.
        """
        start = 1000.0
        probes = [{"request": "GET /?p=%d" % i, "result": "inconclusive",
                   "time": start + i * 60, "verdict": "inconclusive",
                   "class": "web-ssti"}
                  for i in range(decide_mod.CHALLENGE_PROBE_BUDGET)]
        seen, spent = [], []
        for _ in range(len(decide_mod.ESCALATION_LADDER) + 2):
            self.write_state("ladder", {
                "category": "crypto", "challenge_name": "Nameless",
                "event_name": "SomeCTF", "source": "challenges/ladder/handout",
                "classes_considered": ["web-ssti"],
                "hypotheses": [{"id": "h1", "name": "n", "status": "open",
                                "bug_class": "web-ssti", "priority": 50,
                                "time": start}],
                "probes": probes, "strategies_used": list(spent)})
            decision = decide_mod.decide("ladder", now=start + 60 * len(probes))
            if decision["action"] != "escalate":
                break
            rung = decision["escalation"]["rung"]
            self.assertNotIn(rung, spent, "the ladder re-offered a spent rung")
            self.assertTrue(decision["commands"],
                            "an escalation with no command is not a strategy")
            self.assertTrue(
                any("--strategy-used %s" % rung in c for c in decision["commands"]),
                "a rung must tell the operator how to record that it was spent, "
                "or the ladder cannot advance")
            seen.append(rung)
            spent.append(rung)
        self.assertEqual(decision["action"], "stop_report",
                         "the ladder must terminate, not loop")
        self.assertTrue(seen, "the ladder offered nothing at all")
        self.assertEqual(seen, [r for r in decide_mod.ESCALATION_LADDER if r in seen],
                         "rungs must be offered cheapest-first, in ladder order")

    def test_the_two_ladder_definitions_cannot_drift(self):
        """state.py duplicates the ladder because decide.py imports it.

        A rung spelled differently in one file would be silently unrecordable,
        so that strategy would be offered for ever and the ladder would never
        terminate. One number in one place, proven rather than trusted.
        """
        self.assertEqual(tuple(decide_mod.ESCALATION_LADDER),
                         tuple(state.ESCALATION_LADDER))

    def test_the_probe_brake_still_refuses_past_the_ceiling(self):
        """Escalation is additive: it must not have loosened the brake.

        The ladder changes what decide.py ADVISES when the budget is spent. It
        must not make hooks.py accept a twenty-sixth probe, or "change strategy"
        would quietly become "keep probing".
        """
        start = 1000.0
        probes = [{"request": "GET /?p=%d" % i, "result": "inconclusive",
                   "time": start + i * 60, "verdict": "inconclusive",
                   "class": "web-ssti"}
                  for i in range(decide_mod.CHALLENGE_PROBE_BUDGET)]
        self.write_state("braked", {
            "hypotheses": [{"id": "h1", "name": "n", "status": "open",
                            "bug_class": "web-ssti", "priority": 50,
                            "time": start}],
            "probes": probes})
        code = hooks_mod.main(["pre-probe", "braked", "--request",
                               "GET /a-brand-new-mechanism",
                               "--hypothesis-id", "h1"])
        self.assertEqual(code, 2,
                         "the challenge ceiling must still refuse a probe")

    def test_a_novel_white_box_challenge_plans_its_layers_first(self):
        """The case this system was worst at: source, but no chain that fits.

        Rule 6 reuses a solved chain and rule 7a says "classify, then probe".
        Between them the agent fell through to one classifier answer and opened
        one depth skill, which on a layered challenge is the last entry point
        rather than the gate in front of it — CSCV2026 routed to file upload
        while the chain opened at a proxy ACL.
        """
        self.write_state("novel", {
            "category": "web", "source": "challenges/novel/handout",
            "hypotheses": [], "probes": []})
        decision = decide_mod.decide("novel")
        self.assertEqual(decision["action"], "novel_plan")
        self.assertTrue(any("novel_plan.py" in c for c in decision["commands"]),
                        "the controller must name the planner it is asking for")

    def test_a_matching_chain_still_outranks_the_novel_planner(self):
        """Reuse before novelty. Planning is the fallback, never the default."""
        self.write_state("both", {
            "category": "web", "source": "challenges/both/handout",
            "hypotheses": [], "probes": [],
            "chain_candidates": [{"id": "card-1",
                                  "first_confirming_probe": "the card probe"}]})
        decision = decide_mod.decide("both")
        self.assertEqual(decision["action"], "run_probe")
        self.assertEqual(decision["next_probe"]["chain_card"], "card-1")

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
                                    "--response",
                                    "HTTP/1.1 200 OK\n\n<p>49 appeared in the page</p>",
                                    "--hypothesis-id", "h1", "--class", "web-ssti"), 0)
        recorded = self.read_state("t6")["probes"][-1]
        self.assertEqual(recorded["verdict"], "confirms")
        self.assertIn("49", recorded["evidence"])

    def test_a_confirmation_is_checked_against_the_response_not_trusted(self):
        """The guarantee this gate is named for, and it used to be unenforceable.

        post-probe had no --response input at all, so "verdict=confirms must
        quote the response substring that proves it" was checked only as:
        non-empty, not timeout-shaped, right evidence_kind. Any plausible
        sentence passed, and the machine validated the SHAPE of the claim while
        never seeing its truth. tools/web/http_probe.py is the one component
        that holds the request and the response together, which is why it is the
        sanctioned path and why it now emits --response itself.
        """
        self.write_state("t6r", {
            "hypotheses": [{"id": "h1", "name": "ssti", "status": "open",
                            "bug_class": "web-ssti"}], "probes": []})
        common = ("post-probe", "t6r", "--verdict", "confirms",
                  "--evidence-kind", "class", "--class", "web-ssti",
                  "--hypothesis-id", "h1")

        # No response at all: there is nothing to check the quote against.
        self.assertEqual(self.hooks(*common, "--request", "GET /a",
                                    "--evidence", "49 rendered"), 2)

        # A response that does NOT contain the evidence: summarised, retyped or
        # reconstructed. This is the case the old gate could never see.
        self.assertEqual(self.hooks(*common, "--request", "GET /b",
                                    "--evidence", "the template evaluated 7*7",
                                    "--response", "HTTP/1.1 200 OK\n\n<p>49</p>"), 2)

        # A genuine verbatim quote is accepted, and stored.
        self.assertEqual(self.hooks(*common, "--request", "GET /c",
                                    "--evidence", "<p>49</p>",
                                    "--response", "HTTP/1.1 200 OK\n\n<p>49</p>"), 0)
        recorded = self.read_state("t6r")["probes"][-1]
        self.assertEqual(recorded["verdict"], "confirms")
        self.assertIn("49", recorded["evidence"])

        # The response is a check, not a second copy of the evidence: it must
        # not be written into the ledger, which would double every probe's size
        # and store response bytes the proof standard never asked us to keep.
        self.assertNotIn("response", recorded)

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
                                    "--response", "HTTP/1.1 200 OK\n\n49 rendered",
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
        for tool in ("tools/decide.py", "tools/hooks.py", "tools/skill_audit.py",
                     "tools/search_facts.py", "tools/handout_inventory.py"):
            self.assertIn(tool, text, "AGENTS.md must document " + tool)
            self.assertTrue((ROOT / tool).is_file(),
                            "AGENTS.md names a missing tool: " + tool)
        for marker in ("password spray", "ssh pivot", "lateral movement",
                       "root flag"):
            self.assertNotIn(marker.lower(), text.lower(),
                             "AGENTS.md must stay CTF-only, no red team: "
                              + marker)

    def test_search_facts_plans_a_missing_fact_without_treating_search_as_proof(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/search_facts.py"), "ctf-writeup",
             "--challenge", "Example", "--event", "Example CTF",
             "--fact", "published solve path", "--decision", "select the first probe"],
            capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        plan = json.loads(proc.stdout)
        self.assertEqual(plan["action"], "search_external_fact")
        self.assertEqual(plan["missing_fact"], "published solve path")
        self.assertIn("tools/writeup_search.py", plan["commands"][0])
        self.assertTrue(any("untrusted lead" in item.lower()
                            for item in plan["evidence_policy"]))

    def test_search_fact_record_keeps_external_claim_separate_from_probe_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            state_path = Path(temp) / "state.json"
            state_path.write_text(json.dumps({
                "schema_version": 1, "name": "search-test", "hypotheses": [],
                "probes": [], "next_action": None,
            }), encoding="utf-8")
            args = SimpleNamespace(
                record="search-test", url="https://docs.example.test/feature",
                title="Example feature docs", snippet="Feature is enabled by default",
                outcome="supported", local_verification="source: config.enabled = true",
                kind="official-docs", fact="default feature behavior",
                decision="choose the first probe", version="1.2.3",
            )
            payload = {"queries": ["Example 1.2.3 default feature behavior"]}
            with patch.object(search_facts.state_mod, "path_for", return_value=str(state_path)):
                recorded = search_facts.record(args, payload, argparse.ArgumentParser())
            state_data = json.loads(state_path.read_text())
            self.assertEqual(recorded["recorded"]["outcome"], "supported")
            self.assertEqual(len(state_data["searches"]), 1)
            self.assertEqual(state_data["searches"][0]["snippet"], "Feature is enabled by default")
            self.assertEqual(state_data["probes"], [])
            self.assertNotIn("flag", state_data)

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


class KnowledgeStoreTests(unittest.TestCase):
    """The line between what this toolkit solved and what it merely read.

    chain_match ranks by signal rarity, so every card competes for the top slot.
    Letting unverified writeup cards into knowledge/chains/ would dilute that
    ranking with claims nobody checked here, and would quietly turn the
    `verified` label in bug-classes.json into "somebody on the internet said so".
    """

    def test_chain_and_writeup_cards_stay_in_their_own_store(self):
        misplaced = []
        for path in sorted((ROOT / "knowledge" / "chains").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if "classification" in data and "chain" not in data:
                misplaced.append("writeup card in chains/: %s" % path.name)
        for path in sorted((ROOT / "knowledge" / "cards").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if "chain" in data and "first_confirming_probe" in data:
                misplaced.append("chain card in cards/: %s" % path.name)
        self.assertEqual(misplaced, [], "; ".join(misplaced))

    def test_writeup_cards_never_claim_local_verification(self):
        offenders = []
        for path in sorted((ROOT / "knowledge" / "cards").glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            if (data.get("quality") or {}).get("verified_live") is True:
                offenders.append(path.name)
        self.assertEqual(offenders, [],
                         "a writeup card claims verified_live; only a chain card "
                         "written from a run on this machine may: %s" % offenders)

    def test_chain_match_reads_only_the_verified_store(self):
        source = read("tools/chain_match.py")
        self.assertIn('"chains"', source)
        self.assertNotIn('"cards"', source,
                         "chain_match must not read the writeup store")


class KnowledgeScaleTests(unittest.TestCase):
    """Guards that keep the knowledge base usable as it grows.

    Both of these exist because a real defect slipped through: a bug-class skill
    was dropped from the taxonomy while its directory stayed, so classify.py
    stopped routing to it and system_eval silently lost a case, and the chain
    matcher could not retrieve a card from its own handout because an asset-heavy
    challenge exhausted the read budget on images before reaching any code.
    """

    def test_handout_inventory_excludes_solver_workdirs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            chains = root / "knowledge" / "chains"
            challenges = root / "challenges"
            chains.mkdir(parents=True)
            (chains / "clean.json").write_text(json.dumps({
                "id": "clean-card", "challenge": {"name": "Clean Challenge"},
            }), encoding="utf-8")
            (chains / "work.json").write_text(json.dumps({
                "id": "work-card", "challenge": {"name": "Work Challenge"},
            }), encoding="utf-8")
            clean = challenges / "Clean Challenge"
            clean.mkdir(parents=True)
            (clean / "app.py").write_text("print('ok')", encoding="utf-8")
            work = challenges / "Work Challenge"
            work.mkdir(parents=True)
            (work / "state.json").write_text("{}", encoding="utf-8")
            with patch.object(handout_inventory, "ROOT", root), \
                    patch.object(handout_inventory, "CHAINS", chains), \
                    patch.object(handout_inventory, "CHALLENGES", challenges):
                report = handout_inventory.inventory()
            rows = {row["chain_id"]: row for row in report["cards"]}
            self.assertTrue(rows["clean-card"]["handout_available"])
            self.assertFalse(rows["work-card"]["handout_available"])

    def test_every_bug_class_skill_is_in_the_taxonomy(self):
        taxonomy = {c["id"] for c in
                    json.loads(read("knowledge/bug-classes.json"))["classes"]}
        orphans = []
        for entry in sorted((ROOT / "skills").iterdir()):
            skill = entry / "SKILL.md"
            if not skill.is_file():
                continue
            match = re.search(r"^tags:\s*\[([^\]]*)\]", skill.read_text(encoding="utf-8"),
                              re.M)
            if not match:
                continue
            tags = [t.strip() for t in match.group(1).split(",")]
            if "bug-class" in tags and entry.name not in taxonomy:
                orphans.append(entry.name)
        self.assertEqual(orphans, [],
                         "a skill tagged bug-class is missing from "
                         "knowledge/bug-classes.json, so classify.py cannot route "
                         "to it: %s" % orphans)

    def test_http_probe_refuses_a_verdict_when_urllib_dropped_a_header(self):
        """A response to a request that was not sent is not evidence.

        Measured on a live box: `Connection: X-Real-IP` bypassed an API token
        check -- curl and a raw socket both answered 200 {"trades":[]} where the
        plain request answered 401 -- and tools/web/http_probe.py answered 401
        for the identical call, because http.client replaces the Connection
        header with its own. urllib.request.Request even reports the header back
        from header_items(), so nothing looked wrong. A confident negative about
        a request that never went out is worse than a failure, and it blinds the
        tool for exactly web-parser-differential and web-request-smuggling,
        where manipulating that header IS the technique.
        """
        sys.path.insert(0, str(ROOT / "tools" / "web"))
        import httpkit

        # The error path is enough and needs no network: an unroutable port
        # fails fast, and headers_not_sent is reported on both paths.
        dead = "http://127.0.0.1:1/never"
        got = httpkit.request(dead, headers={"Connection": "X-Real-IP"},
                              timeout=2)
        self.assertEqual(got.get("headers_not_sent"), ["Connection"],
                         "httpkit must report a header http.client overrides")

        clean = httpkit.request(dead, headers={"X-Custom": "1"}, timeout=2)
        self.assertEqual(clean.get("headers_not_sent"), [],
                         "an ordinary header is sent and must not be reported "
                         "as dropped")

        for managed in ("Content-Length", "Transfer-Encoding", "Host"):
            got = httpkit.request(dead, headers={managed: "x"}, timeout=2)
            self.assertEqual(got.get("headers_not_sent"), [managed],
                             "%s is managed by http.client too" % managed)

        # And the probe must act on it rather than only report it.
        source = (ROOT / "tools" / "web" / "http_probe.py").read_text(
            encoding="utf-8")
        self.assertIn("headers_not_sent", source,
                      "http_probe ignores the dropped-header signal")
        self.assertIn("DIFFERENT request", source,
                      "the downgrade must say why the verdict is void")
        self.assertNotIn('if dropped and verdict == "confirms"', source,
                         "the guard must be unconditional: the real case was a "
                         "MISS caused by the dropped header, so gating it on "
                         "confirms let a confident negative through")

    def test_validate_refuses_prose_in_the_class_field(self):
        """`class` becomes `post-probe --class`, so prose there is unrunnable.

        Measured on the first live fleet run: the bundle family answered with a
        150-character explanation in this field -- "web-source-map (skill name;
        NOT an id in knowledge/bug-classes.json ...)" -- and --merge passed it
        through verbatim, so three of ten emitted commands could not be run. A
        family that owns no taxonomy class says so with null, which the contract
        already asks for.
        """
        import subagent_fanout as fanout

        base = {
            "layer_id": "bundle", "challenge": "t", "files_read": [],
            "falsifier_outcome": "broken", "conclusion": "hypothesis",
            "cost_minutes": 1, "probes": [],
        }

        prose = dict(base, **{"class": "web-source-map (skill name; NOT an id in "
                                       "knowledge/bug-classes.json)"})
        problems, _ = fanout.validate_report(prose)
        self.assertTrue(any("not an id" in p for p in problems),
                        "prose in `class` was accepted: %s" % problems)

        # null is the correct answer for a family that owns no class, and must
        # keep passing or the recon and bundle families become unreportable.
        problems, _ = fanout.validate_report(dict(base, **{"class": None}))
        self.assertEqual(problems, [], "class null must stay valid: %s" % problems)

        # a real id passes
        taxonomy = json.loads(
            (ROOT / "knowledge" / "bug-classes.json").read_text(encoding="utf-8"))
        real = taxonomy["classes"][0]["id"]
        problems, _ = fanout.validate_report(dict(base, **{"class": real}))
        self.assertEqual(problems, [],
                         "a real taxonomy id was refused: %s" % problems)

    def test_the_web_sweep_stops_when_the_app_publishes_its_own_spec(self):
        """The stop condition the first live run paid 1.1M tokens to learn.

        On GoNuclear the sweep spawned twelve agents over 42 minutes; the answer
        was a 7 KB /api/openapi.json declaring an operation with no `security`
        and a response field named `verifyToken`. A fan-out maps an UNKNOWN
        surface, so a published spec must END the sweep, not precede it.
        """
        path = ROOT / ".claude" / "workflows" / "web-sweep.js"
        if not path.is_file():
            self.skipTest("no web-sweep workflow in this tree")
        text = path.read_text(encoding="utf-8")

        for token in ("openapi.json", "swagger.json", "api-docs",
                      "has_security", "short_circuit"):
            self.assertIn(token, text,
                          "web-sweep.js no longer looks for a published spec (%s)"
                          % token)
        self.assertIn("published_api_spec", text,
                      "the spec short-circuit must name itself in the result so a "
                      "reader can tell a stop from a completed sweep")
        self.assertIn("forceSweep", text,
                      "the stop condition needs a documented bypass for when the "
                      "spec turns out to be a dead end")
        # The cap that stops this workflow disagreeing with dispatch.py.
        self.assertIn("MAX_WIDTH", text,
                      "web-sweep.js must cap its wave like "
                      "tools/contest/dispatch.py does; without it the two "
                      "components disagree and the extra agents only queue")
        self.assertIn("families_held_over_width_cap", text,
                      "what the cap dropped must be reported, or a truncated "
                      "sweep reads as a complete one")

    def test_merge_emits_a_command_the_gate_will_actually_accept(self):
        """Found by running the fleet for real, not by reading the code.

        tools/hooks.py post-probe was hardened to REQUIRE --response on a
        `confirms` verdict and to assert the evidence is a substring of it.
        tools/subagent_fanout.py --merge builds those commands, and it was not
        updated: on the first live fleet run it emitted ten confirming commands,
        not one carried --response, and the gate refused every single one. The
        excerpt was already in the report -- it only had to be passed through.

        A merge that emits an unrunnable command is worse than one that emits
        nothing, because the failure surfaces at the end of a 40-minute sweep.
        """
        import subagent_fanout as fanout

        report = {
            "layer_id": "client", "challenge": "t", "class": "web-cors",
            "files_read": [], "falsifier_outcome": "broken",
            "conclusion": "hypothesis", "cost_minutes": 1,
            "probes": [{
                "request": "GET /api/files",
                "transport": "ok", "status": 401,
                "response_excerpt": "HTTP/1.1 401\naccess-control-allow-origin: https://evil.example\n",
                "evidence": "access-control-allow-origin: https://evil.example",
                "evidence_kind": "class", "verdict": "confirms",
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "client.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            merged = fanout.merge([str(path)], "t")

        confirming = [c for c in merged["commands_for_the_main_thread"]
                      if "--verdict confirms" in c]
        self.assertTrue(confirming, "merge emitted no confirming command to check")
        for command in confirming:
            self.assertIn("--response", command,
                          "a confirming post-probe command without --response is "
                          "refused by the gate: %s" % command[:120])

        # And the response it passes must really contain the evidence, or the
        # command is refused for the second reason instead of the first.
        argv = shlex.split(confirming[0], comments=True)
        evidence = argv[argv.index("--evidence") + 1]
        response = argv[argv.index("--response") + 1]
        self.assertIn(evidence, response,
                      "merge passed a response that does not contain its own "
                      "evidence, so the gate will reject the quote")

    def test_subagent_reports_cannot_claim_more_than_they_measured(self):
        """The fan-out validator is the only thing between model prose and the ledger.

        A subagent's conclusion is hypothesizer output. If a report that summarises
        instead of quoting, or that calls a timeout a confirm, is merged, then model
        text has entered the place a captured response belongs -- which is the one
        failure the whole control loop is built to prevent. Each case below is an
        over-claim that MUST be refused, plus two honest reports that must pass.
        """
        sys.path.insert(0, str(ROOT / "tools"))
        import subagent_fanout as fan

        honest_confirm = {"layer_id": "template-sink", "class": "web-ssti",
                          "falsifier_outcome": "broken", "probes": [{
                              "request": "GET /p?n={{7*7}}", "transport": "ok",
                              "response_excerpt": "<h1>Hello 49</h1>", "evidence": "49",
                              "evidence_kind": "class", "verdict": "confirms"}]}
        honest_negative = {"layer_id": "upload", "class": "web-file-upload",
                           "falsifier_outcome": "held", "probes": [{
                               "request": "GET /uploads/m.txt", "transport": "ok",
                               "response_excerpt": "Content-Type: text/plain",
                               "evidence": "Content-Type: text/plain",
                               "evidence_kind": "class", "verdict": "refutes"}]}
        for name, report in (("honest confirm", honest_confirm),
                             ("honest negative", honest_negative)):
            problems, _ = fan.validate_report(report)
            self.assertEqual(problems, [], "%s was refused: %s" % (name, problems))

        def probe(**over):
            base = {"request": "GET /", "transport": "ok",
                    "response_excerpt": "<h1>Hello 49</h1>", "evidence": "49",
                    "evidence_kind": "class", "verdict": "confirms"}
            base.update(over)
            return {"layer_id": "l", "probes": [base]}

        refusals = {
            "a summary instead of a quote":
                probe(evidence="the template evaluated arithmetic"),
            "a timeout as a confirm":
                probe(transport="timeout", response_excerpt="", evidence=""),
            "surface evidence as a confirm":
                probe(evidence_kind="surface"),
            "a write-shaped probe from a subagent":
                probe(request="DELETE /api/users"),
            "a confirm with no evidence at all":
                probe(evidence="", response_excerpt=""),
            "a transport failure not recorded as inconclusive":
                probe(transport="reset", response_excerpt="", evidence="",
                      evidence_kind="transport", verdict="refutes"),
        }
        for label, report in refusals.items():
            problems, _ = fan.validate_report(report)
            self.assertTrue(problems, "the validator ACCEPTED %s" % label)

        # the probe ceiling is the same five decide.py enforces per class
        sixth = {"layer_id": "l", "probes": [
            {"request": "GET /%d" % i, "transport": "ok", "response_excerpt": "x",
             "evidence": "x", "evidence_kind": "surface", "verdict": "inconclusive"}
            for i in range(fan.PROBE_CEILING + 1)]}
        problems, _ = fan.validate_report(sixth)
        self.assertTrue(any("ceiling" in p for p in problems),
                        "a sixth probe in one layer was not refused: %s" % problems)

    def test_web_fanout_briefs_come_from_the_taxonomy_and_short_circuit(self):
        """The web sweep must not invent a class, and must not sweep past a known answer.

        Two failures this guards. First, a family map that names a class id the
        taxonomy does not have would hand a subagent a first_probe and a falsifier
        that nobody wrote -- so every class id is resolved, and an unresolved one is
        flagged rather than filled in. Second, a strong chain match means the answer
        is already on disk: ten parallel guesses cost more than running that card's
        own probe, so the sweep has to say so instead of starting.
        """
        sys.path.insert(0, str(ROOT / "tools"))
        import subagent_fanout as fan

        taxonomy = {c["id"] for c in json.loads(
            (ROOT / "knowledge" / "bug-classes.json").read_text(encoding="utf-8"))["classes"]}
        named = [cid for spec in fan.WEB_FAMILIES for cid in spec["classes"]]
        self.assertTrue(named, "the web family map names no classes at all")
        unknown = sorted(set(named) - taxonomy)
        self.assertEqual(unknown, [],
                         "the web family map names classes absent from the taxonomy: %s"
                         % unknown)

        agents_dir = ROOT / ".claude" / "agents"
        for spec in fan.WEB_FAMILIES:
            self.assertTrue((agents_dir / (spec["agent"] + ".md")).is_file(),
                            "family %r spawns %r, which has no definition under "
                            ".claude/agents" % (spec["family"], spec["agent"]))
        write_shaped = [s["family"] for s in fan.WEB_FAMILIES if s.get("write_shaped")]
        self.assertEqual(write_shaped, ["race"],
                         "exactly one web family may be write-shaped, and it is the race "
                         "family; got %s" % write_shaped)

        # with no handout there is no reading list and no short circuit, but the
        # families and their taxonomy fields must still be complete
        bare = fan.web_briefs(None, "http://example.invalid", "t")
        self.assertEqual(bare["families"], len(fan.WEB_FAMILIES))
        self.assertIsNone(bare["strong_chain_match"])
        for brief in bare["briefs"]:
            for cls in brief["classes"]:
                self.assertNotIn("_missing_from_taxonomy", cls,
                                 "%s carries an unresolved class: %s"
                                 % (brief["family"], cls))
                self.assertTrue(cls.get("first_probe"),
                                "%s has no first_probe from the taxonomy" % cls["id"])
                self.assertTrue(cls.get("falsifier"),
                                "%s has no falsifier from the taxonomy" % cls["id"])

        # a handout whose card is a STRONG match must short-circuit the sweep
        src = ROOT / "challenges" / "Spell Orsterra"
        if not src.is_dir():
            self.skipTest("the Spell Orsterra handout is not on disk")
        hit = fan.web_briefs(str(src), None, "spell")
        self.assertIsNotNone(hit["strong_chain_match"],
                             "a handout whose own chain card scores `candidate` produced "
                             "no short circuit, so the sweep would run past the answer")
        self.assertNotIn("error", hit["strong_chain_match"],
                         "the short circuit reported an error instead of a match: %s"
                         % hit["strong_chain_match"])
        self.assertIn("first_confirming_probe",
                      hit["strong_chain_match"].get("do_this_instead", ""),
                      "the short circuit does not say to run the card's own probe")

    def test_dfir_family_map_resolves_and_covers_every_dfir_class(self):
        """The DFIR counterpart of the web family map, plus two stricter checks.

        Same failure to prevent: a family naming a class id that nothing defines
        spawns an agent briefed on a class nobody wrote. Two things are checked
        here that the web test does not, because this category is newer and both
        were real mistakes while it was built:

        (a) COVERAGE. Every `dfir-*` class in the taxonomy must be owned by at
            least one family. A class with no family is a class the sweep silently
            never measures -- and `dfir-persistence-trace` was briefly in that
            state, reachable only through an agent that reads EVTX.
        (b) A SHARED CLASS MUST BE SPLIT EXPLICITLY. Three DFIR classes are owned
            by two families each (event-log versus on-disk, Windows versus Linux,
            cleared-log versus timestamp). Both families must carry an `owns`
            field saying which half, or two agents measure the same artifact and
            the main thread cannot tell which report answered the question.
        """
        sys.path.insert(0, str(ROOT / "tools"))
        import subagent_fanout as fan

        taxonomy = {c["id"]: c for c in json.loads(
            (ROOT / "knowledge" / "bug-classes.json").read_text(encoding="utf-8"))["classes"]}
        named = [cid for spec in fan.DFIR_FAMILIES for cid in spec["classes"]]
        self.assertTrue(named, "the dfir family map names no classes at all")
        unknown = sorted(set(named) - set(taxonomy))
        self.assertEqual(unknown, [],
                         "the dfir family map names classes absent from the "
                         "taxonomy: %s" % unknown)
        for cid in set(named):
            self.assertEqual(taxonomy[cid].get("category"), "dfir",
                             "%s is in the dfir family map but its taxonomy "
                             "category is %r" % (cid, taxonomy[cid].get("category")))

        # (a) coverage: no dfir class may be left without a family
        dfir_classes = {cid for cid, cls in taxonomy.items()
                        if cls.get("category") == "dfir"}
        uncovered = sorted(dfir_classes - set(named))
        self.assertEqual(uncovered, [],
                         "these dfir classes have no family, so --dfir would never "
                         "brief an agent on them: %s" % uncovered)

        # (b) a class owned by two families must have both halves named
        counts = {}
        for spec in fan.DFIR_FAMILIES:
            for cid in spec["classes"]:
                counts.setdefault(cid, []).append(spec)
        for cid, specs in counts.items():
            if len(specs) < 2:
                continue
            for spec in specs:
                self.assertTrue(
                    spec.get("owns"),
                    "%s is owned by %d families, so %r must carry an `owns` field "
                    "saying which half it measures" % (cid, len(specs),
                                                       spec["family"]))

        agents_dir = ROOT / ".claude" / "agents"
        for spec in fan.DFIR_FAMILIES:
            self.assertTrue((agents_dir / (spec["agent"] + ".md")).is_file(),
                            "dfir family %r spawns %r, which has no definition "
                            "under .claude/agents" % (spec["family"], spec["agent"]))

        # An investigation reads supplied artifacts, so there is no target to
        # mutate and no family may be write-shaped.
        write_shaped = [s["family"] for s in fan.DFIR_FAMILIES if s.get("write_shaped")]
        self.assertEqual(write_shaped, [],
                         "no dfir family may be write-shaped: an investigation "
                         "reads artifacts; got %s" % write_shaped)

        # with no bundle there is no artifact inventory, but every taxonomy field
        # the brief promises must still be present
        bare = fan.dfir_briefs(None, None, "t")
        self.assertEqual(bare["families"], len(fan.DFIR_FAMILIES))
        self.assertEqual(bare["launch_order"][0], "recon",
                         "recon must be briefed first: every other dfir family "
                         "routes against its inventory")
        for brief in bare["briefs"]:
            self.assertEqual(brief["artifacts_that_fired"], [],
                             "%s invented an artifact hit with no bundle supplied"
                             % brief["family"])
            self.assertIn("pre-flag", brief["recording_rule"],
                          "%s does not say a dfir answer is recorded with pre-flag"
                          % brief["family"])
            for cls in brief["classes"]:
                self.assertNotIn("_missing_from_taxonomy", cls,
                                 "%s carries an unresolved class: %s"
                                 % (brief["family"], cls))
                self.assertTrue(cls.get("first_probe"),
                                "%s has no first_probe from the taxonomy" % cls["id"])
                self.assertTrue(cls.get("falsifier"),
                                "%s has no falsifier from the taxonomy" % cls["id"])

        # The sweep skill's family table must match the code. Measured: adding the
        # eighth family left the skill saying "seven families" with a seven-row
        # table, which is the kind of drift a reader believes over the code.
        sweep = (ROOT / "skills" / "dfir-parallel-sweep" / "SKILL.md")
        if sweep.is_file():
            text = sweep.read_text(encoding="utf-8")
            rows = [l for l in text.splitlines()
                    if l.startswith("| ") and "ctf-dfir-" in l]
            listed = {l.split("|")[1].strip() for l in rows}
            declared = {s["family"] for s in fan.DFIR_FAMILIES}
            self.assertEqual(
                listed, declared,
                "skills/dfir-parallel-sweep/SKILL.md's family table disagrees with "
                "DFIR_FAMILIES: missing %s, extra %s"
                % (sorted(declared - listed), sorted(listed - declared)))

        # chain recall must state its own emptiness rather than looking broken
        recall = bare["chain_recall"]
        self.assertNotIn("error", recall,
                         "dfir chain recall reported an error: %s" % recall)
        self.assertIn(recall.get("status"), ("cannot_fire", "cards_exist"),
                      "dfir chain recall returned no usable status: %s" % recall)

    def test_dfir_merge_emits_pre_flag_not_post_probe(self):
        """A DFIR answer comes from an artifact, so the command that records it
        differs from the web one -- and emitting the wrong one is silent.

        `tools/hooks.py post-probe` records a verdict about a bug class; a
        Sherlock answer is a fact read from a supplied artifact and enters state
        through `pre-flag --source artifact`. A merge that emitted post-probe for
        a dfir class would hand the operator a command that records the wrong
        kind of thing, so this pins the branch.
        """
        sys.path.insert(0, str(ROOT / "tools"))
        import subagent_fanout as fan

        report = {
            "layer_id": "linux", "challenge": "sher-q1",
            "class": "dfir-authentication-trace",
            "falsifier_outcome": "broken",
            "probes": [{
                "request": "linux_auth.py --authlog auth.log --event accepted",
                "transport": "ok", "status": 0,
                "response_excerpt": "Mar  6 06:32:44 web-01 sshd[2455]: Accepted "
                                    "password for root from 198.51.100.77 port 53184 ssh2",
                "evidence": "Accepted password for root from 198.51.100.77",
                "evidence_kind": "impact", "verdict": "confirms",
            }],
        }
        problems, norm = fan.validate_report(report)
        self.assertEqual(problems, [], "the fixture report should validate: %s" % problems)

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "linux.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(report, fh)
            out = fan.merge([path], "sher")
        self.assertEqual(out["rejected"], [], "merge rejected a valid report: %s"
                         % out["rejected"])
        joined = "\n".join(out["commands_for_the_main_thread"])
        self.assertIn("pre-flag", joined,
                      "a dfir class did not produce a pre-flag command: %s" % joined)
        self.assertIn("--source artifact", joined,
                      "the dfir pre-flag command must record --source artifact")
        self.assertNotIn("post-probe", joined,
                         "a dfir class must NOT be recorded with post-probe: %s" % joined)
        # the answer VALUE is the one field a tool must not guess
        self.assertIn("<ANSWER>", joined,
                      "the pre-flag template must leave the answer value for the "
                      "main thread to fill, not invent it")

    def test_subagent_capability_matches_the_invariant(self):
        """What a subagent may do, and the one thing it may never do.

        This test used to ban `Write` outright. That was measured wrong: on a
        GraphQL target every step past recon was a POST and the agent needed to
        author a client and an exploit script to take any of them, so with no
        Write the whole fleet could only look, and the solve happened with no
        subagent at all. Write is now REQUIRED of the ctf-* agents and paired
        with a scratch-only rule; `Edit` stays banned, because Edit is the tool
        that would let an agent surgically rewrite a rule file it had not read.

        The absolute rule is the LEDGER, not the filesystem: `tools/decide.py`
        enforces five probes per class and twenty-five per challenge, so agents
        recording probes in parallel would spend that budget in one round.
        """
        agents = sorted((ROOT / ".claude" / "agents").glob("*.md"))
        self.assertTrue(agents, "no subagent definitions found")
        writers = []
        for path in agents:
            text = path.read_text(encoding="utf-8")
            head = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            self.assertTrue(head, "%s has no YAML frontmatter" % path.name)
            fields = dict(re.findall(r"^(\w[\w-]*):\s*(.+)$", head.group(1), re.M))
            self.assertEqual(fields.get("name"), path.stem,
                             "%s: frontmatter name must equal the filename" % path.name)
            self.assertGreater(len(fields.get("description", "")), 60,
                               "%s: description is too short to route on" % path.name)
            self.assertIn("tools", fields,
                          "%s: no tools list, so it inherits everything" % path.name)
            declared = {t.strip() for t in fields["tools"].split(",")}

            for banned in ("Edit", "NotebookEdit"):
                self.assertNotIn(banned, declared,
                                 "%s declares %s, which can rewrite a rule file in "
                                 "place; agents get Write for scratch work instead"
                                 % (path.name, banned))
            self.assertRegex(
                text, r"[Dd]o not run `tools/hooks\.py`|off-limits",
                "%s does not keep the ledger off-limits; parallel agents would "
                "race the probe budget decide.py enforces" % path.name)

            if "Write" in declared:
                writers.append(path.name)
                self.assertIn("Where you may write", text,
                              "%s has Write but no section saying where" % path.name)
                # two zones: a workspace with full rights OUTSIDE this repository,
                # and this repository read-only. An agent told it may write but not
                # told where will invent a path, and two agents inventing the same
                # path have already destroyed each other's work here.
                self.assertIn("ctf-work", text,
                              "%s has Write but never names the workspace outside this "
                              "repository, so it has nowhere sanctioned to work"
                              % path.name)
                for guarded in ("tools/", "skills/", "knowledge/", "test/"):
                    self.assertIn(guarded, text,
                                  "%s has Write but never names %s as off-limits"
                                  % (path.name, guarded))
                self.assertRegex(
                    text, r"never delete anything above|Never delete anything above",
                    "%s has Write but does not forbid deleting above its own "
                    "directory, which is how one agent destroyed another's work"
                    % path.name)
        self.assertTrue(writers,
                        "no subagent can write at all -- that is the state that made "
                        "the fleet unable to take any step past recon")

    # Tools CLAUDE.md records as measured absent on this machine. An agent told
    # to run one of these fails at the shell, and the failure looks like the
    # technique not working rather than the tool not existing.
    ABSENT_TOOLS = ("pwntools", "gdb", "ROPgadget", "ropper", "one_gadget",
                    "checksec", "patchelf", "strace", "ltrace", "angr",
                    "unicorn", "keystone", "ropper", "pyelftools", "z3", "sage",
                    "fpylll", "gmpy2", "jadx", "procyon", "mono", "decompyle3",
                    "pycdc", "steghide", "zsteg", "outguess", "foremost",
                    "yara", "volatility3", "stem", "pytesseract")

    def test_no_subagent_is_told_to_run_a_tool_this_box_does_not_have(self):
        """Measured twice while building this fleet, both times silently.

        `skills/pwn-rop/SKILL.md` carried whole "ROPgadget Commands" and "ropper
        Commands" sections for tools CLAUDE.md records as ABSENT, and an
        authored crypto agent put `--list` in a bash block for a subcommand that
        is not a flag. Neither is caught by the tool-path or tool-flag tests,
        because those only read `python3 tools/...` lines.

        The rule is narrow on purpose: naming a tool as absent is correct and is
        what these files should do. Only RUNNING it is a violation, so this
        looks for the tool as the first token of a line inside a fenced code
        block, which is the shape of an instruction.
        """
        offenders = []
        for path in sorted((ROOT / ".claude" / "agents").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for block in re.findall(r"```(?:bash|sh|console)?\n(.*?)```", text, re.S):
                for line in block.splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    first = re.split(r"[\s|;&]", stripped.lstrip("$ "))[0]
                    first = first.rsplit("/", 1)[-1]
                    if first in self.ABSENT_TOOLS:
                        offenders.append("%s: %s" % (path.name, stripped[:70]))
        self.assertEqual(sorted(set(offenders)), [],
                         "a subagent is told to run a tool measured absent on this "
                         "machine: %s" % sorted(set(offenders))[:6])

    def test_every_subagent_pins_a_model(self):
        """An unpinned agent silently falls back to the session default.

        Measured: `ctf-crypto-ladder` and `ctf-pwn-triage` shipped with no
        `model:` line at all, so the two hardest-reasoning categories in the
        tree ran on whatever the session happened to be using. Crypto is this
        toolkit's measured zero in a real contest, which makes it the worst
        place for that to be left to chance.
        """
        missing = []
        for path in sorted((ROOT / ".claude" / "agents").glob("*.md")):
            head = re.match(r"^---\n(.*?)\n---\n",
                            path.read_text(encoding="utf-8"), re.S)
            if not head or not re.search(r"(?m)^model:\s*\S+", head.group(1)):
                missing.append(path.name)
        self.assertEqual(missing, [],
                         "these subagents pin no model and inherit the session's: %s"
                         % missing)

    def test_every_solver_subagent_returns_the_flag_contract(self):
        """A solver may reach a flag, so its report has to carry the proof.

        The crypto, pwn, rev, osint and misc fleets differ from the measure-only
        ctf-web-* and ctf-dfir-* families: they are permitted to chain their own
        findings to a flag. That is only safe because the flag comes back with
        the bytes it was read from and the command that produced them, which
        `.claude/workflows/solver-fleet.js` then checks mechanically before a
        human sees it. An agent whose return block omits those keys hands back a
        flag nobody can check.
        """
        required = ("flag_candidate", "flag_source", "flag_evidence",
                    "flag_command", "measured_dead", "next_lead")
        solver = re.compile(r"^ctf-(crypto|pwn|rev|osint|misc)-")
        checked, offenders = 0, []
        for path in sorted((ROOT / ".claude" / "agents").glob("*.md")):
            if not solver.match(path.stem) or path.stem.endswith("-ladder"):
                continue
            checked += 1
            text = path.read_text(encoding="utf-8")
            for key in required:
                if key not in text:
                    offenders.append("%s is missing %s" % (path.name, key))
        self.assertGreater(checked, 10,
                           "only %d solver agents were checked; the pattern has "
                           "stopped matching and this proves nothing" % checked)
        self.assertEqual(sorted(offenders), [],
                         "a solver subagent's return block cannot be verified: %s"
                         % sorted(offenders)[:6])

    def test_a_stage_lead_is_a_card_to_read_and_never_a_probe_to_run(self):
        """The transfer path, and the bound that makes it safe to ship.

        A card's `signals` are literals from its own handout, so a new challenge
        sharing the MECHANISM shares none of them: tools/holdout_eval.py measures
        card-level transfer at 0.0. Its `chain[]` prose is mechanism vocabulary
        instead, and matching on that reaches the right peer about a quarter of
        the time in the top three -- measured against
        test/baselines/mechanism_families.json.

        A quarter is nowhere near enough to grade a match `candidate`. That
        grade gates --record and hands decide.py a probe, so being wrong three
        times in four would be worse than silence. This test is the bound: a
        stage lead must stay weak, must say why, and must never be recordable.
        """
        sys.path.insert(0, str(ROOT / "tools"))
        import chain_match as cm
        cards = [c for c in cm.load_chains() if "_error" not in c]
        self.assertTrue(cards, "no chain cards to index")

        index = cm.build_stage_index(cards)
        self.assertGreater(len(index["units"]), 50,
                           "the stage index covers almost no cards")
        self.assertGreater(sum(len(u) for u in index["units"].values()), 1000,
                           "the stage index holds too few terms to retrieve on")

        # A card scored against its OWN stage prose must produce a lead, which
        # proves the index and the scorer are wired to each other at all.
        probe = max(cards, key=lambda c: len(index["units"].get(c["id"]) or ()))
        tokens = cm.stage_tokens(cm.stage_text(probe))
        weight, hits = cm.stage_lead_score(probe, tokens, index)
        self.assertGreater(weight, 0.0,
                           "a card does not even match its own stage prose")
        self.assertGreaterEqual(hits, cm.STAGE_MIN_HITS)

        # And the lead it produces is weak, explained, and not recordable.
        lead = cm.score_card(probe, "nothing matches here", "nothing matches here",
                             None, source_mode=True, scope={},
                             stage_index=index, query_tokens=tokens)
        self.assertIsNotNone(lead, "a stage overlap must surface as a lead")
        self.assertEqual(lead["match_via"], "stage")
        self.assertEqual(lead["status"], "weak",
                         "a stage lead must never be graded candidate: that "
                         "grade gates --record and feeds decide.py a probe")
        self.assertEqual(lead["signals_matched"], [],
                         "a stage lead matched no literal by definition")
        self.assertEqual(lead["signal_coverage"], 0.0)
        self.assertLessEqual(lead["match_confidence"], 0.30,
                             "a lead must not report a confidence that reads "
                             "like a literal match")
        self.assertIn("do NOT run its probe", lead["why_weak"])

        # record_candidates is the gate between a match and the ledger: a weak
        # entry must not pass it, or a 25%-accurate lead would drive the loop.
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            (root / "challenges" / "leadonly").mkdir(parents=True)
            (root / "challenges" / "leadonly" / "state.json").write_text(
                json.dumps({"schema_version": 1, "name": "leadonly",
                            "hypotheses": [], "probes": [], "next_action": None}),
                encoding="utf-8")
            # record_candidates imports `state` inside the function, so the
            # module object in sys.modules is what it will use.
            with patch.object(cm, "ROOT", str(root)), \
                    patch.object(state, "ROOT", str(root)):
                out = cm.record_candidates("leadonly", [lead])
            self.assertFalse(out.get("recorded"),
                             "a weak stage lead was written into the ledger")
            written = json.loads(
                (root / "challenges" / "leadonly" / "state.json").read_text(
                    encoding="utf-8"))
            self.assertFalse(written.get("chain_candidates"),
                             "a weak lead reached state['chain_candidates'], "
                             "which decide.py rule 6 turns into a probe")

    def test_every_retrieval_alias_re_proves_itself(self):
        """An alias file is a place to smuggle in a wrong pairing, so re-measure.

        chain_match_eval pairs a card to its handout by name. An alias overrides
        that pairing by hand, which is exactly the kind of edit that can move
        top1_rate without anyone auditing why -- so every alias must still hold:
        the directory has to exist, hold real source, and the named card has to
        rank FIRST on it. A stale or invented alias fails here rather than
        quietly flattering the metric.
        """
        path = ROOT / "test" / "baselines" / "chain_match_aliases.json"
        if not path.exists():
            self.skipTest("no alias file; the eval falls back to name matching")
        payload = json.loads(path.read_text(encoding="utf-8"))
        aliases = payload.get("aliases") or {}
        self.assertTrue(payload.get("_why"), "the alias file must say why it exists")
        sys.path.insert(0, str(ROOT / "tools"))
        import chain_match
        import chain_match_eval as ev

        cards = [c for c in chain_match.load_chains(chain_match.CHAINS)
                 if "_error" not in c]
        by_id = {c["id"]: c for c in cards}
        stats = chain_match.load_signal_stats()
        seen_dirs = {}
        absent_dirs = []
        seen_measured = 0
        for name, entry in aliases.items():
            directory, card_id = entry.get("directory"), entry.get("card")
            self.assertTrue(directory and card_id,
                            "alias %r must name both a directory and a card" % name)
            self.assertNotIn(directory, seen_dirs,
                             "directory %r is claimed by two aliases (%s and %s); "
                             "one of them is wrong" % (directory,
                                                      seen_dirs.get(directory), name))
            # Both of these are properties of the alias FILE and need no handout,
            # so they keep running on a clone: two aliases claiming one directory
            # is still wrong, and so is naming a card that no longer exists.
            seen_dirs[directory] = name
            self.assertIn(card_id, by_id,
                          "alias %r names a card that no longer exists: %s" % (name, card_id))
            src = ROOT / "challenges" / directory
            if not src.is_dir():
                # challenges/ is gitignored; only force-added fixtures reach a
                # clone. The RE-MEASUREMENT below needs the handout, so it is
                # skipped here and still runs on any machine that has it.
                absent_dirs.append(directory)
                continue
            text = chain_match.read_source(str(src))
            self.assertTrue(text.strip(),
                            "alias %r points at a directory with no readable "
                            "source, so the pairing cannot have been measured" % name)
            seen_measured += 1
            ranked = ev.rank_cards(cards, text, None, stats)
            self.assertTrue(ranked, "nothing ranked on %r at all" % directory)
            self.assertEqual(
                ranked[0]["id"], card_id,
                "alias %r claims %s for %r, but %s ranks first there -- the alias "
                "is stale or wrong, and it is moving top1_rate" % (
                    name, card_id, directory, ranked[0]["id"]))

        # Say plainly how much of this check actually ran. Silence here would let
        # a clone report a green alias test having re-measured nothing at all.
        if absent_dirs and not seen_measured:
            self.skipTest("no alias handout is present in this checkout, so no "
                          "pairing could be re-measured: %s" % ", ".join(absent_dirs))
        if absent_dirs:
            print("\n  note: %d of %d alias pairing(s) not re-measured, handout "
                  "absent: %s" % (len(absent_dirs), len(aliases), ", ".join(absent_dirs)))

    def test_chain_match_retrieval_does_not_regress(self):
        baseline_path = ROOT / "test" / "baselines" / "chain_match.json"
        if not baseline_path.is_file():
            self.skipTest("no retrieval baseline recorded")
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        floor = baseline.get("floor_top1_rate")
        if floor is None:
            self.skipTest("baseline records no floor")
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "chain_match_eval.py")],
            capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(proc.returncode, 0, proc.stderr[:400])
        report = json.loads(proc.stdout)
        if report["cards_with_ground_truth"] < 5:
            self.skipTest("too few handouts on disk to measure retrieval")
        self.assertGreaterEqual(
            report["top1_rate"], floor,
            "chain_match no longer retrieves the right card often enough: "
            "%.3f < floor %.3f. Fix the matcher or the card's signals; do not "
            "lower the floor to make this pass."
            % (report["top1_rate"], floor))


class LocalSolveRecallTests(unittest.TestCase):
    """The cheapest retrieval route, and the one the tree did not have.

    Measured, which is why these exist: a target named NovaCore was worked with
    a 13-agent sweep for 1.03M tokens while `solved/novacore.md` and a 498-line
    working `challenges/novacore/solver.py` sat on this disk the whole time. The
    flag came, in the end, from that solver with its host and port line edited.
    chain_match reads only knowledge/chains/ and scores card SIGNALS against an
    observation, so nothing in the tree ever asked the simplest question: has a
    challenge of THIS NAME already been solved here?
    """

    def test_a_matching_name_is_found(self):
        hit = chain_match.local_solve("novacore")
        self.assertIsNotNone(hit, "solved/novacore.md is on disk and must be found")
        self.assertIn("solved/novacore.md", hit["notes"])

    def test_a_suffixed_respawn_finds_the_original(self):
        # The case that actually cost the tokens: a re-spawned instance is
        # registered as <name>2 while the solve sits under <name>.
        hit = chain_match.local_solve("novacore2")
        self.assertIsNotNone(hit, "a suffixed name must still find the original solve")
        self.assertIn("solved/novacore.md", hit["notes"])
        self.assertIn("challenges/novacore/solver.py", hit["solvers"])

    def test_an_unseen_name_stays_silent(self):
        # Abstention matters more than recall here: a false hit sends the next
        # agent to read a solve for a different challenge.
        self.assertIsNone(chain_match.local_solve("zzz-never-seen-here"))

    def test_a_short_or_empty_name_cannot_match(self):
        # A 1-3 character name would substring-match most of the corpus.
        for name in ("", None, "a", "ab", "abc"):
            self.assertIsNone(chain_match.local_solve(name),
                              "%r is too short to match on safely" % (name,))

    def test_every_solved_note_finds_itself_and_few_others(self):
        notes = sorted(p.name[:-3] for p in (ROOT / "solved").glob("*.md"))
        self.assertGreater(len(notes), 20, "corpus too small to measure")
        for name in notes:
            hit = chain_match.local_solve(name)
            self.assertIsNotNone(hit, "%s must find its own note" % name)
            self.assertIn("solved/%s.md" % name, hit["notes"])
            # A name may legitimately match a sibling of the same challenge
            # family (red-island / red-island-2), so the bound is low, not one.
            self.assertLessEqual(
                len(hit["notes"]), 3,
                "%s matched %d notes; the prefix rule is too loose and a false "
                "hit sends the next agent to the wrong solve: %s"
                % (name, len(hit["notes"]), hit["notes"]))

    def test_the_check_owns_next_action_ahead_of_every_similarity_score(self):
        # A recorded solve for this exact name must not be printed underneath a
        # "no strong match, plan from source" verdict -- that is how it was
        # missed. It has to be the instruction, not a field.
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "chain_match.py"),
             "--source", "challenges/novacore2", "--json"],
            capture_output=True, text=True, cwd=str(ROOT))
        self.assertIn(proc.returncode, (0, 1), proc.stderr[:400])
        report = json.loads(proc.stdout)
        self.assertEqual(report["input"]["name_checked"], "novacore2",
                         "the name must be derived from the source path")
        self.assertIsNotNone(report["local_solve"])
        self.assertIn("solved/novacore.md", report["next_action"])
        self.assertNotIn("no solved chain is a strong match", report["next_action"])

    def test_the_scout_is_told_to_run_it_first(self):
        # The tool existing is not the fix; the agent that runs first has to
        # know about it. Measured before this: 0 references to solver.py.
        body = (ROOT / ".claude" / "agents" / "ctf-killmap-scout.md").read_text(
            encoding="utf-8")
        self.assertIn("local_solve", body)
        self.assertIn("solver.py", body)
        self.assertIn("--name", body)

class EveryChainCardValidatesTests(unittest.TestCase):
    """The gate validated a card when one was WRITTEN and never the library.

    Measured: 21 of 73 cards on disk failed their own schema, because
    backfill_classification.py wrote a `classification.derived_by` key that
    knowledge/chain-schema.json forbade with additionalProperties:false. The
    writer and the schema disagreed for 21 cards and nothing reported it,
    because validate_card.py is only ever pointed at one file by hand. A
    knowledge base whose own schema rejects a third of it cannot be trusted to
    reject anything, so the whole library is checked here.
    """

    def test_every_chain_card_satisfies_the_chain_schema(self):
        cards = sorted((ROOT / "knowledge" / "chains").glob("*.json"))
        self.assertGreater(len(cards), 60, "chain library unexpectedly small")
        # In-process: 73 subprocesses took 72 seconds, and this runs on the
        # gate for every change.
        sys.path.insert(0, str(ROOT / "tools"))
        import validate_card
        failures = []
        for card in cards:
            try:
                data = json.loads(card.read_text(encoding="utf-8"))
            except ValueError as exc:
                failures.append((card.name, "unparseable: %s" % exc))
                continue
            errors = validate_card.validate(data)
            if errors:
                failures.append((card.name, errors))
        self.assertEqual(
            failures, [],
            "%d of %d chain cards fail their own schema. Fix the card or the "
            "schema -- but do not leave the writer and the schema disagreeing, "
            "which is how 21 cards were invalid without anyone noticing:\n%s"
            % (len(failures), len(cards),
               "\n".join("  %s: %s" % f for f in failures[:10])))

    def test_no_card_in_the_library_carries_a_real_flag(self):
        # validate_card.py already owns the detector and knows that `HTB{...}`
        # is how these cards redact; a second regex here would be a second
        # definition of the same rule, which is how the two rarity scorers in
        # this tree drifted apart. Reuse the one that ships.
        sys.path.insert(0, str(ROOT / "tools"))
        import validate_card
        leaked = [card.name
                  for card in sorted((ROOT / "knowledge" / "chains").glob("*.json"))
                  if validate_card._looks_like_a_real_flag(
                      card.read_text(encoding="utf-8"))]
        self.assertEqual(leaked, [],
                         "flag-shaped strings in chain cards: %s" % leaked)


class ForgedTrapsRepresentEveryCardTests(unittest.TestCase):
    """Step 5b must not silently drop a card it was run for.

    AGENTS.md section 5 says agent_prompt_forge exists so "a card's known_traps
    reach the agent that meets the same trap next". Measured: ctf-web-parser
    owns 10 cards carrying 78 traps, MAX_TRAPS is 12, and the forge concatenated
    them card-by-card -- so the first two or three cards filled the quota and a
    card filed afterwards contributed nothing, while `--check` reported nothing
    stale. Running the step after a solve was a no-op for every mature family.
    """

    def _families(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import subagent_fanout
        return list(subagent_fanout.WEB_FAMILIES) + list(subagent_fanout.DFIR_FAMILIES)

    def test_every_owned_card_contributes_at_least_one_trap(self):
        sys.path.insert(0, str(ROOT / "tools"))
        import agent_prompt_forge as forge
        cards, tax = forge.load_cards(), forge.taxonomy()
        checked = 0
        for family in self._families():
            owned = [c for c in forge.cards_for(family["classes"], cards, tax)
                     if c.get("known_traps")]
            if len(owned) < 2:
                continue
            block = forge.forge(family, cards, tax)
            if "### Traps this tree has already paid for" not in block:
                continue
            section = block.split("### Traps this tree has already paid for")[1]
            section = section.split("### ")[0]
            shown = set(re.findall(r"\*\((\S+?)\)\*", section))
            missing = sorted({c["id"] for c in owned} - shown)
            # Every card may not fit when a family owns more cards than
            # MAX_TRAPS; the invariant is that nothing is dropped while room
            # remains, which round-robin guarantees.
            if len(owned) <= forge.MAX_TRAPS:
                self.assertEqual(
                    missing, [],
                    "%s: %d of %d owned cards contribute no trap to the forged "
                    "prompt while room remained. Traps must be taken one per "
                    "card before any card's second, or filing a new card does "
                    "nothing for the fleet: %s"
                    % (family["agent"], len(missing), len(owned), missing))
            checked += 1
        self.assertGreater(checked, 0, "no family had enough cards to measure")

    def test_a_backslash_in_a_trap_does_not_crash_the_forge(self):
        """apply_to() spliced the block in with re.sub(), where the block is a
        REPLACEMENT TEMPLATE -- so a backslash in any card's trap was read as an
        escape. A card quoting the PHP class App\\Message\\FileQueue crashed the
        gate with `re.PatternError: bad escape \\M`, and it stayed hidden only
        because that trap fell beyond MAX_TRAPS until the ordering changed.
        """
        sys.path.insert(0, str(ROOT / "tools"))
        import agent_prompt_forge as forge
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "agent.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("hand-written top\n\n%s\nold\n%s\n\nhand-written tail\n"
                         % (forge.BEGIN, forge.END))
            block = "%s\nO:22:\"App\\Message\\FileQueue\" and a \\g<0> too\n%s" % (
                forge.BEGIN, forge.END)
            new, changed = forge.apply_to(path, block)
        self.assertTrue(changed)
        self.assertIn(r"App\Message\FileQueue", new,
                      "the backslashes must survive verbatim, not be interpreted")
        self.assertIn(r"\g<0>", new,
                      "a regex group reference in card text must stay literal")
        self.assertIn("hand-written top", new)
        self.assertIn("hand-written tail", new)

    def test_the_prompt_states_how_many_traps_it_left_out(self):
        # Silent truncation is what made the old behaviour invisible.
        sys.path.insert(0, str(ROOT / "tools"))
        import agent_prompt_forge as forge
        cards, tax = forge.load_cards(), forge.taxonomy()
        for family in self._families():
            owned = forge.cards_for(family["classes"], cards, tax)
            total = sum(len(c.get("known_traps") or []) for c in owned)
            if total <= forge.MAX_TRAPS:
                continue
            block = forge.forge(family, cards, tax)
            self.assertIn("NOT in this prompt", block,
                          "%s truncates traps without saying so" % family["agent"])
            return
        self.skipTest("no family exceeds MAX_TRAPS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
