# fickle-tempest (picoCTF) — SOLVED (self-solved)

- Platform: picoCTF. Target handed over as `http://fickle-tempest.picoctf.net:<port>/`
  (the port changes on every instance spin-up; it was 56824 then 62647).
- Date: 2026-09-23
- Stack: Apache 2.4.38, one static page, jQuery, no server-side logic at all
- Flag: redacted; decoded from the QR in the reassembled PNG
- Assistance: none; the page hands you the algorithm.

## The whole challenge is in the page source

```js
var LEN = 16;
$.get("bytes", function(resp) { bytes = Array.from(resp.split(" "), x => Number(x)); });

function assemble_png(u_in){
    var key = "0000000000000000";
    if (u_in.length == LEN) { key = u_in; }
    for (var i = 0; i < LEN; i++) {
        shifter = key.charCodeAt(i) - 48;
        for (var j = 0; j < (bytes.length / LEN); j++) {
            result[(j * LEN) + i] = bytes[(((j + shifter) * LEN) % bytes.length) + i]
        }
    }
    // trailing zeros trimmed, then rendered as a data: PNG
}
```

A PNG is stored as 16 interleaved columns and each column is cyclically rotated
by its own amount, taken from one character of a 16-character key. Submitting
the right key un-rotates every column at once and the image appears.

## Why it collapses to a 12-way search

`/bytes` returns **704** numbers, and 704 / 16 = 44 exactly. That makes
`((j + s) * 16) % 704` equal to `((j + s) mod 44) * 16`, so:

- every shift is one of only **44** values, and
- column `i` only ever reads offsets ending in `+ i`, so **each column is an
  independent one-dimensional problem**.

Row 0 of any PNG is the signature plus the IHDR length and type — exactly one
known byte per column:

```
89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52
```

That single constraint pinned **13 of the 16 columns to one residue**. Columns
8, 9 and 10 kept 2–3 candidates, and the IHDR payload settled them: the
compression and filter bytes of IHDR are always 0. Twelve combinations remained,
each checked properly by zlib-decompressing the concatenated IDAT data.

Result: key `1625882204269635`, a 370x370 PNG of 695 bytes containing a QR code.
The key is recoverable because `shift = charCode - 48`, and shifts 0..43 map to
`'0'`..`'['`, all printable.

## Decoding the QR with nothing installed

No `zbarimg`, no `pyzbar`, no `cv2` on this box, and `pip install pyzbar` fails
because libzbar is missing. PIL and numpy were present, so `qr.py` is a small
hand-written decoder: sample the module grid, read the format info for the mask,
unmask, walk the zigzag data region skipping function patterns, parse the
segments. Reed-Solomon is skipped on purpose — the image is generated, not
photographed, so the codewords are already exact. The decode came out as clean
ASCII in the expected `picoCTF{...}` shape, which is its own correctness check.

Grid: 29 modules => version 3, mask 3, 567 data bits.

## Reusable lessons

- **Check whether the length divides the stride before assuming modular chaos.**
  The `% bytes.length` in the source looks like it scrambles rows across columns,
  but 704 is a multiple of 16, so the modulus is a plain row rotation. Had it
  been 703 (which is what a naive `tr ' ' '\n' | wc -l` reported, because of the
  trailing token) the arithmetic would genuinely have mixed columns. Count the
  array the way the program counts it.
- **A known file header is one constraint per column in any column-interleaved
  scramble.** For a 16-column layout the PNG signature alone gives 16 equations,
  which is usually most of the answer; the next header row supplies the rest.
- **Verify a candidate reassembly by decompressing, not by eyeballing.** Several
  combinations produce a valid-looking signature; only the right one yields an
  inflatable IDAT stream.
- **A missing decoder is not a blocker for generated barcodes.** Skipping
  Reed-Solomon removes most of the work, and a wrong grid or mask fails loudly
  as garbage rather than silently as plausible text.

---

## Second variant, same host — solved 2026-09-23

A different challenge served from the same `fickle-tempest.picoctf.net` hostname
on another port. The page is almost identical; two lines differ and they make
the problem *easier*, not harder.

```js
var key = "00000000000000000000000000000000";   // 32 characters now, not 16
if (u_in.length == key.length) { key = u_in; }
shifter = Number(key.slice((i*2), (i*2)+1));     // ONE character, even index
```

`slice(i*2, i*2+1)` returns a single character, so:

- only the 16 **even-indexed** characters of the 32-character key do anything;
  the odd positions are read by nobody and can be any digit;
- `Number()` of one character is **0..9**, so every column's rotation is capped
  at 9 — even though this blob is 736 values = **46 rows**.

That cap is the whole difference. The first variant had 44 possible shifts per
column; this one has 10. The same PNG-signature constraint then pinned 12 of 16
columns outright, IHDR settled the rest, and only 24 combinations needed the
IDAT decompression check.

    shifts = [9, 5, 0, 1, 8, 9, 7, 5, 7, 2, 8, 3, 7, 6, 7, 7]
    key    = "90500010809070507020803070607070"   (odd positions arbitrary)
    image  = 370x370, 728 bytes, QR version 3, mask 4

Flag: redacted; a different flag from the first variant, so the two are genuinely
separate challenges rather than one instance re-rolled.

### Reusable lesson (new)

- **Read how the key is sliced, not just how long it is.** A longer key looks
  like a bigger search space; here the 32-character key is weaker than the
  16-character one, because a one-character slice caps each shift at 9 while the
  data has 46 rows. Widening the key while narrowing the per-element read is a
  net loss for the defender, and spotting it turns 46^16 into 10^16 and then,
  with the header constraint, into 24.
