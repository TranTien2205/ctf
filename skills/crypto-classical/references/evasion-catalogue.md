# Evasion catalogue — the hide-the-family shapes

## The "it's just text" shape

A `ct` that *looks* like language — `π` (scrambled English letters) or `σ`
(ETAOIN shape). `cipher_id` IC~0.066 either way; the *order* is the tell.

## The encoding-in-disguise

A `ct` that looks like a cipher but is `+/=`/hex/`01` — `enc_detect`. The
charset is the discriminator.

## The layered trap

`ct → cipher_id → decode → cipher_id → decode` — `cipher_id` on each output;
the layers' stats are independent.

## The wrong-alphabet

A `KEYWORD`-mixed `σ` — `subst` solves it; the keyword shows in `σ`'s order.

## The partial-cipher

Letters `σ`'d, digits/spaces kept — the format (`flag{`) survives.

## The short-ct trap

Under ~30 chars the stats fail — the `flag{` positions carry the solve.

## The honest status

Evasion is *hiding the family* — `cipher_id`'s stats + the format find it.
