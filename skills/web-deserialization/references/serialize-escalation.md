# Deserialization Escalation — when the basic chain is blocked

## The escalation order — when the first gadget fails

```
1. confirm the deserializer STILL ran (parser error, not silence)
2. is it a version mismatch? → serialVersionUID error → re-version the chain
3. is it a filter? → allowed_classes/Binder/find_class → the whitelist's gap
4. is it a signature? → key-hunt/alg=none/kid/confusion
5. is it a mangle? → encoding-channels → wrap correctly
6. is it egress? → file-write/error/time side-channel instead of OOB
7. is it the sink unreachable? → second-order/job-queue path
8. a different mechanism layer → the bridge skills
```

## Version-mismatch → the right chain

`InvalidClassException`/`serialVersionUID` errors NAME the version — the
exception is the oracle. Re-pick the chain for the measured lib version,
not the assumed one. `GadgetProbe` probes per-lib if errors don't surface.

## Filter → the whitelist's own gadget

- `allowed_classes` → a whitelisted class that has a magic method
- `safe_load` → a permitted class with a hook
- `Binder` → a whitelisted type that reaches a gadget
- `find_class` → a whitelisted module re-exporting a dangerous name
- `ObjectInputFilter` → a `com.app.*` class that IS the gadget

## Signature → the key-attack ladder

```
alg=none → kid path-traversal → jku/x5u → RS→HS confusion → key in source/env
→ default-key list → key-derivation trick → padding-oracle on encrypt
```

`signature-bypass.md` is the module — the signature is a key problem, not
a grammar problem.

## Mangle → the encoding fix

- `addslashes`/`'` → `S:` hex-escape type
- `htmlspecialchars` → base64-then-mangle
- `urldecode` double → double-urlencode
- a second decode layer → match the wrapper the app applies
- `S:` for NULs that `s:` can't carry

## Egress-dead → the local-impact chain

- file-write gadget → write the flag/webshell to a path you GET
- error-exfil → the flag inside an exception's message
- time-oracle → a `sleep` gadget → the delta is the bit
- `nslookup`-still-works → DNS-only egress

## Sink-unreachable → the second-order path

- the value is stored, not parsed → find the consumer (session/cache/job/db)
- the write is signed but the store isn't → poison the store's read path
- the endpoint unserializes only on a specific action → find the trigger

## The "pivot the mechanism" rule

When `allowed_classes`+`safe_load`+a verified binder all block → the
*deserialization class* is closed for that channel — pivot to a DIFFERENT
class (`web-file-upload`, `web-sqli`, `file-read-primitives`) that reaches
the same flag. A deser that can't land isn't the only path to the flag.

## The budget allocation — how much per rung

```
fingerprint+corrupt+marker   ~5 probes   → detection mechanism class
version-probe+re-version     ~5 probes   → version mechanism class  
filter-gap-hunt              ~5 probes   → filter mechanism class
signature/key hunt           ~5 probes   → signature mechanism class
side-channel/file-write      ~5 probes   → impact mechanism class
25 probes/45min ceiling → escalate per AGENTS.md ladder
```

## The "the deserializer ran, the gadget didn't" distinction

The class-confirm (parser error on your bytes) and the impact-confirm (the
gadget fired) are different proofs. A confirmed deserializer with a failing
gadget means the CHAIN is wrong (version/filter), not the sink — keep
iterating on the chain, not the reachability.

## Output to record

- Which rung the chain failed on + the evidence
- Which escalation path unblocked it
- The verbatim final confirmation
