"""The adapter that puts the hybrid fan-out on the tool table.

`argus/orchestrator.py` was written, tested, and imported by nothing: 1500
lines no engagement could reach. These pin the seam, and in particular the
one defect driving it found - a refusal that read as an empty result.
"""
from __future__ import annotations

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
