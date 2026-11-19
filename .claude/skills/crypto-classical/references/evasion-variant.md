# Evasion variant — the hide-the-family shapes, by variant

## The `π`-in-disguise variant

A `ct` that *looks* like language — English letter counts, scrambled order —
`π`. `cipher_id` IC~0.05-0.066; the *order* is the tell — the digraphs `TH`
are broken (the letters are permuted apart).

## The `σ`-in-disguise variant

A `ct` that *looks* like language — ETAOIN shape but not English — `σ`.
`cipher_id` IC~0.066, flat chi² — `subst` anneal.

## The encoding-in-disguise variant

A `ct` that looks like a cipher but is `+/=`/hex/`01` — `enc_detect`. The
charset is the discriminator — always the first read.

## The layered variant

`enc → cipher → enc` — `cipher_id` on each output — the layers' stats are
independent; the outer layer's IC is *its* transform's.

## The keyed-alphabet variant

`σ = KEYWORD + rest` — `subst` finds `σ` anyway; the keyword shows in `σ`'s
order — `monoalphabetic-variants*.md`.

## The partial-cipher variant

Letters `σ`'d/`k`'d, digits/spaces kept — the format (`flag{`) survives —
`known-plaintext*.md`.

## The short-ct variant

Under ~30 chars the stats fail — the `flag{`/`CTF{` positions carry —
`known-plaintext*.md`.

## The verify

`pt` language + `enc(pt)=ct`.
