"""The agent half of the hybrid sweep: the caller that was missing.

argus/orchestrator.py's agent half was complete and tested to twelve cases
and had no caller - both adapters passed agent_fn=None, so the tool half
always ran alone. These cover the piece that closes it, and the hazards that
piece has to live beside.

MEASURED on the lab before any of this existed, one ffuf run against OWASP
Juice Shop: tools alone found 6 endpoints, tools plus an agent half
supplying five words found 10 - /api-docs, /api-docs/, /ftp and /rest added,
none lost.
"""
from __future__ import annotations

import pathlib
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from argus import orchestrator                        # noqa: E402
from argus.tools.wordlist_agent import (              # noqa: E402
    MAX_ATTEMPTS, WordlistAgent, make_agent_fn)


class _Good:
    def __init__(self, text="admin\nbackup\n/api/v2\nq=1"):
        self.text = text
        self.seen = []

    def chat(self, messages, tools, system):
        self.seen.append((messages, tools, system))
        return {"content": [{"type": "text", "text": self.text}],
                "usage": {"input_tokens": 120, "output_tokens": 18}}


class _Raising:
    def __init__(self, message):
        self.message = message

    def chat(self, messages, tools, system):
        raise RuntimeError(self.message)


# ------------------------------------------------- the agent_fn contract

def test_it_satisfies_the_contract_the_orchestrator_checks():
    """One positional str in, a non-blank str out, and the orchestrator's own
    parser turns it into suggestions. Driven through `_call_agent` rather
    than asserted about, so the contract is the real one."""
    agent = WordlistAgent(_Good(), "m")
    half = orchestrator._call_agent(agent, "prompt")
    assert half.ran and half.note == "", half
    assert half.suggestions == ["admin", "backup", "/api/v2", "q=1"], half


def test_a_reply_shape_neither_provider_produces_is_empty_not_a_crash():
    """The two clients return different shapes and a third could appear. An
    exception here would be raised on a daemon thread whose traceback nobody
    sees, so an unreadable reply is "" and the orchestrator reports it."""
    class _Odd:
        def chat(self, m, t, s):
            return {"nothing": "useful"}

    agent = WordlistAgent(_Odd(), "m")
    assert agent("x") == ""
    half = orchestrator._call_agent(agent, "p")
    assert half.ran is False and "no text" in half.note


def test_a_provider_error_never_carries_the_providers_bytes():
    """MEASURED HAZARD. The adapters embed up to 500 bytes of a provider's
    response body in LLMError, `_call_agent` puts the message into the
    sweep's note, and the artifact redaction only replaces secrets the
    operator declared. A gateway that echoes an Authorization header into an
    error body would land that credential in the session artifacts.

    So only the exception TYPE leaves this module.
    """
    leak = ("401 {'error':{'message':'invalid x-api-key',"
            "'key':'sk-ant-LEAKED123'}}")
    agent = WordlistAgent(_Raising(leak), "haiku-x")
    assert agent("x") == ""

    stats = agent.stats()
    blob = repr(stats)
    assert "sk-ant-LEAKED123" not in blob, blob
    assert "invalid x-api-key" not in blob, blob
    assert "RuntimeError" in stats["last_error"]
    assert "withheld" in stats["last_error"]
    assert stats["failures"] == 1 and stats["calls"] == 0


def test_the_spend_is_counted_and_attributed_to_the_model_it_used():
    """MEASURED HAZARD, both directions. Sharing the agent loop's client
    races its `self.input_tokens += ...`, which is a non-atomic
    read-modify-write, and corrupts the run's cost line. Giving this half a
    private client instead makes its spend invisible, because nothing
    aggregates a second client's counters - so it keeps its own and hands
    them back, named with the model that was actually billed.
    """
    agent = WordlistAgent(_Good(), "claude-haiku-5-5")
    agent("a")
    agent("b")
    stats = agent.stats()
    assert stats == {"model": "claude-haiku-5-5", "calls": 2, "failures": 0,
                     "input_tokens": 240, "output_tokens": 36}, stats


def test_it_is_safe_to_share_across_concurrent_sweeps():
    """exploit_fanout hands ONE agent_fn to up to sixteen sweeps running at
    once, each calling it from its own thread, so this is shared mutable
    state by construction. Sixteen threads, counted."""
    agent = WordlistAgent(_Good(), "m")
    threads = [threading.Thread(target=agent, args=(f"p{i}",))
               for i in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    stats = agent.stats()
    assert stats["calls"] == 16, stats
    assert stats["input_tokens"] == 16 * 120, stats
    # exchanges are capped so a fan-out does not hold sixteen prompts and
    # replies for the whole sweep
    assert len(agent.exchanges) <= 16


def test_it_never_raises_whatever_the_client_does():
    """The orchestrator absorbs an exception into a note, but a BaseException
    - a KeyboardInterrupt, a SystemExit from a library - is a different
    path, and this runs on a daemon thread either way."""
    class _Base:
        def chat(self, m, t, s):
            raise KeyboardInterrupt("interrupted")

    agent = WordlistAgent(_Base(), "m")
    assert agent("x") == ""
    assert agent.stats()["failures"] == 1


def test_it_asks_for_no_tools_and_no_system_prompt():
    """A wordlist needs neither, and a tools array would invite the model to
    try calling one from inside a side-call that has no dispatcher."""
    client = _Good()
    WordlistAgent(client, "m")("the prompt")
    messages, tools, system = client.seen[0]
    assert tools == []
    assert system == ""
    assert messages == [{"role": "user", "content": "the prompt"}]


# ---------------------------------------------- construction, and refusals

def test_no_configuration_is_a_reason_not_a_crash():
    agent, why = make_agent_fn(None)
    assert agent is None
    assert "no configuration" in why


def test_the_attempt_count_is_one_because_the_thread_cannot_be_cancelled():
    """MEASURED HAZARD. The orchestrator abandons the agent thread after
    max(5.0, timeout_s - elapsed), as little as five seconds, and a Python
    thread cannot be killed. Five attempts carry 2+4+8+16+32 = 62 seconds of
    time.sleep regardless of the timeout, so an abandoned call would keep
    retrying and keep SPENDING after its result has nowhere to go."""
    assert MAX_ATTEMPTS == 1

    from argus.llm import ClaudeClient
    from argus.providers import OpenAICompatClient
    # the knob exists on both providers and defaults to the old behaviour
    assert ClaudeClient("k", "https://x", "m").max_attempts == 5
    assert ClaudeClient("k", "https://x", "m", max_attempts=1).max_attempts == 1
    assert OpenAICompatClient("k", "https://x", "m").max_attempts == 5
    assert OpenAICompatClient("k", "https://x", "m",
                              max_attempts=2).max_attempts == 2
    # and it cannot be made zero, which would mean "never call"
    assert ClaudeClient("k", "https://x", "m", max_attempts=0).max_attempts == 1


def test_the_model_comes_from_the_table_by_role_not_from_a_name():
    """`for_role` returns a Model, not a string. The first version of this
    code did `str(picked or "")`, which is the dataclass REPR - a name the
    table would not find, routed to Anthropic as a nonsense model. Caught by
    checking the return type, not by a failed call."""
    from argus import models
    from argus.tools.wordlist_agent import AGENT_ROLE

    picked = models.for_role(AGENT_ROLE)
    assert picked is not None, f"the table offers no {AGENT_ROLE!r} role"
    assert isinstance(getattr(picked, "key", None), str) and picked.key
    assert picked.key in repr(picked)      # the trap: repr CONTAINS the key
    assert str(picked) != picked.key, \
        "if these were equal the original bug would be invisible"
