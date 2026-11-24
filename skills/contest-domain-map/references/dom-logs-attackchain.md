# Domain: log forensics and attack-chain reconstruction

Reference module for `contest-domain-map`. The event vocabulary for this
domain sounds like "system logs", "trace the attacker", "rebuild the
intrusion", "timeline". The owning router is
`skills/dfir-sherlock-triage/SKILL.md` — this module says what to hand it
and which corpus families do the work.

## Route

- Bundle of honest artifacts plus numbered questions -> `dfir-sherlock-triage`
- One log file, one question -> `skills/forensics-log-analysis/SKILL.md`
- A pcap among the logs -> `skills/forensics-pcap-carve/SKILL.md` first;
  the network record anchors every other timeline

## First commands

```bash
python3 tools/state.py <id> --category dfir --challenge-name "<name>" --event "<event>"
python3 tools/file_type.py <artifact>           # what each blob actually is
ls -la <bundle>/                                 # the inventory IS the first answer
python3 tools/subagent_fanout.py --dfir          # eight bounded measurements at once
```

## The corpus families inside the router

`qx-*` modules name a question shape per artifact family:
`qx-whologgedin`, `qx-whenhappened`, `qx-whatexecuted`, `qx-whatpersists`,
`qx-whaterased`, `qx-whatexfil`, `qx-privilegeescal`, `qx-lateralmove`.
Match the QUESTION to the family, then the family names the artifact and
the parser.

## Cross-artifact correlation — the part a single-artifact answer misses

An attack chain is one actor across many artifacts. The reconstruction
method, in order:

1. **Entity key.** Pick the pivot the chain shares: a username, a PID, a
   source IP, a parent process GUID. Every artifact gets queried by that
   key, not skimmed.
2. **Anchor event.** The earliest record carrying the key — first failed
   logon, first odd child process, first beacon interval. Everything
   before it is noise for this chain.
3. **Merge by timestamp, not by artifact.** auth.log entries, bash_history,
   syslog, journald, $MFT times and the pcap flows go into ONE ordering;
   each record keeps its artifact tag. `tools/log_summary.py` normalises
   log lines; pcap timestamps come from `tshark -T fields -e frame.time_epoch`.
4. **TTP slots.** Order the merged record into the sequence it actually
   shows: access -> execution -> persistence -> lateral/exfil -> cleanup.
   A slot with no record is an honest gap — say "persistence not
   evidenced", never invent it.
5. **Boundary clocks.** Artifacts may sit in different timezones or have
   skew; state the offset assumption once, up front, and mark any record
   that only fits under a different skew as suspect.

## What not to do

- Do not grep the whole bundle for "flag" — Sherlock answers are facts,
  and a grep that hits nothing teaches nothing.
- Do not answer a question from one artifact when the bundle contains the
  artifact that actually owns it (who logged in -> auth.log/wtmp, NOT bash
  history).
- Timezones: a UTC artifact next to a local-time one silently misorders
  the chain; the offset assumption goes in the report either way.
