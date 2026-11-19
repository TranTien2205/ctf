"""Static gates over the documents that are injected into a worker's context.

`argus/system.py` already derives what to tell an agent whose grant is
narrower than the shared playbook (`_grant_block`, and the `NO_LEDGER_BLOCK`
swap at `build_system`) - its own docstring records that an unconditional
`next_action()` instruction survived in a prompt no role could obey, which is
the bug that block exists to prevent.

Skill cards and role prompts are static text injected PAST that filter:
`load_skill` returns a card verbatim and `RoleCard.prompt()` appends a role
prompt verbatim, so nothing compares either against the role's tool grant.
Measured consequence, which is why this file exists: `report-writing.md` told
the report worker to call `next_action` and to read a `record_finding` result,
and `CARDS['report'].tools` grants neither - `dispatch` answers
"tool next_action is not available to role 'report'" and `AgentLoop` filters
the schema out of the model's tool list entirely, so the worker cannot even
see it. The same context also carried the system prompt's derived line saying
those tools belong to another worker, so the two contradicted each other.

These checks are deliberately static. They read the shipped text and the
shipped code and compare them; they start no agent and send no request.
"""
from __future__ import annotations

import inspect
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from argus import proof
from argus.team.cards import CARDS
from argus.tools.registry import TOOL_SCHEMAS

SKILLS = ROOT / "argus" / "skills"
ROLES = ROOT / "argus" / "team" / "roles"

TOOL_NAMES = {t["name"] for t in TOOL_SCHEMAS}


# --------------------------------------------------------------- extraction

def tools_named_in(text: str) -> set[str]:
    """Registry tools this document tells its reader to call.

    Two spellings, because cards use both: `name(args)` and a bare backticked
    `name`. `system._tools_named_in` reads only the first - which is why the
    backticked `next_action` and `record_finding` instructions in
    report-writing.md were invisible to every existing check. Only names that
    are real registered tools count; a prose word in backticks is not a
    promise, a tool name is.
    """
    found = set()
    for m in re.finditer(r"`([a-z_][a-z0-9_]*)`", text):
        if m.group(1) in TOOL_NAMES:
            found.add(m.group(1))
    for m in re.finditer(r"\b([a-z_][a-z0-9_]*)\s*\(", text):
        if m.group(1) in TOOL_NAMES:
            found.add(m.group(1))
    return found


def every_role_tool() -> set[str]:
    out: set[str] = set()
    for card in CARDS.values():
        out |= set(card.tools)
    return out


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ------------------------------------------- 1. cards name reachable tools

def test_the_extractor_sees_a_backticked_tool_name_too():
    """Instrument first: a check whose detector misses the shape it is for
    passes forever on nothing. This repo has four recorded instances of the
    instrument being the defect, so prove the detector before trusting it.
    """
    planted = "call `next_action` and read the `record_finding` result"
    assert tools_named_in(planted) == {"next_action", "record_finding"}
    # ...and a prose word in backticks is still not a tool
    assert tools_named_in("the `missing` checks and the `grade`") == set()


def test_every_tool_a_skill_card_names_is_callable_by_some_role():
    """A card naming a tool no card grants is a step no worker can take.

    Union over the role cards, not over the registry: a registered tool that
    no role holds is still unreachable from a card read inside a team run.
    """
    union = every_role_tool()
    offgrant = {}
    for card in sorted(SKILLS.glob("*.md")):
        extra = sorted(tools_named_in(read(card)) - union)
        if extra:
            offgrant[card.name] = extra
    assert not offgrant, f"named in a card, granted to no role: {offgrant}"


def test_report_writing_names_only_tools_the_report_role_holds():
    """The failing direction of this file.

    `report-writing.md` is the card whose signal row is "Findings recorded;
    the report is next", so the role that loads it is `report`. Measured
    before the fix: the card named `next_action`, `record_finding` and
    `finish_engagement`, none of which `CARDS['report'].tools` contains.
    """
    named = tools_named_in(read(SKILLS / "report-writing.md"))
    denied = sorted(named - set(CARDS["report"].tools))
    assert not denied, (
        f"report-writing.md instructs {denied}; dispatch refuses them for "
        f"role 'report' and loop.py filters their schemas out of the "
        f"model's tool list")
    # the card has to be about tools at all - an empty set would pass the
    # assertion above while teaching nothing
    assert "read_findings" in named


