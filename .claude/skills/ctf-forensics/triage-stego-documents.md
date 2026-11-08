# Steganography and documents

Data hidden inside a carrier that renders normally. Depth in `steganography.md`,
`stego-image.md`, `stego-advanced.md` and `stego-advanced-2.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Steganography

```bash
steghide extract -sf image.jpg
zsteg image.png              # PNG/BMP analysis
stegsolve                    # Visual analysis
```

- **Binary border stego:** Black/white pixels in 1px image border encode bits clockwise
- **FFT frequency domain:** Image data hidden in 2D FFT magnitude spectrum; try `np.fft.fft2` visualization
- **DTMF audio:** Phone tones encoding data; decode with `multimon-ng -a DTMF`
- **Multi-layer PDF:** Check hidden comments, post-EOF data, XOR with keywords, ROT18 final layer
- **SSTV + LSB:** SSTV signal may be red herring; check 2-bit LSB of audio samples with `stegolsb`
- **SVG keyframes:** Animation `keyTimes`/`values` attributes encode binary/Morse via fill color alternation
- **PNG chunk reorder:** Fix chunk order: IHDR → ancillary → IDAT (in order) → IEND
- **File overlays:** Check after IEND for appended archives with overwritten magic bytes
- **APNG frame extraction:** Animated PNG has multiple frames; extract with `apngdis` or parse `fdAT`/`fcTL` chunks. See [steganography.md](steganography.md#apng-animated-png-frame-extraction-icectf-2016).
- **PNG height/CRC manipulation:** Modify IHDR height field, brute-force until CRC matches to reveal hidden rows. See [steganography.md](steganography.md#png-heightcrc-manipulation-for-hidden-content-h4ckit-ctf-2016).
- **Pixel coordinate chain stego:** Linked-list traversal where R=data byte, G/B=next pixel coordinates. See [stego-image.md](stego-image.md#pixel-coordinate-chain-steganography-h4ckit-ctf-2016).
- **AVI frame differential:** XOR consecutive video frames to reveal hidden data in pixel differences. See [stego-image.md](stego-image.md#avi-frame-differential-pixel-steganography-h4ckit-ctf-2016).

- **Custom freq DTMF:** Non-standard dual-tone frequencies; generate spectrogram first (`ffmpeg -i audio -lavfi showspectrumpic`), map custom grid to keypad digits, decode variable-length ASCII
- **JPEG DQT LSB:** Unused quantization tables (ID 2, 3) carry LSB-encoded data; access via `Image.open().quantization` and extract bit 0 from each of 64 values
- **Multi-track audio subtraction:** Two nearly-identical audio tracks in MKV/video; `sox -m a0.wav "|sox a1.wav -p vol -1" diff.wav` cancels shared content, flag appears in spectrogram of difference signal (5-12 kHz band)
- **Packet interval timing:** Identical packets with two distinct interval values (e.g., 10ms/100ms) encode binary; filter by interface, compute inter-packet deltas, threshold to bits

See [steganography.md](steganography.md), [stego-advanced.md](stego-advanced.md), and [stego-advanced-2.md](stego-advanced-2.md) for full code examples and decoding workflows.


## PDF Analysis

```bash
exiftool document.pdf        # Metadata (often hides flags!)
pdftotext document.pdf -     # Extract text
strings document.pdf | grep -i flag
binwalk document.pdf         # Embedded files
```

**Advanced PDF stego (Nullcon 2026 rdctd):** Six techniques -- invisible text separators, URI annotations with escaped braces, Wiener deconvolution on blurred images, vector rectangle QR codes, compressed object streams (`mutool clean -d`), document metadata fields.

See [steganography.md](steganography.md) for full PDF steganography techniques and code.


