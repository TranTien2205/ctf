"""The adapter that puts the hybrid fan-out on the tool table.

`argus/orchestrator.py` was written, tested, and imported by nothing: 1500
lines no engagement could reach. These pin the seam, and in particular the
one defect driving it found - a refusal that read as an empty result.
"""
from __future__ import annotations
import inspect

import pathlib
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from argus.config import Config                      # noqa: E402
from argus.httpclient import GuardedClient           # noqa: E402
from argus.ratelimit import RateLimiter              # noqa: E402
from argus.scope import ScopeGuard                   # noqa: E402
from argus.session import Session                    # noqa: E402
from argus.tools import Context                      # noqa: E402
from argus.tools import sweep as sweep_mod           # noqa: E402
from argus.tools.sweep import _clean_wordlist, recon_sweep as sweep  # noqa: E402


@pytest.fixture()
def ctx(tmp_path):
    base = "http://127.0.0.1:1/"
    sess = Session(tmp_path, base, {"model": "test"})
    guard = ScopeGuard(base, allow_private=True)
    return Context(cfg=Config(target=base), scope=guard, session=sess,
                   client=GuardedClient(guard, sess, RateLimiter(0.0),
                                        max_requests=10),
                   skills_dir=None)


# ----------------------------------------------------- the wordlist is input

def test_a_model_written_word_that_reads_as_a_flag_never_reaches_argv():
    """ffuf takes a value beginning with '-' as the next option, so a word
    like `-oOUT` turns a scan into a file write. The wordlist comes from a
    model reasoning over bytes the target chose, so it is target-influenced
    input and is filtered like any other."""
    words, refused = _clean_wordlist("admin\n-oOUT\n--config=/etc/passwd\nlogin\n")
    assert words == ["admin", "login"]
    assert len(refused) == 2
    assert all("flag" in r for r in refused)


def test_a_word_with_a_control_character_is_refused():
    words, refused = _clean_wordlist("ok\nbad\x00word\n")
    assert words == ["ok"]
    assert refused and "control character" in refused[0]


def test_the_wordlist_is_capped_and_says_what_it_dropped():
    """Silent truncation reads as "we tried everything"."""
    words, refused = _clean_wordlist("\n".join(f"w{i}" for i in range(500)))
    assert len(words) == sweep_mod.MAX_WORDS
    assert refused and "cap" in refused[0]


def test_an_over_long_word_is_refused_not_trimmed():
    words, refused = _clean_wordlist("ok\n" + "x" * 500 + "\n")
    assert words == ["ok"]
    assert refused and "longer than" in refused[0]


# -------------------------------------------------- a refusal is a decision

def test_an_out_of_scope_target_says_nothing_was_scanned(ctx, monkeypatch):
    """MEASURED BUG. The orchestrator refused correctly and spawned nothing,
    but this adapter reported `endpoint_count: 0` under the verdict "no
    endpoint came back ... the wordlist did not name it". A model reading
    that widens its wordlist and retries forever instead of learning the
    target is out of scope. The refusal has to be the headline.
    """
    spawned = []
    monkeypatch.setattr(sweep_mod.orchestrator.subprocess, "Popen",
                        lambda *a, **k: spawned.append(a) or (_ for _ in ()).throw(
                            AssertionError("a process was spawned for an "
                                           "out-of-scope target")))
    out = sweep(ctx, "http://somewhere-else.invalid/", tools="ffuf", timeout_s=20)
    assert spawned == []
    assert out.get("refused") is True, out
    assert "NOTHING WAS SCANNED" in out["verdict"], out["verdict"]
    assert "scope" in out["verdict"].lower()


def test_the_empty_result_wording_is_only_used_when_tools_really_ran(ctx):
    """The two sentences must not be interchangeable: "nothing is there" and
    "nothing ran" are opposite claims about the target."""
    out = sweep(ctx, "http://elsewhere.invalid/", tools="ffuf", timeout_s=20)
    assert "the wordlist did not name it" not in out.get("verdict", "")


