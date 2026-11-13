#!/usr/bin/env python3
"""spectrogram.py -- render a WAV's frequency-domain picture, in the
terminal, without Audacity/sonic-visualiser.

"Flag drawn in the spectrogram" is the most common audio-stego shape
after LSB: the tool computes an STFT with numpy and prints an ASCII
ramp -- an agent can READ the picture from stdout and does not need
an image viewer. --png writes a real grayscale PNG (stdlib zlib
encoder) when a pixel-exact copy is wanted.

    python3 tools/spectrogram.py mystery.wav
    python3 tools/spectrogram.py mystery.wav --cols 140 --rows 48 \
        --fmax 4000 --png spec.png
    python3 tools/spectrogram.py --selftest

Mono-mixdown; 16/8/24/32-bit PCM WAV via the wave module. Other
formats report "not PCM WAV" -- ffmpeg/sndfile are the converters.
The falsifier is the picture itself: a flat-noise spectrogram means
the flag is not drawn in frequency; route back to lsb_scan /
dtmf_decode.
"""
import argparse
import json
import struct
import sys
import wave
import zlib

import numpy as np

RAMP = " .:-=+*#%@"


def _read_wav(path):
    w = wave.open(path, "rb")
    try:
        ch, sw, fr, n = (w.getnchannels(), w.getsampwidth(),
                         w.getframerate(), w.getnframes())
        raw = w.readframes(n)
    finally:
        w.close()
    if sw == 1:
        a = np.frombuffer(raw, np.uint8).astype(np.float64) - 128
    elif sw == 2:
        a = np.frombuffer(raw, "<i2").astype(np.float64)
    elif sw == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3)
        a = (b[:, 0].astype(np.int32)
             | (b[:, 1].astype(np.int32) << 8)
             | (b[:, 2].astype(np.int32) << 16))
        a = np.where(a >= 1 << 23, a - (1 << 24), a).astype(np.float64)
    elif sw == 4:
        a = np.frombuffer(raw, "<i4").astype(np.float64)
    else:
        raise ValueError("unsupported sample width %d" % sw)
    if ch > 1:
        a = a.reshape(-1, ch).mean(axis=1)
    return a, fr


def spectrogram(samples, rate, cols=100, rows=32, fmax=None):
    """Return (grid, freqs, times): grid[time][freq] in dB, normalised
    0..1 for rendering."""
    fmax = fmax or rate / 2
    n = len(samples)
    if n == 0:
        raise ValueError("empty audio")
    win = max(16, min(2048, n // max(cols, 1)))
    hop = max(1, (n - win) // max(cols - 1, 1))
    window = np.hanning(win)
    frames = []
    for i in range(cols):
        s = i * hop
        if s + win > n:
            pad = np.zeros(s + win - n)
            seg = np.concatenate([samples[s:], pad])
        else:
            seg = samples[s:s + win]
        frames.append(np.abs(np.fft.rfft(seg * window)))
    spec = np.array(frames).T            # [freq][time]
    fbins = np.fft.rfftfreq(win, 1.0 / rate)
    keep = fbins <= fmax
    spec = spec[keep]
    fbins = fbins[keep]
    # resample freq axis to `rows` bins (linear)
    if spec.shape[0] > rows:
        idx = np.linspace(0, spec.shape[0] - 1, rows).astype(int)
        spec = spec[idx]
        fbins = fbins[idx]
    with np.errstate(divide="ignore"):
        db = 20 * np.log10(spec + 1e-12)
    lo, hi = np.percentile(db[np.isfinite(db)], [5, 99.5]) \
        if np.isfinite(db).any() else (0, 1)
    grid = np.clip((db - lo) / (hi - lo + 1e-12), 0, 1)
    return grid, fbins, np.arange(spec.shape[1]) * hop / rate


def render_ascii(grid, freqs):
    """grid [freq][time] -> terminal rows, low freq at the bottom."""
    lines = []
    rows, cols = grid.shape
    for r in range(rows - 1, -1, -1):
        f = freqs[r] if r < len(freqs) else 0
        line = "".join(RAMP[min(int(v * (len(RAMP) - 1)),
                              len(RAMP) - 1)] for v in grid[r])
        lines.append("%6d |%s" % (int(f), line))
    return "\n".join(lines)


def write_png(path, grid):
    """Minimal grayscale PNG: grid [freq][time] floats -> 8-bit."""
    rows, cols = grid.shape
    img = np.flipud((grid * 255).astype(np.uint8))
    raw = b"".join(b"\x00" + img[r].tobytes() for r in range(rows))

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + \
            struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", cols, rows,
                                        8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


def _selftest():
    import tempfile, os
    rate, dur = 8000, 2
    t = np.arange(rate * dur) / rate
    # two tones: 800 Hz in first half, 3200 Hz in second half
    sig = np.zeros_like(t)
    half = len(t) // 2
    sig[:half] = np.sin(2 * np.pi * 800 * t[:half])
    sig[half:] = np.sin(2 * np.pi * 3200 * t[half:])
    pcm = (sig * 30000).astype("<i2")
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        w = wave.open(path, "wb")
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm.tobytes())
        w.close()
        a, fr = _read_wav(path)
        grid, freqs, _ = spectrogram(a, fr, cols=60, rows=24)
        assert grid.shape == (24, 60), grid.shape
        # energy in the right quadrants
        f800 = int(np.argmin(np.abs(freqs - 800)))
        f3200 = int(np.argmin(np.abs(freqs - 3200)))
        assert grid[f800, 15] > 0.8, grid[f800, 15]
        assert grid[f3200, 45] > 0.8, grid[f3200, 45]
        # the opposite quadrants stay quiet
        assert grid[f800, 45] < 0.3, grid[f800, 45]
        assert grid[f3200, 15] < 0.3, grid[f3200, 15]
        txt = render_ascii(grid, freqs)
        assert "#" in txt or "@" in txt
        pngp = path + ".png"
        write_png(pngp, grid)
        head = open(pngp, "rb").read(8)
        assert head == b"\x89PNG\r\n\x1a\n"
    finally:
        os.unlink(path)
        if os.path.exists(path + ".png"):
            os.unlink(path + ".png")
    print("spectrogram selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="terminal spectrogram "
                                 "for audio-stego")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--cols", type=int, default=100)
    ap.add_argument("--rows", type=int, default=32)
    ap.add_argument("--fmax", type=float,
                    help="max frequency shown (default Nyquist)")
    ap.add_argument("--png", help="also write a grayscale PNG here")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    try:
        samples, rate = _read_wav(a.file)
    except (wave.Error, EOFError) as exc:
        print(json.dumps({"ok": False, "note": "not PCM WAV: %s -- "
                          "convert with ffmpeg first" % exc}))
        return
    grid, freqs, times = spectrogram(samples, rate, a.cols, a.rows,
                                     a.fmax)
    print("# %s -- %d samples @ %d Hz, %d cols x %d rows, "
          "fmax %.0f Hz" % (a.file, len(samples), rate,
                            grid.shape[1], grid.shape[0],
                            freqs[-1] if len(freqs) else 0))
    print(render_ascii(grid, freqs))
    if a.png:
        write_png(a.png, grid)
        print("# wrote %s" % a.png)


if __name__ == "__main__":
    raise SystemExit(main())
