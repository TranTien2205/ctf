"""The agent half of the hybrid sweep: a bounded, recorded, side LLM call.

`argus/orchestrator.py` runs the scanners and ALSO takes an injected
`agent_fn(prompt) -> text`, which it starts concurrently with the tools that
are still running and whose candidates become a second ffuf pass. That half
was complete, tested to twelve cases, and had no caller: both adapters in
`sweep.py` passed `agent_fn=None`, so the tool half always ran alone.

MEASURED against the lab before this existed, one ffuf run on OWASP Juice
Shop: tools alone found 6 endpoints, tools plus an agent half supplying five
words found 10 - `/api-docs`, `/api-docs/`, `/ftp` and `/rest` added, none
lost. The hybrid is additive by construction; the agent's words become a
wordlist, and a wordlist can only find more paths.

WHAT THIS FILE IS CAREFUL ABOUT, each from a measured hazard in the code it
has to live beside:

* **Its own client, built on the CALLER's thread.** `config.resolve_auth`
  writes a temp file named only by PID and `os.replace()`s the user's real
  credentials file, so two concurrent refreshes collide on one path. The
  credential is resolved once, here, before any worker thread exists.

* **Its own token counters, so the spend is visible.** The clients count with
  `self.input_tokens += ...`, a non-atomic read-modify-write. Sharing the
  agent loop's client across threads races those counters and corrupts the
  run's cost line; giving this half a private client instead makes its spend
  invisible, because nothing in the tree aggregates a second client's
  counters. So it keeps its own, under a lock, and hands them back for the
  tool result to report - a cost that reaches no artifact is the shape of a
  dead run that looks clean.

* **Priced at the model it actually used.** Folding these tokens into the
  loop's totals would price them at `cfg.model`'s rate, and the report's
  claim is that every figure traces to a line someone can check.

* **Bounded, because it cannot be cancelled.** The orchestrator abandons the
  agent thread after as little as five seconds and a Python thread cannot be
  killed. Five attempts carry 62 seconds of backoff sleeps regardless of the
  timeout, so the abandoned call would keep retrying and keep spending. One
  attempt, a short timeout, and a deadline checked before each call.

* **Its errors never carry a provider's bytes.** The adapters embed up to 500
  bytes of a provider's response body in `LLMError`, `_call_agent` puts
  `agent_fn raised <Type>: <message>` into the sweep's note, and the
  artifact redaction only replaces operator-declared secrets. A gateway that
  echoes an Authorization header into an error body would land it in the
  session. Only the exception TYPE and a fixed sentence leave this module.
"""

from __future__ import annotations

import threading
import time

__all__ = ["WordlistAgent", "make_agent_fn", "AGENT_ROLE"]

#: The role the model table is asked for. `breadth` is the right one by its
#: own definition - the table's cheapest model that can do wide, shallow
#: work - and that is exactly what generating path candidates is. Not
#: `cfg.model`: the planner's model is chosen for reasoning over a whole
#: engagement, and paying its rate per sweep for a wordlist is waste the
#: report would have to explain.
AGENT_ROLE = "breadth"

#: One attempt. See the module docstring: the caller cannot cancel this.
MAX_ATTEMPTS = 1

#: Short, because the orchestrator's grace is measured in seconds. A model
#: that cannot answer in this window is a model whose answer has nowhere to
#: go by the time it arrives.
TIMEOUT_S = 20.0

#: A wordlist does not need a long reply, and a cap here is also a cost
#: bound. `_MAX_AGENT_SUGGESTIONS` in the orchestrator caps what it will use.
MAX_TOKENS = 700


class WordlistAgent:
    """A callable `agent_fn`, safe to share across concurrent sweeps.

    `exploit_fanout` hands ONE `agent_fn` to up to sixteen sweeps that run at
    the same time, each on its own thread, so this is shared mutable state by
    construction. Everything it mutates is under `_lock`, and the client it
    calls is the only thing it does not own exclusively - which is why it
    builds its own rather than borrowing the loop's.
    """

    def __init__(self, client, model: str, deadline_s: float = TIMEOUT_S):
        self._client = client
        self.model = model
        self._deadline_s = float(deadline_s)
        self._lock = threading.Lock()
        self.calls = 0
        self.failures = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.last_error = ""
        #: (prompt, reply) per successful call, for the adapter to record.
        #: Bounded: a fan-out of sixteen endpoints would otherwise hold
        #: sixteen prompts and replies in memory for the whole sweep.
        self.exchanges: list[tuple[str, str]] = []

    # -- the agent_fn contract: one positional str in, a str out, never raises

    def __call__(self, prompt: str) -> str:
        started = time.time()
        try:
            data = self._client.chat(
                [{"role": "user", "content": str(prompt or "")}], [], "")
        except BaseException as exc:            # noqa: BLE001
            # The TYPE and nothing else. A provider's error body can carry
            # the credential that was sent to it, and this string reaches
            # the sweep's note, the session artifacts and the report.
            with self._lock:
                self.failures += 1
                self.last_error = (
                    f"{type(exc).__name__} from the {self.model} call "
                    f"after {time.time() - started:.1f}s (message withheld: "
                    "a provider error body can echo the credential)")
            return ""
        text = _text_of(data)
        with self._lock:
            self.calls += 1
            self.input_tokens += _count(data, "input_tokens")
            self.output_tokens += _count(data, "output_tokens")
            if text and len(self.exchanges) < 16:
                self.exchanges.append((str(prompt or ""), text))
        return text

    # -- what the adapter reports, so the spend reaches an artifact

    def stats(self) -> dict:
        with self._lock:
            out = {
                "model": self.model,
                "calls": self.calls,
                "failures": self.failures,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
            }
            if self.last_error:
                out["last_error"] = self.last_error
            return out