def test_the_subset_check_catches_a_planted_off_grant_tool():
    """Same instrument, the other direction: a card body that names an
    exploit-only tool must be flagged against the report grant."""
    planted = "then call `probe_sqli` and record it with `record_finding`"
    denied = tools_named_in(planted) - set(CARDS["report"].tools)
    assert denied == {"probe_sqli", "record_finding"}


def test_role_prompt_names_only_tools_that_role_holds():
    """The same rule for the other static document in a worker's context.

    `system._grant_block` derives this for the shared playbook; a role prompt
    is appended after it and is checked by nothing.
    """
    bad = {}
    for name, card in sorted(CARDS.items()):
        path = ROLES / card.prompt_file
        if not path.exists():
            continue
        denied = sorted(tools_named_in(read(path)) - set(card.tools))
        if denied:
            bad[card.prompt_file] = denied
    assert not bad, f"role prompts instruct tools their own card denies: {bad}"


# ------------------------------------------------- 2. grade vocabulary

_GRADE_ADJECTIVE = re.compile(
    r"(?i)\b(?:a|an|the)\s+`?([a-z][a-z-]{2,20})`?\s+grade\b")

# Narrow on purpose: these are the shapes that assert a ceiling held a grade
# down, which is a claim about the matrix and not a turn of phrase.
_CAP_CLAIM = re.compile(
    r"(?i)capped\s+grade|capped\s+at\s+`?[a-z]+`?|ceiling\s+held"
    r"|\bis\s+capped\b|\bare\s+capped\b")

# Empty, and it emptied the way an exemption should. `ssrf.md` was listed
# here because it still said the class "is capped at `candidate` here on
# purpose" while the matrix had no ceiling left - a sentence loaded into the
# agent's prompt telling it not to collect the one artifact `proven` now
# needs. The entry carried the note that this list fails the day the claim
# goes, the claim went, and the list failed. An exemption that cannot
# outlive its reason is the only kind worth having.
_CAP_CLAIM_EXEMPT: set[str] = set()


def capped_classes() -> set[str]:
    return {s.vuln_class for s in proof.MATRIX.values() if s.ceiling}


def test_a_grade_word_in_a_skill_card_is_a_real_grade():
    """`proof.GRADES` is the whole vocabulary; prose may not add to it.

    Measured before the fix: report-writing.md:53 taught "A capped grade
    means the ceiling held it down rather than the evidence falling short".
    `capped` is not a grade - it is a separate annotation field on `Verdict`,
    rendered as `capped_by_this_system` - so the one card about not inventing
    facts invented a grade.
    """
    allowed = set(proof.GRADES) | {"proof", "ungraded"}
    bad = {}
    for card in sorted(SKILLS.glob("*.md")):
        invented = sorted(set(_GRADE_ADJECTIVE.findall(read(card))) - allowed)
        if invented:
            bad[card.name] = invented
    assert not bad, (
        f"cards name grades outside proof.GRADES {proof.GRADES}: {bad}")


def test_the_grade_word_check_catches_a_planted_invented_grade():
    assert _GRADE_ADJECTIVE.findall(
        "Never round up. A capped grade means the ceiling held it down") \
        == ["capped"]
    assert "capped" not in proof.GRADES


def test_no_skill_card_claims_a_cap_the_matrix_does_not_apply():
    """A cap is a fact about `ProofSpec.ceiling`, not a way to excuse a
    shortfall. With no class capped, a card that blames a ceiling sends the
    reader to write "capped by this system" over a `candidate` whose real
    unmet check is printed in the report beside it.
    """
    capped = capped_classes()
    claims = {}
    for card in sorted(SKILLS.glob("*.md")):
        if card.name in _CAP_CLAIM_EXEMPT:
            continue
        hits = _CAP_CLAIM.findall(read(card))
        if hits:
            claims[card.name] = hits
    if not capped:
        assert not claims, (
            f"no class in the matrix has a ceiling, but {claims} claim one")
    else:
        # a real cap must name the classes it applies to
        for name in claims:
            text = read(SKILLS / name)
            assert any(f"`{k}`" in text for k in capped), name


