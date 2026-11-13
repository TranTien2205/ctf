#!/usr/bin/env python3
"""vhdx_read.py -- VHDX dynamic disk reader (MS-VHDX layout).

Completes the VM-image set (`qcow2_read`, `vhd_read`, `vmdk_info`,
`e01_read`): VHDX is the current Hyper-V format and what Windows VMs
ship as. Layout: `vhdxfile` identifier, two 64KB `head` headers at
64K/128K (only the higher-sequence one is live), a `regi` region
table at 192K naming the BAT and Metadata regions, a `metadata`
table giving block size + virtual disk size + sector sizes, then a
BAT of u64 entries -- state in bits 0-2 (6=fully present), file
offset in megabytes in bits 20-63. Sector-bitmap entries interleave
one per `chunk_ratio` (2^23 / logical_sector_size) payload blocks --
the block b BAT index is `b + b // chunk_ratio`.

Unmapped/partial blocks are reported, not fabricated: reads return
zeroes for them only with a `note` marking which ranges were sparse.

  python3 tools/forensics/vhdx_read.py disk.vhdx info
  python3 tools/forensics/vhdx_read.py disk.vhdx read 0 512 --hex
  python3 tools/forensics/vhdx_read.py disk.vhdx --selftest
"""
import argparse
import json
import struct

BAT_GUID = bytes.fromhex("6677c22d23f600429d64115e9bfd4a08")
META_GUID = bytes.fromhex("06a27c8b90479a4bb8fe575f050f886e")
ITEM_FILE_PARAMS = bytes.fromhex("3767a1ca36fa434db3b633f0aa44e76b")
ITEM_DISK_SIZE = bytes.fromhex("2442a52f1bcd7648b2115dbed83bf4b8")
ITEM_LSS = bytes.fromhex("1dbf41816fa90947ba47f233a8faab5f")
ITEM_PSS = bytes.fromhex("c748a3cd5d4471449cc9e9885251c556")
BAT_STATE = {0: "not_present", 1: "undefined", 2: "zero",
             3: "unmapped", 6: "fully_present", 7: "partially_present"}


def _info(data):
    if data[:8] != b"vhdxfile":
        return {"error": "not a VHDX (vhdxfile signature missing)"}
    out = {}
    # headers at 64K/128K: pick higher sequence
    best = None
    for off in (0x10000, 0x20000):
        if data[off:off + 4] == b"head" and off + 0x40 <= len(data):
            seq, = struct.unpack("<Q", data[off + 8:off + 16])
            if best is None or seq > best[0]:
                best = (seq, off)
    out["live_header"] = None if best is None else hex(best[1])
    # region table at 192K
    if data[0x30000:0x30004] != b"regi":
        out["error"] = "no regi region table at 0x30000"
        return out
    nreg, = struct.unpack("<I", data[0x30008:0x3000C])
    regions = {}
    for i in range(min(nreg, 32)):
        e = 0x30010 + i * 32
        guid = data[e:e + 16]
        foff, rlen, req = struct.unpack("<QII", data[e + 16:e + 32])
        regions[guid] = {"file_offset": foff, "length": rlen,
                         "required": bool(req)}
    out["regions"] = {"bat": regions.get(BAT_GUID),
                      "metadata": regions.get(META_GUID)}
    mo = regions.get(META_GUID)
    if mo:
        m = data[mo["file_offset"]:mo["file_offset"] + mo["length"]]
        if m[:8] == b"metadata":
            nent, = struct.unpack("<H", m[10:12])
            items = {}
            for i in range(min(nent, 32)):
                e = 32 + i * 32
                iid = m[e:e + 16]
                ioff, ilen = struct.unpack("<II", m[e + 16:e + 24])
                items[iid] = m[ioff:ioff + ilen]
            if ITEM_FILE_PARAMS in items:
                bs, fl = struct.unpack("<II", items[ITEM_FILE_PARAMS][:8])
                out["block_size"] = bs
                out["leave_sectors_unallocated"] = bool(fl & 1)
            if ITEM_DISK_SIZE in items:
                out["virtual_size"], = struct.unpack(
                    "<Q", items[ITEM_DISK_SIZE][:8])
            if ITEM_LSS in items:
                out["logical_sector_size"], = struct.unpack(
                    "<I", items[ITEM_LSS][:4])
            if ITEM_PSS in items:
                out["physical_sector_size"], = struct.unpack(
                    "<I", items[ITEM_PSS][:4])
    bo = regions.get(BAT_GUID)
    if bo and "block_size" in out:
        lss = out.get("logical_sector_size", 512)
        out["chunk_ratio"] = (1 << 23) // lss
        vsize = out.get("virtual_size", 0)
        out["bat_entries"] = (vsize // out["block_size"]
                              if vsize else None)
    return out


