# Common questions deep — the cache-poisoning operator's FAQ, exhaustively

## Is a reflected header on a MISS a poisoning?

```text
no — a marker reflected on a MISS means the response came from the
origin, not the cache — a REFLECTION, not a poisoning. the poisoning
requires a stored copy that serves YOUR input to a different requester
— a HIT on the second identical request.
```

## Is a keyed input poisonable?

```text
no — a keyed input keys the cache entry per-value — YOUR input's
effect is in YOUR copy only — a different requester gets a different
key — a keyed input isn't poisonable.
```

## What makes an input unkeyed?

```text
a request part the app reads but the cache key ignores — the default
key is the URL; headers are unkeyed unless the config adds them or
the response carries Vary. a stripped param, an unkeyed header, an
unkeyed cookie — the read-but-not-keyed inputs.
```

## Is an authenticated-page-served-anonymously a deception?

```text
yes — an authenticated page cached under a shared URL — the cache
keys on the URL, not the auth state — the stored copy is the
privileged page served to anyone — the auth state wasn't in the key.
the falsifier: a 302 to /login — the cache didn't serve the page.
```

## Is a cache-buster a poisoning vector?

```text
no — a keyed param the app ignores keys the entry per-value — the
stored response is YOUR requests only — a cache-buster DEFEATS the
poisoning by keying the entry per-value. use a cachebuster to confine
your probe's blast, not to poison.
```

## What's the blast radius?

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast is the URL's requester base — a
public URL poisons every visitor; a cachebuster URL poisons only your
key's requests.
```

## How long does a deception persist?

```text
the stored copy's TTL — the deception persists for the TTL — a short
TTL is a short-lived deception; a long TTL is a persistent one. the
TTL is min(the response's max-age, the proxy's configured TTL).
```

## Is a personalized page a deception?

```text
yes — a personalized page cached under a shared URL — the stored copy
serves YOUR session's content to every requester — a per-user leak.
the falsifier: a Vary: Cookie — a per-session copy — not a shared one.
```

## Is a path-normalization boundary a poisoning?

```text
yes — a path the cache and the app normalize differently — the stored
copy's URL is the victim's URL, the response is YOUR request's — a
route confusion. the falsifier: the app and the cache normalize the
same way — no confusion.
```

## How do I confirm a poisoning?

```text
the three-part evidence:
1. the probe request STORED — a HIT on the second identical request
2. the keyed input left OUT of the cache key — the unkeyed input
3. the reflected value reaching a response the victim receives — the
   clean request reflects the marker
a reflected header on a MISS is not a poisoning.
```

## What's the difference from request-smuggling?

```text
a smuggling is a DESYNC — a smuggled request reaches a different
route. a poisoning is a STORED response served to the wrong context —
no desync, no smuggled request — a stored copy's key-mismatch.
```

## What's the difference from a parser-differential?

```text
a parser-differential is a PARSE difference — a front-end and a
back-end parse differently. a poisoning is a STORE — a stored copy
serves YOUR input — no parse, a stored key-mismatch.
```

## What's the difference from an xs-leaks?

```text
an xs-leaks is an OPAQUE response you measure — a side-channel read.
a poisoning is a stored response served to the wrong context — a
real serve, not a measure.
```

## When do I move off the class?

```text
every candidate input IS keyed → no unkeyed input → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
a reflected marker on a MISS → a reflection, not a poisoning → a
different class.
```
