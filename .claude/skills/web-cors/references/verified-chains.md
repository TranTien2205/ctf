# Verified chains — the CORS class's standing in the ledger

This is a CATALOGUE class — no solved challenge in this repository
has a verified CORS chain card yet. This file records the standing,
the adjacent verified shapes, and what a future card would need.

---

## 1. The standing — catalogue, not verified

```text
knowledge/chains/ carries no web-cors card — the class is standard
published knowledge, not local measured experience. the skill's
content is the corpus's best-effort operational summary; it is NOT
a claim that a CORS solve has been verified here.
```

## 2. The adjacent verified shapes — the classes that DID land

```text
the web-csrf cards (2) — the WRITE side of the same delivery: a
bot-driven cross-origin request that fires a write. the CORS read
is the mirror image — the same fetch mechanics, opposite halves.

the web-xs-leaks card — a cross-origin side-channel measurement —
the fallback when the CORS read is closed but a measurable
difference exists.

the web-ssrf cards — a server-side fetch — the other 'the server
reads it' primitive.
```

## 3. What a verified CORS card would need

```text
a challenge where:
- an ACAO+ACAC pair allows a foreign origin (reflected, null, or
  bypassed)
- the session cookie rides the fetch (SameSite=None+Secure)
- a sensitive endpoint (/api/me, /api/flag) returns the flag
- the exfil reaches the attacker listener
→ the card: the endpoint, the ACAO shape, the bypass battery result,
  the exploit page, the exfil evidence, the flag.
```

## 4. The candidate-shapes that would promote the class

```text
a reflected ACAO+ACAC on a flag endpoint — the canonical card
a null-allowed CORS + a data: URL bot — the opaque-origin card
a subdomain-trust + a controlled-sub read — the subdomain card
a CORS-read → CSRF-write chain — the multi-class card
```

## 5. The falsifier that keeps the class honest

```text
a `*` on a sensitive endpoint is NOT a CORS vuln — a `*`+credentialed
is rejected by every browser. a card that 'solved' via a `*` is a
misclassified public-read, not a CORS solve.
```

## 6. The promotion rule — when the class becomes verified

```text
when a real challenge's CORS read exfiltrates the flag through the
evidence gate (hooks.py pre-flag), the solve is filed via
tools/classify_solve.py → a knowledge/chains/<id>.json card → the
class's status flips to verified and this file is replaced by the
real card's summary.
```

## 7. The honest-content rule for a catalogue class

```text
the skill's corpus is operational standard knowledge — payloads,
probes, matrices — but no 'we solved this exact shape here' claims.
a catalogue skill never presents its content as measured experience;
it presents it as the best-known playbook.
```
