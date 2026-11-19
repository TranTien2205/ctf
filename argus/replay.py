"""Deterministic re-verification: send the recorded request again.

The proof matrix reads BYTES and a second model reads the INTERPRETATION.
Neither asks whether the target still does it. This does, with no model in
the loop at all: the request a finding cites is sent again through the same
scoped, recording client, and the only question is whether the quoted bytes
come back.

Three outcomes, and the third is first-class:

  reproduced       the target produced the quoted bytes again
  not_reproduced   the request was sent and the bytes did not come back
  inconclusive     the question could not be put to the target

`inconclusive` is not a soft `not_reproduced`. A finding that fails to
reproduce may be perfectly real - the target may have been patched between
the run and the replay, the exploit may be stateful, or the proof may rest
on a value that only occurs once. Reporting those as refutations would turn
a verification tool into a generator of false retractions, which is the
same failure as a fabricated finding pointed the other way.

AND REDACTION MAKES MOST REAL ENGAGEMENTS INCONCLUSIVE BY DEFAULT.
A recorded request stores `credential_sha256_16` - the HASH of each
credential header, never the value. Measured on this repository's own
sealed sessions:

    argus-lab        64 requests,  2 carry a credential   (3%)
    argus-lab-team   74 requests,  2 carry a credential   (2%)
    bwapp            23 requests, 23 carry a credential (100%)
    dvwa             18 requests, 18 carry a credential (100%)

The self-written lab barely authenticates; the two third-party
applications authenticate on every request. So on the targets that look
like real work, a replay without the operator re-supplying the credential
can say nothing at all - and it must SAY that rather than report a target
that refused an unauthenticated request as a finding that did not hold.

Like `judge`, this never raises a finding's standing: it cannot promote,
it cannot touch `grade`, and a failure to reproduce is recorded and never
cleared by a later success.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

#: Headers the wire computes from the scoped URL. Replaying a recorded
#: Content-Length against a body the client re-encodes is how a replay
#: becomes a different request than the one it claims to repeat.
HOP_BY_HOP = frozenset({
    "host", "content-length", "transfer-encoding", "connection",
    "keep-alive", "proxy-authenticate", "proxy-authorization", "te",
    "trailer", "upgrade",
})

#: What `not_reproduced` is allowed to mean. Anything else is inconclusive.
OUTCOMES = ("reproduced", "not_reproduced", "inconclusive")


@dataclass
class Replay:
    """One re-verification attempt, and what it is allowed to claim."""
    finding_id: str
    outcome: str
    reason: str
    source_id: str = ""          # the recorded entry this repeated
    evidence_id: str = ""        # the replay's OWN recorded exchange
    status: int = 0
    ts: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if self.outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {OUTCOMES}")

    def to_dict(self) -> dict:
        out = {"finding_id": self.finding_id, "outcome": self.outcome,
               "reason": self.reason, "ts": self.ts}
        for key in ("source_id", "evidence_id"):
            if getattr(self, key):
                out[key] = getattr(self, key)
        if self.status:
            out["status"] = self.status
        return out


def _entry_response_body(entry: dict) -> str:
    resp = entry.get("response")
    if not isinstance(resp, dict):
        return ""
    return str(resp.get("body") or "")


def witness_for(finding: dict, entries: list[dict]) -> dict | None:
    """The cited entry whose RESPONSE contains the quoted bytes.

    Not merely the first cited id: a finding cites the pair, and only the
    response half can be re-verified. Looking for the excerpt rather than
    taking `evidence_ids[0]` is the same correlation the proof matrix
    makes - "the target produced the quoted bytes" names an entry, and that
    entry is the one worth sending again.
    """
    quote = str(finding.get("evidence_excerpt") or "").strip()
    if not quote:
        return None
    cited = {str(i) for i in (finding.get("evidence_ids") or [])}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if cited and str(entry.get("id")) not in cited:
            continue
        if quote and quote in _entry_response_body(entry):
            return entry
    return None


def credentials_needed(entry: dict, supplied: dict | None) -> list[str]:
    """Credential headers the recorded request carried and the replay lacks.

    The transcript holds `credential_sha256_16: {"cookie": "<16 hex>"}` -
    the hash, so the value cannot be replayed from the record. A header
    supplied at replay time covers it; nothing else does.
    """
    req = entry.get("request")
    if not isinstance(req, dict):
        return []
    recorded = req.get("credential_sha256_16") or {}
    if not isinstance(recorded, dict):
        return []
    have = {str(k).lower() for k in (supplied or {})}
    return sorted(str(name).lower() for name in recorded
                  if str(name).lower() not in have)


def replay_headers(entry: dict) -> dict[str, str]:
    """The recorded headers, minus what must not be replayed.

    Credential headers are dropped rather than sent: their recorded value
    IS the hash, and sending a 16-hex-digit string where a session cookie
    belongs would be a request the target refuses for a reason that has
    nothing to do with the finding. The client's own default headers carry
    whatever the operator supplied instead.
    """
    req = entry.get("request")
    if not isinstance(req, dict):
        return {}
    creds = {str(k).lower() for k in (req.get("credential_sha256_16") or {})}
    out: dict[str, str] = {}
    for name, value in (req.get("headers") or {}).items():
        low = str(name).lower()
        if low in HOP_BY_HOP or low in creds:
            continue
        out[str(name)] = str(value)
    return out


def supplied_headers(client) -> dict:
    """What the caller configured the client to send on every request.

    The client stores these PRIVATELY, as `_default_headers`, and reading
    it is deliberate: the client is the only thing that knows what will
    actually go on the wire, and accepting the headers as a separate
    argument would let a caller claim a credential the client does not
    send. `test_the_client_still_exposes_the_headers_this_reads` holds the
    name, because the first version of this read a public attribute that
    does not exist and therefore reported every supplied credential as
    missing.
    """
    for name in ("_default_headers", "default_headers"):
        value = getattr(client, name, None)
        if isinstance(value, dict):
            return value
    return {}


def replay_finding(client, finding: dict, entries: list[dict]) -> Replay:
    """Send a finding's cited request again and report what came back.

    Never raises: a replay that cannot be performed is a verdict of
    `inconclusive` with the reason, not an exception that aborts the run
    over one unreplayable finding.
    """
    fid = str(finding.get("id") or "")
    quote = str(finding.get("evidence_excerpt") or "").strip()
    if not quote:
        return Replay(fid, "inconclusive",
                      "the finding quotes no bytes, so there is nothing to "
                      "look for in a fresh response")

    entry = witness_for(finding, entries)
    if entry is None:
        return Replay(fid, "inconclusive",
                      "no cited entry's response contains the quoted bytes, "
                      "so the exchange to repeat cannot be identified")

    missing = credentials_needed(entry, supplied_headers(client))
    if missing:
        return Replay(
            fid, "inconclusive",
            f"the recorded request carried {', '.join(missing)} and the "
            "transcript stores the hash, not the value - supply it with "
            "--header to replay this one",
            source_id=str(entry.get("id") or ""))

    req = entry.get("request") or {}
    try:
        result = client.send(
            str(req.get("method") or "GET"),
            str(req.get("url") or ""),
            headers=replay_headers(entry),
            body=req.get("body"),
            tool="replay",
            note=f"re-verifying {fid}")
    except BaseException as exc:                              # noqa: BLE001
        # The exception TYPE only. A transport error's message can echo the
        # URL with a credential in it, and the scope guard's refusal is the
        # one thing a verification step must not launder into a result.
        return Replay(fid, "inconclusive",
                      f"the request could not be sent ({type(exc).__name__})",
                      source_id=str(entry.get("id") or ""))

    body = str(result.get("body") or "")
    status = int(result.get("status") or 0)
    rid = str(result.get("request_id") or "")

    # THE CLIENT DOES NOT RAISE ON A TRANSPORT FAILURE. It returns
    # {"error": "ConnectError: [Errno 111] Connection refused", "status": 0,
    # "body": ""} - measured against a dead port on a real socket. So the
    # `except` above never fires for the commonest reason a replay cannot
    # be performed, and without this branch an unreachable target produced
    # `not_reproduced` for every finding: a target that is merely DOWN
    # would retract an entire engagement.
    #
    # Only the error's TYPE is repeated. A transport message can carry the
    # URL, and a URL can carry a credential.
    err = str(result.get("error") or "")
    if err or status == 0:
        kind = err.split(":", 1)[0].strip() or "no status"
        return Replay(fid, "inconclusive",
                      f"the target did not answer ({kind}), so it was never "
                      "asked whether it still does this",
                      source_id=str(entry.get("id") or ""),
                      evidence_id=rid)
    if quote in body:
        return Replay(fid, "reproduced",
                      f"the target returned the quoted bytes again "
                      f"(HTTP {status})",
                      source_id=str(entry.get("id") or ""),
                      evidence_id=rid, status=status)
    return Replay(fid, "not_reproduced",
                  f"the request was sent and answered HTTP {status}, and the "
                  "quoted bytes were not in the response. That is not a "
                  "retraction: a patched target, a stateful exploit or a "
                  "once-only value all look like this",
                  source_id=str(entry.get("id") or ""),
                  evidence_id=rid, status=status)


def apply_replay(finding: dict, replay: Replay) -> dict:
    """Fold a replay into a finding WITHOUT ever raising its standing.

    The same three one-way doors `judge.apply_verdict` uses, for the same
    reason. `grade` belongs to the proof matrix and is not touched here.
    Every attempt is KEPT: a later `reproduced` does not erase an earlier
    `not_reproduced`, because a target that answers differently on two
    replays is information about the target and not a correction.
    """
    out = dict(finding)
    history = finding.get("replays")
    history = list(history) if isinstance(history, list) else (
        [finding["replay"]] if isinstance(finding.get("replay"), dict) else [])
    history.append(replay.to_dict())
    out["replays"] = history
    out["replay"] = replay.to_dict()
    if replay.outcome == "not_reproduced":
        out["replay_failed"] = True          # one-way, never cleared
    return out


def reverified(finding: dict) -> bool:
    """Has the target been asked again about this finding?

    `inconclusive` is NOT a re-verification - the question never reached
    the target. Counting it as one is how a finding nobody could check
    would look checked, which is the same hole as treating a judge's
    transport failure as a completed review.
    """
    history = [r for r in (finding.get("replays") or []) if isinstance(r, dict)]
    if not history and isinstance(finding.get("replay"), dict):
        history = [finding["replay"]]
    return any(r.get("outcome") in ("reproduced", "not_reproduced")
               for r in history)
