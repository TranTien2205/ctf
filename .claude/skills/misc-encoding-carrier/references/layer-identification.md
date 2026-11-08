# Layer identification: name the carrier before decoding

A carrier puzzle is a stack of encodings — the skill is naming each layer in
one look, not decoding all of them at once. Identify the outermost layer,
strip it, repeat.

## The identification alphabet

| Look at | Says |
|---|---|
| `A-Za-z0-9+/=` tail with `=`/`==` padding | base64 |
| `A-Za-z0-9` no `+/=`, `=` tail | base64-url or base62 |
| `0-9a-fA-F` even length | hex |
| `01 ` spaces mostly | binary / byte string |
| `[];'<>,.-+` | brainfuck family |
| `Ook. ?!` | Ook! |
| `.:;!?'()[]{}@#$%^&*_-~` punctuation only | JSFuck / aaencode |
| `ABCDEFGHIJKLMNOPQRSTUVWXYZ` with subs | Caesar/ROT/substitution |
| `UU..` or `begin 644` | uuencode |
| `MzU...` nested base64 | base64 of base64 |
| `-----BEGIN` | PEM/OpenPGP armor — the layer is crypto, not encoding |
| `#!...` esolang header | the layer is a language, not encoding |
| `gzip PK 7z RAR` magic bytes | compressed — decode = decompress first |

`file <data>` and `binwalk -e` settle the byte-level cases instantly.

## The working loop

```bash
# one layer at a time, never guess
data | head -c 80          # look at the head, not the whole thing
file -                    # what the bytes say they are
base64 -d 2>/dev/null | file -   # peel and re-identify
```

When a layer decodes to something that still isn't text — repeat the table on
the output, not on the input.

## Common carriers in CTF

| Layer stack | Recognize |
|---|---|
| base64 → base32 → hex → text | the shrinking alphabet ladder |
| compressed → base64 | `PK`, `1f 8b`, `BZh` magic under the base64 |
| charset-substituted base64 | same alphabet, wrong order — solve the map first |
| whitespace/zero-width | `xxd -g1` shows the bytes the terminal hides |
| emoji/unicode-encoded | zero-width joiner and regional-indicator tricks |
| audio → morse / spectral | `sox`, spectogram view in Audacity |
| image → LSB / palette | `zsteg`, `stegsolve`, `steghide` |

## Falsifier

The bytes are already the flag, or the "carrier" is a cipher whose key isn't
given — it's a crypto class, not an encoding; route there instead.

## Traps

- `file` lies on polyglot/magic-less data — trust the hex pattern, not the
  guess.
- `=` padding can be stripped; `base64 -d` fails on stripped input — re-pad
  to a multiple of 4 first.
- A layer that decodes to *printable but wrong* text is usually a charset
  or substitution layer, not a failed decode.
- Zero-width Unicode is invisible in a terminal — `xxd` on the raw bytes
  shows what you can't see.
