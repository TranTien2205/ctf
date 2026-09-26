#!/usr/bin/env python3
"""The checksec answer, computed from the ELF itself.

`checksec` is measured ABSENT on this machine. Every fact it prints is in the
file: NX in PT_GNU_STACK's flags, PIE in e_type plus DF_1_PIE, RELRO in
PT_GNU_RELRO plus DT_BIND_NOW, the canary in the symbol table. Reading them
directly also states WHY, which a one-line checksec table does not.
"""
from . import elf as _elf

PF_X = 0x1
CANARY_SYMS = ("__stack_chk_fail", "__stack_chk_guard", "__intel_security_cookie")
# each entry: symbol -> what it buys an attacker, stated as the next step
DANGEROUS = {
    "gets": "unbounded read; overflow with no size limit at all",
    "strcpy": "no bound; overflow when source is attacker-length",
    "strcat": "no bound; overflow onto an existing buffer",
    "sprintf": "no bound; overflow via format output length",
    "vsprintf": "no bound; same as sprintf",
    "scanf": "check the format: %s with no width is unbounded",
    "__isoc99_scanf": "check the format: %s with no width is unbounded",
    "read": "bounded by its third argument; compare that to the buffer",
    "memcpy": "bounded by its third argument; check where that comes from",
    "alloca": "stack allocation from a runtime value; clobbers the frame",
    "system": "already imported: a one-argument ret2system is in reach",
    "execve": "already imported: full exec without a libc leak",
    "execl": "already imported: exec with a literal path",
    "mprotect": "page permissions are writable+executable on demand: shellcode",
    "printf": "format string if the first argument is attacker-controlled",
    "fprintf": "format string if the format is attacker-controlled",
    "snprintf": "bounded, but a %n write still lands if format is controlled",
    "puts": "single-argument leak primitive for ret2plt",
    "free": "heap: pair with malloc for a use-after-free or double-free",
    "malloc": "heap: allocator-level chain rather than a stack overflow",
}


def protections(e):
    """Return the protections, each with the evidence that decided it."""
    syms = e.symbols()
    stack = next((s for s in e.segments if s["type"] == _elf.PT_GNU_STACK), None)
    relro_seg = next((s for s in e.segments if s["type"] == _elf.PT_GNU_RELRO), None)
    dyn = dict(e.dynamic())
    flags = dyn.get(_elf.DT_FLAGS, 0)
    flags1 = dyn.get(_elf.DT_FLAGS_1, 0)
    bind_now = (_elf.DT_BIND_NOW in dyn or bool(flags & _elf.DF_BIND_NOW)
                or bool(flags1 & _elf.DF_1_NOW))

    if stack is None:
        nx, nx_why = True, "no PT_GNU_STACK: the kernel default is non-executable"
    else:
        nx = not (stack["flags"] & PF_X)
        nx_why = "PT_GNU_STACK flags=0x%x, X bit %s" % (
            stack["flags"], "set" if stack["flags"] & PF_X else "clear")

    pie = e.type == "DYN" and (bool(flags1 & _elf.DF_1_PIE) or e.interpreter() is not None)
    if relro_seg is None:
        relro, relro_why = "none", "no PT_GNU_RELRO segment"
    elif bind_now:
        relro, relro_why = "full", "PT_GNU_RELRO present and BIND_NOW is set"
    else:
        relro, relro_why = "partial", "PT_GNU_RELRO present but BIND_NOW is not set"

    canary = sorted(s for s in CANARY_SYMS if s in syms)
    stripped = e.section(".symtab") is None
    static = e.interpreter() is None
    # measured on a binary built with -fno-stack-protector and -static: the symbol
    # is present anyway, because static glibc carries its own. In a static binary
    # the symbol proves only that SOMETHING in the image was built with the
    # canary, never that the vulnerable function was.
    canary_why = ("symbols present: " + ", ".join(canary)) if canary else \
        "no __stack_chk_* symbol in .symtab/.dynsym"
    if canary and static:
        canary_why += ("  -- BUT this binary is statically linked, so the symbol "
                       "may come from libc rather than from the target function; "
                       "check the function's own prologue for a %fs:0x28 load "
                       "before believing it")
    return {
        "arch": "%s-%d" % (e.machine, e.bits),
        "type": e.type,
        "entry": hex(e.entry),
        "nx": {"value": nx, "why": nx_why},
        "pie": {"value": pie, "why": "e_type=%s, DF_1_PIE %s, interp=%s" % (
            e.type, "set" if flags1 & _elf.DF_1_PIE else "clear", e.interpreter())},
        "relro": {"value": relro, "why": relro_why},
        "canary": {"value": bool(canary), "why": canary_why,
                   "trustworthy": not (canary and static)},
        "stripped": {"value": stripped,
                     "why": ".symtab absent" if stripped else ".symtab present"},
        "static": {"value": static,
                   "why": "no PT_INTERP" if static else "interp=" + e.interpreter()},
        "interpreter": e.interpreter(),
        "needed": e.needed(),
    }


def dangerous(e):
    """Imported or defined functions that name the next step, not just a risk."""
    syms = e.symbols()
    out = []
    for name in sorted(syms):
        key = name.lstrip("_") if name.lstrip("_") in DANGEROUS else name
        if key in DANGEROUS:
            out.append({"symbol": name, "means": DANGEROUS[key]})
    return out


def leads(prot, dang):
    """Turn the protections into the ordered set of routes actually still open.

    This is the part checksec never gives you: the table is only useful once it
    has been read as 'which technique does this leave'.
    """
    names = {d["symbol"] for d in dang}
    out = []
    if not prot["canary"]["value"]:
        out.append("no canary: a linear stack overflow reaches the saved return "
                   "address directly; find the offset first")
    elif not prot["canary"].get("trustworthy", True):
        out.append("a canary symbol exists but this binary is static, so it may "
                   "belong to libc: disassemble the target function and look for "
                   "a %fs:0x28 load before paying for a leak you may not need")
    else:
        out.append("canary present: leak it (format string, or an overread that "
                   "prints past the buffer) or pivot without touching it")
    if prot["nx"]["value"]:
        if prot["relro"]["value"] == "full":
            out.append("NX + full RELRO: no shellcode and no GOT overwrite; the "
                       "route is ROP or ret2libc")
        else:
            out.append("NX with %s RELRO: shellcode is out, but the GOT is still "
                       "writable -- a GOT overwrite is on the table" % prot["relro"]["value"])
    else:
        out.append("NX is OFF: the stack is executable, so shellcode is viable "
                   "and no gadget hunt is needed")
    if prot["pie"]["value"]:
        out.append("PIE: every address needs a leak first; a partial overwrite of "
                   "the low bytes of a return address avoids needing one")
    else:
        out.append("no PIE: binary addresses are fixed, so gadgets and PLT entries "
                   "can be used with no leak")
    if "system" in names:
        out.append("system is already imported: ret2system, no libc leak needed")
    if prot["static"]["value"]:
        out.append("statically linked: no libc version to identify, and the whole "
                   "gadget corpus is inside this one file")
    elif "libc.so.6" in prot["needed"]:
        out.append("dynamic against libc.so.6: identify the exact libc build "
                   "before using any offset from it")
    if prot["stripped"]["value"]:
        out.append("stripped: .dynsym still names the imports, but local function "
                   "names are gone -- work from the entry point and PLT calls")
    return out
