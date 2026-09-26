#!/usr/bin/env python3
"""Minimal ELF reader, standard library only.

pwntools, gdb, ROPgadget, ropper, checksec and patchelf are all measured ABSENT on
this machine, and pip here is EXTERNALLY-MANAGED, so a tool that imports any of
them is a tool that does not run. Everything needed for first-contact triage --
the protections, the dynamic imports, the symbol table -- is in the file itself.
"""
import struct

ET = {0: "NONE", 1: "REL", 2: "EXEC", 3: "DYN", 4: "CORE"}
MACHINE = {0x03: "x86", 0x3E: "x86-64", 0x28: "arm", 0xB7: "aarch64",
           0x08: "mips", 0x14: "ppc", 0x15: "ppc64", 0xF3: "riscv"}
PT_GNU_STACK, PT_GNU_RELRO, PT_INTERP, PT_DYNAMIC, PT_LOAD = 0x6474E551, 0x6474E552, 3, 2, 1
DT_NEEDED, DT_BIND_NOW, DT_FLAGS, DT_FLAGS_1, DT_RPATH, DT_RUNPATH = 1, 24, 30, 0x6FFFFFFB, 15, 29
DF_BIND_NOW, DF_1_PIE, DF_1_NOW = 0x8, 0x08000000, 0x1


class NotAnELF(ValueError):
    """The file does not start with \\x7fELF."""


class ELF:
    def __init__(self, data):
        if len(data) < 64 or data[:4] != b"\x7fELF":
            raise NotAnELF("no ELF magic")
        self.data = data
        self.bits = 64 if data[4] == 2 else 32
        self.little = data[5] == 1
        self.e = "<" if self.little else ">"
        self.type = ET.get(self._u16(16), str(self._u16(16)))
        self.machine = MACHINE.get(self._u16(18), hex(self._u16(18)))
        if self.bits == 64:
            self.entry = self._u64(24); phoff = self._u64(32); shoff = self._u64(40)
            phentsize = self._u16(54); phnum = self._u16(56)
            shentsize = self._u16(58); shnum = self._u16(60); shstrndx = self._u16(62)
        else:
            self.entry = self._u32(24); phoff = self._u32(28); shoff = self._u32(32)
            phentsize = self._u16(42); phnum = self._u16(44)
            shentsize = self._u16(46); shnum = self._u16(48); shstrndx = self._u16(50)
        self.segments = [self._phdr(phoff + i * phentsize) for i in range(phnum)]
        self.sections = self._sections(shoff, shentsize, shnum, shstrndx)

    # ---- primitives
    def _u16(self, o): return struct.unpack_from(self.e + "H", self.data, o)[0]
    def _u32(self, o): return struct.unpack_from(self.e + "I", self.data, o)[0]
    def _u64(self, o): return struct.unpack_from(self.e + "Q", self.data, o)[0]
    def _word(self, o): return self._u64(o) if self.bits == 64 else self._u32(o)

    def _phdr(self, o):
        if self.bits == 64:
            p_type, flags = self._u32(o), self._u32(o + 4)
            off, vaddr = self._u64(o + 8), self._u64(o + 16)
            filesz, memsz = self._u64(o + 32), self._u64(o + 40)
        else:
            p_type, off, vaddr = self._u32(o), self._u32(o + 4), self._u32(o + 8)
            filesz, memsz, flags = self._u32(o + 16), self._u32(o + 20), self._u32(o + 24)
        return {"type": p_type, "flags": flags, "offset": off, "vaddr": vaddr,
                "filesz": filesz, "memsz": memsz}

    def _cstr(self, o):
        end = self.data.find(b"\x00", o)
        return self.data[o:end if end != -1 else len(self.data)].decode("utf8", "replace")

    def _sections(self, shoff, size, num, strndx):
        if not shoff or not num:
            return []
        raw = []
        for i in range(num):
            o = shoff + i * size
            if self.bits == 64:
                raw.append({"name_off": self._u32(o), "type": self._u32(o + 4),
                            "flags": self._u64(o + 8), "addr": self._u64(o + 16),
                            "offset": self._u64(o + 24), "size": self._u64(o + 32),
                            "link": self._u32(o + 40), "entsize": self._u64(o + 56)})
            else:
                raw.append({"name_off": self._u32(o), "type": self._u32(o + 4),
                            "flags": self._u32(o + 8), "addr": self._u32(o + 12),
                            "offset": self._u32(o + 16), "size": self._u32(o + 20),
                            "link": self._u32(o + 24), "entsize": self._u32(o + 36)})
        if strndx < len(raw):
            base = raw[strndx]["offset"]
            for s in raw:
                s["name"] = self._cstr(base + s["name_off"])
        else:
            for s in raw:
                s["name"] = ""
        return raw

    def section(self, name):
        for s in self.sections:
            if s.get("name") == name:
                return s
        return None

    # ---- dynamic
    def dynamic(self):
        seg = next((s for s in self.segments if s["type"] == PT_DYNAMIC), None)
        if not seg:
            return []
        step = 16 if self.bits == 64 else 8
        out, o, end = [], seg["offset"], seg["offset"] + seg["filesz"]
        while o + step <= min(end, len(self.data)):
            tag, val = self._word(o), self._word(o + step // 2)
            if tag == 0:
                break
            out.append((tag, val))
            o += step
        return out

    def needed(self):
        dyn = self.dynamic()
        strtab = self.section(".dynstr")
        if not strtab:
            return []
        return [self._cstr(strtab["offset"] + v) for t, v in dyn if t == DT_NEEDED]

    def interpreter(self):
        seg = next((s for s in self.segments if s["type"] == PT_INTERP), None)
        return self._cstr(seg["offset"]) if seg else None

    def symbols(self):
        """Every name in .symtab and .dynsym; stripped binaries still have .dynsym."""
        names = set()
        for sym, strt in ((".symtab", ".strtab"), (".dynsym", ".dynstr")):
            s, st = self.section(sym), self.section(strt)
            if not s or not st or not s["entsize"]:
                continue
            for i in range(s["size"] // s["entsize"]):
                o = s["offset"] + i * s["entsize"]
                if o + 4 > len(self.data):
                    break
                n = self._cstr(st["offset"] + self._u32(o))
                if n:
                    names.add(n)
        return names


def load(path):
    with open(path, "rb") as fh:
        return ELF(fh.read())
