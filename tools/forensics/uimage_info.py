#!/usr/bin/env python3
"""uimage_info.py -- u-boot legacy uImage header + payload extract.

Firmware handouts ship uImage kernels/ramdisks. The 64-byte
big-endian header (magic 0x27051956) names os/arch/type/compression
and carries the data size and two CRC32s. FIT images are a different
format (FDT blob, magic d00dfeed) -- those route to dtb_dump.

    python3 tools/forensics/uimage_info.py kernel.uimg
    python3 tools/forensics/uimage_info.py kernel.uimg --extract kernel.gz
    python3 tools/forensics/uimage_info.py --selftest
"""
import argparse
import gzip
import json
import lzma
import struct
import sys
import zlib

MAGIC = 0x27051956

OS = {1: "openbsd", 2: "netbsd", 3: "freebsd", 4: "4_4bsd", 5: "linux",
      6: "svr4", 7: "esix", 8: "solaris", 9: "irix", 10: "sco",
      11: "dell", 12: "ncr", 13: "lynxos", 14: "vxworks", 15: "psos",
      16: "qnx", 17: "u-boot", 18: "rtems", 21: "integrity",
      23: "plan9", 24: "openrtos", 25: "arm-trusted-firmware",
      26: "tee", 27: "opensbi", 28: "efi"}
ARCH = {1: "alpha", 2: "arm", 3: "i386", 4: "ia64", 5: "mips",
        6: "mips64", 7: "ppc", 8: "s390", 9: "sh", 10: "sparc",
        11: "sparc64", 12: "m68k", 14: "microblaze", 15: "nios2",
        16: "blackfin", 17: "avr32", 18: "stv8100", 20: "or1k",
        21: "aarch64", 22: "arm64", 23: "arc", 24: "x86_64",
        25: "xtensa", 26: "riscv", 27: "riscv64", 28: "loongarch"}
TYPE = {1: "standalone", 2: "kernel", 3: "ramdisk", 4: "multi",
        5: "firmware", 6: "script", 7: "filesystem", 8: "flatdt",
        9: "kwbimage", 10: "imximage", 11: "ublimage", 12: "omapimage",
        13: "aisimage", 14: "kernel_noload", 15: "pblimage",
        16: "mxsimage", 17: "gpimage", 18: "atmelimage",
        19: "x86_setup", 20: "riscv", 24: "sunxi_toc0"}
COMP = {0: "none", 1: "gzip", 2: "bzip2", 3: "lzma", 4: "lzo",
        5: "lz4", 6: "zstd"}


def parse(data: bytes):
    if len(data) < 64:
        return {"ok": False, "error": "file shorter than 64-byte "
                "uImage header"}
    magic, hcrc, ts, size, load, ep, dcrc = struct.unpack(">7I",
                                                         data[:28])
    if magic != MAGIC:
        if data[:4] == b"\xd0\x0d\xfe\xed":
            return {"ok": False,
                    "error": "FDT magic -- this is a FIT/DTB image; "
                    "route to tools/forensics/dtb_dump.py"}
        return {"ok": False, "error": f"bad magic "
                f"{data[:4].hex()} (want 27051956)"}
    os_t, arch, typ, comp = data[28], data[29], data[30], data[31]
    name = data[32:64].split(b"\x00")[0].decode("utf-8", "replace")
    out = {"ok": True, "name": name, "timestamp": ts,
           "data_size": size, "load_addr": hex(load),
           "entry_point": hex(ep),
           "os": OS.get(os_t, f"unknown-{os_t}"),
           "arch": ARCH.get(arch, f"unknown-{arch}"),
           "type": TYPE.get(typ, f"unknown-{typ}"),
           "compression": COMP.get(comp, f"unknown-{comp}"),
           "header_crc_ok": zlib.crc32(data[:4] + b"\x00" * 4 +
                                      data[8:64]) & 0xFFFFFFFF
           == hcrc}
    if len(data) >= 64 + size:
        out["data_crc_ok"] = zlib.crc32(data[64:64 + size]) \
            & 0xFFFFFFFF == dcrc
        out["trailing"] = len(data) - 64 - size
    else:
        out["data_crc_ok"] = None
        out["error"] = (f"file truncated: need {size} data bytes, "
                        f"have {max(0, len(data) - 64)}")
    return out


def extract(data: bytes):
    size = struct.unpack(">I", data[12:16])[0]
    payload = data[64:64 + size]
    comp = data[31]
    if comp == 1:
        return gzip.decompress(payload)
    if comp == 3:
        return lzma.decompress(payload)
    if comp in (2, 4, 5, 6):
        raise NotImplementedError(
            f"{COMP.get(comp)} compression has no stdlib decoder -- "
            "extract raw and use an external tool")
    return payload


def _selftest():
    # build a tiny uImage: gzipped "flag{uimage}" payload
    payload = gzip.compress(b"flag{uimage}")
    name = b"Linux-5.4".ljust(32, b"\x00")
    hdr = struct.pack(">7I", MAGIC, 0, 1700000000, len(payload),
                      0x8000, 0x8000, zlib.crc32(payload) & 0xFFFFFFFF)
    hdr += bytes([5, 2, 2, 1]) + name
    hdr = hdr[:4] + struct.pack(">I",
                                zlib.crc32(hdr[:4] + b"\x00" * 4 +
                                           hdr[8:64]) & 0xFFFFFFFF) \
        + hdr[8:]
    img = hdr + payload
    info = parse(img)
    assert info["ok"] and info["name"] == "Linux-5.4", info
    assert info["os"] == "linux" and info["arch"] == "arm"
    assert info["type"] == "kernel" and info["compression"] == "gzip"
    assert info["header_crc_ok"] and info["data_crc_ok"]
    assert extract(img) == b"flag{uimage}"
    bad = parse(b"\x00" * 64)
    assert not bad["ok"] and "bad magic" in bad["error"]
    print("uimage_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="u-boot uImage header "
                                 "parser + payload extract")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--extract", metavar="OUT",
                    help="write the payload (decompressed when "
                    "gzip/lzma) to OUT")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    data = open(a.file, "rb").read()
    info = parse(data)
    print(json.dumps(info, indent=1))
    if a.extract and info.get("ok"):
        open(a.extract, "wb").write(extract(data))
        print(f"[+] payload -> {a.extract}")


if __name__ == "__main__":
    raise SystemExit(main())
