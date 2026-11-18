# Deserialization — depth reference

Load when `deserialization` found a serialized blob in a cookie, param,
hidden field, or body. Identification comes before exploitation — the format
decides the gadget tooling and whether a safe probe exists at all.

## Format identification (decode the blob, check magic bytes)

| Format | Base64 starts | Raw bytes | Shape |
|---|---|---|---|
| Java serialized | `rO0AB` | `ac ed 00 05` | binary; often `application/x-java-serialized-object` |
| .NET BinaryFormatter | `AAEAAAD/////` | `00 01 00 00 00 ff ff ff ff` | binary; ViewState is the base64 variant (`/wEP`) |
| Python pickle | `gAN`, `gAR` | `\x80\x03`, `\x80\x04` | opcodes readable in raw form |
| PHP serialize | — | text | `O:4:"User":2:{s:…}` / `a:2:{i:…}` |
| Ruby Marshal | — | `\x04\x08` | binary |
| Node node-serialize | — | JSON text | `{"k":"_$$ND_FUNC$$_function(){…}"}` |

Where blobs hide: cookies (session/remember-me), hidden form fields, JWT-like
custom tokens, API bodies, uploaded `.ser`/`.bin` files.

## Safe confirmation without a gadget

Detonating a gadget chain blind is a write-shaped action — confirm the
*deserialization* first, then reason about reach:

| Format | Safe probe |
|---|---|
| any | corrupt one byte → deserialization-specific stack trace in the error (`InvalidClassException`, `ClassNotFoundException`, `unserialize(): Error`, `pickle.UnpicklingError`) |
| Java | gadget-less `String`/`URL` object → DNS callback via `run_exploit` manifest or manual send |
| PHP | object with `__wakeup`/`__destruct` side effect visible in response |
| Python | `__reduce__`-free payload that only alters the decoded value |
| .NET | known-benign type that survives `BinaryFormatter`/`DataContractSerializer` |

A DNS/HTTP callback to a listener you control is the strongest blind proof —
it executes at deserialize time, before the app can refuse the object.

## Per-language notes

- **Java**: `ysoserial` gadget chains need the target's classpath library
  (CommonsCollections*, etc.). Fingerprint via error strings/framework
  headers first; `GadgetProbe`-style enumeration is the manual fallback.
- **.NET**: `ysoserial.net` payloads; check `__VIEWSTATE` MAC — a signed
  ViewState needs the machine key (leak via path traversal/`.bak` files)
  before any gadget fires.
- **PHP**: `phpggc` chains keyed to the framework in `fingerprint`'s
  stack hints (Laravel, Symfony, Drupal, WordPress).
- **Python**: unpickling is code execution by construction — but so is the
  probe. Keep it to `cos.system`/sleep or OOB callback.
- **Ruby**: `__send__`/marshal gadgets vary heavily by Rails version.

## Evidence honesty

- "I sent a ysoserial payload and nothing happened" is not a negative and
  not a finding — classpath guess, no signal either way.
- A deserialization finding needs one of: framework-named stack trace on
  corruption, observed side-effect of a benign object, or the OOB callback.
  Cite the recorded exchange.
- Report the *format + sink location* even when exploit chains fail — a
  confirmed `unserialize` of request data is the finding; gadget reach is
  a severity amplifier, not the bug.

## Severity guide

- Code exec / OOB callback proven: critical
- Confirmed deserialization of request data, gadget path plausible: high
- Confirmed format but no side-effect shown (signing may block): medium —
  name the signing/MAC obstacle explicitly
