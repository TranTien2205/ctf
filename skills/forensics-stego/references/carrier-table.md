# Carrier -> tool -> command

Run the cheap universal triage first (`file`, `binwalk`, `strings -n 8`,
`exiftool`), then the row matching the carrier.

| Carrier | Tool | Command |
|---|---|---|
| any file | appended data / embed | `binwalk -e file` ; `binwalk --dd='.*' file` |
| PNG / BMP | pixel LSB + planes | `zsteg -a img.png` ; `stegsolve` GUI bit planes |
| JPEG | steghide / outguess / jsteg | `steghide extract -sf img.jpg` ; `outguess -r img.jpg out` |
| JPEG header | jpegdump / djpeg | check trailing bytes after FFD9 |
| GIF | frame diffing | split frames (`convert img.gif %d.png`), diff consecutive |
| WAV / audio | spectrogram | open in Audacity -> Spectrogram view; look for text/dtmf/morse |
| MP3 | ID3 + LSB tools | `exiftool` tags; `mp3stego` for the audio channel |
| whitespace/doc | text stego | `stegsnow -C file` (spaces/tabs); hidden tracks in Office zip |
| PDF | object streams | `pdf-parser.py`, `pdfimages -all` |
| Zip/disk | deleted/carved | `photorec`, `foremost` |

## Reading a zsteg line

`b1,rgb,lsb,xy .. text: "flag{...}"` reads: bit-plane 1 of the rgb channels,
least significant bit, x-then-y order. The payload is on the right of `..`.
No hits on `zsteg` default? `-a` tries every plane/order — slower but the
negative is then honest.

## Passphrases

`steghide` prompts for a passphrase — it is almost always a word already
recovered in the challenge (an EXIF comment, a decoded string, the filename).
Record every word you recover; try them all before reaching for a wordlist.

## When nothing lands

An honest negative needs: no appended data, no embedded signature, EXIF
clean, and at least the common planes tried (`b1-3, rgb/bgr, lsb/msb`). Then
the answer is the *content* — the image itself is the clue (what/where/who),
route to osint-media-metadata or misc-encoding-carrier.
