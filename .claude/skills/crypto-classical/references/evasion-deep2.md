# Evasion deep 2 — the hide-the-family shapes, expanded

## The "it's just text" shape — `π`/`σ` in disguise

A `ct` that *looks* like language — `π` (English letters, scrambled order) or
`σ` (ETAOIN shape). `cipher_id` IC~0.066 either way — the *order* is the tell:
scrambled → `π`; ETAOIN-shape-but-not-English → `σ`. The digraphs split them:
`TH` broken → `π`; `σ(TH)` present → `σ`.

## The encoding-in-disguise — `+/=`/hex/`01`

A `ct` that looks like a cipher but is an encoding — `enc_detect`. The charset
is the discriminator — always the first read. A `subst` anneal on a `base64`
blob is a wasted probe.

## The layered trap — `enc → cipher → enc`

A `ct` that decodes to another `ct` — `base64 → caesar → morse`. `cipher_id`
on the *output*, not a re-attack on the first layer. Each layer's stats are
independent — the outer layer's IC is *its* transform's, not the inner's.

## The wrong-alphabet — a keyed `σ`

`σ = KEYWORD + rest-of-alphabet` — `subst` finds `σ` anyway; the keyword shows
in the recovered `σ` order — `σ = KEYWORDABCDEFG...`. The anneal doesn't need
to know the keyword.

## The partial-cipher — letters only, the rest kept

Only letters `σ`'d/`k`'d — digits, punctuation, spaces kept — the decode reads
with the format intact. `flag{`/`CTF{`/`{`,`}` survive — the format leak.

## The short-ct trap — stats unreliable

Under ~30 chars the IC/chi²/Kasiski are unreliable — a 15-char `ct` reading
IC 0.04 is *not* a vigenere. The `flag{`/`CTF{` positions and common letters
carry the solve — `known-plaintext.md`.

## The `π(σ(p))` trap — order matters

A transposition of a substituted text — the letters aren't English.
Un-scramble `π` (position-only) *first*, then `subst`. Solving `σ` first on
the scrambled `ct` fails — the `σ` operates on the un-scrambled letters.

## The honest status

Evasion here is *hiding the family* — `cipher_id`'s statistics + the `flag{`
format find it.
