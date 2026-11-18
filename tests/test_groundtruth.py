"""The oracle argus cannot write.

Every number argus produces about itself is argus marking its own work. A
target that publishes its own scoreboard is the one source in an engagement
that this package cannot influence, so these pin the two things that make it
worth quoting: it is read in full, and it never credits this run with a
solve that predates it.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from argus import groundtruth as G   # noqa: E402


class _FakeSession:
    def __init__(self):
        self._transcript = {}


class _FakeClient:
    """A client whose returned body is a PREFIX of the recorded one.

    That is what `GuardedClient` really does - 12,000 returned against
    200,000 recorded - and it is the defect this module was written over.
    """
    RETURN_CAP = 12000

    def __init__(self, body: str, truncated_at: int | None = None):
        self.session = _FakeSession()
        self._body = body
        self._truncated = truncated_at
        self.sent = []

    def send(self, method, url, **kw):
        rid = f"r{len(self.sent) + 1}"
        self.sent.append((method, url, kw))
        resp = {"status": 200, "headers": {}, "body": self._body}
        if self._truncated:
            resp["body_truncated_at"] = self._truncated
        self.session._transcript[rid] = {"id": rid, "response": resp}
        return {"request_id": rid, "status": 200,
                "body": self._body[:self.RETURN_CAP]}


def _board(n_total=118, solved_keys=()):
    rows = []
    for i in range(n_total):
        key = f"ch{i}"
        rows.append({"key": key, "name": f"Challenge {i}",
                     "category": "Injection" if i % 2 else "XSS",
                     "difficulty": 1 + (i % 6),
                     "solved": key in solved_keys,
                     # padding so the document is comfortably over the
                     # 12,000-character return cap, as the real one is
                     "description": "x" * 160})
    return json.dumps({"data": rows})


# ------------------------------------------------- read it whole, or refuse

def test_the_scoreboard_is_read_from_the_recorded_body_not_the_prefix():
    """MEASURED: Juice Shop's scoreboard is 69KB and the client returns the
    first 12,000 characters. Parsing the returned value raised
    "Unterminated string at char 11978" - and the dangerous case is the one
    that does NOT raise: a cut landing on a record boundary parses cleanly
    and yields a short list, so a count would be wrong with no error."""
    raw = _board()
    client = _FakeClient(raw)
    assert len(raw) > _FakeClient.RETURN_CAP, "fixture must exceed the cap"
    board = G.read_scoreboard(client, "http://t.test/")
    assert board.total == 118, "the full list, not the prefix"


def test_a_truncated_recording_is_refused_rather_than_counted():
    """If even the recorded body was cut, a count taken from it is short -
    so this fails loudly instead of returning a number that is quietly
    wrong. A measurement that can be silently wrong is worse than one that
    stops."""
    client = _FakeClient(_board(), truncated_at=200000)
    with pytest.raises(ValueError, match="truncated"):
        G.read_scoreboard(client, "http://t.test/")


def test_the_read_goes_through_the_client_so_it_is_on_the_record():
    client = _FakeClient(_board())
    G.read_scoreboard(client, "http://t.test/")
    assert len(client.sent) == 1
    method, url, kw = client.sent[0]
    assert method == "GET" and url.endswith("/api/Challenges")
    assert kw.get("tool") == "groundtruth"


def test_an_unknown_app_is_refused_by_name():
    with pytest.raises(ValueError, match="no scoreboard is known"):
        G.read_scoreboard(_FakeClient(_board()), "http://t.test/", app="nope")


def test_a_target_that_is_not_the_app_is_refused():
    with pytest.raises(ValueError, match="did not return JSON"):
        G.read_scoreboard(_FakeClient("<html>hello</html>"), "http://t.test/")


# -------------------------------------------- never credit a prior solve

def test_a_solve_that_predates_the_run_is_not_credited_to_it():
    """The scoreboard is cumulative. Without the difference, a target
    someone exercised yesterday credits this run with work it did not do -
    the same absolute-where-a-differential-is-needed mistake this package
    keeps finding in its own gate."""
    before = G.read_scoreboard(_FakeClient(_board(solved_keys={"ch1"})), "http://t.test/")
    after = G.read_scoreboard(_FakeClient(_board(solved_keys={"ch1"})), "http://t.test/")
    assert len(before.solved) == 1
    assert G.newly_solved(before, after) == []

    out = G.correlate(before, after, [{"grade": "proven", "vuln_class": "sqli"}])
    assert out["solved_before"] == 1 and out["solved_after"] == 1
    assert out["newly_solved"] == []
    assert out["confirmed_approx"] == []


def test_a_solve_during_the_run_is_reported_and_mapped_approximately():
    before = G.read_scoreboard(_FakeClient(_board(solved_keys={"ch1"})), "http://t.test/")
    after = G.read_scoreboard(_FakeClient(_board(solved_keys={"ch1", "ch3"})), "http://t.test/")
    gained = G.newly_solved(before, after)
    assert [c["key"] for c in gained] == ["ch3"]

    out = G.correlate(before, after, [{"grade": "proven", "vuln_class": "sqli"}])
    assert [c["key"] for c in out["confirmed_approx"]] == ["ch3"]
    assert out["confirmed_approx"][0]["argus_classes"] == ["sqli"]
    assert "approximate" in out["caveat"]


def test_a_solve_argus_claimed_nothing_for_is_reported_separately():
    """Either the run tripped it blind, or the mapping is too narrow. Both
    want a human; neither is a failure of the gate, and folding them into
    the confirmed count would invent agreement."""
    before = G.read_scoreboard(_FakeClient(_board()), "http://t.test/")
    after = G.read_scoreboard(_FakeClient(_board(solved_keys={"ch2"})), "http://t.test/")
    out = G.correlate(before, after, [{"grade": "proven", "vuln_class": "sqli"}])
    assert out["confirmed_approx"] == []          # ch2 is XSS, we claimed sqli
    assert [c["key"] for c in out["unclaimed"]] == ["ch2"]


def test_only_proven_findings_count_as_a_claim():
    before = G.read_scoreboard(_FakeClient(_board()), "http://t.test/")
    after = G.read_scoreboard(_FakeClient(_board(solved_keys={"ch1"})), "http://t.test/")
    out = G.correlate(before, after, [{"grade": "candidate", "vuln_class": "sqli"}])
    assert out["proven_findings"] == 0
    assert out["confirmed_approx"] == [], "a candidate is not a claim to confirm"


# --------------------------------------------------- the agent cannot see it

def test_the_oracle_is_not_on_the_tool_table():
    """An agent that can read the scoreboard can read the answers, and the
    measurement would then be of a system that was told what to find."""
    from argus.tools import registry
    names = {t["name"] for t in registry.TOOL_SCHEMAS}
    assert not any("groundtruth" in n or "scoreboard" in n for n in names), names
    import inspect
    src = inspect.getsource(registry)
    assert "groundtruth" not in src


# ------------------------------- the oracle reaches an operator, not a tool

def test_the_subcommand_exists_and_is_not_a_tool():
    """A module nothing calls is the defect this session spent its length
    fixing in `orchestrator.py`, so the oracle needed a caller. It had to be
    a SUBCOMMAND and not a tool entry: an agent that can read the scoreboard
    can read the answers."""
    import argparse
    from argus import cli
    parser = cli.build_parser() if hasattr(cli, "build_parser") else None
    if parser is None:                                 # pragma: no cover
        src = (ROOT / "argus" / "cli.py").read_text(encoding="utf-8")
        assert '"groundtruth"' in src
        return
    names = set()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            names |= set(action.choices)
    assert "groundtruth" in names, sorted(names)

    from argus.tools import registry
    assert "groundtruth" not in {t["name"] for t in registry.TOOL_SCHEMAS}


def test_the_command_takes_no_flag_that_does_nothing():
    """MEASURED: a `--allow-private` flag was added, and it was inert for
    exactly the targets it was meant for. `ScopeGuard.__init__` sets
    `allow_private = allow_private or target_private`, and the only request
    this command makes goes to the target itself - so a private scoreboard
    host grants itself and a public one has no private host to reach.
    Running it against `http://192.168.223.221:3000` without the flag
    produced the same full output as with it. A flag in `--help` that does
    nothing is a false statement about the program."""
    src = (ROOT / "argus" / "cli.py").read_text(encoding="utf-8")
    block = src[src.index('p_gt = sub.add_parser('):]
    block = block[:block.index("p_diff = sub.add_parser(")]
    assert "--allow-private" not in block, \
        "the inert flag is back on the groundtruth subcommand"


def test_the_runtime_output_directory_cannot_be_committed():
    """CLAUDE.md: "`engagements/` is runtime output. Never commit it."
    MEASURED: it was not in `.gitignore` at all - `git status` showed it as
    untracked, so one `git add -A` would have staged an engagement's
    evidence, including a target's recorded response bodies. The instruction
    was being held up by the habit of naming paths on every commit, which is
    discipline and not a guarantee. This asserts the guarantee."""
    patterns = {line.strip() for line in
                (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()}
    assert "engagements/" in patterns or "engagements" in patterns, \
        "engagements/ is runtime output and nothing stops it being committed"
