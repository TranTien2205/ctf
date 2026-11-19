# Field notes (deep) — the class's learning-loop

## The learning-loop for open-redirect

```text
the catalogue class has NO local solves — the corpus is published
knowledge. The LEARNING-LOOP records what a live target actually does
to turn the corpus into local experience.
```

## The field-note shape — what a solve records

```text
field-note: web-open-redirect
challenge: <the-challenge-name>
the-surface: /login?next= (the endpoint + param)
the-filter:  startswith('/') (the fingerprinted check)
the-arm:     //evil.com (the bypass that fired)
the-oracle:  Location: //evil.com (the verbatim evidence)
the-chain:   open-redirect -> the post-login phishing launder
the-outcome: the flag / the impact
the-trap:    the arms that DIDN'T work (the negatives)
```

## The field-note categories — what to capture

### the filter-shape note

```text
the target's filter was X; the arms that fired were Y — a MEASURED
filter-shape to reuse: a `startswith('/')` -> `//`; a `contains` ->
substring; an allowlist -> the `@`/`\@`/subdomain/encoded
```

### the arm-that-fired note

```text
the arm is the reusable lesson — `//evil.com` on a `startswith('/')`;
`evil.com\@target.com` on a `hostname` check; the arms the corpus names
CONFIRMED on this target
```

### the negative note — the arms that DIDN'T fire

```text
the arms that were closed: `//evil.com` -> Location: / (blocked);
`javascript:` -> 400 (rejected); the negatives are the filter's
fingerprint — record which arms the filter catches
```

### the chain note

```text
the laundered-trust the open-redirect fed: the OAuth-code launder, the
SSRF-fetch, the bot-visit, the standalone phishing — the chain's shape
```

### the trap note — the thing that cost time

```text
the trap: the param was `return` not `next`; the redirect was the stored
two-step; the filter was a `netloc` check not a `hostname` check — the
per-target trap
```

## The proposed-vs-confirmed discipline

```text
a field-note marked `proposed` is unverified — an observation from one
target, not a generalizable lesson. A `confirmed` field-note was checked
on a second target OR verified against the verbatim evidence.

proposed: "target.com's filter is a contains-check — the substring arm fired"
confirmed: "the substring arm fires on contains-checks (verified on X, Y)"
```

## The field-note -> corpus upgrade

```text
when a field-note's arm fires on a SECOND target with a DIFFERENT
fingerprint -> the arm is a NEW bypass -> add it to the corpus ->
the catalogue class becomes locally-informed
```

## The field-note file — `../field-notes.md`

```text
the field-notes live at the skill root — append a note per solve; the
`../../../LEARNING_LOOP.md` is the format; the notes accumulate into the class's
local experience — the upgrade from catalogue to verified
```

## The field-note-record — the template

```markdown
## <date> — <challenge> — web-open-redirect

- the surface: <endpoint>?<param>=
- the filter: <the fingerprinted check>
- the arm: <the bypass that fired>
- the oracle: <the verbatim Location>
- the chain: <the laundered-trust>
- the traps: <the negatives + the cost>
- verdict: confirmed | proposed
```
