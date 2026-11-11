---
name: forensics-stego
description: >
  Action-oriented depth skill for Steganography / hidden data. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: misc-encoding-carrier, forensics-pcap-carve.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [forensics, stego, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Steganography / hidden data

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

file + binwalk + strings on the carrier first — the answer is often appended, not encoded

**Falsifier** — the observation that closes this class: no appended data, no embedded signature, no metadata anomaly, and the pixel/audio payload decodes to noise on every standard channel
## Recognise

A media file is the handout and the flag (or the next step) is hidden inside
it: appended bytes, an embedded archive, LSB pixel data, an audio channel, or
metadata. The carrier decides the tool — never guess a stego tool before the
carrier is identified.

## Confirm safely

All reads are local and non-destructive; the only real risk is spending the
budget on the wrong channel. Work a copy of the artifact and record which
channel yielded.

## Extraction order

1. `file` + `binwalk` + `strings -n 8` — appended data and embedded archives
   are the most common CTF carrier and the cheapest to check.
2. `exiftool` — metadata fields hide flags and the next-step hint.
3. `zsteg` (PNG/BMP), `steghide` (JPEG), `outguess`, or `binwalk -e` for the
   format-specific channel; `sonic-visualiser`/Audacity for audio.
4. Only then bit-level work: `stegsolve`/`zsteg -a` across bit planes.

`references/carrier-table.md` maps carrier -> tool -> command.

## Traps

- `file` reporting "data" usually means a renamed container — read the magic
  bytes with `xxd | head`, do not trust the extension.
- A steghide passphrase often IS a string found earlier in the challenge —
  try recovered words before brute force.
- An all-noise LSB decode on the wrong bit plane looks identical to a
  negative result; record which planes were tried.

## Operational probe

```bash
python3 tools/forensics/carve_scan.py challenge.png     # stdlib: magic offsets + trailing data + flag-format runs
python3 tools/forensics/carve_scan.py challenge.png --extract out/   # carve each hit to a file
file challenge.png && binwalk challenge.png && strings -n 8 challenge.png | head
exiftool challenge.png
zsteg -a challenge.png 2>/dev/null | head -20
```

`carve_scan` is the absent-binwalk fallback: it finds embedded magics and
data trailing a container's real end — the common CTF hide — plus a
flag-format pass over printable runs.

`python3 tools/forensics/img_struct.py photo.png` is the finer-grained
first look for image containers specifically: the PNG chunk list with a
per-chunk CRC check (a bad CRC is itself a tamper signal), the JPEG
marker walk to SOS and EOI, the GIF trailer, byte count after the real
end-of-image, and embedded-format signatures (zip/rar/pdf/png/jpeg)
with offsets. Run it before `lsb_scan` — a polyglot or appended blob is
cheaper to rule out than a bit-plane sweep.

When the PNG itself is corrupted (bad CRCs, garbage between chunks,
missing IEND), `python3 tools/forensics/png_fix.py broken.png
--fix out.png` rewrites chunk CRCs, drops non-chunk bytes and appends
the missing terminator, reporting each repair — a tampered chunk is a
signal, not just damage. It refuses to invent pixel data: a damaged
IDAT stream is reported, not faked.

For the LSB half there is now a stdlib option too:

```bash
python3 tools/forensics/lsb_scan.py challenge.png            # PNG/BMP/WAV, planes 1-3
python3 tools/forensics/lsb_scan.py challenge.png --planes 1 # the common one
```

It walks the same matrix `zsteg -a` reports (b1-3, r/g/b/a/rgb/bgr,
xy/yx, lsb/msb) and prints every stream that decodes printable, with the
flag-format pass on top. For `.wav` it runs the same matrix over PCM
sample bytes (8-bit raw, 16-bit lo/hi split). When the WAV is a phone
dial / tone sequence instead of hidden bits,
`python3 tools/dtmf_decode.py dial.wav` decodes the touch-tone grid
(Goertzel power estimate over the eight DTMF frequencies, 8/16-bit PCM,
stereo mixed down) into the digit string; `--frames` shows each
window's chosen low/high pair for boundary cases. When the audio lives
inside a capture instead of a file,
`python3 tools/forensics/rtp_extract.py call.pcap` lists the RTP
streams by SSRC (codec, packet count, seq loss) and
`... --ssrc 0xNNN --out call.wav` decodes PCMU/PCMA through stdlib
audioop+wave — the output feeds `dtmf_decode` directly. JPEG stego,
MP3 channels and deeper planes still need the external tools below.

## Routing

Shares signals with: `../misc-encoding-carrier/`, `../forensics-pcap-carve/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/forensics-stego/references/README.md`
- `skills/forensics-stego/references/carrier-table.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
