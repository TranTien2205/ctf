# Common questions — the cache-poisoning confusions, answered once

## Q: a reflected marker — is that a cache poisoning?

No — a marker reflected on a MISS is a REFLECTION — the response came
from the origin, not the cache. a poisoning requires the STORED copy
to serve YOUR input to a DIFFERENT requester — the clean request
must reflect the marker AND the cache indicator must show a HIT.

## Q: the app reads the header — is it poisonable?

Not necessarily — the app reading the header doesn't matter if the
cache KEYS on it. the vulnerability is the KEY mismatch — a request
part the app reads but the cache ignores. check the unkeyed-input
surface — the cache key, not the app's read, is the vector.

## Q: a Vary: Cookie — is the input keyed?

yes — a Vary: Cookie header keys the entry on the cookie — a per-
session copy — YOUR input's effect is in YOUR copy only — not a
shared poisoning. a Vary'd header is keyed; an unkeyed one isn't.

## Q: an authenticated page served anonymously — how?

the cache keys on the URL, not the auth state — an authenticated
page stored under a URL the anonymous requester also fetches — the
stored copy is the privileged page served to anyone. the deception:
the cache doesn't distinguish 'your authenticated copy' from 'the
anonymous requester's copy'.

## Q: a 302 to login — is that a deception?

no — an anonymous request that 302s to /login isn't a deception —
the cache didn't serve the privileged page — a redirect to login is
the safe behavior. the anonymous request must return the privileged
page (a 200 with the content).

## Q: a cache-buster — does it defeat the poisoning?

yes — a keyed param the app ignores keys the entry per-value — the
stored response is YOUR requests only — a cache-buster defeats the
poisoning. a keyed param isn't poisonable.

## Q: the cache has no status header — does it exist?

maybe — a cache may not add a status header — check the source/
config for the cache layer — proxy_cache, vcl_hash, cache_page,
flask_caching — a cache may exist without a status header.

## Q: the blast radius — who does a poisoned entry hit?

every requester of the URL until the entry expires — a public URL
poisons every visitor — the blast radius is the URL's requester
base. use a harmless marker; keep the window short; clean up.

## Q: the TTL — how long does the deception last?

the stored entry lives until its TTL — the deception persists for
the TTL — a short TTL is a short-lived deception; a long TTL is a
persistent one. measure the TTL to bound the attack's window.

## Q: a path-normalization confusion — is that a cache deception?

only if a stored copy serves the confusion to a different requester —
a routing bug alone isn't a cache deception — the stored-copy
requirement still holds.

## Q: a keyed input — can I still poison?

no — a keyed input keys the entry per-value — the stored response
serves YOUR input only to YOUR requests — a keyed input isn't
poisonable. the unkeyed input is the whole vulnerability.

## Q: the deception needs a bot — why?

the deception stores YOUR content but no privileged bot views the
stored copy — the poisoned page needs a victim viewer — a bot that
requests the poisoned URL — the stored copy reaches the privileged
context.

## Q: a no-store directive — is the page cacheable?

no — a Cache-Control: no-store or private — the page isn't cached —
a different class. check the response's Cache-Control.

## Q: an unkeyed input — how do I find it?

for each candidate input — send it → check the stored copy serves
it to a CLEAN request — a keyed input's marker doesn't reach a
different requester; an unkeyed one's does. the unkeyed-input check
is the poisoning vector's test.

## Q: the deception vs the poisoning — the difference?

a POISONING — YOUR input's effect stored under a URL the victim
requests — the stored copy serves it to every requester.
a DECEPTION — a stored response served to the WRONG context — a
privileged page to an anonymous requester, a personalized page to
a public requester. the deception is the wrong-context serve; the
poisoning is the injected input.
