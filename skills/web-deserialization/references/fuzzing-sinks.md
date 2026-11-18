# Fuzzing Sinks — finding the deserializer when you can't see source

## The hunt order — cheapest first

```
1. enumerate every endpoint/param that takes an opaque value
2. classify each: is its value a serialized-format candidate?
3. corrupt-and-diff each candidate — the cheapest confirm
4. only then gadget-fingerprint the survivors
```

## The endpoint inventory — where the sink lives

```bash
# every input the app takes — the crawl
grep -rE "unserialize|readObject|pickle|Marshal|yaml.load|Deserialize" src/
# black-box: walk the app's surface —
#   every POST field, every cookie, every header, every uploaded file,
#   every WebSocket frame, every job-queue write
```

## The value-shape classifier — score each param

| Value shape | Score | Action |
|---|---|---|
| base64/blob ≥64 bytes, opaque | HIGH | decode → fingerprint → corrupt-diff |
| `eyJ...`/`rO0AB`/`O:`/`BAh`/`AAEAAAD` magic | CONFIRM | format module → gadget |
| `{json}` object with typed field (`$type`,`@type`,`py/object`) | HIGH | type-tag probe |
| `!!`/`!<` YAML tag | MED | yaml-deser.md |
| XML body | MED | XStream/XMLDecoder probe |
| plain string | LOW | not deserialization |
| integer/small enum | LOW | probably not |

## The corrupt-and-diff sweep

For each HIGH candidate, send three variants:

```
A. the original value            → baseline response
B. the value, one byte flipped   → parser error? timing delta?
C. a syntactically-valid different object → different response?
```

```
B != A  → the value is parsed — a parser exists → DESERIALIZATION SUSPECT
B == A  → the value is stored verbatim / ignored → dead end
C != A  → the value's CONTENT matters → semantically consumed
```

## The probe-class oracle — works on every format

Send a blob naming a class the app can't have:

```
Java:   O:→ com.attacker.ProbeDoesNotExist
PHP:    O:12:"AttackerProbe":0:{}
pickle: cattacker.probe\nProbe\n\nR.
Ruby:   !ruby/object:Attacker::Probe
.NET:   {"$type":"Attacker.Probe, X"}
YAML:   !!attacker.Probe
```

Error names YOUR class → the deserializer built/tried-to-load it → confirmed.
Different error on a real-looking class = the filter rejects it → still info.

## Blind-fingerprinting the version — no source, no stack trace

```
Java:   GadgetProbe per-lib probe → callback only if that class loads
PHP:    each framework's classes → a POP on the wrong lib errors differently
        — the error's class-name leaks what's loaded
.NET:   a $type probe per formatter — the JsonException names the binder
pickle: a GLOBAL probe per module — find_class rejection names the path
```

## The timing-oracle fallback — when nothing reflects

If every error is swallowed:

```
a blob that deserializes a LARGE object graph → measurably slower
a blob that triggers a remote lookup          → measurably slower
a blob that fails fast                        → fast
```

A 200-500ms consistent delta between "deep graph" and "flat" is a weak yes —
corroborate with OOB before claiming. Timing alone never confirms.

## The OOB net — the strongest blind confirm

```bash
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name sink1
```

- URLDNS/JNDI/`nslookup` gadget per candidate — callback fires when the
  stored/sent object is deserialized, no response needed
- SoapClient-WSDL fetch (PHP)
- `Runtime.exec("curl")` / `nslookup` in a chain

## The "no candidate found" — what it means

- The app's blobs are all plain JSON → probably not deserialization at all;
  pivot to injection/idor/logic
- The blobs are encrypted with no oracle → key-attack or different class
- The blob is a signature-wrapped JSON (JWT/itsdangerous) → JWT/auth skill

## Output to record

- Which params were candidates + which were ruled out (with evidence)
- The one that confirmed + the probe that did it
- The format+version the fingerprint established
