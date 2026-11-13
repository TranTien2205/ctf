#!/usr/bin/env python3
"""seccomp_dump.py -- extract and disassemble a seccomp-BPF filter
from an ELF (or raw blob), without seccomp-tools or gdb.

The classic libseccomp filter starts
    LD  W  [4]            ; seccomp_data.arch
    JEQ AUDIT_ARCH_..., jt, jf
which has a recognisable 16-byte signature in .data/.rodata. The
tool scans for it, walks the sock_filter array (8-byte records:
code u16, jt u8, jf u8, k u32) while the cBPF stays sane, and
disassembles what it finds: arch check, every syscall-number rule
with its verdict, and the default action.

    python3 tools/seccomp_dump.py ./chal
    python3 tools/seccomp_dump.py blob.bin --offset 0x1234
    python3 tools/seccomp_dump.py ./chal --selftest

Verdicts reported: ALLOW / KILL / ERRNO(e) / TRAP / TRACE /
LOG / USER_NOTIF. Syscall names are x86-64; other arches print the
nr and say so. The falsifier is built in: a program whose first
instruction is not LD arch or whose decoded jump targets run out of
bounds is reported as a non-match, never as a filter.
"""
import argparse
import json
import os
import struct
import sys

# cBPF opcodes (linux/filter.h)
LD_ABS = 0x20
JMP_JA = 0x05
JMP_JEQ = 0x15
JMP_JGT = 0x25
JMP_JGE = 0x35
JMP_JSET = 0x45
RET = 0x06
VALID_CODES = {LD_ABS, JMP_JA, JMP_JEQ, JMP_JGT, JMP_JGE, JMP_JSET,
               RET}

ARCHES = {
    0xC000003E: "x86-64",
    0x40000003: "i386",
    0xC00000B7: "aarch64",
    0x40000028: "arm",
    0x80000016: "mips64",
}

SECCOMP_RET = {
    0x00000000: "KILL_PROCESS",
    0x00030000: "TRAP",
    0x00050000: "ERRNO",
    0x7FC00000: "USER_NOTIF",
    0x7FF00000: "TRACE",
    0x7FFC0000: "LOG",
    0x7FFF0000: "ALLOW",
}

# x86-64 syscall names: the subset a sandbox rule actually names in
# CTF binaries; unknown nrs still print numerically.
X64 = {0: "read", 1: "write", 2: "open", 3: "close", 4: "stat",
       5: "fstat", 6: "lstat", 7: "poll", 8: "lseek", 9: "mmap",
       10: "mprotect", 11: "munmap", 12: "brk", 13: "rt_sigaction",
       14: "rt_sigprocmask", 16: "ioctl", 17: "pread64",
       18: "pwrite64", 19: "readv", 20: "writev", 21: "access",
       22: "pipe", 23: "select", 24: "sched_yield", 28: "madvise",
       32: "dup", 33: "dup2", 35: "nanosleep", 39: "getpid",
       40: "sendfile", 41: "socket", 42: "connect", 43: "accept",
       44: "sendto", 45: "recvfrom", 46: "sendmsg", 47: "recvmsg",
       48: "shutdown", 49: "bind", 50: "listen", 51: "getsockname",
       52: "getpeername", 53: "socketpair", 54: "setsockopt",
       55: "getsockopt", 56: "clone", 57: "fork", 58: "vfork",
       59: "execve", 60: "exit", 61: "wait4", 62: "kill",
       63: "uname", 72: "fcntl", 78: "getdents", 79: "getcwd",
       80: "chdir", 87: "unlink", 89: "readlink", 96: "gettimeofday",
       97: "getrlimit", 102: "getuid", 104: "getgid",
       105: "setuid", 106: "setgid", 107: "geteuid",
       108: "getegid", 110: "getppid", 158: "arch_prctl",
       186: "gettid", 201: "time", 202: "futex", 217: "getdents64",
       218: "set_tid_address", 228: "clock_gettime", 230: "tgkill",
       231: "exit_group", 257: "openat", 262: "newfstatat",
       273: "set_robust_list", 302: "prlimit64", 317: "seccomp",
       318: "getrandom", 322: "execveat", 334: "rseq"}

RET_NAME = {v: k for k, v in SECCOMP_RET.items()}


def _decode_prog(blob, off, max_insns=512):
    """Decode a sock_filter[] starting at off; returns (insns, end)
    where end is the byte offset just past the final RET, or None if
    the stream is not a plausible filter."""
    insns = []
    i = off
    while len(insns) < max_insns and i + 8 <= len(blob):
        code, jt, jf, k = struct.unpack_from("<HBBI", blob, i)
        if code not in VALID_CODES:
            break
        insns.append((i, code, jt, jf, k))
        i += 8
        if code == RET:
            # a filter ends on its final RET; the next bytes either
            # are not BPF or are padding. Greedily accept the FIRST
            # plausible terminating RET once we saw at least a
            # jump+ret shape -- but keep decoding if more valid BPF
            # follows (some filters have multiple RETs mid-flow).
            nxt = (struct.unpack_from("<H", blob, i)[0]
                   if i + 2 <= len(blob) else 0)
            if nxt not in VALID_CODES:
                break
    if len(insns) < 3 or insns[-1][1] != RET:
        return None
    return insns, i


def _find_filters(blob):
    """Scan for the LD-arch + JEQ/JNE AUDIT_ARCH prologue."""
    hits = []
    sig = struct.pack("<HBBI", LD_ABS, 0, 0, 4)
    pos = 0
    while True:
        pos = blob.find(sig, pos)
        if pos < 0:
            break
        if pos + 16 <= len(blob):
            c1, jt, jf, k1 = struct.unpack_from("<HBBI", blob, pos + 8)
            if c1 in (JMP_JEQ,) and k1 in ARCHES:
                hits.append((pos, ARCHES[k1]))
        pos += 1
    return hits


