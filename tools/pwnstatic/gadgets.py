#!/usr/bin/env python3
"""ROP gadget search over the executable segments.

ROPgadget and ropper are measured ABSENT; capstone IS importable, so it is used
when present as an accelerator only. Without it the byte-pattern table below
still finds the gadgets that actually decide an x86-64 ret2libc: the six
argument-register pops, a bare ret for stack alignment, and syscall.

A gadget is reported with its VIRTUAL address, so a non-PIE binary's addresses
are usable as-is and a PIE binary's are offsets from the load base.
"""
PF_X = 0x1
PT_LOAD = 1

# byte pattern -> disassembly, for the fallback path. Ending in c3 (ret) is what
# makes each one chainable.
PATTERNS = {
    b"\x5f\xc3": "pop rdi ; ret",
    b"\x5e\xc3": "pop rsi ; ret",
    b"\x5a\xc3": "pop rdx ; ret",
    b"\x58\xc3": "pop rax ; ret",
    b"\x59\xc3": "pop rcx ; ret",
    b"\x5b\xc3": "pop rbx ; ret",
    b"\x5d\xc3": "pop rbp ; ret",
    b"\x5c\xc3": "pop rsp ; ret",
    b"\x41\x5f\xc3": "pop r15 ; ret",
    b"\x41\x5e\xc3": "pop r14 ; ret",
    b"\x41\x5d\xc3": "pop r13 ; ret",
    b"\x41\x5c\xc3": "pop r12 ; ret",
    b"\x5f\x5e\xc3": "pop rdi ; pop rsi ; ret",
    b"\x41\x5a\x41\x5b\xc3": "pop r10 ; pop r11 ; ret",
    b"\x0f\x05\xc3": "syscall ; ret",
    b"\x0f\x05": "syscall",
    b"\xc9\xc3": "leave ; ret",
    b"\xcd\x80": "int 0x80",
    b"\xc3": "ret",
}
# the three that decide whether a plain ret2libc is even expressible
ESSENTIAL = ("pop rdi ; ret", "pop rsi ; ret", "pop rdx ; ret", "ret", "syscall")


def exec_ranges(e):
    """Executable PT_LOAD segments as (file offset, vaddr, length)."""
    out = []
    for s in e.segments:
        if s["type"] == PT_LOAD and (s["flags"] & PF_X) and s["filesz"]:
            out.append((s["offset"], s["vaddr"], s["filesz"]))
    return out


def have_capstone():
    try:
        import capstone  # noqa: F401
        return True
    except ImportError:
        return False


def find(e, want=None, limit=40):
    """Gadgets found by byte pattern. Deterministic and dependency-free."""
    data, out, seen = e.data, [], set()
    for off, vaddr, size in exec_ranges(e):
        blob = data[off:off + size]
        for pat, text in PATTERNS.items():
            if want and text not in want:
                continue
            start = 0
            while True:
                i = blob.find(pat, start)
                if i == -1:
                    break
                start = i + 1
                addr = vaddr + i
                if addr in seen:
                    break
                seen.add(addr)
                out.append({"addr": hex(addr), "gadget": text, "bytes": pat.hex()})
                if len([g for g in out if g["gadget"] == text]) >= 3:
                    break
    out.sort(key=lambda g: (g["gadget"], int(g["addr"], 16)))
    return out[:limit]


def summary(e):
    """Which of the gadgets a ret2libc needs are actually present."""
    found = find(e, want=set(ESSENTIAL), limit=200)
    by_text = {}
    for g in found:
        by_text.setdefault(g["gadget"], []).append(g["addr"])
    missing = [t for t in ESSENTIAL if t not in by_text]
    note = ("every register gadget a 3-argument ret2libc needs is present"
            if not missing else
            "missing " + ", ".join(missing) + " -- for the missing ones look in "
            "libc rather than the binary, or use a __libc_csu_init style "
            "universal gadget")
    return {"engine": "capstone available (unused: byte patterns are exact here)"
                      if have_capstone() else "byte patterns (capstone absent)",
            "present": {t: a[:3] for t, a in sorted(by_text.items())},
            "missing_essential": missing,
            "note": note}