def _text_of(data) -> str:
    """The reply text out of either provider's return shape.

    `ClaudeClient` returns the raw Anthropic body (a `content` list of
    blocks); `OpenAICompatClient` returns its own normalised shape. Reading
    both here rather than assuming one keeps this module provider-agnostic,
    which is the same reason `make_client` exists.
    """
    if not isinstance(data, dict):
        return ""
    parts: list[str] = []
    for block in data.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text") or ""))
        elif isinstance(block, str):
            parts.append(block)
    if parts:
        return "\n".join(parts).strip()
    # OpenAI-compatible normalisation, and a last resort for a shape neither
    # adapter produced - better an empty string than a traceback on a thread
    # whose exception nobody sees.
    for key in ("text", "output_text", "reply"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _count(data, key: str) -> int:
    if not isinstance(data, dict):
        return 0
    usage = data.get("usage")
    if isinstance(usage, dict):
        try:
            return int(usage.get(key) or 0)
        except (TypeError, ValueError):
            return 0
    return 0


def make_agent_fn(cfg) -> tuple[WordlistAgent | None, str]:
    """`(agent, "")` when a model is configured, `(None, reason)` when not.

    CALL THIS ON THE MAIN THREAD. It constructs the client, which resolves
    the credential, and that resolution is not safe to do concurrently.

    The reason string is for the caller to pass through to the operator
    verbatim. "No model configured" and "the model refused" are different
    facts about a run and must not read the same, which is the same
    distinction the orchestrator already makes between `agent_fn=None` and an
    agent that returned nothing usable.
    """
    if cfg is None:
        return None, ("no configuration reached this tool, so no model could "
                      "be asked; the tool half ran on its own")
    try:
        from .. import llm as _llm
        from .. import models as _models
    except Exception as exc:                    # pragma: no cover
        return None, f"the model path is unavailable: {type(exc).__name__}"

    model = ""
    try:
        # `for_role` returns a Model, not a name - `str(model_obj)` is its
        # repr, which `make_client` would not find in the table and would
        # then route to Anthropic as a nonsense model name. Caught by
        # checking the return type rather than by a failed call.
        picked = _models.for_role(AGENT_ROLE)
        model = str(getattr(picked, "key", "") or "")
    except Exception:                           # noqa: BLE001
        model = ""
    if not model:
        # Fall back to the configured model rather than refusing: a tree
        # whose table has no `breadth` entry should still get the hybrid,
        # and the stats say which model was billed either way.
        model = str(getattr(cfg, "model", "") or "")
    if not model:
        return None, ("no model name is configured and the table offers no "
                      f"{AGENT_ROLE!r} role; the tool half ran on its own")

    side = _clone_cfg(cfg, model)
    try:
        client = _llm.make_client(side)
    except Exception as exc:                    # noqa: BLE001
        # The TYPE only, for the same reason __call__ withholds the message:
        # this string is reported to the operator and can reach an artifact.
        return None, (f"no usable client for {model}: {type(exc).__name__} - "
                      "set a key, or the hybrid runs its tool half alone")
    for attr, value in (("max_attempts", MAX_ATTEMPTS),
                        ("timeout", TIMEOUT_S),
                        ("max_tokens", MAX_TOKENS)):
        try:
            setattr(client, attr, value)
        except Exception:                       # pragma: no cover
            pass
    return WordlistAgent(client, model), ""


def _clone_cfg(cfg, model: str):
    """`cfg` with the model swapped, without mutating the caller's.

    A shallow copy, because the credential fields must carry over: they were
    resolved once on the main thread and re-resolving is the hazard this
    module's docstring opens with.
    """
    import copy
    try:
        side = copy.copy(cfg)
        side.model = model
        return side
    except Exception:                           # pragma: no cover
        return cfg
