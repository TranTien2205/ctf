#!/usr/bin/env python3
"""Decode USB HID traffic from a pcap: keyboard reports to keystrokes,
mouse reports to movement. The 'usb.capdata' staple of CTF pcaps with
no tshark on the box.

  python3 tools/forensics/usb_hid.py capture.pcap keys
  python3 tools/forensics/usb_hid.py capture.pcap mouse
  python3 tools/forensics/usb_hid.py --raw hexfile.txt keys
  python3 tools/forensics/usb_hid.py --selftest

Reads classic pcap linktype 189 (USB_LINUX) or 220 (USB_LINUX_MMAPPED);
interrupt-in URBs carry the report in their trailing data. --raw takes
a text file of one hex report per line instead of a pcap.

Keyboard output is the typed stream: modifier byte honoured, releases
collapse, shifted symbols mapped. Output is what the bytes spell —
verify the flag-shaped run before trusting it, the tool decodes, it
does not guess.
"""
import argparse, json, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcap_parse import parse_pcap  # noqa: E402

KEYMAP = {i: c for i, c in enumerate("abcdefghijklmnopqrstuvwxyz", 4)}
KEYMAP.update({0x1E + i: c for i, c in enumerate("1234567890")})
KEYMAP.update({0x28: "\n", 0x2B: "\t", 0x2C: " ", 0x2A: "<bs>",
               0x29: "<esc>", 0x39: "<capslock>"})
KEYMAP.update({0x2D: "-", 0x2E: "=", 0x2F: "[", 0x30: "]", 0x31: "\\",
               0x33: ";", 0x34: "'", 0x35: "`", 0x36: ",", 0x37: ".",
               0x38: "/"})
SHIFTMAP = {"1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^",
            "7": "&", "8": "*", "9": "(", "0": ")", "-": "_", "=": "+",
            "[": "{", "]": "}", "\\": "|", ";": ":", "'": '"', "`": "~",
            ",": "<", ".": ">", "/": "?"}


def _reports_from_pcap(path):
    """Yield (ts, report-bytes) from interrupt-in URBs."""
    linktype, pkts, err = parse_pcap(path)
    if err:
        return None, err
    if linktype not in (189, 220):
        return None, "linktype %d is not USB (189/220) — this capture "
        "carries network traffic, not URBs" % linktype
    out = []
    for ts, data in pkts:
        if len(data) < 40:
            continue
        # URB header: .., urb_type @8, transfer_type @9, endpoint @10
        transfer = data[9]
        data_flag = data[13]
        dlen = struct.unpack("<I", data[36:40])[0]
        if transfer != 1 or not dlen:   # interrupt URB with payload
            continue
        payload = data[64:64 + dlen] if data_flag == 0 else b""
        if payload:
            out.append((ts, payload))
    return out, None


def _reports_from_raw(path):
    out = []
    with open(path, "r", errors="replace") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                continue
            try:
                out.append((i, bytes.fromhex(line)))
            except ValueError:
                return None, "line %d is not hex" % i
    return out, None


def keys(reports):
    """Decode 8-byte HID keyboard reports into a typed stream."""
    stream, presses = [], 0
    for _ts, rep in reports:
        if len(rep) < 8:
            continue
        mods = rep[0]
        shift = bool(mods & 0x22)
        for kc in rep[2:8]:
            if kc == 0:
                continue
            presses += 1
            c = KEYMAP.get(kc)
            if c is None:
                c = "<0x%02x>" % kc
            elif shift:
                c = SHIFTMAP.get(c, c.upper())
            stream.append(c)
    return {"stream": "".join(stream), "presses": presses,
            "note": "each report's key slots are emitted once; held keys "
                    "appear once per report so repeated chars may be a "
                    "held key — check raw if a run looks odd"}


def mouse(reports):
    """Decode HID mouse reports: buttons, dx, dy[, wheel] per report."""
    moves, clicks, pts = 0, 0, []
    for _ts, rep in reports:
        if len(rep) < 3:
            continue
        btn = rep[0]
        dx = struct.unpack("b", rep[1:2])[0]
        dy = struct.unpack("b", rep[2:3])[0]
        moves += 1
        if btn:
            clicks += 1
        pts.append([dx, dy, btn])
    return {"reports": moves, "button_events": clicks, "points": pts,
            "note": "points are [dx,dy,buttons]; dx>0 right, dy>0 down. "
                    "replay them as pen strokes if the capture drew a flag"}


def _selftest() -> int:
    import tempfile
    # synthetic pcap, linktype 189, one interrupt URB per keystroke
    def urb(report):
        hdr = bytearray(64)
        hdr[8] = 0x43           # urb_type 'C' (complete) — value unused
        hdr[9] = 1              # transfer_type interrupt
        hdr[10] = 0x81          # endpoint IN
        hdr[13] = 0             # data present
        struct.pack_into("<I", hdr, 36, len(report))
        return bytes(hdr) + report

    def rep(mods, key):
        return bytes([mods, 0, key, 0, 0, 0, 0, 0])

    typed = [rep(0, k) for k in (0x09, 0x0F, 0x04, 0x0A)]  # f l a g
    typed += [rep(2, 0x36), rep(0, 0x37)]                # { .  -> "{."
    typed[4] = rep(2, 0x2F)                              # shift+[ = {
    typed[5] = rep(2, 0x30)                              # shift+] = }
    pkts = [(float(i), urb(r)) for i, r in enumerate(typed)]
    gh = b"\xd4\xc3\xb2\xa1" + struct.pack("<HHIIII", 2, 4, 0, 0, 65535,
                                          189)
    body = b"".join(struct.pack("<IIII", int(t), 0, len(d), len(d)) + d
                    for t, d in pkts)
    with tempfile.NamedTemporaryFile("wb", suffix=".pcap",
                                     delete=False) as fh:
        fh.write(gh + body)
        path = fh.name
    try:
        reps, err = _reports_from_pcap(path)
        assert err is None, err
        out = keys(reps)
        assert out["stream"] == "flag{}", out
    finally:
        os.unlink(path)
    # raw mode: same reports from a hex file
    with tempfile.NamedTemporaryFile("w", suffix=".txt",
                                     delete=False) as fh:
        fh.write("\n".join(r.hex() for r in typed))
        rp = fh.name
    try:
        reps, _ = _reports_from_raw(rp)
        assert keys(reps)["stream"] == "flag{}"
    finally:
        os.unlink(rp)
    print("usb_hid selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src", nargs="?", help="pcap path (or file with --raw)")
    ap.add_argument("mode", nargs="?", choices=["keys", "mouse"],
                    default="keys")
    ap.add_argument("--raw", action="store_true",
                    help="src is a text file of hex reports, not a pcap")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.src:
        ap.error("a pcap path is required")
    reps, err = (_reports_from_raw if a.raw else _reports_from_pcap)(a.src)
    if err:
        print(json.dumps({"error": err}))
        return 1
    if not reps:
        print(json.dumps({"error": "no interrupt-in reports with data — "
                                   "check this capture actually carries "
                                   "HID traffic"}))
        return 1
    print(json.dumps((mouse if a.mode == "mouse" else keys)(reps),
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
