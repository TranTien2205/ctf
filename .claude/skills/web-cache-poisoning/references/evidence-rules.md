# Evidence rules — what counts as a confirmed cache-poisoning

The proof standard for the class — what a confirm actually requires.

---

## 1. The candidate-vs-confirm split — the whole distinction

```text
a CANDIDATE — a reflected marker on a MISS, a cache-status header,
a classifier match, a chain-card match. a HYPOTHESIS, not a finding.

a CONFIRM — the marker persists into a CLEAN request's response AND
the cache indicator shows the stored copy served it. the stored
copy is the evidence; the reflected marker on a MISS is not.
```

## 2. The three-part confirm — the required evidence

```text
the confirm requires all three:
- the probe request STORED — a HIT on the second identical request
- the keyed input left OUT of the cache key — the unkeyed input
- the reflected value reaching a response the victim actually
  receives — the clean request reflects the marker
a reflected header on a MISS is not a poisoning — it must come from
the stored copy.
```

## 3. The MISS-vs-HIT distinction — the stored-copy requirement

```text
a MISS — the response came from the origin, not the cache — a
reflected marker on a MISS is a REFLECTION, not a poisoning.
a HIT — the response came from the stored copy — a reflected marker
on a HIT is the stored copy serving YOUR input — the poisoning.
```

## 4. The clean-request requirement — a different session

```bash
# the poisoning request — stores the marker
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
# the CLEAN request — a different session, the same URL
curl "$BASE/page?cb=<unique>"   # does it reflect <marker>?
```

```text
the clean request must reflect the marker — a stored copy that
serves YOUR input to a DIFFERENT request is the poisoning. a
marker that only reflects on YOUR request is a reflection.
```

## 5. The authenticated-page-served-anonymously — the deception confirm

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # anonymous — HIT?
```

```text
the anonymous request returning the authenticated page (a 200 with
the privileged content, not a 302 to login) is the deception's
confirm.
```

## 6. The cache-status requirement — the stored-copy indicator

```bash
# the cache status — the stored copy's indicator
curl -sI "$BASE/page?cb=<unique>" | grep -i 'x-cache\|cf-cache\|age'
#   X-Cache-Status: HIT — the stored copy served it
#   Age: N — the copy's age
```

```text
a HIT status or an Age header proves the stored copy served the
response — the marker's reflection came from the cache, not the
origin.
```

## 7. The negative-result discipline — a keyed input is a finding

```text
an input that IS part of the cache key → the stored copy is keyed
per-input — the stored response serves YOUR input only to YOUR
requests → a proved negative: THIS input is keyed, not poisonable.
record it — a keyed input narrows the search.
```

## 8. The blast-radius record — the shared-store effect

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — record the URL's requester base and the TTL — the blast
radius is a finding about the deception's scope.
```

## 9. The TTL record — the persistence

```text
the stored entry lives until its TTL — record the TTL — the
deception's persistence is a finding.
```

## 10. The falsifier record — a dead surface is a finding

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class. record the measurement — a keyed input
is a finding, not a failure.
```

## 11. The flag gate — the final standard

```text
a flag counts ONLY when read from a live response or a supplied
artifact — the deception's confirm is the privileged content served
to the wrong requester — not just a marker's reflection.
```