def _read(data, info, voff, length):
    bat = info.get("regions", {}).get("bat")
    bs = info.get("block_size")
    if not bat or not bs:
        raise ValueError("no BAT region or block size")
    ratio = info["chunk_ratio"]
    out = bytearray()
    sparse = []
    pos = 0
    while pos < length:
        g = voff + pos
        blk = g // bs
        inblk = g % bs
        take = min(bs - inblk, length - pos)
        idx = blk + blk // ratio
        eoff = bat["file_offset"] + idx * 8
        if eoff + 8 > len(data):
            sparse.append((g, take, "beyond_bat"))
            out += b"\x00" * take
        else:
            ent, = struct.unpack("<Q", data[eoff:eoff + 8])
            state = ent & 7
            foff = (ent >> 20) << 20
            if state in (6, 7) and foff + inblk + take <= len(data):
                out += data[foff + inblk:foff + inblk + take]
                if state == 7:
                    sparse.append((g, take, "partially_present"))
            else:
                sparse.append((g, take, BAT_STATE.get(state, str(state))))
                out += b"\x00" * take
        pos += take
    return bytes(out), sparse


def _selftest():
    img = bytearray(0x400000)
    img[:8] = b"vhdxfile"
    img[0x10000:0x10004] = b"head"
    struct.pack_into("<Q", img, 0x10008, 1)     # seq
    img[0x20000:0x20004] = b"head"
    struct.pack_into("<Q", img, 0x20008, 2)     # live: higher seq
    # region table
    img[0x30000:0x30004] = b"regi"
    struct.pack_into("<I", img, 0x30008, 2)
    bat_off, meta_off = 0x100000, 0x180000
    img[0x30010:0x30010 + 16] = BAT_GUID
    struct.pack_into("<QII", img, 0x30020, bat_off, 0x4000, 1)
    img[0x30030:0x30030 + 16] = META_GUID
    struct.pack_into("<QII", img, 0x30040, meta_off, 0x4000, 1)
    # metadata
    img[meta_off:meta_off + 8] = b"metadata"
    struct.pack_into("<H", img, meta_off + 10, 4)
    items = [(ITEM_FILE_PARAMS, struct.pack("<II", 0x200000, 0)),
             (ITEM_DISK_SIZE, struct.pack("<Q", 0x200000 * 4)),
             (ITEM_LSS, struct.pack("<I", 512)),
             (ITEM_PSS, struct.pack("<I", 512))]
    for i, (iid, blob) in enumerate(items):
        e = meta_off + 32 + i * 32
        img[e:e + 16] = iid
        ioff = meta_off + 32 + 4 * 32 + i * 16
        struct.pack_into("<II", img, e + 16, ioff - meta_off, len(blob))
        img[ioff:ioff + len(blob)] = blob
    # BAT: block0 present at 0x300000, block1 unmapped
    payload = b"flag{vhdx_blk}" + b"\x00" * (0x200000 - 14)
    img[0x300000:0x300000 + len(payload)] = payload
    struct.pack_into("<Q", img, bat_off,
                     ((0x300000 >> 20) << 20) | 6)
    struct.pack_into("<Q", img, bat_off + 8, 0)   # block1 not present
    info = _info(bytes(img))
    assert info["live_header"] == "0x20000", info
    assert info["block_size"] == 0x200000
    assert info["virtual_size"] == 0x800000
    assert info["chunk_ratio"] == 16384
    body, sparse = _read(bytes(img), info, 0, 64)
    assert body[:14] == b"flag{vhdx_blk}", body[:14]
    body, sparse = _read(bytes(img), info, 0x200000, 64)
    assert body == b"\x00" * 64 and sparse, sparse
    print("vhdx_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="VHDX disk reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("cmd", nargs="?", default="info",
                    choices=["info", "read"])
    ap.add_argument("off", nargs="?", type=lambda x: int(x, 0), default=0)
    ap.add_argument("length", nargs="?", type=lambda x: int(x, 0),
                    default=512)
    ap.add_argument("--hex", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    info = _info(data)
    if a.cmd == "info":
        print(json.dumps(info, indent=1, default=str))
        return
    body, sparse = _read(data, info, a.off, a.length)
    print(json.dumps({"offset": a.off, "length": a.length,
                      "sparse_ranges": sparse,
                      "data": body.hex() if a.hex else
                      body.decode("utf-8", "replace")}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
