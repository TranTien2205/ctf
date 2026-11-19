# Evasion — when the obvious shape hides the cipher

## The "it's just text" shape

A ciphertext that *looks* like language but isn't — a transposition (the
letters are language) or a substitution (the shape is ETAOIN). `cipher_id`
separates them.

## The encoding-in-disguise

A `ct` that looks like a cipher but is an encoding — `+/=`/hex/`01` →
`enc_detect.py`. The charset is the discriminator.

## The layered trap

A `ct` that decodes to another `ct` — a layered cipher; `cipher_id` on the
output, not a re-attack on the first.

## The wrong-alphabet

A keyed `σ` — `subst` finds `σ` anyway; the key word is recoverable from the
`σ` order.

## The partial-cipher

Only letters transformed, digits/punct kept — the decode reads with the format
intact.

## The honest status

Evasion here is *hiding* the family, not evading a defense — `cipher_id` finds
it.
