#!/usr/bin/env python3
"""Decide the ONE next action for one service in an attack-defense contest.

The runbook's steady-state loop asks three questions every tick -- is the service
green, did anyone new attack us, who stopped yielding flags -- and each answer
lives in a different JSON file written by a different tool. At minute 200 nobody
opens three files and diffs them against the last tick. This tool opens them and
says which of the three is currently unanswered, and what to type.

    python3 tools/ad/tick.py runs/notes/ledger.json --init notes   # once
    python3 tools/ad/tick.py runs/notes/ledger.json                # every tick
    python3 tools/ad/tick.py runs/notes/ledger.json record --kind patch-verdict \
        --field id=p1 --field verdict=regression

The ordering is the whole tool, and it comes from the scoring rather than from
taste: availability is scored continuously and a minute of downtime can never be
won back, while a flag is scored once per tick and the next tick brings another
one. So a red or unmeasured service outranks every attack; a submitter that has
stopped accepting flags outranks a new exploit, because those flags are already
stolen and are sitting in a file; and a capture nobody has mined outranks
inventing a hypothesis, because another team's working exploit is cheaper to read
than a bug is to find.

Two guards carry it:

  * a missing or stale measurement is UNANSWERED, never green. This is the local
    analogue of "a timeout is never a confirm". The commonest way to lose
    availability is to keep attacking for six minutes while the last saved check
    is from before the service fell over.
  * no action that sends packets at another team is returned while the service is
    red or unanswered. That is enforced structurally at the end of `decide_next`
    and not only by the order of the rules, so a later edit that reorders them
    cannot quietly switch the guard off.

Sibling plane, deliberately: nothing here imports tools/state.py, tools/hooks.py
or tools/decide.py, and nothing here writes challenges/<name>/state.json. The
jeopardy controller budgets one target and gates one verified flag; this loop has
one target per team and a flag per team per tick.

`traffic_mine.param_names` is imported for exactly one reason. A mined candidate
carries no parameter list of its own, and the miner truncates its `query` to 300
characters and its `body` to 500, so a stable fingerprint has to be recomputed
from what survived. Importing the scorer's own function keeps one definition of
"a parameter" in the tree instead of two that drift apart.

Paths inside the ledger are read exactly as written, relative to the working
directory, because every command this tool prints is also meant to be run from
the tree root. Only single directories are listed and nothing is walked
recursively: a recursive walk on a contest box is how a collector meets a hung
network mount and never returns.

Output is JSON on stdout, like every other tool in this tree.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import traffic_mine  # noqa: E402

TEMPLATE = os.path.join(HERE, "ledger.template.json")

# Expressed in ticks and counts on purpose. A per-attempt-and-per-minute pair is
# the jeopardy controller's contract and belongs to tools/decide.py; restating it
# here would be a second number that can drift from the one being enforced.
BUDGET = {
    "defensive": "unbudgeted",
    "ticks_per_exploit_idea": 2,
    "max_unverified_patches": 1,
}

# The two actions that put packets on another team's service. Everything else is
# reading your own files. This set is what the structural guard tests, so adding
# an outbound action means adding it here as well.
ATTACK_ACTIONS = frozenset({"promote_candidate", "farm"})

# A directory listing is bounded because a rotating capture directory is the one
# place here that can hold an unbounded number of files, and the only things
# needed from it are the count and the newest mtime.
MAX_DIR_ENTRIES = 20000

VALID_PHASES = ("intake", "steady")


# ------------------------------------------------------------------ ledger io
def atomic_json(path, data):
    """Write JSON so a ctrl-C mid-write cannot leave a half-parsed ledger.

    Same shape as tools/state.py's atomic_json, reimplemented rather than
    imported: tools/ad is a sibling control plane and importing the jeopardy
    state module would be the first thread of exactly the coupling this
    directory exists to avoid.
    """
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                         dir=directory, delete=False) as handle:
            temporary = handle.name
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def init_ledger(path, service, template_path=TEMPLATE):
    """Write a new ledger from the template. Returns (ok, payload).

    Refuses an existing file. A second --init halfway through a contest would
    silently discard the intake record, the rollback strings and the exploit
    ideas, which is the one file in this directory that cannot be rebuilt from
    anything else on disk.
    """
    if os.path.exists(path):
        return False, {"ok": False, "reason":
                       "%s already exists; --init would discard the intake "
                       "record, the rollback strings and the exploit ideas, and "
                       "none of them can be rebuilt from another file" % path}
    try:
        with open(template_path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        return False, {"ok": False, "reason": "cannot read the template: %s" % exc}
    # Substituted in the serialized form so the placeholder is replaced inside
    # every path at once; the template has no other use for the angle brackets.
    ledger = json.loads(raw.replace("<service>", service))
    ledger["service"] = service
    atomic_json(path, ledger)
    return True, {"ok": True, "mode": "ad-tick-init", "ledger": path,
                  "service": service,
                  "intake_steps": [s["step"] for s in ledger.get("intake", [])],
                  "next": "fill authorized_event and the paths block, then run: "
                          "python3 tools/ad/tick.py %s" % path}


# ---------------------------------------------------------------------- facts
def _stat_mtime(path):
    try:
        return os.stat(path).st_mtime
    except OSError:
        return None


def _dir_stats(path):
    """(file_count, newest_mtime) for ONE directory. No recursion, ever."""
    count, newest = 0, None
    try:
        with os.scandir(path) as it:
            for entry in it:
                if count >= MAX_DIR_ENTRIES:
                    break
                try:
                    if not entry.is_file():
                        continue
                    when = entry.stat().st_mtime
                except OSError:
                    continue
                count += 1
                if newest is None or when > newest:
                    newest = when
    except OSError:
        return None, None
    return count, newest


def _newest_json(path):
    """(path, mtime) of the newest .json under `path`, or of `path` itself."""
    if os.path.isdir(path):
        best, best_when, seen = None, None, 0
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if seen >= MAX_DIR_ENTRIES:
                        break
                    seen += 1
                    if not entry.name.endswith(".json"):
                        continue
                    try:
                        when = entry.stat().st_mtime
                    except OSError:
                        continue
                    if best_when is None or when > best_when:
                        best, best_when = entry.path, when
        except OSError:
            return None, None
        return best, best_when
    if os.path.isfile(path):
        return path, _stat_mtime(path)
    return None, None


def _last_json_line(path, limit=65536):
    """The last complete JSON object in a line-per-tick log, or None.

    Reads the tail only. flag_farm.py appends one JSON line per tick for the
    whole contest, and reading the whole file every tick to find the last line
    is a cost that grows all afternoon.
    """
    try:
        with open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(max(0, size - limit))
            blob = fh.read().decode("utf-8", "replace")
    except OSError:
        return None
    for line in reversed(blob.split("\n")):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            return json.loads(line)
        except ValueError:
            continue
    return None


def path_of(ledger, key):
    """A path from the ledger, or a visible placeholder.

    A placeholder is printed rather than the string "None": a command holding
    <sla-spec> is one an operator fixes, and a command holding None is one they
    paste.
    """
    value = ((ledger or {}).get("paths") or {}).get(key)
    return value if value else "<%s>" % key.replace("_", "-")


def gather_facts(ledger, now=None):
    """Read every derived fact off disk. Never raises.

    Each fact that cannot be read becomes a null plus one line in
    `facts_missing`. A fact that is absent must never arrive at the decision as
    a zero or a False, because both read as "measured and fine".
    """
    now = time.time() if now is None else now
    facts, missing = {}, []
    paths = (ledger or {}).get("paths") or {}

    sla_path, sla_when = _newest_json(paths.get("sla_saves") or "")
    facts["sla_save"] = sla_path
    facts["sla_ok"] = None
    facts["sla_failed"] = []
    facts["sla_age_seconds"] = None
    if sla_path is None:
        missing.append("sla_saves: no saved sla_check run under %r"
                       % path_of(ledger, "sla_saves"))
    else:
        try:
            with open(sla_path, encoding="utf-8") as fh:
                saved = json.load(fh)
        except (OSError, ValueError) as exc:
            missing.append("sla_saves: %s is unreadable (%s)" % (sla_path, exc))
        else:
            facts["sla_ok"] = bool(saved.get("ok"))
            facts["sla_failed"] = [r.get("name") for r in saved.get("results", [])
                                   if not r.get("ok")]
            facts["sla_age_seconds"] = round(now - sla_when, 1) if sla_when else None

    live_count, live_when = _dir_stats(paths.get("capture_live") or "")
    facts["live_files"] = live_count
    facts["live_newest"] = live_when
    facts["live_age_seconds"] = round(now - live_when, 1) if live_when else None
    if live_count is None:
        missing.append("capture_live: %r is not a directory; the live capture is "
                       "not running or has not been split yet"
                       % path_of(ledger, "capture_live"))

    mined_path, mined_when = _newest_json(paths.get("mined") or "")
    facts["mined_path"] = mined_path
    facts["mined_newest"] = mined_when
    facts["mined_age_seconds"] = round(now - mined_when, 1) if mined_when else None
    facts["mined_top"] = None
    if mined_path is None:
        missing.append("mined: no traffic_mine output under %r"
                       % path_of(ledger, "mined"))
    else:
        try:
            with open(mined_path, encoding="utf-8") as fh:
                mined = json.load(fh)
        except (OSError, ValueError) as exc:
            missing.append("mined: %s is unreadable (%s)" % (mined_path, exc))
        else:
            top = mined.get("top") or []
            facts["mined_top"] = top[0] if top else None

    farm_path = paths.get("farm_log") or ""
    last = _last_json_line(farm_path) if farm_path else None
    farm_when = _stat_mtime(farm_path) if farm_path else None
    facts["last_farm_age_seconds"] = (round(now - farm_when, 1)
                                      if farm_when else None)
    facts["new_flags"] = None
    facts["immune"] = []
    facts["teams_yielding"] = []
    facts["submit_error"] = None
    facts["pending_flags"] = None
    facts["alert"] = None
    if last is None:
        missing.append("farm_log: no JSON tick line in %r"
                       % path_of(ledger, "farm_log"))
    else:
        facts["new_flags"] = last.get("new_flags")
        facts["immune"] = last.get("immune") or []
        facts["teams_yielding"] = last.get("teams_yielding") or []
        facts["submit_error"] = last.get("submit_error")
        facts["pending_flags"] = last.get("pending_flags")
        facts["alert"] = last.get("ALERT")

    return facts, missing


# --------------------------------------------------------------- fingerprints
def candidate_fingerprint(entry):
    """A stable id for a mined candidate, from method, path and parameter names.

    Not from the request bytes: the miner truncates `query` to 300 characters and
    `body` to 500, so two hits of the same exploit with different payload lengths
    would fingerprint differently and the same idea would be promoted twice.
    """
    names = traffic_mine.param_names({"query": entry.get("query") or "",
                                      "body": entry.get("body") or ""})
    blob = "%s\n%s\n%s" % (entry.get("method") or "", entry.get("path") or "",
                           "\n".join(sorted(names)))
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:12]


# -------------------------------------------------------------------- helpers
def sla_state(ledger, facts):
    """('green' | 'red' | 'unanswered', one sentence saying why).

    'unanswered' and 'red' are treated identically by the ordering, and the
    distinction is kept only so the operator knows whether to restart a service
    or to re-measure one. Neither is ever treated as green.
    """
    tick_seconds = float((ledger or {}).get("tick_seconds") or 60)
    ok = facts.get("sla_ok")
    age = facts.get("sla_age_seconds")
    if ok is None or age is None:
        return "unanswered", ("no saved sla_check run could be read, so the "
                              "service is unmeasured; unmeasured is not green")
    if not ok:
        failed = [f for f in (facts.get("sla_failed") or []) if f]
        return "red", ("the newest saved run is red: %s"
                       % (", ".join(failed) if failed else "check names missing"))
    if age > 2 * tick_seconds:
        return "unanswered", ("the newest saved run passed but is %.0fs old, more "
                              "than two ticks of %.0fs; a save older than the "
                              "outage it would report is not evidence"
                              % (age, tick_seconds))
    return "green", ("every check in the newest save passed, %.0fs ago" % age)


def _payload(action, rationale, commands, facts, missing, now, **extra):
    out = {
        "mode": "ad-tick",
        "at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now)),
        "action": action,
        "rationale": rationale,
        # `why` is the same sentence under the name the runbook uses; `rationale`
        # is the name tools/decide.py uses. Two readers, one string.
        "why": rationale,
        "budget": dict(BUDGET),
        "facts": facts,
        "facts_missing": list(missing),
        "commands": list(commands),
    }
    out.update(extra)
    return out


def _intake_commands(ledger, step):
    """One real command list per intake step, built from this ledger's paths.

    The off-box evidence directory is a placeholder on purpose: the ledger cannot
    name it, because a path this ledger knows is a path on the box being imaged.
    """
    spec = path_of(ledger, "sla_spec")
    saves = (path_of(ledger, "sla_saves") or "").rstrip("/")
    table = {
        "snapshot-before-touching": [
            "ss -ltnp > <off-box-evidence-dir>/t0-listening.txt",
            "date -Is; hostname; who",
            "systemctl list-units --type=service --state=running --no-pager",
        ],
        "evidence-copied-off-box": [
            "timeout 300 rsync -a /var/log/ <off-box-evidence-dir>/var-log/",
            "timeout 300 rsync -a /etc/ <off-box-evidence-dir>/etc/",
            "find <off-box-evidence-dir> -type f -exec sha256sum {} + "
            "> <off-box-evidence-dir>/SHA256SUMS",
        ],
        "sla-spec-written-and-green": [
            "python3 tools/ad/sla_check.py %s --save %s/t0-before-rotation.json"
            % (spec, saves),
        ],
        "credentials-rotated": [
            "python3 tools/ad/sla_check.py %s --save %s/after-rotation.json "
            "--compare %s/t0-before-rotation.json" % (spec, saves, saves),
        ],
        "unknown-keys-and-accounts-removed": [
            "awk -F: '($3 == 0 || $3 >= 1000) && $7 !~ /nologin|false/ "
            "{print $1, $3, $7}' /etc/passwd",
            "timeout 30 find /root /home -maxdepth 4 -name authorized_keys "
            "-exec sha256sum {} +",
        ],
        "planted-persistence-swept": [
            "cat skills/ad-planted-backdoor-hunt/SKILL.md",
            "systemctl list-timers --all --no-pager",
            "timeout 30 find /etc/cron.d /etc/cron.daily /var/spool/cron "
            "-type f -newermt '-14 days'",
        ],
        "baseline-capture-started": [
            "dumpcap -i <iface> -q -f 'tcp port <port>' -a duration:120 "
            "-w <baseline>.pcap",
            "python3 tools/ad/cap_split.py --pcap <baseline>.pcap --out %s"
            % path_of(ledger, "capture_baseline"),
            "dumpcap -i <iface> -q -f 'tcp port <port>' -b filesize:51200 "
            "-b files:20 -w <live>.pcap",
        ],
        "farm-dry-run-proven": [
            "python3 tools/ad/flag_farm.py %s --once --dry-run"
            % path_of(ledger, "farm_config"),
        ],
    }
    # An operator may add a step this table has never heard of, and refusing to
    # answer would be worse than saying so.
    return table.get(step, ["# no command table entry for the step %r: do it by "
                            "hand, then record it" % step])


def _measure_command(ledger, now, label="t"):
    saves = (path_of(ledger, "sla_saves") or "").rstrip("/")
    stamp = time.strftime("%H%M%S", time.localtime(now))
    return ("python3 tools/ad/sla_check.py %s --save %s/%s%s.json"
            % (path_of(ledger, "sla_spec"), saves, label, stamp))


def _record_command(ledger_path, kind, fields):
    parts = ["python3 tools/ad/tick.py %s record --kind %s" % (ledger_path, kind)]
    for key, value in fields:
        parts.append("--field %s=%s" % (key, value))
    return " ".join(parts)


# ----------------------------------------------------------------- the decider
def decide_next(ledger, facts, now=None, ledger_path="<ledger>"):
    """The decision, as a pure function of two dicts. No filesystem, no clock.

    Pure so the offline selftest can drive every branch with literal dicts. The
    moment this reads a file, the ordering rules stop being testable and the only
    way to check them is a contest.
    """
    now = time.time() if now is None else now
    ledger = ledger or {}
    facts = facts or {}
    missing = facts.get("_missing") or []
    tick_seconds = float(ledger.get("tick_seconds") or 60)
    patches = ledger.get("patches") or []
    ideas = ledger.get("exploit_ideas") or []
    state, state_why = sla_state(ledger, facts)

    result = _rules(ledger, facts, now, ledger_path, missing, tick_seconds,
                    patches, ideas, state, state_why)

    # The structural half of the second guard. The rule order already puts
    # restore_service first; this makes reordering them unable to switch the
    # guard off, which is the failure mode of a guard that is only an ordering.
    if result["action"] in ATTACK_ACTIONS and state != "green":
        return _payload(
            "restore_service",
            "an attack action (%s) was reached while the service is %s: %s. "
            "Availability is scored continuously and cannot be won back; a flag "
            "is scored once per tick and the next tick brings another one."
            % (result["action"], state, state_why),
            [_measure_command(ledger, now)], facts, missing, now,
            suppressed_action=result["action"])
    return result


def _rules(ledger, facts, now, ledger_path, missing, tick_seconds,
           patches, ideas, state, state_why):
    # 1. intake, while the phase says intake. Defensive and unbudgeted.
    if ledger.get("phase") == "intake":
        steps = ledger.get("intake") or []
        pending = [s for s in steps if not s.get("done")]
        if pending:
            step = pending[0]["step"]
            return _payload(
                "intake_step",
                "intake is not finished: %d of %d steps remain, and the first is "
                "%s. Every step before it is done." % (len(pending), len(steps), step),
                _intake_commands(ledger, step)
                + [_record_command(ledger_path, "intake", [("step", step)])],
                facts, missing, now, step=step,
                remaining=[s["step"] for s in pending])
        if steps:
            return _payload(
                "close_intake",
                "every intake step is recorded done but the phase is still "
                "intake, so the steady-state rules cannot run.",
                [_record_command(ledger_path, "phase", [("phase", "steady")])],
                facts, missing, now)

    # 2. availability, before anything else. Unmeasured counts as not green.
    if state != "green":
        commands = [_measure_command(ledger, now)]
        if state == "red":
            commands.append("journalctl -u %s -n 50 --no-pager"
                            % (ledger.get("service") or "<unit>"))
            commands.append("systemctl status %s --no-pager"
                            % (ledger.get("service") or "<unit>"))
        applied = [p for p in patches
                   if p.get("applied_at") and not p.get("reverted_at")]
        extra = {}
        if applied:
            extra["last_applied_patch"] = applied[-1].get("id")
            extra["rollback_if_this_patch_did_it"] = applied[-1].get("rollback")
        return _payload(
            "restore_service",
            "%s Nothing else is worth a keystroke until this is green: "
            "availability is scored continuously." % state_why,
            commands, facts, missing, now, sla_state=state, **extra)

    # 3. a measured regression outranks everything else defensive.
    regressed = [p for p in patches
                 if p.get("verdict") == "regression" and not p.get("reverted_at")]
    if regressed:
        patch = regressed[0]
        rollback = patch.get("rollback")
        if not rollback:
            return _payload(
                "revert_patch",
                "patch %s is recorded as a regression and has no rollback "
                "string, so this tool cannot tell you what to undo. That field "
                "is the entire reason a patch is recorded before it is applied."
                % patch.get("id"),
                [], facts, missing, now, patch=patch.get("id"),
                blocked="no rollback recorded for this patch")
        return _payload(
            "revert_patch",
            "patch %s regressed a check that passed before it and has not been "
            "reverted. The rollback below is the string you recorded, printed "
            "verbatim; this tool never runs it." % patch.get("id"),
            [rollback], facts, missing, now, patch=patch.get("id"),
            after_the_rollback=_record_command(
                ledger_path, "patch-reverted", [("id", patch.get("id"))]))

    # 4. an applied patch with no verdict. --save and --compare in one run.
    unverified = [p for p in patches
                  if p.get("applied_at") and p.get("verdict") in (None, "")
                  and not p.get("reverted_at")]
    if unverified:
        patch = unverified[0]
        saves = (path_of(ledger, "sla_saves") or "").rstrip("/")
        baseline = patch.get("baseline_save") or "%s/before-%s.json" % (
            saves, patch.get("id"))
        return _payload(
            "verify_patch",
            "patch %s is applied and has no verdict. An unverified patch uses "
            "the whole allowance of %d, so nothing else is patched until this "
            "one is compared against its own before-save."
            % (patch.get("id"), BUDGET["max_unverified_patches"]),
            ["python3 tools/ad/sla_check.py %s --save %s/after-%s.json --compare %s"
             % (path_of(ledger, "sla_spec"), saves, patch.get("id"), baseline),
             _record_command(ledger_path, "patch-verdict",
                             [("id", patch.get("id")), ("verdict", "<ok|regression>")])],
            facts, missing, now, patch=patch.get("id"),
            exit_codes="sla_check exits 0 green, 1 REVERT, 2 already red, "
                       "3 the spec is unusable")

    # 5. a planned patch with no before-picture fresh enough to be one.
    planned = [p for p in patches if not p.get("applied_at")
               and not p.get("reverted_at")]
    age = facts.get("sla_age_seconds")
    if planned and (age is None or age > tick_seconds):
        patch = planned[0]
        saves = (path_of(ledger, "sla_saves") or "").rstrip("/")
        return _payload(
            "snapshot_before_patch",
            "patch %s is planned and the newest green save is %s old, more than "
            "one tick of %.0fs. Without a before-picture taken next to the edit, "
            "--compare cannot tell your patch apart from a check that was "
            "already drifting." % (patch.get("id"),
                                   "unknown" if age is None else "%.0fs" % age,
                                   tick_seconds),
            ["python3 tools/ad/sla_check.py %s --save %s/before-%s.json"
             % (path_of(ledger, "sla_spec"), saves, patch.get("id")),
             _record_command(ledger_path, "patch-applied",
                             [("id", patch.get("id"))])],
            facts, missing, now, patch=patch.get("id"))

    # 6. flags already stolen and not accepted. They are held, not lost, and
    #    every tick spent mining is another batch behind the same broken submitter.
    pending_flags = facts.get("pending_flags") or 0
    if facts.get("alert") or (facts.get("submit_error") and pending_flags):
        return _payload(
            "fix_submission",
            "the farm is holding %s flag(s) that the scoreboard has not "
            "accepted (%s). Those flags are already stolen, so fixing the "
            "submitter scores them; mining finds a second exploit whose flags "
            "will be held by the same fault."
            % (pending_flags, facts.get("alert") or facts.get("submit_error")),
            ["tail -n 3 %s" % path_of(ledger, "farm_log"),
             "python3 -c \"import json;print(json.load(open('%s')).get('submit'))\""
             % path_of(ledger, "farm_config"),
             "python3 tools/ad/flag_farm.py %s --once --dry-run"
             % path_of(ledger, "farm_config")],
            facts, missing, now,
            check="submit.url, submit.method, submit.format, submit.header and "
                  "submit.token against the event rules. flag_farm holds pending "
                  "flags in <config>.pending and retries them, so nothing is lost "
                  "while this is wrong.")

    # 7. a capture nobody has read. Someone else's working exploit is cheaper to
    #    read than a bug is to find.
    live_newest = facts.get("live_newest")
    mined_newest = facts.get("mined_newest")
    if live_newest and (mined_newest is None or live_newest > mined_newest):
        return _payload(
            "mine_traffic",
            "the live capture holds %s request file(s) newer than the newest "
            "mined output, so requests other teams sent you have not been "
            "ranked yet." % facts.get("live_files"),
            ["python3 tools/ad/cap_split.py --pcap <newest-live>.pcap --out %s "
             "--append" % path_of(ledger, "capture_live"),
             "python3 tools/ad/traffic_mine.py --baseline %s --live %s --top 10 "
             "> %s/mine-%s.json"
             % (path_of(ledger, "capture_baseline"),
                path_of(ledger, "capture_live"),
                (path_of(ledger, "mined") or "").rstrip("/"),
                time.strftime("%H%M%S", time.localtime(now)))],
            facts, missing, now,
            trap="never feed the miner a tshark follow dump: it carries the "
                 "server's response into the parsed request, and the replay "
                 "built from it points your own response at a third team")

    # 8. the top-ranked candidate has never been written up as an idea.
    top = facts.get("mined_top")
    if top:
        fingerprint = candidate_fingerprint(top)
        known = {i.get("fingerprint") for i in ideas}
        if fingerprint not in known:
            return _payload(
                "promote_candidate",
                "the top-ranked mined request (%s %s, score %s) is not in the "
                "ledger yet: %s"
                % (top.get("method"), top.get("path"), top.get("score"),
                   "; ".join(top.get("reasons") or [])[:200]),
                [top.get("replay") or "# the mined entry carries no replay line",
                 _record_command(ledger_path, "exploit-idea",
                                 [("fingerprint", fingerprint),
                                  ("note", "<what-it-does>")])],
                facts, missing, now, fingerprint=fingerprint,
                run_it="set TARGET to ONE team host from the farm config and run "
                       "the replay once by hand before it goes near the farm")

    # 9. an idea that has had its allowance of ticks and yielded nothing.
    stale = [i for i in ideas
             if not i.get("verdict")
             and i.get("first_seen_at")
             and now - float(i["first_seen_at"])
             > BUDGET["ticks_per_exploit_idea"] * tick_seconds]
    if stale:
        idea = stale[0]
        return _payload(
            "park_exploit_idea",
            "exploit idea %s has been open for more than %d ticks with no "
            "verdict. Park it and take the next candidate; a third variant of "
            "the same idea produces no new signal."
            % (idea.get("fingerprint"), BUDGET["ticks_per_exploit_idea"]),
            [_record_command(ledger_path, "idea-verdict",
                             [("fingerprint", idea.get("fingerprint")),
                              ("verdict", "parked")])],
            facts, missing, now, fingerprint=idea.get("fingerprint"))

    # 10. a working exploit whose farm is not running, or whose log has stopped.
    working = [i for i in ideas if i.get("verdict") == "working"]
    farm_age = facts.get("last_farm_age_seconds")
    if working and (farm_age is None or farm_age > 2 * tick_seconds):
        return _payload(
            "farm",
            "exploit idea %s is marked working and the farm log is %s. A working "
            "exploit that is not running scores nothing."
            % (working[0].get("fingerprint"),
               "missing" if farm_age is None else "%.0fs old" % farm_age),
            ["python3 tools/ad/flag_farm.py %s >> %s"
             % (path_of(ledger, "farm_config"), path_of(ledger, "farm_log")),
             "tail -n 1 %s" % path_of(ledger, "farm_log")],
            facts, missing, now,
            first_time="run it once with --once --dry-run first if the team list "
                       "or the flag format changed")

    # 11. all three questions are answered. Say what is being watched and how old
    #     each answer is, so "nothing to do" is a measurement and not a shrug.
    watching = [
        {"question": "is the service green", "file": facts.get("sla_save"),
         "age_seconds": facts.get("sla_age_seconds")},
        {"question": "did anyone new attack us",
         "file": path_of(ledger, "capture_live"),
         "age_seconds": facts.get("live_age_seconds"),
         "files": facts.get("live_files")},
        {"question": "who stopped yielding flags",
         "file": path_of(ledger, "farm_log"),
         "age_seconds": facts.get("last_farm_age_seconds"),
         "immune": facts.get("immune")},
    ]
    return _payload(
        "hold",
        "all three steady-state questions are answered and nothing is stale. "
        "Read the immune list: a team that stopped yielding while others still "
        "yield has patched, and their patch is the shortest description of the "
        "bug you are exploiting.",
        [_measure_command(ledger, now),
         "python3 tools/ad/traffic_mine.py --baseline %s --live %s --top 10"
         % (path_of(ledger, "capture_baseline"), path_of(ledger, "capture_live")),
         "tail -n 1 %s" % path_of(ledger, "farm_log")],
        facts, missing, now, watching=watching)


def decide(ledger, now=None, facts=None, ledger_path="<ledger>"):
    """decide_next with the facts taken from the ledger dict itself.

    The short form the runbook and the selftest use: a ledger carrying a `facts`
    key decides with no filesystem at all. A real ledger has no such key, and
    then every fact is null -- which correctly reads as unanswered rather than as
    green.
    """
    ledger = ledger or {}
    if facts is None:
        facts = ledger.get("facts") or {}
    return decide_next(ledger, facts, now, ledger_path)


# --------------------------------------------------------------------- record
# Table-driven: a kind is its required fields, its optional fields and the closed
# value sets. A free-form writer would let `--field verdit=ok` through and the
# patch would sit unverified forever with nobody able to see why.
RECORD_KINDS = {
    "intake": {"required": ("step",), "optional": ("note",), "values": {}},
    "phase": {"required": ("phase",), "optional": (),
              "values": {"phase": VALID_PHASES}},
    "patch": {"required": ("id", "rollback"), "optional": ("what",), "values": {}},
    "patch-applied": {"required": ("id",), "optional": ("note", "baseline_save"),
                      "values": {}},
    "patch-verdict": {"required": ("id", "verdict"), "optional": ("note",),
                      "values": {"verdict": ("ok", "regression")}},
    "patch-reverted": {"required": ("id",), "optional": ("note",), "values": {}},
    "exploit-idea": {"required": ("fingerprint",),
                     "optional": ("note", "replay", "path"), "values": {}},
    "idea-verdict": {"required": ("fingerprint", "verdict"), "optional": ("note",),
                     "values": {"verdict": ("working", "parked")}},
    "claim": {"required": ("text",), "optional": ("evidence",), "values": {}},
}


def parse_fields(raw):
    """['a=b'] -> {'a': 'b'}. Returns (fields, reason)."""
    fields = {}
    for item in raw or []:
        if "=" not in item:
            return None, ("--field %r has no '=': write --field name=value" % item)
        key, _, value = item.partition("=")
        key = key.strip()
        if not key:
            return None, "--field %r has an empty name" % item
        fields[key] = value
    return fields, None


def apply_record(ledger, kind, fields, now=None):
    """Apply one record to the ledger dict in place. Returns (ok, payload).

    Pure apart from the clock, so every refusal is provable offline.
    """
    now = time.time() if now is None else now
    spec = RECORD_KINDS.get(kind)
    if spec is None:
        return False, {"ok": False, "reason": "unknown --kind %r; one of: %s"
                       % (kind, ", ".join(sorted(RECORD_KINDS)))}
    allowed = set(spec["required"]) | set(spec["optional"])
    unknown = sorted(set(fields) - allowed)
    if unknown:
        return False, {"ok": False, "reason":
                       "--kind %s does not take the field(s) %s; it takes: %s"
                       % (kind, ", ".join(unknown), ", ".join(sorted(allowed)))}
    absent = [f for f in spec["required"] if not fields.get(f)]
    if absent:
        return False, {"ok": False, "reason":
                       "--kind %s needs --field %s"
                       % (kind, " --field ".join("%s=<value>" % f for f in absent))}
    for key, values in (spec.get("values") or {}).items():
        if key in fields and fields[key] not in values:
            return False, {"ok": False, "reason":
                           "--field %s=%r is not one of: %s"
                           % (key, fields[key], ", ".join(values))}

    stamp = round(now, 1)
    if kind == "intake":
        for step in ledger.setdefault("intake", []):
            if step.get("step") == fields["step"]:
                step["done"] = True
                step["at"] = stamp
                if fields.get("note"):
                    step["note"] = fields["note"]
                return True, {"ok": True, "recorded": kind, "step": fields["step"]}
        return False, {"ok": False, "reason":
                       "no intake step named %r in this ledger; the steps are: %s"
                       % (fields["step"],
                          ", ".join(s.get("step", "?")
                                    for s in ledger.get("intake") or []))}

    if kind == "phase":
        ledger["phase"] = fields["phase"]
        return True, {"ok": True, "recorded": kind, "phase": fields["phase"]}

    if kind == "patch":
        patches = ledger.setdefault("patches", [])
        if any(p.get("id") == fields["id"] for p in patches):
            return False, {"ok": False, "reason":
                           "patch %r is already in the ledger; use "
                           "patch-applied, patch-verdict or patch-reverted"
                           % fields["id"]}
        patches.append({"id": fields["id"], "what": fields.get("what", ""),
                        "rollback": fields["rollback"], "planned_at": stamp,
                        "applied_at": None, "baseline_save": None,
                        "verdict": None, "reverted_at": None})
        return True, {"ok": True, "recorded": kind, "id": fields["id"]}

    if kind in ("patch-applied", "patch-verdict", "patch-reverted"):
        for patch in ledger.get("patches") or []:
            if patch.get("id") != fields["id"]:
                continue
            if kind == "patch-applied":
                patch["applied_at"] = stamp
                if fields.get("baseline_save"):
                    patch["baseline_save"] = fields["baseline_save"]
            elif kind == "patch-verdict":
                patch["verdict"] = fields["verdict"]
            else:
                patch["reverted_at"] = stamp
            if fields.get("note"):
                patch["what"] = fields["note"]
            return True, {"ok": True, "recorded": kind, "id": fields["id"]}
        return False, {"ok": False, "reason":
                       "no patch with id %r; record it with --kind patch first, "
                       "so the rollback string exists before the edit does"
                       % fields["id"]}

    if kind == "exploit-idea":
        ideas = ledger.setdefault("exploit_ideas", [])
        if any(i.get("fingerprint") == fields["fingerprint"] for i in ideas):
            return False, {"ok": False, "reason":
                           "exploit idea %r is already in the ledger"
                           % fields["fingerprint"]}
        ideas.append({"fingerprint": fields["fingerprint"],
                      "note": fields.get("note", ""),
                      "replay": fields.get("replay", ""),
                      "path": fields.get("path", ""),
                      "first_seen_at": stamp, "verdict": None})
        return True, {"ok": True, "recorded": kind,
                      "fingerprint": fields["fingerprint"]}

    if kind == "idea-verdict":
        for idea in ledger.get("exploit_ideas") or []:
            if idea.get("fingerprint") == fields["fingerprint"]:
                idea["verdict"] = fields["verdict"]
                if fields.get("note"):
                    idea["note"] = fields["note"]
                return True, {"ok": True, "recorded": kind,
                              "fingerprint": fields["fingerprint"]}
        return False, {"ok": False, "reason":
                       "no exploit idea with fingerprint %r" % fields["fingerprint"]}

    # claim
    ledger.setdefault("claims", []).append(
        {"text": fields["text"], "evidence": fields.get("evidence", ""),
         "at": stamp})
    return True, {"ok": True, "recorded": kind, "claims": len(ledger["claims"])}


# ----------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ledger", help="path to this service's ledger JSON")
    ap.add_argument("verb", nargs="?", choices=["record"], default=None,
                    help="'record' writes to the ledger; omit it to decide")
    ap.add_argument("--init", metavar="SERVICE",
                    help="write a new ledger for this service from "
                         "tools/ad/ledger.template.json; refuses to overwrite")
    ap.add_argument("--kind", help="what to record; see --help for the list")
    ap.add_argument("--field", action="append", default=[], metavar="NAME=VALUE",
                    help="one field of the record; repeatable")
    args = ap.parse_args()

    if args.init:
        ok, payload = init_ledger(args.ledger, args.init)
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0 if ok else 2

    try:
        with open(args.ledger, encoding="utf-8") as fh:
            ledger = json.load(fh)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "reason":
                          "cannot read the ledger %s (%s: %s)"
                          % (args.ledger, type(exc).__name__, exc),
                          "fix": "python3 tools/ad/tick.py %s --init <service>"
                                 % args.ledger}, ensure_ascii=False, indent=1))
        return 2

    if args.verb == "record":
        fields, reason = parse_fields(args.field)
        if reason:
            print(json.dumps({"ok": False, "reason": reason}, ensure_ascii=False,
                             indent=1))
            return 2
        ok, payload = apply_record(ledger, args.kind, fields)
        if ok:
            atomic_json(args.ledger, ledger)
            payload["ledger"] = args.ledger
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0 if ok else 2

    now = time.time()
    facts, missing = gather_facts(ledger, now)
    facts["_missing"] = missing
    result = decide_next(ledger, facts, now, args.ledger)
    # Carried in facts only to reach decide_next as a pure argument; printing it
    # twice would make the payload contradict itself if one copy were edited.
    result["facts"].pop("_missing", None)
    result["service"] = ledger.get("service")
    result["phase"] = ledger.get("phase")
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
