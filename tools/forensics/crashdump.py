#!/usr/bin/env python3
"""crashdump.py -- Windows crash dump (*.dmp) header inventory.

DFIR bundles ship minidumps/kernel dumps and ask "why did it crash"
or "what was loaded". volatility handles full memory analysis; this
answers the header questions without it: signature (PAGE + DU64 /
DUMP / FDMP marker), machine type, bugcheck code and its four
parameters, and the kernel pointer fields (DTB, PFN database,
PsLoadedModuleList, PsActiveProcessHead) a deeper tool consumes.

The documented header fields stop at the bugcheck parameters --
the PHYSICAL_MEMORY_DESCRIPTOR offset varies by dump flavour, so
this tool does not guess it. For content, `ioc_scan --utf16` on the
file itself covers strings/URLs/credentials.

  python3 tools/forensics/crashdump.py memory.dmp
  python3 tools/forensics/crashdump.py --selftest
"""
import argparse
import json
import struct

DUMP_KIND = {"DU64": "kernel/full (64-bit)", "DUMP": "kernel/full (32-bit)"}
MACHINE = {0x8664: "x64", 0x014C: "x86", 0xAA64: "arm64", 0x0200: "ia64"}
BUGCHECK = {
    0x01: "APC_INDEX_MISMATCH", 0x0A: "IRQL_NOT_LESS_OR_EQUAL",
    0x1E: "KMODE_EXCEPTION_NOT_HANDLED",
    0x24: "NTFS_FILE_SYSTEM",
    0x3B: "SYSTEM_SERVICE_EXCEPTION",
    0x50: "PAGE_FAULT_IN_NONPAGED_AREA",
    0x7E: "SYSTEM_THREAD_EXCEPTION_NOT_HANDLED",
    0xC2: "BAD_POOL_CALLER", 0xD1: "DRIVER_IRQL_NOT_LESS_OR_EQUAL",
    0xEF: "CRITICAL_PROCESS_DIED",
    0xF7: "DRIVER_OVERRAN_STACK_BUFFER",
    0x100: "KERNEL_MODE_EXCEPTION_NOT_HANDLED",
    0x109: "CRITICAL_STRUCTURE_CORRUPTION",
    0x116: "VIDEO_TDR_FAILURE",
    0x119: "VIDEO_SCHEDULER_INTERNAL_ERROR",
    0x133: "DPC_WATCHDOG_VIOLATION",
    0x139: "KERNEL_SECURITY_CHECK_FAILURE",
    0x13A: "KERNEL_MODE_HEAP_CORRUPTION",
    0x143: "DPC_WATCHDOG_VIOLATION (processor)",
    0x154: "UNEXPECTED_STORE_EXCEPTION",
    0x1A0: "KERNEL_SECURITY_CHECK_FAILURE / WIN32K",
    0xC0000218: "STATUS_CANNOT_LOAD_REGISTRY_FILE",
}


def _q(d, o):
    return struct.unpack("<Q", d[o:o + 8])[0]


def _i(d, o):
    return struct.unpack("<I", d[o:o + 4])[0]


def parse(data):
    if data[:4] == b"MDMP" and len(data) >= 16:
        return {"kind": "minidump", "signature_valid": True,
                "version": "0x%x" % _i(data, 4),
                "streams": _i(data, 8),
                "stream_dir_rva": _i(data, 12),
                "note": "stream dir lists modules/memory/exception "
                        "streams; pair with ioc_scan --utf16"}
    if len(data) < 0x60 or data[:4] != b"PAGE":
        return {"error": "not a crash dump (PAGE/MDMP signature missing)"}
    marker = data[4:8].decode("latin-1")
    out = {"kind": DUMP_KIND.get(marker, marker),
           "signature_valid": marker in DUMP_KIND}
    if marker not in DUMP_KIND:
        out["warning"] = "unrecognised dump marker %r" % marker
        return out
    out["version"] = "%d.%d" % (_i(data, 8), _i(data, 12))
    out["directory_table_base"] = "0x%x" % _q(data, 0x10)
    out["pfn_database"] = "0x%x" % _q(data, 0x18)
    out["ps_loaded_module_list"] = "0x%x" % _q(data, 0x20)
    out["ps_active_process_head"] = "0x%x" % _q(data, 0x28)
    mt = _i(data, 0x30)
    out["machine"] = MACHINE.get(mt, "0x%x" % mt)
    out["processors"] = _i(data, 0x34)
    bc = _i(data, 0x38)
    out["bugcheck_code"] = "0x%x" % bc
    out["bugcheck_name"] = BUGCHECK.get(bc, "unknown")
    out["bugcheck_params"] = ["0x%x" % _q(data, 0x40 + 8 * i)
                            for i in range(4)]
    return out


def _selftest():
    d = bytearray(0x2000)
    d[:8] = b"PAGEDU64"
    struct.pack_into("<II", d, 8, 10, 0x19041)
    struct.pack_into("<QQQQ", d, 0x10, 0x1aa000, 0xfffff800, 0, 0)
    struct.pack_into("<III", d, 0x30, 0x8664, 8, 0x139)
    struct.pack_into("<QQQQ", d, 0x40, 3, 0xdeadbeef, 0, 0)
    out = parse(bytes(d))
    assert out["machine"] == "x64", out
    assert out["bugcheck_code"] == "0x139"
    assert out["bugcheck_name"] == "KERNEL_SECURITY_CHECK_FAILURE"
    assert out["bugcheck_params"][1] == "0xdeadbeef"
    assert out["signature_valid"]
    m = bytearray(64)
    m[:4] = b"MDMP"
    struct.pack_into("<III", m, 4, 0xA793, 12, 0x400)
    out2 = parse(bytes(m))
    assert out2["streams"] == 12 and "minidump" in out2["kind"]
    assert parse(b"junk")["error"]
    print("crashdump selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="Windows crash dump hdr")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    print(json.dumps(parse(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
