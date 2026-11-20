# The stego workflow — carrier decides the tool

A media file is the handout; the flag hides inside: appended bytes,
an embedded archive, LSB pixel data, an audio channel, or metadata.
The carrier decides the tool — never guess a stego tool before the
carrier is identified.

## The order

1. `file` + `binwalk` + `strings -n 8` — appended data and embedded
   archives are the most common CTF carrier and the cheapest to check.
2. `exiftool` — metadata fields hide flags and next-step hints.
3. Format channel — `zsteg` (PNG/BMP), `steghide` (JPEG), outguess,
   `binwalk -e`, sonic-visualiser/Audacity for audio.
4. Bit-level — `stegsolve`/`zsteg -a`/`lsb_scan` across bit planes.

## The stdlib route

    python3 tools/forensics/carve_scan.py f.png --extract out/
    python3 tools/forensics/img_struct.py photo.png
    python3 tools/forensics/lsb_scan.py f.png --planes 1
    python3 tools/forensics/png_fix.py broken.png --fix out.png
    python3 tools/dtmf_decode.py dial.wav
    python3 tools/spectrogram.py mystery.wav
    python3 tools/forensics/rtp_extract.py call.pcap --ssrc 0xN --out c.wav
