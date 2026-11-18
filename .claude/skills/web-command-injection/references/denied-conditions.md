# Denied Conditions — the falsifier table

## What kills this class — the proofs that cmdi is NOT live

A class is dead when you can state a falsifier AND show it holds. Each
row is a falsifier + the probe that establishes it + the class it routes to.

## The falsifier table

| Falsifier | How you show it | Routes to |
|---|---|---|
| The value never reaches any exec | white-box: traced from input to every sink | — class dead |
| Every separator is stripped/rejected | probe set: `;`/`&`/`|`/`\n`/`` ` ``/`$()` all literal or 4xx | filter-map → `char-restriction.md` |
| The sink is argv-form (execFile/argv) | `ping: x;id: not found` — the whole arg is the argv element | `argument-injection.md` |
| No evaluator accepts the markers | `7*7`/`{{7*7}}`/`${7*7}`/`#{7*7}`/`<%=7*7%>` all literal | `web-ssti` if template-form, dead otherwise |
| `escapeshellarg` + arg can't be a flag | the wrapped binary takes no exec-capable flag | `argument-injection.md` → dead |
| The "exec" is a whitelist of fixed commands | input maps to a lookup, never an arg | dead |
| The "sink" is in dead code / a different path | `system()` exists but the input never reaches it | class dead |
| The input is `intval`/`is_numeric`/`ip2long`-validated | only digits/IPs pass | arg-injection at most |
| The input is a `basename`/`realpath`/`preg_match`ed pathname | path-cleaned | `file-read-primitives` |
| The tool name itself is user-set but the arg is fixed | `system($tool.' -fixed')` — tool-name is the param | tool-name injection is the surface |

## The "not this class" routes — when to hand off

| Observed | Actual class |
|---|---|
| `{{7*7}}`/`${x}`/`#{x}` evaluates | `web-ssti` |
| `eval()`/`exec()`/`new Function`/`Runtime.exec` language-level | `eval-injection.md` (this class's sibling) |
| `execFile`/`spawn`-array/`ProcessBuilder`-list | `argument-injection.md` — this skill's sub-domain |
| the arg is a FILENAME inside the command | `filename-injection.md` + `web-file-upload` |
| the flag lives where the app reads it, not the shell | `file-read-primitives` |
| the URL the app fetches is user-set | `web-ssrf` — not cmdi |
| the session/cookie/token is the leak | `web-auth-session`/`web-idor` |
| the X-* header is the tainted surface | `web-host-header`/header-classes |
| `ping:`/`nslookup:`/`host:`/`dig:` arg-position only | `argument-injection.md` |

## The record-format — writing the kill

```
python3 tools/state.py <n> --hypothesis 'shell injection in host param'
python3 tools/hooks.py pre-probe <n> --request 'x;id' --hypothesis-id <id> --class command-injection
<probe>
python3 tools/hooks.py post-probe <n> --hypothesis-id <id> \
  --class command-injection --verdict refutes \
  --evidence 'ping: x;id: Name or service not known' \
  --response '<verbatim error bytes>'
```

Then the kill-map note in `knowledge/attempts/<challenge>.json` — which
layer is dead and what would reopen it.

## The "the falsifier almost held but..." boundary cases

- `escapeshellarg` present BUT the arg-position allows flags → live
- argv-form BUT the binary's own flags exec → arg-injection lives
- `;` blocked BUT `%0a` works → a different separator
- `system()` present BUT input goes through `preg_replace` first —
  whether the regex closes the surface — `filter-bypass.md`

## The "every probe failed but I can't state why" — the unknown-class state

If you can't state a falsifier, you haven't proven the class dead —
the budget is spent, escalate per `tools/decide.py`.

## Output to record

- which falsifier held + the verbatim evidence + the routed-to class
