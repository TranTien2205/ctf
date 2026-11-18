# Evidence Rules — what confirms vs what only suggests

## The contract — a gadget is only proven by its OUTPUT

Deserialization is the easiest class to *claim* and the hardest to *prove*.
The standards:

| Verdict | What it takes |
|---|---|
| confirms (class) | a parser-specific error/timing delta on YOUR bytes, OR an OOB callback, OR a marker object reflected — anything that proves the deserializer ran |
| confirms (impact) | the flag verbatim in a live response/OOB line, or RCE output verbatim, or a file-write whose contents you then read back |
| inconclusive | 500 with no parser signature, a redirect, an acceptance-with-no-effect, a gadget that produced no observable |
| falsified | identical response+timing on valid vs malformed, `allowed_classes`/`safe_load`/`TypeNameHandling.None` verified, or a key-gated blob with no reachable key |

## What counts as "the deserializer ran"

- **PHP**: `unserialize(): Error at offset`, `__PHP_Incomplete_Class`,
  a `Warning: unserialize()` string in the response/log
- **Java**: `InvalidClassException` (naming your probe class),
  `StreamCorruptedException`, `ClassNotFoundException`, the serialVersionUID
  mismatch message
- **pickle**: `UnpicklingError`, `EOFError`, `AttributeError: Can't get
  attribute 'PWNED_X1'`, `find_class` rejection mentioning your module
- **Marshal**: `ArgumentError: dump format error`, `TypeError`
- **.NET**: `SerializationException`, `EndOfStreamException`, a
  `TypeNameHandling` JsonException naming your `$type` string
- **YAML**: `ConstructorException`/`could not determine a constructor` on
  your typed tag

## What does NOT count

- a 200 with no parser signature — acceptance is not deserialization
- a 500 with a generic error — need the parser-specific string
- a timeout — could be WAF, could be a crash mid-parse, never a confirm
- the gadget's *expected* response — only the actual verbatim output counts
- a `PWNED_X1` you typed into a reflection that the app echoes — the marker
  must come from the deserializer's OWN processing (an error naming the
  class, or the object's rendering), not your input echoed

## The OOB-callback rule

A DNS/HTTP hit proves the deserializer resolved/fetched — but tag the
callback with the probe id (`canary --name p3`) so a stray fetch isn't
mistaken for your chain. `oob_listener.py hits` is the ledger.

## The gadget-confirm hierarchy

```
1. flag in response              → impact confirmed, stop
2. RCE output in response        → impact confirmed, escalate to flag
3. OOB callback on a gadget      → class confirmed + code path reached
4. file-write then read-back     → impact confirmed via a second request
5. parser error on your bytes    → class confirmed, gadget not yet proven
6. timing differential           → weak — corroborate before claiming
```

## The `pre-flag` discipline

```bash
# a flag-shaped string is a candidate until the gate writes it:
python3 tools/hooks.py pre-flag $C --value 'flag{...}' \
  --source 'the verbatim response/OOB line it came from'
```

`post-probe` on a `confirms` verdict requires `--evidence` to be a substring
of `--response` — hand-assembled claims are checked, not trusted.

## The rollback rule — a gadget that errored isn't a negative

A `InvalidClassException`/`unserialize() error`/pickle `EOFError` on your
gadget means the bytes were WRONG or the version was wrong — the sink is
still live. Only a falsifier (below) closes the class. Log the error's
*parser signature* as evidence the deserializer is real, then fix the bytes.

## Falsifiers — the only things that close the class

- malformed blob → byte-identical response+timing to a valid blob
- `unserialize($x,['allowed_classes'=>false])` AND no phar/file-op path
- `safe_load`/`SafeConstructor`/`TypeNameHandling.None`/`SerializationBinder`
  whitelist verified AND no permitted-class gadget
- signed blob + unleaked key + alg=none/kid/confusion all blocked
- the stored value is never deserialized on any read path (verified in src)

## Output to record

- The verbatim response excerpt or OOB-log line that carries the proof
- The `post-probe` command exactly as written to the ledger
- For an impact confirm: the flag-bearing bytes verbatim
