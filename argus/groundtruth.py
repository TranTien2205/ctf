"""An independent oracle: what the TARGET says, not what argus says.

Every number argus produces about itself is argus marking its own work. A
proof gate makes that marking honest, but it cannot make it independent:
`proven` means the evidence met a requirement this package wrote.

Some deliberately vulnerable applications publish a scoreboard - OWASP Juice
Shop serves `GET /api/Challenges` with 118 challenges, each carrying a
`solved` flag the application sets when it observes the exploit succeed.
That flag is set by the TARGET, from its own view of its own state, and no
part of argus can write it. It is the closest thing to ground truth an
engagement against such a target can have.

WHY THIS IS NOT A TOOL. It is deliberately absent from `tools/registry.py`:
an agent that can read the scoreboard can read the answers. The measurement
would then be of a system that was told what to find, which is a different
and much weaker claim than the one this is for. The operator reads it,
before and after, around a run the agent drove blind.

WHAT IT DOES NOT CLAIM. Juice Shop's categories ("Injection", "XSS") and
argus's proof classes (`sqli`, `rce`, `xss`) are different vocabularies with
no exact mapping, so the correlation below is reported as approximate and
the raw per-challenge list is kept beside it. A challenge already solved
before the run is excluded: the scoreboard is cumulative and a target that
someone else exercised yesterday would otherwise credit this run.
"""

from __future__ import annotations

import json
import time
import urllib.parse
from dataclasses import dataclass, field

__all__ = ["Scoreboard", "SCOREBOARDS", "read_scoreboard", "newly_solved",
           "correlate", "CATEGORY_HINTS"]

# Applications that publish their own state, and where. Adding one is a data
# change: a path, and the shape of what it returns.
SCOREBOARDS = {
    "juice-shop": {
        "path": "/api/Challenges",
        "root": "data",
        "fields": ("key", "name", "category", "difficulty", "solved"),
    },
}

# Approximate, and labelled approximate wherever it is used. A category is
# the target's word for a family of bugs; a proof class is this package's
# word for what a specific artifact proves. They overlap, they are not the
# same partition, and a table that presents them as equal invents a
# precision neither side has.
CATEGORY_HINTS = {
    "Injection": ("sqli", "nosqli", "rce", "ssti", "xxe"),
    "XSS": ("xss",),
    "Broken Access Control": ("idor", "method", "massassign"),
    "Broken Authentication": ("jwt", "lockout", "enum", "auth"),
    "Sensitive Data Exposure": ("disclosure", "lfi"),
    "Improper Input Validation": ("upload", "redirect", "crlf"),
    "Security Misconfiguration": ("cors", "xfh", "method"),
    "XXE": ("xxe",),
    "Insecure Deserialization": ("deserialize",),
    "Unvalidated Redirects": ("redirect",),
}


@dataclass
class Scoreboard:
    source: str
    app: str
    read_at: float
    total: int
    challenges: list[dict] = field(default_factory=list)

    @property
    def solved(self) -> list[dict]:
        return [c for c in self.challenges if c.get("solved")]

    def keys_solved(self) -> set:
        return {c.get("key") for c in self.solved if c.get("key")}


def _recorded_body(client, sent: dict) -> str:
    """The body as RECORDED, never the prefix the client returns.

    The transcript holds `body[:200000]`; the return value holds
    `body[:12000]`. Everything here counts records, so it reads the first.
    If the recorded body is itself truncated the caller is told, because a
    count taken from a cut list is not a count.
    """
    session = getattr(client, "session", None)
    entry = None
    if session is not None:
        entry = (getattr(session, "_transcript", {}) or {}).get(
            (sent or {}).get("request_id"))
    if isinstance(entry, dict):
        response = entry.get("response") or {}
        if response.get("body_truncated_at"):
            raise ValueError(
                "the scoreboard response was truncated at "
                f"{response['body_truncated_at']} bytes, so any count taken "
                "from it would be short. Raise the body cap or read the "
                "scoreboard outside the client.")
        body = response.get("body")
        if isinstance(body, str):
            return body
    return str((sent or {}).get("body") or "")


def read_scoreboard(client, base_url: str, app: str = "juice-shop",
                    timeout_s: int = 20) -> Scoreboard:
    """Read a target's own scoreboard THROUGH the guarded client.

    Through the client, not around it: the read is an in-scope request like
    any other and lands in the transcript, so a number quoted from it can be
    traced to the response that carried it. A measurement taken off the
    record is a measurement nobody can check.
    """
    spec = SCOREBOARDS.get(app)
    if spec is None:
        raise ValueError(f"no scoreboard is known for {app!r}; "
                         f"known: {sorted(SCOREBOARDS)}")
    url = urllib.parse.urljoin(base_url if base_url.endswith("/")
                               else base_url + "/", spec["path"].lstrip("/"))
    sent = client.send("GET", url, tool="groundtruth",
                       note=f"{app} scoreboard (operator-side, not agent-visible)")

    # MEASURED: Juice Shop's scoreboard is 69KB and `GuardedClient.send`
    # hands back `body[:12000]` to bound what reaches a model, storing the
    # full body in the transcript. Parsing the RETURNED value raised
    # "Unterminated string at char 11978" - and the dangerous case is the
    # one that does not raise: a cut landing on a record boundary parses
    # cleanly and yields a SHORT challenge list, so this module would
    # report a wrong total with no error anywhere. A measurement that can
    # be quietly wrong is worse than one that fails.
    body = _recorded_body(client, sent)
    try:
        data = json.loads(body)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{url} did not return JSON ({exc}); "
                         f"is this really {app}?") from exc
    rows = data.get(spec["root"]) if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise ValueError(f"{url} returned no {spec['root']!r} list")
    keep = spec["fields"]
    challenges = [{k: row.get(k) for k in keep}
                  for row in rows if isinstance(row, dict)]
    return Scoreboard(source=url, app=app, read_at=time.time(),
                      total=len(challenges), challenges=challenges)