def test_a_tool_this_adapter_does_not_drive_is_refused_by_name(ctx):
    out = sweep(ctx, "http://127.0.0.1:1/", tools="sqlmap")
    assert "error" in out
    assert "sqlmap" in out["error"] and "run_external" in out["error"]


def test_a_missing_url_is_refused(ctx):
    assert "error" in sweep(ctx, "")


# ------------------------------------------------------------ honest replies

def test_the_adapter_never_claims_the_agent_half_ran(ctx):
    """The orchestrator's `agent_fn` is deliberately not wired here - the
    model IS the caller, so calling back into it would re-enter the agent
    loop from inside a tool call. The reply must say the half did not run."""
    out = sweep(ctx, "http://127.0.0.1:1/", tools="ffuf", timeout_s=20)
    assert out.get("agent_ran") is False
    assert "wordlist=" in out.get("note", ""), "the reply must say whose turn the other half is"


def test_the_tool_is_on_the_table_and_dispatchable():
    """A module nothing imports is 1500 lines no engagement can reach."""
    from argus.tools import registry
    names = {t["name"] for t in registry.TOOL_SCHEMAS}
    assert "recon_sweep" in names
    schema = next(t for t in registry.TOOL_SCHEMAS if t["name"] == "recon_sweep")
    props = schema["input_schema"]["properties"]
    assert {"url", "tools", "wordlist", "timeout_s"} <= set(props)
    assert schema["input_schema"]["required"] == ["url"]


# ------------------------------- the fan-out half, and the fourth orphan

def test_the_fanout_is_on_the_tool_table():
    """`exploit_fanout` was written, tested and reached by nothing - found by
    auditing the package for public functions with no caller anywhere, which
    returned it and `schemas_for` out of several hundred. Fourth orphan of
    this session."""
    from argus.tools import registry
    assert "fanout_sweep" in {t["name"] for t in registry.TOOL_SCHEMAS}


def test_the_fanout_is_granted_and_taught():
    """The three steps past the registry entry, missed twice in this session
    before being done in the same edit as the third."""
    from argus.team.cards import EXPLOIT
    assert "fanout_sweep" in EXPLOIT.tools
    card = (ROOT / "argus" / "team" / "roles" / "exploit.md").read_text(
        encoding="utf-8")
    assert "fanout_sweep" in card, "a role that holds a tool must be told why"


def test_a_non_url_is_refused_with_its_reason_not_dropped(ctx):
    out = sweep_mod.fanout_sweep(ctx, endpoints="notaurl\nalso bad")
    assert "error" in out
    reasons = [r["reason"] for r in out["refused"]]
    assert all("http(s)" in r for r in reasons), out


def test_the_endpoint_list_is_capped_and_says_so(ctx, monkeypatch):
    """A model picks this list, so the cap is lower than the orchestrator's
    500 - an engagement that wants 200 endpoints swept at once is an
    operator's decision, not a tool call's. And the cap is REPORTED: a
    caller who sent 80 and got 24 would keep sending 80 otherwise.

    The orchestrator is stubbed because the point is the list, not the
    scanners - and running 24 real sweeps to check an arithmetic bound
    would make this test cost minutes.
    """
    passed = {}

    def fake_fanout(target, endpoints, **kw):
        passed["endpoints"] = list(endpoints)
        return []

    monkeypatch.setattr(sweep_mod.orchestrator, "exploit_fanout", fake_fanout)
    many = "\n".join(f"http://t.local/{i}" for i in range(80))
    out = sweep_mod.fanout_sweep(ctx, endpoints=many)

    assert len(passed["endpoints"]) == sweep_mod.MAX_FANOUT_ENDPOINTS
    assert out["requested"] == sweep_mod.MAX_FANOUT_ENDPOINTS
    assert any("capped" in r["reason"] for r in out["not_submitted"]), out


