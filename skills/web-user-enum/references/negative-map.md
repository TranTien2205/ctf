# Negative map — every dead end and what it actually means

## The cell-addressed negatives

| The negative | What it means | What it does NOT mean |
|---|---|---|
| `/login`:body uniform | the text channel is equalized | the timing/side cells are closed |
| `/login`:status uniform | the code+`Location` equalized | the body is closed |
| `/login`:timing uniform | `verify()` is equalized or sub-jitter | the content is closed |
| `/login`:side uniform | no cookie/send/lock differential | the form is fully closed |
| `/login` all-uniform | the LOGIN form is closed | register/reset/check are closed |
| `/register` uniform | no taken-check leak | `/login` is closed |
| `/check-*` absent | no direct endpoint | the form channels are closed |
| `/graphql` resolvers uniform | no GraphQL oracle | the REST forms are closed |
| `?u=` returns same | that endpoint is not an oracle | the login form is closed |
| the seeded list all-negative | the seeded names absent | the oracle is broken (it works; the names don't exist) |

## The oracle-vs-names confusion — the most common false negative

A confirmed oracle + an all-negative seeded list means the NAMES are
absent, not that the oracle is broken. The oracle is proven by
`KNOWN` vs `FAKE`; the list just found no real names. Record:
`oracle: verified; names: none in the seeded list` — then widen the
list (bundle/source fixtures, content authors) rather than re-probing.

## The format negative

A `404`/`400` on `admin@x.c` where `admin` (no at) hits the oracle is
a FORMAT negative — the email format is not the live slot, not that
the account is absent. Record `format: username (not email)`.

## The normalization negative

`admin`/`Admin`/`ADMIN` all hitting the same oracle = normalization,
not a fake-negative. Record `normalization: case-insensitive`.

## The throttle negatives

| The negative | What it means |
|---|---|
| XFF does NOT reset `429` | the counter is not per-IP — try session/endpoint/method |
| fresh-session does NOT reset | not per-session — try IP/endpoint |
| the alias endpoint also `429`s | the limiter is shared, not route-scoped |
| a `GET` is also counted | the limiter is method-agnostic |
| a spray-under still `423`s | the lock is per-IP not per-account |

## The honest-negative record

```
negative: <form>:<channel> uniform (measured: three arms, verbatim)
negative: oracle verified; names: none in <list>
negative: <bypass-vector> does not reset the <counter-key>
```

Every negative is a measured result, not an absence of a result.