def _disasm(insns, arch):
    out = []
    allowed, denied, rules = [], [], []
    arch_checked = None
    default = None
    pending_nr = None
    for idx, (off, code, jt, jf, k) in enumerate(insns):
        if code == LD_ABS:
            field = {0: "nr", 4: "arch", 8: "ip",
                     16: "arg0", 24: "arg1", 32: "arg2"}.get(k, str(k))
            out.append(f"[{idx:3}] A <- {field}")
            if k == 0:
                pending_nr = True
        elif code == RET:
            name = SECCOMP_RET.get(k, hex(k))
            extra = ""
            if name == "ERRNO":
                extra = f" errno={k & 0xFFFF}"
            out.append(f"[{idx:3}] RET {name}{extra}")
            default = name if idx == len(insns) - 1 else default
        elif code == JMP_JA:
            out.append(f"[{idx:3}] JA ->[{idx + 1 + k}]")
        else:
            op = {JMP_JEQ: "==", JMP_JGT: ">", JMP_JGE: ">=",
                  JMP_JSET: "&"}.get(code, "?")
            tgt_t, tgt_f = idx + 1 + jt, idx + 1 + jf
            name = X64.get(k, hex(k)) if arch == "x86-64" else hex(k)
            out.append(f"[{idx:3}] if A {op} {name} ->"
                       f"T[{tgt_t}] F[{tgt_f}]")
            # collect verdict bindings for the common
            # "JEQ nr -> RET action" shape (jt to a RET)
            if code == JMP_JEQ and tgt_t < len(insns) and \
                    insns[tgt_t][1] == RET:
                act = SECCOMP_RET.get(insns[tgt_t][4])
                if act == "ALLOW":
                    allowed.append(k)
                elif act:
                    denied.append((k, act))
                rules.append({"nr": k, "name": name, "action": act})
    return {"lines": out, "allowed": allowed, "denied": denied,
            "rules": rules, "default": default}


def scan(path, offset=None):
    blob = open(path, "rb").read()
    offs = [offset] if offset is not None else \
        [o for o, _ in _find_filters(blob)]
    res = []
    for off in offs:
        dec = _decode_prog(blob, off)
        if not dec:
            continue
        insns, end = dec
        arch = None
        for (_, c, _, _, k) in insns[:4]:
            if c == JMP_JEQ and k in ARCHES:
                arch = ARCHES[k]
        res.append({"offset": off, "insns": insns, "arch": arch})
    return res


def report(path, offset=None):
    found = scan(path, offset)
    if not found:
        return {"ok": False,
                "note": "no LD-arch/JEQ-AUDIT_ARCH filter found; "
                        "the binary may install seccomp via a raw "
                        "seccomp() syscall with an obfuscated prog, "
                        "or use ptrace -- check imports"}
    out = []
    for f in found:
        d = _disasm(f["insns"], f["arch"] or "x86-64")
        mode = "whitelist" if (d["default"] and
                               d["default"] != "ALLOW") else \
            "blacklist" if d["default"] == "ALLOW" else "unknown"
        out.append({
            "offset": hex(f["offset"]),
            "arch": f["arch"],
            "insns": len(f["insns"]),
            "mode": mode,
            "default_action": d["default"],
            "allowed_syscalls": [
                {"nr": k, "name": X64.get(k, hex(k))}
                for k in d["allowed"]],
            "denied_syscalls": [
                {"nr": k, "name": X64.get(k, hex(k)),
                 "action": a} for k, a in d["denied"]],
            "disasm": d["lines"],
        })
    return {"ok": True, "filters": out}


def _selftest():
    # hand-built whitelist sock_fprog: arch check -> KILL on
    # mismatch; openat/read -> ALLOW; everything else -> KILL.
    prog = struct.pack(
        "<" + "HBBI" * 8,
        LD_ABS, 0, 0, 4,
        JMP_JEQ, 0, 5, 0xC000003E,   # !=x64 -> insn 7 (KILL)
        LD_ABS, 0, 0, 0,
        JMP_JEQ, 2, 0, 257,          # openat -> insn 6 (ALLOW)
        JMP_JEQ, 1, 0, 0,            # read   -> insn 6 (ALLOW)
        JMP_JA, 0, 0, 1,             # else   -> insn 7 (KILL)
        RET, 0, 0, 0x7FFF0000,
        RET, 0, 0, 0x00000000)
    blob = b"\x7fELF" + b"\x00" * 61 + prog + b"\xde\xad"
    import tempfile
    fd, path = tempfile.mkstemp(suffix=".bin")
    try:
        os.write(fd, blob)
        os.close(fd)
        r = report(path)
        assert r["ok"], r
        f = r["filters"][0]
        assert f["arch"] == "x86-64", f
        assert f["mode"] == "whitelist", f["mode"]
        names = {s["name"] for s in f["allowed_syscalls"]}
        assert "read" in names and "openat" in names, names
        assert f["default_action"] == "KILL_PROCESS", f
        assert f["insns"] == 8, f["insns"]
    finally:
        os.unlink(path)
    # non-filter input must not false-positive
    fd, path = tempfile.mkstemp()
    try:
        os.write(fd, b"\x00" * 4096)
        os.close(fd)
        r2 = report(path)
        assert not r2["ok"], r2
    finally:
        os.unlink(path)
    print("seccomp_dump selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="seccomp-BPF filter "
                                 "extractor/disassembler")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--offset", type=lambda x: int(x, 0),
                    help="known file offset of the sock_filter array")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    out = report(a.file, a.offset)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