def test_duplicate_endpoints_are_collapsed(ctx, monkeypatch):
    passed = {}
    monkeypatch.setattr(
        sweep_mod.orchestrator, "exploit_fanout",
        lambda target, endpoints, **kw: passed.setdefault("e", list(endpoints)) and [])
    sweep_mod.fanout_sweep(ctx, endpoints="http://t.local/a\nhttp://t.local/a\n"
                                           "http://t.local/b")
    assert passed["e"] == ["http://t.local/a", "http://t.local/b"]


def test_nothing_scanned_is_the_verdict_not_a_count_of_zero():
    """The defect `recon_sweep` was fixed for, in the fan-out's own words.
    MEASURED against the lab: two out-of-scope endpoints returned
    `refused: True` and "NOTHING WAS SCANNED across 2 endpoint(s)" naming
    the guard's own message, with "do not widen the endpoint list" - because
    a model told its list was empty widens the list and retries forever.
    """
    import argus.tools.sweep as m
    src = inspect.getsource(m.fanout_sweep)
    assert "NOTHING WAS SCANNED" in src
    assert "not a result about the" in src
    # and the dedup: one entry per endpoint, not per tool
    assert 'x["endpoint"] == result.target' in src, \
        "a three-tool sweep of one refused endpoint must not read as three"


# ------------------------------------- the wiring itself, not just the parts

def test_both_adapters_pass_a_real_agent_half():
    """Found by a plant that FAILED to apply. Three defects planted into the
    agent half were caught and a fourth - reverting an adapter to
    `agent_fn=None` - did not match its anchor, so it never planted, and the
    suite passed. That pass was the finding: nothing here asserted the
    wiring, only the parts either side of it.

    This is the whole point of the change. The orchestrator's agent half was
    complete and tested to twelve cases and had NO CALLER for as long as
    both adapters passed None.
    """
    import inspect

    import argus.tools.sweep as m

    for fn in (m.recon_sweep, m.fanout_sweep):
        src = inspect.getsource(fn)
        assert "agent_fn=agent" in src, (
            f"{fn.__name__} does not hand the orchestrator an agent half; "
            "the tool half would run alone and nothing else here would say so")
        assert "agent_fn=None" not in src, \
            f"{fn.__name__} still passes None somewhere"
        assert "_agent_half(ctx)" in src, (
            f"{fn.__name__} must build the agent on ITS OWN thread - the "
            "credential resolution is not safe to do concurrently")


def test_a_missing_model_is_reported_as_itself_not_as_an_empty_answer(ctx, monkeypatch):
    """MEASURED. With no credential, `make_agent_fn` still returns an agent -
    the client constructs fine and the CALL is what fails - so the
    orchestrator sees "" and reports `agent_ran=False` with the note
    "agent_fn returned no text". That reads as "the model ran and had
    nothing to say" when the model was never reached.
    """
    import argus.tools.sweep as m
    from argus.tools.wordlist_agent import WordlistAgent

    class _Dead:
        def chat(self, messages, tools, system):
            raise RuntimeError("401 no credential")

    monkeypatch.setattr(m, "_agent_half",
                        lambda c: (WordlistAgent(_Dead(), "haiku-x"), ""))
    monkeypatch.setattr(m.orchestrator.subprocess, "Popen",
                        lambda *a, **k: (_ for _ in ()).throw(
                            FileNotFoundError("no scanner here")))
    out = m.recon_sweep(ctx, "http://127.0.0.1:1/", tools="ffuf", timeout_s=20)

    assert out["agent_half"]["available"] is True
    assert out["agent_half"]["failures"] == 1
    assert "could not reach haiku-x" in out["agent_note"], out["agent_note"]
    assert "not a finding about the target" in out["agent_note"]
    assert "returned no text" not in out["agent_note"], \
        "the orchestrator's note is accurate about what it saw and wrong " \
        "about what happened; it has to be replaced, not appended to"