def newly_solved(before: Scoreboard, after: Scoreboard) -> list[dict]:
    """Challenges the target marked solved BETWEEN the two reads.

    The scoreboard is cumulative. Without this difference a target someone
    exercised yesterday credits this run with work it did not do - the same
    absolute-where-a-differential-is-needed mistake this package keeps
    finding in its own gate.
    """
    had = before.keys_solved()
    return [c for c in after.solved if c.get("key") not in had]


def correlate(before: Scoreboard, after: Scoreboard,
              findings: list[dict]) -> dict:
    """What the target confirmed, beside what argus claimed.

    Returns both halves and does not reduce them to one score. The useful
    question is not "what percentage" - it is whether anything argus called
    `proven` has independent confirmation, and whether the target recorded
    anything argus never claimed.
    """
    gained = newly_solved(before, after)
    proven = [f for f in findings or () if str(f.get("grade", "")).lower() == "proven"]
    claimed_classes = {str(f.get("vuln_class", "")).lower() for f in proven}

    confirmed, unmapped = [], []
    for ch in gained:
        hints = CATEGORY_HINTS.get(ch.get("category") or "", ())
        hit = sorted(claimed_classes & set(hints))
        (confirmed if hit else unmapped).append(
            {**ch, "argus_classes": hit})

    # THE THIRD QUADRANT. Target solved + argus claimed is `confirmed`;
    # target solved + argus silent is `unclaimed`; and a claim the board
    # does not corroborate had nowhere to go, so a run that claimed EVERY
    # class scored the same confirmation as one that claimed the right one.
    # Measured on the live target after a real SQLi login bypass flipped
    # `loginAdminChallenge`: claiming `sqli` and claiming all of
    # sqli/xss/rce/idor/ssrf both reported `confirmed=['loginAdminChallenge']`
    # with nothing to separate them. Breadth was free.
    #
    # It is NOT called a false positive. The board covers only this
    # application's own challenges, so a real finding outside that set is
    # uncorroborated rather than wrong - and a class whose challenges were
    # already solved before the run cannot be corroborated at all. The
    # honest report is the ratio and the names, for a human to read.
    corroborated = {cls for ch in confirmed for cls in ch["argus_classes"]}
    uncorroborated = sorted(claimed_classes - corroborated)

    return {
        "app": after.app,
        "source": after.source,
        # How much of what argus claimed the board speaks to at all. A run
        # that claims one class and gets it confirmed reads 1/1; one that
        # claims five and gets the same single confirmation reads 2/5.
        #
        # 2, not 1, and the reason is worth stating rather than hiding: one
        # category maps to SEVERAL classes, so `loginAdminChallenge`
        # (category Injection) corroborates any of sqli/nosqli/rce/ssti/xxe
        # that was claimed. Measured: claiming all five classes scored 2/5
        # off a single SQLi login bypass, because `rce` is in the same hint
        # set. So this numerator is an UPPER BOUND on corroboration, and
        # `uncorroborated_classes` is the half that cannot be inflated that
        # way - it listed three classes for the shotgun claim and none for
        # the focused one, which is the discrimination this was added for.
        "claims_corroborated_upper_bound": len(corroborated),
        "claims_made": len(claimed_classes),
        "uncorroborated_classes": uncorroborated,
        # Exact, because a challenge is a challenge: how many of the
        # newly-solved ones matched any claim at all.
        "newly_solved_matched": len(confirmed),
        "scoreboard_total": after.total,
        "solved_before": len(before.solved),
        "solved_after": len(after.solved),
        "newly_solved": gained,
        # The target confirmed something in a family argus also claimed.
        # "Confirmed" is as strong as the category mapping, which is
        # approximate - the challenge keys are listed so a reader can check.
        "confirmed_approx": confirmed,
        # The target recorded a solve argus claimed nothing for. Either the
        # run tripped it blind, or the mapping is too narrow. Both are worth
        # a human look, and neither is a failure of the gate.
        "unclaimed": unmapped,
        "proven_findings": len(proven),
        "proven_classes": sorted(claimed_classes),
        "caveat": ("category-to-class mapping is approximate; the per-challenge "
                   "keys above are the evidence, the counts are a summary of "
                   "them. The scoreboard is the target's own record and no "
                   "part of argus can write it. An uncorroborated class is "
                   "not a false positive: this board covers only this "
                   "application's own challenges."),
    }
