# Verify the Flag — the last-mile rules

## The standard — a flag is a flag only through `pre-flag`

A flag-shaped string is a *candidate* until it's written through
`tools/hooks.py pre-flag`. The bar:

- it came from a **live response** or a **supplied artifact** — a real HTTP
  response body/header, an OOB-listener log line, a file the gadget wrote
- the verbatim excerpt quotes it — `pre-flag --source` carries the bytes
- it has NOT been hand-typed, guessed, or reconstructed

## The `pre-flag` invocation

```bash
python3 tools/hooks.py pre-flag $C \
  --value 'flag{the_actual_string_from_the_response}' \
  --source 'the verbatim response body or OOB-log line it came from'
```

`pre-flag` records the candidate + provenance — then the solve is written
through `post-probe`/`record_solve` with the evidence attached.

## The deserialization-specific last-mile

### The flag lands where the gadget's OUTPUT lands

- `os.system('cat /flag')` returns `0` — the flag went to stdout, which
  isn't in the response → use `check_output`/`popen().read()`/`eval(open())`
  OR exfil the output
- a file-write gadget → the flag is in the FILE you then GET
- an OOB gadget → the flag is in YOUR listener log
- an error-exfil gadget → the flag is inside the 500 stack trace

### The "is it really the flag" check

- `flag{`/`HTB{`/`CTF{`/`FLAG{` prefix + `}` suffix — format confirm
- it came from `/flag`, an env var, a DB row, or a config — the SOURCE is
  plausible (not a string you typed into a field that echoes)
- the response is the gadget's output channel — a `cat /flag` echo, not a
  reflected `flag{` you sent

### The "flag-shaped echo" trap

An app that *reflects* your input is a trap — `{"flag":"flag{x}"}` you sent
coming back is NOT a flag. The flag must come from the SERVER's data — a
file read, an env var, a DB row — not your own bytes echoed.

## The `post-probe` impact write

```bash
python3 tools/hooks.py post-probe $C \
  --hypothesis-id H1 --class web-deserialization --verdict confirms \
  --evidence-kind impact --evidence 'flag{...}' \
  --response 'the response carrying the flag verbatim'
```

The gate asserts `evidence ⊆ response` — the flag text MUST be a substring
of the quoted response. A flag you claim without the bytes fails the gate.

## The "the gadget ran but no flag" case

The RCE worked — `id` returned `uid=33` — but no flag yet. The flag's
location is a NEW problem:

```bash
# hunt it — the standard locations:
cat /flag /flag.txt flag.txt ./flag /app/flag /var/www/flag
env | grep -i flag                        # FLAG env var
find / -name '*flag*' 2>/dev/null         # the find
cat /proc/1/environ | tr '\0' '\n'        # process env
cat config.php settings.py .env web.config  # config-file flag
mysql -e 'SELECT * FROM flags'            # DB flag
```

The flag isn't always at `/flag` — `find`, `env`, config files, the DB.
The RCE being confirmed doesn't end the challenge — the flag's READ does.

## The "flag in a file the gadget reads" shape

A deserialization challenge often puts the flag in a file only the *gadget's
RCE* can read — `/root/flag`, `flag.txt` in a private dir, a `flag` row the
chain queries. The RCE confirm (`id`) is a waypoint; the flag read is the
endpoint.

## The "verify and clean" close

```
□ flag via pre-flag — the value+source recorded
□ the gadget's verbatim output in the ledger
□ webshell/persistent files removed
□ background listeners/jobs killed
□ stored-object payloads neutralized
□ chain card written — knowledge/chains/<id>.md
```

## The "flag format you didn't expect" note

Some events use `FLAG{`/`HTB{`/`flag{`/the event's custom prefix — read the
event's rules for the format. A `flag{` guess that isn't the event's format
is a candidate, not a flag — the *actual* bytes the challenge yields are
the answer.

## Output to record

- `pre-flag` invocation + the verbatim source
- `post-probe` `--evidence-kind impact` the ledger entry
- cleanup notes (files removed, processes killed)