def test_every_cap_exemption_is_still_needed():
    """The exemption list says what it is for, or it says nothing.

    Pattern borrowed from selftest's "every tool-name exemption is still
    needed": an exemption nothing needs is an invitation to add rather than
    to check.
    """
    stale = sorted(n for n in _CAP_CLAIM_EXEMPT
                   if not (SKILLS / n).exists()
                   or not _CAP_CLAIM.search(read(SKILLS / n)))
    assert not stale, (
        f"{stale} are exempted from the cap check and no longer claim a cap "
        f"- delete the exemption")


# ------------------------------------- 3. INDEX counts what is on disk

_NUMBER_WORD = {"no": 0, "none": 0, "one": 1, "two": 2, "three": 3,
                "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10}

# `\s+` between every word, not a literal space: the sentence is wrapped in
# the shipped file, and a regex that only matched the unwrapped form failed on
# `assert m` instead of on the count - a failing direction for the wrong
# reason, which is the same defect as a check that cannot fail.
_METHODOLOGY_ONLY = re.compile(
    r"(?i)\b([A-Za-z]+)\s+modules?\s+(?:are|is)\s+methodology\s+only\s+and"
    r"\s+carr(?:y|ies)\s+no\s+requirement:"
    r"((?:\s*`[a-z0-9_-]+`\s*,?\s*(?:and\s*)?)+)")


def methodology_only_modules() -> set[str]:
    """Modules with no proof requirement, derived from the matrix.

    `module_spec`, not `spec_for`, because that is what `load_skill` uses at
    runtime and the two do not answer the same question: `spec_for` resolves
    a CLASS name, `module_spec` resolves a MODULE name and knows that a
    `<class>-refs` depth reference belongs to `<class>`.

    MEASURED: with `spec_for` this counted 12 methodology-only modules
    against INDEX.md's four, and INDEX.md was right - all eight `*-refs`
    modules carry their class's requirement, which `load_skill('sqli-refs')`
    returns. A test that resolves names differently from the runtime
    disagrees with reality and reports the runtime as the defect.
    """
    return {p.stem for p in SKILLS.glob("*.md")
            if p.name != "INDEX.md" and proof.module_spec(p.stem) is None}


def test_index_counts_and_names_the_methodology_only_modules():
    """`load_skill('index')` returns this text verbatim beside the module
    listing, so a sentence the listing contradicts is read as fact.

    Measured before the fix: INDEX.md said "Three modules are methodology
    only ... `auth-enum`, `auth-session`, `triage`" while
    `proof.spec_for('report-writing')` is None, making four. The numeric
    count gate in selftest cannot see it - its regex wants a digit and this
    count is spelled as a word.
    """
    text = read(SKILLS / "INDEX.md")
    m = _METHODOLOGY_ONLY.search(text)
    assert m, ("INDEX.md no longer states which modules carry no proof "
               "requirement - a deleted sentence must not read as agreement")
    word, names = m.group(1).lower(), set(re.findall(r"`([a-z0-9_-]+)`",
                                                     m.group(2)))
    expected = methodology_only_modules()
    assert word in _NUMBER_WORD, f"{word!r} is not a number word"
    assert _NUMBER_WORD[word] == len(expected), (
        f"INDEX.md says {word} ({_NUMBER_WORD[word]}), the matrix leaves "
        f"{len(expected)} modules without a requirement: {sorted(expected)}")
    assert names == expected, (
        f"INDEX.md names {sorted(names)}, the matrix leaves "
        f"{sorted(expected)} without a requirement")


def test_every_module_in_the_signal_table_exists_on_disk():
    """A signal row pointing at no file is an invented module."""
    text = read(SKILLS / "INDEX.md")
    rows = re.findall(r"^\|.*\|\s*`([a-z0-9_-]+)`\s*\|\s*$", text, re.M)
    assert rows, "the signal table no longer parses"
    missing = sorted(r for r in rows
                     if not (SKILLS / f"{r}.md").exists()
                     and proof.spec_for(r) is None)
    assert not missing, f"INDEX.md points at {missing}, which do not exist"


# ------------------------------------- 4. read_findings is described once

# field word in a prompt -> the finding key it promises the reader
_FIELD_WORDS = {
    "id": "id", "ids": "id", "title": "title", "titles": "title",
    "severity": "severity", "category": "category", "categories": "category",
    "url": "url", "urls": "url",
    "excerpt": "evidence_excerpt", "excerpts": "evidence_excerpt",
    "evidence": "evidence_ids",
    "grade": "grade", "grades": "grade",
    "description": "description", "remediation": "remediation",
    "cvss": "cvss",
}


def slim_finding_keys() -> set[str]:
    """What `read_findings` actually returns per row - measured by calling it
    with a finding that carries every field, not by reading its docstring.

    `read_findings` reads `ctx.session.findings` and nothing else, so a stub
    session is the whole dependency and this stays an offline check.
    """
    from types import SimpleNamespace

    from argus.tools.team import read_findings

    full = {
        "id": "F01", "title": "t", "severity": "high",
        "category": "sqli", "url": "http://127.0.0.1/x",
        "evidence_excerpt": "bytes", "evidence_ids": ["R1"],
        "grade": "candidate", "description": "d", "remediation": "r",
        "cvss": "7.5",
    }
    ctx = SimpleNamespace(session=SimpleNamespace(findings=[full]))
    rows = read_findings(ctx)["findings"]
    assert rows, "read_findings returned nothing for a session with a finding"
    # the premise of the test below: the slim view really does drop fields
    assert set(rows[0]) < set(full), "read_findings is no longer a slim view"
    return set(rows[0])


def bullet_for(text: str, tool: str) -> str:
    """The prompt bullet that describes one tool, continuation lines included."""
    out, grabbing = [], False
    for line in text.splitlines():
        if re.match(rf"^\s*[-*]\s*`{re.escape(tool)}`", line):
            grabbing, out = True, [line]
            continue
        if grabbing:
            if not line.strip() or re.match(r"^\s*[-*]\s", line):
                break
            out.append(line)
    return "\n".join(out)


def test_the_report_role_prompt_promises_only_fields_read_findings_returns():
    """Two documents land in one report worker's context and described the
    same tool in opposite ways.

    Measured before the fix: roles/report.md:6 promised "every recorded
    finding with severity, category, URL, evidence ids and excerpts", while
    `argus/tools/team.py:read_findings` returns only id, title, severity,
    category and url. A worker that believed the prompt either wrote
    excerpt-backed prose from fields it never received, or spent turns
    hunting a tool that returns them - and no tool its role holds does.

    Only the role prompt's bullet is parsed, not the card's prose: the card
    names `excerpts` in order to say they are NOT in the slim view, which a
    word-level check would read backwards.
    """
    returned = slim_finding_keys()
    bullet = bullet_for(read(ROLES / "report.md"), "read_findings")
    assert bullet, "roles/report.md no longer describes read_findings"
    promised = {_FIELD_WORDS[w] for w in re.findall(r"[a-z]+", bullet.lower())
                if w in _FIELD_WORDS}
    overpromised = sorted(promised - returned)
    assert not overpromised, (
        f"roles/report.md promises {overpromised} from read_findings; it "
        f"returns {sorted(returned)}")


def test_the_field_promise_check_catches_the_shape_it_is_for():
    returned = slim_finding_keys()
    planted = ("- `read_findings` - every recorded finding with severity,\n"
               "  category, URL, evidence ids and excerpts.\n")
    bullet = bullet_for(planted, "read_findings")
    promised = {_FIELD_WORDS[w] for w in re.findall(r"[a-z]+", bullet.lower())
                if w in _FIELD_WORDS}
    assert sorted(promised - returned) == ["evidence_excerpt", "evidence_ids"]


# ------------------------------------- 5. the worker is routed to the card

def test_the_report_role_prompt_routes_the_worker_to_its_card():
    """A card nothing points at is a document the worker never reads.

    The only reference to `report-writing` in the tree was INDEX.md's signal
    row, which costs a `load_skill('index')` turn to see; the role's turn cap
    is 15, so the document most likely to be read was the role prompt alone.
    """
    text = read(ROLES / "report.md")
    assert "report-writing" in text, (
        "roles/report.md never names its own methodology card")
    assert "load_skill" in text, (
        "naming the card without naming the call that loads it is not a route")
    assert (SKILLS / "report-writing.md").exists()
    assert "load_skill" in CARDS["report"].tools


# --------------------------- 6. where a worker's finish summary really goes

def test_the_card_states_the_summary_route_the_code_implements():
    """The card claimed `finish` "is where the summary is written".

    True in solo mode (`AgentLoop.run` renders with `ctx.finish_summary`),
    false for a report worker: the coordinator builds every worker with
    `report=False` and renders the Executive summary from the LEAD's result
    only, so a worker's `finish` text reaches the artifact just inside the
    collapsed working-notes appendix.

    The premise is asserted from the source, so if the coordinator is ever
    changed to read the report worker's summary this test says to update the
    card rather than silently going green on stale prose.
    """
    from argus.team.coordinator import TeamRun
    worker_src = inspect.getsource(TeamRun._start_worker)
    run_src = inspect.getsource(TeamRun.run)
    assert "report=False" in worker_src, (
        "premise changed: workers now render their own report")
    assert 'self._results.get("lead"' in run_src, (
        "premise changed: the Executive summary no longer comes from the "
        "lead's result alone")

    card = read(SKILLS / "report-writing.md")
    assert "`finish`, which is where the summary is written" not in card, (
        "the card still tells a report worker that finish publishes its "
        "summary; in team mode only the lead's does")
    # and it has to name the route that does reach the lead
    assert tools_named_in(card) & {"note", "post_board_note"}, (
        "the card must name a route a report worker actually holds for "
        "getting its narrative to the lead")


# ----------------------- 7. a named module is a module that exists

_SKILL_REF = re.compile(
    r"""load_skill\(\s*["']([a-z0-9_<>-]+)["']\s*\)"""
    r"""|load_skill`?\s+(?:for\s+)?(?:the\s+)?`([a-z0-9_-]+)`""")


def skill_names_in(text: str) -> set[str]:
    """Modules a document tells its reader to load, either spelling."""
    out = set()
    for a, b in _SKILL_REF.findall(text):
        name = a or b
        if name and "<" not in name:
            out.add(name)
    return out


def test_every_module_a_context_document_names_exists_on_disk():
    """selftest's proof-class gate reads every `load_skill("x")` literal as a
    claim that x is a proof-matrix class, so it fails on a TRUE statement
    about one of the four methodology-only modules (`triage`, `auth-enum`,
    `auth-session`, `report-writing` - all on disk, all with
    `proof.spec_for(...) is None`). That over-reach is in a file this module
    does not own; this is the check it should be, over the documents that are
    injected into a worker's context: a named module must exist, whether or
    not it carries a requirement.
    """
    checked = 0
    missing = {}
    for doc in sorted(SKILLS.glob("*.md")) + sorted(ROLES.glob("*.md")):
        for name in skill_names_in(read(doc)):
            checked += 1
            if not (SKILLS / f"{name}.md").exists() \
                    and proof.spec_for(name) is None:
                missing.setdefault(doc.name, set()).add(name)
    assert checked, "no document names a module to load - the check is empty"
    assert not missing, f"documents point at modules that do not exist: {missing}"


def test_the_module_reference_check_reads_both_spellings():
    assert skill_names_in('call load_skill("sqli") first') == {"sqli"}
    assert skill_names_in("call load_skill('index') first") == {"index"}
    assert skill_names_in(
        "Your first call is `load_skill` for the `report-writing` module") \
        == {"report-writing"}
    # a placeholder is not a module name
    assert skill_names_in('`load_skill("<name>")`') == set()
    # and the failing direction
    assert skill_names_in('load_skill("no-such-module")') \
        == {"no-such-module"}
    assert not (SKILLS / "no-such-module.md").exists()

if __name__ == "__main__":                              # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))


def test_the_two_resolvers_agree_on_every_module_on_disk():
    """`spec_for` and `module_spec` answer different questions, and a caller
    that reaches for the wrong one gets a confident wrong answer.

    `spec_for` resolves a CLASS name. `module_spec` resolves a MODULE name
    and knows a `<class>-refs` file is the depth tier of `<class>`. The test
    above used the first where the runtime uses the second and reported
    eight modules as carrying no requirement when every one of them does.

    So: wherever both resolve, they must agree. Where only `module_spec`
    does, the module must be a `-refs` file whose base IS a class - that is
    the one shape the extra resolution exists for, and anything else
    resolving only there means a second mapping has grown beside this one.
    """
    both, refs_only, neither = [], [], []
    for path in sorted(SKILLS.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        stem = path.stem
        by_class = proof.spec_for(stem)
        by_module = proof.module_spec(stem)
        if by_class is not None and by_module is not None:
            assert by_class.vuln_class == by_module.vuln_class, (
                f"{stem}: spec_for says {by_class.vuln_class}, "
                f"module_spec says {by_module.vuln_class}")
            both.append(stem)
        elif by_module is not None:
            refs_only.append(stem)
        elif by_class is None:
            neither.append(stem)

    for stem in refs_only:
        assert stem.endswith("-refs"), (
            f"{stem} resolves only through module_spec and is not a -refs "
            "module, so a second name mapping has grown beside the matrix")
        base = stem[: -len("-refs")]
        assert proof.spec_for(base) is not None, (
            f"{stem} points at {base!r}, which is not a proof class")
        assert proof.module_spec(stem).vuln_class == proof.spec_for(base).vuln_class

    assert both, "no module resolves as its own class - the mapping is gone"
    assert refs_only, "no -refs module resolves; the depth tier is unreachable"


# ----------------------------- 6. the cards obey the repository's refusals

# CLAUDE.md: "Denial of service, persistence, lateral movement, credential
# dumping, data exfiltration, or any demonstration whose proof is the damage"
# - and for execution, "proven with `id; echo <nonce>` and stops there".
#
# These cards are returned by `load_skill` into the model's prompt, and an
# entry skill routes to its `-refs` module the moment a class is confirmed,
# so a line here is an INSTRUCTION, not a document. Measured before the fix:
# `load_skill('ssrf-refs')` handed the model `…/iam/security-credentials/
# <role>` and `…/service-accounts/default/token` under the heading "high-value
# first targets", a pivot table of internal services to enumerate, and
# "cite the recorded response body verbatim" for a credentials response.
_FORBIDDEN_SHAPES = {
    r"iam/security-credentials": "fetches the instance's IAM credentials",
    r"service-accounts/default/token": "fetches the instance's OAuth token",
    r"_cat/indices": "lists an internal service's contents",
    r"INTO OUTFILE '/path/shell": "drops a webshell (persistence)",
    r"sp_configure 'xp_cmdshell',1": "enables a disabled exec facility on the target",
    # `document.cookie` is fine; `document.cookie` as the VALUE SENT is not.
    # The trailing `(?!\.)` is what separates them: `.length` and `.split`
    # are measurements of the cookie, and the card's own surviving shapes
    # use exactly those.
    r"\+\s*document\.cookie(?!\.)": "sends the victim's session cookie off-box",
    r"JSON\.stringify\(localStorage\)": "sends the victim's whole storage off-box",
    r"\?t='\+h\.match": "sends a CSRF token's value off-box",
}

# A forbidden shape may be NAMED, but only inside a paragraph that refuses
# it. English cannot be parsed, so this is a fixed vocabulary and nothing
# else counts - which is the point: a card that wants to name one of these
# has to write the refusal beside it.
#
# The unit is the PARAGRAPH, not the line. Measured: the first version of
# this check read line by line and reported `ssrf-refs.md:39` as an
# instruction, when line 38 is "DO NOT follow the credential paths -" and 39
# is its continuation. A refusal does not fit on one line, so a line is the
# wrong window to judge one in.
_REFUSAL_WORDS = ("do not", "don't", "never", "not to do", "refuses",
                  "instead of", "adds nothing", "stops there",
                  "changes the target", "do not depend")


def _paragraphs(text: str):
    """(first line number, text) per blank-line-separated block."""
    out, buf, start = [], [], 1
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not buf:
                start = i
            buf.append(line)
        elif buf:
            out.append((start, "\n".join(buf)))
            buf = []
    if buf:
        out.append((start, "\n".join(buf)))
    return out


def test_no_card_instructs_an_action_the_repository_refuses():
    """Plant-tested: restoring the pre-merge `ssrf-refs.md` metadata table
    names two shapes, and the pre-merge `xss-refs.md` payload block two
    more."""
    offences = []
    for path in sorted(SKILLS.glob("*.md")):
        for lineno, para in _paragraphs(read(path)):
            low = para.lower()
            refused = any(w in low for w in _REFUSAL_WORDS)
            for pattern, why in _FORBIDDEN_SHAPES.items():
                m = re.search(pattern, para)
                if m and not refused:
                    offences.append(
                        f"{path.name}:{lineno} {why}: "
                        f"{para[max(0, m.start() - 20):m.end() + 20].strip()[:70]}")
    assert not offences, (
        "skill cards instruct actions CLAUDE.md refuses - these load into the "
        "model's prompt, so each one is an instruction:\n  " +
        "\n  ".join(offences))


def test_the_proof_shaped_capability_is_still_there():
    """The counterpart. Blanket-refusing the whole area would remove real
    capability, and these are the artifacts that prove a class WITHOUT
    taking anything: `/etc/passwd` is world-readable and holds no secret,
    the same reason `id` is the execution proof, and a metadata root that
    answers 200 settles that the IMDS is exposed without holding its keys.
    """
    sqli = read(SKILLS / "sqli-refs.md")
    assert "LOAD_FILE('/etc/passwd')" in sqli
    assert "pg_read_file('/etc/passwd')" in sqli

    ssrf = read(SKILLS / "ssrf-refs.md")
    assert "169.254.169.254/latest/meta-data/" in ssrf, \
        "the reachability probe is the finding and must stay"
    assert "IMDSv2-hardened honestly" in ssrf, \
        "reporting a hardened target is a real result, not a failure"

    xss = read(SKILLS / "xss-refs.md")
    assert "+d.length" in xss, \
        "the measurement-not-value shape the card already had must stay"
    assert "document.cookie.length" in xss, \
        "cookie reachability is provable from its size"


def test_every_gradeable_class_is_taught_by_some_card():
    """The reverse of "every card names a real class", and it has to use the
    runtime's own mechanism or it over-reports.

    MEASURED: a first pass asked only whether a card's STEM resolves to the
    class and flagged six - `enum`, `jwt`, `lockout`, `massassign`, `method`
    and `dos`. Five of those are taught by a card with a different name,
    which `load_skill` already knows: `_also_taught` derives the extra
    classes from the driving tools a module names, through the same
    tool->class mapping the ledger uses. `auth-enum` teaches `enum`,
    `auth-session` teaches `lockout`, `jwt` and `massassign`, `triage`
    teaches `method`. Counting that way, the real answer is that only `dos`
    has no card - and `dos` has no required checks either, which is how a
    refused-by-construction class looks.

    So this is the invariant rather than a fix: a class added with no card
    at all, by name or by driving tool, fails here instead of handing an
    agent a requirement with no methodology behind it.
    """
    from argus.tools.analysis import _also_taught

    covered: dict[str, list[str]] = {}
    for path in sorted(SKILLS.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        spec = proof.module_spec(path.stem)
        own = spec.vuln_class if spec else ""
        if own:
            covered.setdefault(own, []).append(path.stem)
        for extra in _also_taught(read(path), own):
            covered.setdefault(extra, []).append(f"{path.stem} (also)")

    uncovered = [c for c in sorted(proof.classes())
                 if c not in covered and proof.spec_for(c).required]
    assert not uncovered, (
        f"{uncovered} are gradeable classes no skill card teaches, by name "
        "or through a driving tool - an agent loading for them gets a proof "
        "requirement and no methodology")

    # and the five that depend on `_also_taught` are asserted by name, so
    # the mechanism cannot quietly stop working and leave this green
    for klass, teacher in (("enum", "auth-enum"), ("lockout", "auth-session"),
                           ("jwt", "auth-session"), ("massassign", "auth-session"),
                           ("method", "triage")):
        assert any(t.startswith(teacher) for t in covered.get(klass, [])), (
            f"{klass} is no longer reached through {teacher}; "
            f"covered by {covered.get(klass)}")


def full_finding_keys() -> set[str]:
    """What `read_findings_full` returns per row - measured the same way.

    Measured, not read off a docstring, and for the same reason the slim
    helper above is: the prompt and the tool are two documents that landed
    in one worker's context and once described the same tool in opposite
    ways.
    """
    from types import SimpleNamespace

    from argus.tools.team import read_findings_full

    full = {
        "id": "F01", "title": "t", "severity": "high",
        "category": "sqli", "vuln_class": "sqli", "url": "http://127.0.0.1/x",
        "evidence_excerpt": "bytes", "evidence_ids": ["R1"],
        "grade": "candidate", "description": "d", "remediation": "r",
        "cvss": "7.5",
        "proof": {"requirement": "a row from a named table",
                  "missing": ["the query named its target"]},
    }
    ctx = SimpleNamespace(session=SimpleNamespace(findings=[full]))
    rows = read_findings_full(ctx)["findings"]
    assert rows, "read_findings_full returned nothing"
    return set(rows[0])


def test_the_full_view_carries_what_the_report_skill_demands():
    """MEASURED GAP this closes. `read_findings` is a dedup view and says so:
    "workers only need class+endpoint+id to skip already-proven work". The
    report role used it for a different job - `report-writing.md` instructs
    that "every claim traces to an id" and that "the grade is not
    decoration" - and the slim view carries neither an evidence id nor a
    grade nor the excerpt.

    So the role was told to trace claims to ids by a card whose tools could
    not show it one, and `report.md` documented the dead end honestly:
    "no tool of yours returns them ... write the sentence without the
    quote". The data was never missing - it is in findings.json and the
    deterministic renderer reads all of it. The one agent whose whole job is
    the narrative was the one denied it.
    """
    returned = full_finding_keys()
    for needed in ("evidence_ids", "evidence_excerpt", "grade",
                   "proof_missing", "proof_requirement"):
        assert needed in returned, (
            f"{needed} is what the report skill asks the role to use; "
            f"read_findings_full returns {sorted(returned)}")
    # and the slim view is still slim, so widening it was not the fix
    assert "evidence_ids" not in slim_finding_keys(), (
        "read_findings was widened instead - every recon and exploit worker "
        "pays for whatever that view returns, which is why its narrowness is "
        "deliberate")


def test_the_report_role_holds_the_full_view_and_is_told_to_start_there():
    from argus.team.cards import LEAD, REPORT

    assert "read_findings_full" in REPORT.tools
    # the lead writes the executive summary when no report worker ran, so it
    # needs the same view for the same reason
    assert "read_findings_full" in LEAD.tools

    card = read(ROLES / "report.md")
    bullet = bullet_for(card, "read_findings_full")
    assert bullet, "report.md does not describe the tool it was granted"
    assert "START HERE" in bullet, \
        "a role that holds a tool and is not told to use it holds it the " \
        "way the registry held the orchestrator"


def test_the_full_views_bullet_promises_only_fields_it_returns():
    """The same invariant as the slim one, for the tool that replaced it in
    this role's workflow. Without this, the new bullet is unguarded - and
    the old bullet was guarded precisely because two documents once
    described one tool in opposite ways."""
    returned = full_finding_keys()
    bullet = bullet_for(read(ROLES / "report.md"), "read_findings_full")
    promised = {_FIELD_WORDS[w] for w in re.findall(r"[a-z]+", bullet.lower())
                if w in _FIELD_WORDS}
    overpromised = sorted(promised - returned)
    assert not overpromised, (
        f"report.md promises {overpromised} from read_findings_full; it "
        f"returns {sorted(returned)}")
