# Evasion deep — when the obvious shape hides the cipher

## The "it's just text" shape

A ciphertext that *looks* like language but isn't — a transposition (the
letters are English, the order is scrambled) or a substitution (the freq
shape is ETAOIN). `cipher_id`'s IC separates them — IC~0.066 either way, but
the *order* is the tell: scrambled → `π`.

## The encoding-in-disguise

A `ct` that looks like a cipher but is an encoding — `+/=`/hex/`01` →
`enc_detect`. The charset is the discriminator. A `subst` anneal on a `base64`
blob is a wasted probe.

## The layered trap

A `ct` that decodes to another `ct` — `base64 → caesar → morse`. `cipher_id`
on the *output*, not a re-attack on the first layer. Each layer's stats are
independent.

## The wrong-alphabet

A keyed `σ` (`KEYWORD + rest`) — `subst` finds `σ` anyway; the keyword shows
in the recovered `σ` order — `σ = KEYWORDABCDEFG...`.

## The partial-cipher

Only letters transformed, digits/punct/spaces kept — the decode reads with the
format intact. `flag{`/`CTF{`/`{`,`}` survive.

## The short-ct trap

Under ~30 chars the IC/chi²/Kasiski are unreliable — a 15-char `ct` reading
IC 0.04 is *not* a vigenere. The `flag{`/`CTF{` positions and common letters
carry the solve.

## The honest status

Evasion here is *hiding the family* — not evading a defense. `cipher_id`'s
statistics find it; the `flag{` format leaks it.
