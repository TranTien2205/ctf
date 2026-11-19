# Workflow — XS-leak end to end

The loop: name the sub-shape → inventory the oracle → measure the
feasibility → build the channel → reconstruct the secret.

---

## 1. Name the sub-shape — classic or sealed

```bash
# can attacker JS run on an origin the bot reaches?
curl -s -i "$BASE/" | grep -i 'content-security-policy'
grep -rnoiE 'bot|visit|report|url.*=|page\.|script-src|CSP' <src> | head -20
#   a bot that takes an attacker URL → CLASSIC
#   a fixed URL + a script-blocking CSP → SEALED
```

## 2. Inventory the oracle — what does the response leak

```text
a frame-count, an error, a redirect, a timing, a cache, a size, a
server-state mutation, a CSS-match — each a measurable difference.
```

## 3. Measure the feasibility — the arithmetic

```text
- secret's lifetime (a 60s TTL → the whole leak fits in it)
- request rate needed vs available (thousands of markers = tens-hundreds rps)
- bits per visit (1 vs thousands — a token vs a recency channel)
- the secret's character-set (a sorted/limited alphabet reduces search)
```

## 4. Build the channel — the oracle

```text
CLASSIC → a client-side oracle — frame-count, error, timing, cache
SEALED  → a server-state channel OR a declarative CSS oracle
```

## 5. The control pair — the channel's sanity check

```text
an always-matching selector/input + a never-matching — the YES/NO
pair. if they don't separate → the channel is broken.
```

## 6. The leak run — the bot's visit

```bash
# deliver the attacker page / the seed
curl -X POST "$BASE/report" -d 'url=<the page or the seed-url>'
# for a sealed channel — the bot's GET seeds the oracle
```

## 7. The read-back — the oracle's answer

```bash
# classic → your page's own JS reads the oracle
# sealed → read the server-state — the surviving keys, the counter,
#          the timestamps — or the font/URL loads on your listener
python3 tools/web/oob_listener.py hits
```

## 8. The reconstruction — from bits/n-grams to the secret

```text
a boolean oracle → a binary search per character position
a character-set oracle → a sorted set — the secret's set is the answer
an n-gram oracle → a beam search over overlapping n-grams
```

## 9. The flag — through the gate

```bash
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source '<the leak channel>' --evidence '<the reconstructed secret>'
```

## 10. The negative path

```text
a sealed shape with no CSS oracle and no server-state channel →
the oracle surface is dead → a different class or a measured closure
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "xs-leaks: <classic|sealed> — oracle=<channel> — secret=<target>"
```
