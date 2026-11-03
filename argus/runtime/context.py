"""Context assembly and compaction — the harness's real work.

A long engagement produces far more tool output than any context window holds,
and the naive fixes both fail: dropping the oldest messages loses the
measurement that explains the current state, and summarising everything loses
the exact strings a proof depends on.

What this does instead: the **ledger** is the memory, and the transcript is a
short working set. Old tool results collapse to one line each (tool, summary,
evidence id) because the full record is on disk and can be re-read with
ledger.read_evidence. The last few results stay verbatim, since that is where
the next decision is made.
"""
from __future__ import annotations

from .providers.base import Message
from ..util import bound


def compact(messages: list[Message], profile) -> tuple[list[Message], int]:
    """Collapse old tool results until the transcript fits. Returns the new list
    and how many results were collapsed."""
    budget = profile.history_chars
    total = sum(message.chars() for message in messages)
    if total <= budget:
        return messages, 0
    keep_verbatim = 4
    out = list(messages)
    collapsed = 0
    for index, message in enumerate(out):
        if total <= budget:
            break
        if index >= len(out) - keep_verbatim:
            break
        if message.role != "tool" or message.content.startswith("[collapsed]"):
            continue
        before = message.chars()
        first_line = (message.content or "").strip().splitlines()[0] if message.content else ""
        marker = _evidence_id(message.content)
        out[index] = Message(role="tool", tool_call_id=message.tool_call_id, name=message.name,
                             content=f"[collapsed] {message.name}: {bound(first_line, 220)}"
                                     + (f" (evidence {marker}; ledger.read_evidence to re-read)"
                                        if marker else ""))
        total -= before - out[index].chars()
        collapsed += 1
    if total > budget:
        # Still too large: drop the oldest collapsed lines, which are pure index.
        trimmed = [m for i, m in enumerate(out)
                   if i >= len(out) - keep_verbatim or not m.content.startswith("[collapsed]")]
        out = trimmed or out[-keep_verbatim:]
    return out, collapsed


def _evidence_id(text: str) -> str:
    for line in (text or "").splitlines():
        if line.startswith("evidence_id:"):
            return line.split(":", 1)[1].strip()
    return ""


def observation(result_text: str, profile) -> str:
    """One tool result, bounded for this model. The head is kept and the tail is
    kept: a tool that prints a summary first and a table last loses the middle,
    which is the right thing to lose."""
    return bound(result_text, profile.observation_cap, tail=min(1500, profile.observation_cap // 4))
