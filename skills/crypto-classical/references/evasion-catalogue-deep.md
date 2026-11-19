# Evasion catalogue deep — the hide-the-family shapes, fully indexed

## The `π`-in-disguise — `evasion*.md`

A `ct` that *looks* like language — English counts, scrambled order — `π`.
`cipher_id` IC~0.05-0.066; the digraphs `TH` broken (the letters permuted
apart). `railfence*.md`,`transposition-variants*.md`.

## The `σ`-in-disguise — `evasion*.md`

A `ct` ETAOIN-shaped but not English — `σ`. `cipher_id` IC~0.066, flat chi².
`subst*.md`,`monoalphabetic-variants*.md`.

## The encoding-in-disguise — `evasion*.md`

A `ct` that looks like a cipher but is `+/=`/hex/`01` — `enc_detect`.
`encoding-*.md`,`detection.md` — the charset is the tell.

## The layered — `evasion*.md`,`multi-step-chains*.md`

`enc → cipher → enc` — `cipher_id` on each output — the layers' stats
independent.

## The keyed-alphabet — `evasion*.md`,`monoalphabetic-variants*.md`

`σ = KEYWORD + rest` — `subst` finds `σ` anyway; the keyword in `σ`'s order.

## The partial-cipher — `evasion*.md`,`known-plaintext*.md`

Letters `σ`'d, digits/spaces kept — the format survives.

## The short-ct — `evasion*.md`,`edge-cases*.md`,`known-plaintext*.md`

Under ~30 chars the stats fail — the `flag{`/`CTF{` positions carry.

## The `π(σ(p))` — `evasion*.md`,`multi-step-chains*.md`

`π` first (position-only), then `subst`.

## The honest status — `verified-chains*.md`

Evasion is *hiding the family* — `cipher_id`'s stats + the `flag{` format
find it.
