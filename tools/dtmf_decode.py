#!/usr/bin/env python3
"""dtmf_decode.py -- decode DTMF touch-tones from a WAV (dtmfcard fallback).

Usage:
  python3 tools/dtmf_decode.py dial.wav
  python3 tools/dtmf_decode.py dial.wav --frames
  python3 tools/dtmf_decode.py --selftest

Each DTMF symbol is the sum of one low-group tone (697/770/852/941
Hz) and one high-group tone (1209/1336/1477/1633 Hz). The decoder
slides a window over the PCM stream, scores all eight frequencies
with the Goertzel power estimator, picks the strongest low and
high, and collapses consecutive identical pairs into digits.
Supports PCM 8/16-bit, mono or interleaved channels; stereo is
mixed down. Phone-dial and number-station style challenges hand
you exactly this file shape.
"""
import argparse
import json
import math
import struct
import sys
import tempfile
import wave
from pathlib import Path

LOWS = [697, 770, 852, 941]
HIGHS = [1209, 1336, 1477, 1633]
KEYS = {"6971209": "1", "6971336": "2", "6971477": "3",
        "6971633": "A", "7701209": "4", "7701336": "5",
        "7701477": "6", "7701633": "B", "8521209": "7",
        "8521336": "8", "8521477": "9", "8521633": "C",
        "9411209": "*", "9411336": "0", "9411477": "#",
        "9411633": "D"}


def pcm(path):
    """-> (samples list of float -1..1, rate). 8/16-bit PCM WAV."""
    w = wave.open(str(path), "rb")
    nch, sw, rate, n = (w.getnchannels(), w.getsampwidth(),
                        w.getframerate(), w.getnframes())
    raw = w.readframes(n)
    w.close()
    if sw == 1:
        vals = [(b - 128) / 128 for b in raw]
    elif sw == 2:
        vals = [v / 32768 for v in
                struct.unpack(f"<{len(raw) // 2}h", raw)]
    else:
        raise ValueError(f"unsupported sample width {sw}")
    if nch > 1:
        vals = [sum(vals[i:i + nch]) / nch
                for i in range(0, len(vals), nch)]
    return vals, rate


def goertzel(xs, rate, freq):
    n = len(xs)
    k = round(n * freq / rate)
    coeff = 2 * math.cos(2 * math.pi * k / n)
    s0 = s1 = s2 = 0.0
    for x in xs:
        s0 = x + coeff * s1 - s2
        s2, s1 = s1, s0
    return s1 * s1 + s2 * s2 - coeff * s1 * s2


def decode(samples, rate, win_ms=40, hop_ms=20, thresh=0.02):
    win, hop = int(rate * win_ms / 1000), int(rate * hop_ms / 1000)
    seq, frames = [], []
    for st in range(0, len(samples) - win, hop):
        seg = samples[st:st + win]
        rms = math.sqrt(sum(x * x for x in seg) / win)
        if rms < thresh:
            frames.append({"t": st / rate, "digit": None})
            continue
        pl = {f: goertzel(seg, rate, f) for f in LOWS}
        ph = {f: goertzel(seg, rate, f) for f in HIGHS}
        lo, hi = max(pl, key=pl.get), max(ph, key=ph.get)
        key = f"{lo}{hi}"
        d = KEYS.get(key)
        frames.append({"t": st / rate, "digit": d,
                       "lo": lo, "hi": hi})
        if d and (not seq or seq[-1]["digit"] != d):
            seq.append({"digit": d, "t": st / rate})
    return {"digits": "".join(s["digit"] for s in seq),
            "sequence": seq, "frames": frames}


def _selftest():
    rate, tone_dur, gap = 8000, 0.12, 0.05
    inv = {"1": (697, 1209), "4": (770, 1209), "7": (852, 1209),
           "*": (941, 1209), "0": (941, 1336), "#": (941, 1477)}
    samples = []
    for ch in "147*0#":
        lo, hi = inv[ch]
        n = int(rate * tone_dur)
        samples += [0.4 * (math.sin(2 * math.pi * lo * i / rate)
                           + math.sin(2 * math.pi * hi * i / rate))
                    for i in range(n)]
        samples += [0.0] * int(rate * gap)
    tmp = Path(tempfile.mkdtemp()) / "d.wav"
    w = wave.open(str(tmp), "wb")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(rate)
    w.writeframes(struct.pack(f"<{len(samples)}h",
                              *[int(x * 32767) for x in samples]))
    w.close()
    vals, r = pcm(tmp)
    res = decode(vals, r)
    assert res["digits"] == "147*0#", res["digits"]
    print("dtmf_decode selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="decode DTMF digits from a WAV")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--frames", action="store_true",
                    help="emit per-frame analysis, not just digits")
    ap.add_argument("--thresh", type=float, default=0.02)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    vals, rate = pcm(a.file)
    res = decode(vals, rate, thresh=a.thresh)
    if not a.frames:
        res.pop("frames")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
