# Insecure deserialization

**When:** a cookie, param, body or uploaded file is deserialized server-side.
Recognize the formats BEFORE attacking:

`probe_deserialize(url, param)` sends gadget payloads for each ecosystem and reports the parser errors they raise. A parser error is a SURFACE, not execution: the class is proven the way rce is, so the gadget must carry `id; echo <nonce>` and the response must return the identity line AND that nonce.

| Bytes | Format |
|---|---|
| `rO0AB` (base64) / `\xAC\xED\x00\x05` | Java serialization |
| `O:8:"..."`, `a:2:{...}` | PHP serialize |
| `(dp1` / `gASV` (base64 starts KQ/ YQ) | Python pickle |
| `--- !ruby/object:` | Ruby YAML marshal |
| `{"@type":"com.x","$type":"..."}` | JSON polymorphic typing |
| `.NET` `__VIEWSTATE`, `__EVENTVALIDATION` | ASP.NET LOSFormatter |

## Detection without gadgets

- Type confusion: send a valid object of the wrong type (string where dict
  expected) -> deserialization errors differ from validation errors
- PHP: `O:8:"stdClass":0:{}` vs malformed `O:8` syntax - a parse error
  confirms `unserialize()` ran on your input
- Error/timing oracles: Java deserialization of a garbage-serialized stream
  throws `ClassNotFoundException`/`StreamCorruptedException` with class
  names - the class names ARE proof the stream was read
- YAML (Python): `!!python/object/new:os.system` is RCE; `!!python/object/apply:...`
  - only when PyYAML `load()` (not `safe_load`) is suspected

## Exploitation discipline on real targets

- Gadget chains need the app's classpath: identify framework first
  (commons-collections, Spring, groovy). Do not spray ysoserial payloads -
  each is a live payload; pick ONE matching the stack, or state that
  gadget verification needs source/classpath access.
- Signing/HMAC-wrapped blobs: deserialization behind a signature is dead
  unless a key/leak exists - move the hunt to `auth-session`.
- Safe proof: a class-resolution error or a sleep gadget demonstrating the
  stream was consumed beats blind RCE attempts.

## Falsifier

Input rejected at parse, `safe_load`/allowlisted classes enforced, or the
blob is integrity-protected and the verifier rejects any modification.

## Severity guide

RCE via gadget (benign proof): critical. File write/SSRF gadget: high.
Deserialization confirmed but no reachable gadget shown: medium-high -
document the primitive honestly.
