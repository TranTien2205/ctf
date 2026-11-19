# Common questions — the XS-leak confusions, answered once

The questions that come up every time, with the direct answer.

---

## Q: the response is opaque — how do I read it?

You don't — you MEASURE its shape. the browser loads the response
(frames it, caches it, times it, errors on it, CSS-matches it) and
each behavior differs with the content. frames.length, onload/
onerror, timing, cache, CSS-match — the side-channel is the answer,
never the bytes.

## Q: classic vs sealed — what's the difference?

CLASSIC: the bot visits YOUR URL → your JS measures a side-channel.
SEALED: a fixed URL + script-blocked CSP → no JS → a declarative
(CSS) or server-state channel. the deciding question: can ANY
origin the bot reaches run one line of your JS? a 'no' forces the
sealed shape.

## Q: a `no-cors` fetch — can I read the response?

No — a `no-cors` response is opaque. but the FETCH still fires —
the response's SHAPE (whether it loaded, how long it took, how
many frames it rendered) is measurable — that's the leak. the
response body is never read.

## Q: does SameSite=Lax save the target?

Only in the classic shape — a cross-site fetch doesn't carry a Lax
cookie. in the sealed shape the bot only visits the target itself —
a same-site request carries it. and a meta-refresh issued BY THE
TARGET bypasses the Lax gate entirely — it's a same-site navigation.

## Q: a `*` ACAO — is that an XS-leak?

No — a `*` ACAO is a CORS PUBLIC read — the response IS readable
(non-credentialed) — a real read primitive, not a measure. an
XS-leak is only when the response is OPAQUE and you infer it.

## Q: the bot is airgapped — can I still exfil?

the classic shape's exfil is your listener — an airgapped bot can't
reach it. use a server-state channel (a counter/recency/token you
read on the target), a write-back, or a DOM-writeback — not an
external exfil.

## Q: `unsafe-inline` in the CSP — does JS run?

'unsafe-inline' in default-src/style-src allows STYLES — the CSS
oracle works even when script-src blocks JS. read the CSP as a
list of what's NOT allowed — a style/font hole is the channel.

## Q: a character-set oracle — does that give the secret?

for a SORTED secret — yes, the set IS the answer (the ordering is
known). for an UNSORTED secret — no, the set alone doesn't order it
— you need an n-gram/beam reconstruction.

## Q: how many bits per bot visit?

a one-shot token = 1 bit. a counter = a few. a recency/LRU =
thousands. a CSS oracle's one load = a whole char-set. measure the
channel's bandwidth before assuming 'one bit' — the visit count
depends on it.

## Q: the control pair — is it really needed?

always. a failed run and a negative answer look identical without
an always-true and never-true control. the pair separates 'no
leak' from 'broken channel' — without it, a 'no signal' is
uninterpretable.

## Q: a sorted secret — the set IS the answer?

yes — 'take N random chars, sort them' → the character set fully
determines the string — the ordering is known. sort the leaked set
→ the token. no ordering work needed.

## Q: the flood — does it destroy the flag?

an LRU flood evicts the least-recently-used keys — possibly the
secret itself. check whether the secret lives in the same store;
only flood an instance that's yours alone. read the blast_radius
on the chain card first.

## Q: the secret's in the page text, not an attribute — does the CSS match?

no — a CSS attribute-selector needs the secret IN an attribute
(data-secret, value, etc.). a secret in TEXT content needs a
different channel — a unicode-range @font-face reads the rendered
text.

## Q: a JSONP endpoint — is that an XS-leak?

no — a JSONP endpoint serves data AS JavaScript — a real read
primitive (a script-tag read), not a side-channel measure. the
boundary: a channel that returns the DATA is a read; a channel that
returns a BIT is a measure.

## Q: a postMessage broadcast — is that an XS-leak?

no — a postMessage '*' broadcast transmits the data — a real read
primitive, not a measure. the data is sent, not inferred.

## Q: the one-shot token — when do I spend it?

LAST — its 'did it survive' is one bit AND burns the check. narrow
the answer with the cheaper channels (a counter, a recency, a CSS
oracle) first — spend the one-shot on the last narrowing.

## Q: a sorted vs unsorted secret — how do I tell?

a secret built by 'take N chars, sort them' is sorted — the char-set
IS the answer. a secret with an unknown order is unsorted — an
n-gram/beam reconstruction is needed. check the generator — a
`sorted()` call or a sorted charset is the sorted case.

## Q: the managed-policy bot — is the sealed shape forced?

yes — URLBlocklist ['*'] + URLAllowlist — the bot can ONLY visit
the target's origin — NO attacker URL reaches it — a declarative/
server-state channel is the only one that works.

## Q: the CSS oracle needs the secret in what form?

an ATTRIBUTE for an attribute-selector (body[secret^="ab"]) —
a secret in TEXT content needs a unicode-range @font-face (it reads
the rendered text, not an attribute).

## Q: how do I verify a reconstructed secret?

submit it → confirm acceptance, or check the confidence score
clears a threshold. a reconstructed token that doesn't verify is
a candidate, not the answer — the verify step is the confirm.
