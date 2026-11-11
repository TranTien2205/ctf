#!/usr/bin/env python3
"""rtp_extract.py -- pull RTP streams out of a pcap and decode to WAV.

VoIP/audio misc challenges ship a capture whose RTP stream carries the
flag (DTMF tones, Morse, voice). tshark can do this, but when it is not
on the box: RTP over UDP has v=2 in the first two bits, a 12-byte
header, a payload type (0=PCMU, 8=PCMA are the audio classics), and a
sequence number. Group by SSRC, sort by seq (16-bit wrap), drop
duplicates, then audioop.ulaw2lin/alaw2lin -> 16-bit PCM -> .wav.

  python3 tools/forensics/rtp_extract.py call.pcap
  python3 tools/forensics/rtp_extract.py call.pcap --ssrc 0x1234 --out call.wav
  python3 tools/forensics/rtp_extract.py call.pcap --ssrc 0x1234 --raw out.raw
  python3 tools/forensics/rtp_extract.py --selftest

Unknown payload types are listed but written only as --raw bytes, never
silently "decoded". Non-RTP UDP is ignored.
"""
import argparse
import audioop
import json
import struct
import sys
import wave

PT_NAMES = {0: "PCMU/8000", 3: "GSM/8000", 8: "PCMA/8000", 9: "G722/8000",
            10: "L16/44100/st", 11: "L16/44100", 18: "G729/8000",
            96: "dynamic"}


def _pkts(data):
    """-> list of (is_udp, payload) from pcap or pcapng bytes."""
    out = []
    if data[:4] in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4"):
        e = "<" if data[:4] == b"\xd4\xc3\xb2\xa1" else ">"
        i = 24
        while i + 16 <= len(data):
            incl = struct.unpack(e + "I", data[i + 8:i + 12])[0]
            out.append(data[i + 16:i + 16 + incl])
            i += 16 + incl
    elif data[:4] == b"\x0a\x0d\x0d\x0a":
        i = 0
        while i + 12 <= len(data):
            blen = struct.unpack("<I", data[i + 4:i + 8])[0]
            if blen < 12 or i + blen > len(data):
                break
            if struct.unpack("<I", data[i:i + 4])[0] == 6:        # EPB
                incl = struct.unpack("<I", data[i + 20:i + 24])[0]
                out.append(data[i + 28:i + 28 + incl])
            i += blen
    frames = []
    for f in out:
        if len(f) < 14 or f[12:14] != b"\x08\x00":                # not IPv4
            continue
        ip = f[14:]
        if len(ip) < 20 or ip[9] != 17:                          # not UDP
            continue
        ihl = (ip[0] & 0xF) * 4
        udp = ip[ihl:]
        if len(udp) < 8:
            continue
        ulen = struct.unpack(">H", udp[4:6])[0]
        frames.append(udp[8:ulen] if ulen >= 8 else udp[8:])
    return frames


def _streams(data):
    """-> {ssrc: {"pt", "packets": [(seq, payload)], "lost", "rate"}}."""
    streams = {}
    for pay in _pkts(data):
        if len(pay) < 12 or pay[0] >> 6 != 2:
            continue
        cc, pt = pay[0] & 0xF, pay[1] & 0x7F
        hlen = 12 + cc * 4
        if pay[0] & 0x10:                                        # extension
            if len(pay) < hlen + 4:
                continue
            hlen += 4 + struct.unpack(">H", pay[hlen + 2:hlen + 4])[0] * 4
        if hlen >= len(pay):
            continue
        seq, ssrc = struct.unpack(">H", pay[2:4])[0], \
            struct.unpack(">I", pay[8:12])[0]
        st = streams.setdefault(ssrc, {"pt": pt, "packets": {}})
        st["packets"][seq] = pay[hlen:]
    for st in streams.values():
        seqs = sorted(st["packets"])
        span = (seqs[-1] - seqs[0]) % 65536 + 1 if seqs else 0
        st["first_seq"], st["count"] = seqs[0], len(seqs)
        st["lost"] = max(0, span - len(seqs))
        st["codec"] = PT_NAMES.get(st["pt"], "pt%d" % st["pt"])
        st["ordered"] = [st["packets"][s] for s in seqs]
        del st["packets"]
    return streams


def decode(st):
    pt, blob = st["pt"], b"".join(st["ordered"])
    if pt == 0:
        return audioop.ulaw2lin(blob, 2), 8000, 1, "PCMU"
    if pt == 8:
        return audioop.alaw2lin(blob, 2), 8000, 1, "PCMA"
    if pt == 11:
        return blob, 44100, 1, "L16"
    if pt == 10:
        return blob, 44100, 2, "L16-stereo"
    return None, None, None, "unsupported pt %d" % pt


def _selftest():
    import io
    payloads = [bytes([i & 0xFF]) * 160 for i in range(5)]
    pkts = b""
    for i, pl in enumerate(payloads):
        rtp = struct.pack(">BBHII", 0x80, 0, 100 + i, i * 160, 0xAABB) + pl
        udp = struct.pack(">HHHH", 4000, 4004, 8 + len(rtp), 0) + rtp
        ip = bytes([0x45, 0, 0, 20 + len(udp), 0, 0, 0, 0, 64, 17,
                    0, 0, 127, 0, 0, 1, 127, 0, 0, 1])
        f = b"\x00" * 12 + b"\x08\x00" + ip + udp
        pkts += struct.pack("<4I", 0, 0, len(f), len(f)) + f
    pcap = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1) + pkts
    sts = _streams(pcap)
    st = sts[0xAABB]
    assert st["count"] == 5 and st["lost"] == 0 and st["codec"] == "PCMU/8000"
    pcm, rate, ch, name = decode(st)
    assert name == "PCMU" and rate == 8000 and len(pcm) == 5 * 160 * 2
    w = io.BytesIO()
    with wave.open(w, "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    assert w.getvalue()[:4] == b"RIFF"
    print("rtp_extract selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="RTP stream extractor")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--ssrc", help="hex or decimal ssrc to extract")
    ap.add_argument("--out", help="write decoded WAV here")
    ap.add_argument("--raw", help="write concatenated payload bytes here")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("pcap path required")
    streams = _streams(open(a.path, "rb").read())
    if not (a.out or a.raw):
        print(json.dumps({hex(k): {kk: vv for kk, vv in v.items()
                                   if kk != "ordered"}
                          for k, v in streams.items()}, indent=1))
        return
    sel = int(a.ssrc, 0) if a.ssrc else \
        (max(streams, key=lambda k: streams[k]["count"]) if streams else None)
    if sel not in streams:
        print(json.dumps({"error": "no such ssrc",
                          "have": [hex(k) for k in streams]}))
        return 1
    st = streams[sel]
    if a.raw:
        open(a.raw, "wb").write(b"".join(st["ordered"]))
    if a.out:
        pcm, rate, ch, name = decode(st)
        if pcm is None:
            print(json.dumps({"error": name, "hint": "use --raw"}))
            return 1
        with wave.open(a.out, "wb") as wf:
            wf.setnchannels(ch)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(pcm)
    print(json.dumps({"ssrc": hex(sel), "codec": st["codec"],
                      "packets": st["count"], "lost": st["lost"],
                      "wrote": a.out or a.raw}))


if __name__ == "__main__":
    raise SystemExit(main())
