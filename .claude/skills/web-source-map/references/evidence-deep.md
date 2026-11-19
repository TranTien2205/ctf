# Evidence (deep) — the verbatim-excerpt and the lead provenance

## The provenance requirement

Every lead carries its provenance: the file it came from, the verbatim
string, the verify result. A lead without provenance is not traceable —
"found an endpoint" is not a finding; "`/api/admin` in `main.js:1`,
verified `200` live" is.

## The evidence ladder

| Level | What | Example |
|---|---|---|
| surface | a string in the bundle | `"/api/admin"` literal |
| claim | the client asserts it exists | the `fetch('/api/admin')` call |
| class | verified live | `curl` → `200` real response |
| impact | the routed class exploits it | IDOR reads another user |
| flag | the flag gated and read | `pre-flag` → live/artifact |

Only `class`-level and above is a finding; `surface`/`claim` are leads.

## The verbatim-excerpt gate

A `confirms` through `post-probe` requires `--evidence` be a verbatim
substring of `--response` — for a map find, the response the endpoint
returned or the response the secret unlocked. "The bundle had a key" is
not evidence; the bytes it unlocked are.

```bash
python3 tools/hooks.py post-probe <challenge> \
  --hypothesis-id <h> --class <class> --verdict confirms \
  --evidence-kind class --evidence '<verbatim excerpt>' \
  --response '<the response bytes>'
```

## The pre-flag gate

A flag-shaped string in recovered source is a *candidate*:

```bash
python3 tools/hooks.py pre-flag <challenge> --value '<candidate>' \
  --source '<the source or response>' --evidence '<the verbatim excerpt>'
```

The flag counts only when read from a live response or supplied
artifact and passed through the gate.

## The untrusted-source caveat

The bundle and map are attacker-controlled. A recovered `sourcesContent`
file is what the build *claimed*, not necessarily the server's truth —
a dev comment may describe a fix that did not ship, a "secret" may be
planted. Read the source as a spec; verify its claims live. A `sources`
traversal is rejected — the map could be hostile.

## The negative provenance

A dead lead records the same provenance — source file + verbatim string
+ the dead response. The negative is traceable to where the lead came
from.
