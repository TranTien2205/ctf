# Field notes - Authentication and logon trace

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

---

## 2026-10-01 · Brutus · proposed

- source note: `solved/htb-brutus.md`
- chain card: `knowledge/chains/htb-brutus-authlog-wtmp-bruteforce-join-utc-from-wtmp.json`
- verification: verified_live — Each answer was read from a supplied artifact and recorded through tools/hooks.py pre-flag --source artifact, with the record excerpt pasted from tools/forensics/linux_auth.py output rather than retyped; the tool builds each record's raw line from the unpacked bytes so the excerpt and the artifact cannot disagree. tools/decide.py returned record_solve for Brutus-q3. Answer VALUES are deliberately not recorded in this card or in solved/htb-brutus.md: a Sherlock answer is a graded secret exactly as a flag is, and both files are committed. Measured coverage: 385 auth.log lines parsed with 0 unparsed, 29 wtmp records, and 7 of the 8 questions answerable directly from the two artifacts.
- classified as: `dfir-authentication-trace` (score 1.0, 1 signals matched)
- signals that fired: auth.log

**Confirming probe that worked**

> python3 tools/forensics/linux_auth.py --authlog <auth.log> --summary --challenge <name>

Expected: address_ranking holds at least one entry with succeeded_after_failures true, carrying both a failure count and first_accepted_line as a verbatim auth.log line

Falsifier: every address with failed attempts has accepted 0, so no brute force succeeded on this host and the authentication-trace class is closed for this bundle

**Traps recorded on this solve**

- auth.log carries NO YEAR and NO TIMEZONE OFFSET; a tool that assumes the current year is wrong by whole years and looks right, so a UTC timestamp must come from wtmp, whose tv_sec is a real UTC epoch
- ranking source addresses by failure count names the loudest scanner, not the one that got in; order on failures FOLLOWED by an acceptance
- three numbers in one auth.log all read like a session id - the sshd PID in brackets, `Starting session: shell on pts/N ... id 0`, and systemd-logind `New session N` - and only the last is the session number a question means
- the wtmp set contains legitimate administrator sessions from a different address spanning weeks, so the attacker record must be selected by the address recovered from the brute-force question; without that pivot the latest interactive login is a legitimate one
- there are several logind New session records, so the one for the compromised account still has to be chosen by user and time rather than taken as the only match
- btmp holds FAILED logins while wtmp holds successful ones; reporting a btmp record as a login is a wrong answer, so always record which file a record came from
- a trailing partial record in wtmp means the file is truncated or still being written, which is itself a finding - a parser that silently drops the tail hides it
- a sudo COMMAND= line records what was requested, not that it succeeded
- a rotated log is several files (auth.log.1, auth.log.2.gz) and the earliest event is often in one nobody opened; state which files were actually read
- .bash_history has no timestamps unless HISTTIMEFORMAT was set and is written on shell exit, so a still-open session may be absent entirely
- one question in this Sherlock asks for a MITRE ATT&CK sub-technique id, which appears in NO artifact: it is published knowledge, so recording it through pre-flag --source artifact would claim an artifact read that never happened

**Blast radius**: none: every artifact is supplied and read-only, there is no target to mutate and no live host involved. The only real risk in this category is the opposite one - answering a UTC question from auth.log, whose times carry no year and no timezone, which produces a confidently wrong answer rather than any damage.

- status: proposed
