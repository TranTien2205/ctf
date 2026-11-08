# Structured-field differentials

The differential is not only in request lines. Any value two components both
parse — a cookie, an email header, a token, a parameter — can be decoded by one
and passed literally by the other.

## Cookie decoding

**Probe** (SerialFlow):

```text
GET /   Cookie: session="AA\101BB"
GET /   Cookie: session=AAABB
```

Expected: the quoted-octal form decodes `\101` to `A` at the backend while the
frontend — or the signature/lookup layer — compared the raw bytes. The two
sessions collide on the server but were distinct strings on the wire, which is
exactly the gap a lookup keyed on raw input misses.

The decoding alphabet: `\0NN` octal escapes, `\"` quote escapes, doubled
semicolons, `%`-encoding inside an already-decoded slot, and charset shifts
(UTF-8 vs latin-1 on the same bytes).

## Email and other header parsing

**Probe** (secure-email-service):

```text
Subject: x\nFrom : <other identity>
```

Send one message whose Subject carries a folded header, then read back what the
application's *own* parser reports as the sender. Expected: the two layers
disagree — the MTA saw `x` as the subject and dropped or split the fold, while
the application's parser treated it as a second `From` and reported the
attacker-chosen identity. The gap is not SMTP forgery; it is *which* parse the
application displays or authorizes against.

The same shape applies wherever a header value crosses parsers: folded
whitespace, `\r\n` variants, `Name :` with a space before the colon, duplicated
headers with different values.

## The general pattern

```text
<value>      # arm A: literal
<f(value)>   # arm B: same value under a different encoding the backend applies
```

Expected: arm B is treated as equal to arm A by the backend but different by
the gate, or vice versa. Falsifier: both arms are identical end to end — one
decoder owns the field and there is no differential.

## Traps

- Compare *what the application reports*, not what was sent — the observable
  lives on the second parse.
- A cookie that round-trips through a signing or lookup layer amplifies the
  gap: signed raw bytes vs decoded identity is two different principals.
