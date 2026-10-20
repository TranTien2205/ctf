# Brutus (HTB Sherlocks) — forensics / DFIR

Answers read from the supplied artifacts and recorded through
`tools/hooks.py pre-flag --source artifact`. **Values are not recorded here**: a
Sherlock answer is a graded secret exactly as a flag is, and this file is
committed.

First Sherlock worked in this tree. It is also the first exercise of
`tools/forensics/linux_auth.py` and of the `ctf-dfir-*` fleet, so the lessons
below are about the artifacts, not about the puzzle.

## Artifacts

Two files and a decoy, 43 KB and 11 KB:

    auth.log      385 syslog lines, 0 unparsed
    wtmp          29 × 384-byte struct utmp records
    utmp.py       a helper shipped with the bundle; not needed

Entirely text and a fixed-width binary struct, so **no absent parser blocks any
part of it** — unusual for this category, where `evtx_dump`, `regipy` and
`volatility3` are all missing on this box.

## Method

One command ranks the source addresses:

    python3 tools/forensics/linux_auth.py --authlog auth.log --summary --challenge <q>

`--summary` orders by **failures followed by an acceptance**, not by failure
count, and reports `succeeded_after_failures` per address. The bundle contains a
second address with a single failure and no acceptance, so a count-ordered list
would still have put the right one first here — but it would do so by luck, and
the join is what actually answers the question.

Everything after that is a filter over the same two files:

| Question shape | Filter |
|---|---|
| which account was taken | `--event accepted` |
| the UTC login time | `--wtmp wtmp --ut-type USER_PROCESS --ip <addr from Q1>` |
| the session number | `--event logind-session` |
| the account added for persistence | `--event useradd --event group-member` |
| what was run as root | `--event sudo` |
| when the session ended | `--contains 'session <N>'` |

## The traps, which is why this note exists

**`auth.log` carries no year and no timezone offset.** The format is
`Mar  6 06:31:31 host sshd[2411]: …` — there is no year in it at all, and the
times are host-local with nothing recording the zone. `wtmp` is the only artifact
here with a real UTC epoch (`tv_sec`), so a question asking for a **UTC**
timestamp must be answered from `wtmp`. `linux_auth.py` refuses the auth.log
timestamp rather than emitting it: without `--year` the parsed value shows
`????-03-06 …` and the `--answer` is returned with a `refused` reason and no
`pre_flag`.

**The wtmp filter has to be pivoted on the address from the first question.**
There are 8 `USER_PROCESS` records across six weeks, and most are a legitimate
administrator from a different address. Taking "the most recent interactive
login" without filtering by the attacker's address selects a legitimate session.
With `--ip` and `--user` the 29 records narrow to exactly 1.

**Three different numbers in this one log all read like a session id**: the sshd
PID in brackets, `Starting session: shell on pts/1 … id 0`, and
`systemd-logind[411]: New session 37 of user root.` Only the last is the session
number the question means. The tool extracts them as `pid`, `id` and `session`
precisely so the answer is chosen rather than guessed — and there are four
`New session` records, so the one belonging to the compromised account still has
to be selected by user and time.

**One question is not answerable from any artifact.** The MITRE ATT&CK
sub-technique id for persistence via a new account is published knowledge, not
something in the bundle. It cannot go through `pre-flag --source artifact`
honestly as a *read* value; record it as the catalogue fact it is.

**`sudo` records the command as requested, not its outcome.** Two sudo commands
appear; neither line proves the command succeeded.

## Ledger

One question is one challenge, because `tools/decide.py` budgets 25 probes and 45
active minutes per challenge and that fits one question, not twenty:

    python3 tools/state.py Brutus-q3 --category dfir --target <bundle> \
      --challenge-name "Brutus Q3 manual login timestamp" --event "HTB Sherlocks"
    python3 tools/hooks.py pre-flag Brutus-q3 --value '<answer>' \
      --source artifact --evidence '<record excerpt pasted from the tool>'
    python3 tools/decide.py Brutus-q3     # -> record_solve

The excerpt is pasted from `linux_auth.py`'s own output, never retyped: the tool
builds each record's `raw` line from the unpacked bytes so the two cannot
disagree.
