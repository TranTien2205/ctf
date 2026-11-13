#!/usr/bin/env python3
"""esolang_run.py -- detect and run esoteric-language blobs.

Classic misc shape: the handout is a blob of punctuation and the
flag is what the program prints. Detects and executes:

  brainfuck   > < + - . , [ ]          tape machine
  Ook!        Ook. Ook? Ook!           orangutan syntax over brainfuck
  Deadfish    i d s o                  accumulator ( -1 and 256 -> 0 )
  Whitespace  space / tab / LF only    stack machine (WS 0.3 subset)
  JSFuck      [ ] ( ) ! +              evaluated via `node` if present

    python3 tools/esolang_run.py prog.bf
    python3 tools/esolang_run.py prog.ook --lang ook
    cat prog.ws | python3 tools/esolang_run.py - --lang whitespace
    python3 tools/esolang_run.py --selftest

Auto-detect runs the heuristics in the safe order (whitespace first,
JSFuck before brainfuck since their alphabets overlap). Execution is
bounded: step limit + output cap, input ops read --input instead of
blocking on stdin. JSFuck needs `node`; without it the tool reports
the language and stops instead of guessing.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys

BF = "><+-.,[]"
STEPS = 2_000_000
OUTCAP = 100_000


def detect(src: str) -> str:
    t = src
    if t and set(t) <= {" ", "\t", "\n", "\r"} and " " in t:
        return "whitespace"
    compact = re.sub(r"\s+", "", t)
    if re.fullmatch(r"(Ook[.!?])+", compact):
        return "ook"
    if compact and set(compact) <= set("idso"):
        return "deadfish"
    if compact and set(compact) <= set("[]()!+"):
        return "jsfuck"
    bf_chars = sum(1 for c in t if c in BF)
    if bf_chars and bf_chars >= max(8, len(t) * 0.5):
        return "brainfuck"
    return "unknown"


def run_bf(code: str, inp: bytes = b"") -> str:
    tape, ptr, out, ip = [0] * 30000, 0, [], 0
    steps = 0
    stack = []
    jumps = {}
    for i, c in enumerate(code):
        if c == "[":
            stack.append(i)
        elif c == "]":
            j = stack.pop()
            jumps[i] = j
            jumps[j] = i
    n = len(code)
    while ip < n:
        c = code[ip]
        steps += 1
        if steps > STEPS:
            raise RuntimeError("step limit exceeded -- possible "
                               "infinite loop")
        if c == ">":
            ptr += 1
            if ptr >= len(tape):
                tape.extend([0] * 1000)
        elif c == "<":
            ptr = max(0, ptr - 1)
        elif c == "+":
            tape[ptr] = (tape[ptr] + 1) & 0xFF
        elif c == "-":
            tape[ptr] = (tape[ptr] - 1) & 0xFF
        elif c == ".":
            out.append(tape[ptr])
            if len(out) > OUTCAP:
                raise RuntimeError("output cap exceeded")
        elif c == ",":
            tape[ptr] = inp[0] if inp else 0
            inp = inp[1:]
        elif c == "[":
            if tape[ptr] == 0:
                ip = jumps[ip]
        elif c == "]":
            if tape[ptr] != 0:
                ip = jumps[ip]
        ip += 1
    return bytes(out).decode("utf-8", "replace")


def run_ook(src: str, inp: bytes = b"") -> str:
    toks = re.findall(r"Ook([.!?])", src)
    pairs = list(zip(toks[0::2], toks[1::2]))
    table = {(".", "?"): ">", ("?", "."): "<", (".", "."): "+",
             ("!", "!"): "-", ("!", "."): ".", (".", "!"): ",",
             ("!", "?"): "[", ("?", "!"): "]"}
    code = "".join(table.get(p, "") for p in pairs)
    if not code:
        raise ValueError("no valid Ook! instruction pairs")
    return run_bf(code, inp)


def run_deadfish(src: str) -> str:
    acc, out = 0, []
    for c in src:
        if acc in (-1, 256):
            acc = 0
        if c == "i":
            acc += 1
        elif c == "d":
            acc -= 1
        elif c == "s":
            acc *= acc
        elif c == "o":
            out.append(str(acc))
        if len(out) > OUTCAP:
            raise RuntimeError("output cap exceeded")
    return " ".join(out)


def run_ws(src: str, inp: bytes = b"") -> str:
    """Whitespace 0.3 subset: stack, arithmetic, heap, flow, output.
    Input commands are stubbed from --input bytes."""
    S, T, L = " ", "\t", "\n"
    src = src.replace("\r\n", "\n").replace("\r", "")
    i = 0
    prog = []
    labels = {}

    def num():
        nonlocal i
        sign = -1 if src[i] == T else 1
        i += 1
        bits = ""
        while i < len(src) and src[i] != L:
            bits += "0" if src[i] == S else "1"
            i += 1
        i += 1
        return sign * int(bits or "0", 2)

    def label():
        nonlocal i
        s = ""
        while i < len(src) and src[i] != L:
            s += src[i]
            i += 1
        i += 1
        return s

    while i < len(src):
        c = src[i]
        if c == S:                       # stack manipulation
            i += 1
            d = src[i]
            i += 1
            if d == S:
                prog.append(("push", num()))
            elif d == T:
                e = src[i]
                i += 1
                prog.append(("copy", num()) if e == S
                            else ("slide", num()))
            elif d == L:
                e = src[i]
                i += 1
                prog.append({S: ("dup", None), T: ("swap", None),
                             L: ("discard", None)}[e])
        elif c == T:
            i += 1
            if src[i] == S:              # arithmetic
                i += 1
                op = {S + S: "add", S + T: "sub", S + L: "mul",
                      T + S: "div", T + T: "mod"}[src[i] + src[i + 1]]
                i += 2
                prog.append((op, None))
            elif src[i] == T:            # heap
                i += 1
                prog.append(("store", None) if src[i] == S
                            else ("retr", None))
                i += 1
            else:                        # io
                i += 1
                op = {S + S: "outc", S + T: "outn",
                      T + S: "inc", T + T: "inn"}[src[i] + src[i + 1]]
                i += 2
                prog.append((op, None))
        elif c == L:                     # flow control
            i += 1
            d = src[i]
            i += 1
            if d == S:
                e = src[i]
                i += 1
                prog.append({S: ("mark", label()),
                             T: ("call", label()),
                             L: ("jmp", label())}[e])
            elif d == T:
                e = src[i]
                i += 1
                prog.append({S: ("jz", label()), T: ("jn", label()),
                             L: ("ret", None)}[e])
            elif d == L:
                prog.append(("end", None))
        else:
            i += 1
    for pc, (op, arg) in enumerate(prog):
        if op == "mark":
            labels[arg] = pc
    st, heap, calls, out, pc = [], {}, [], [], 0
    steps = 0
    while pc < len(prog):
        op, arg = prog[pc]
        steps += 1
        if steps > STEPS:
            raise RuntimeError("step limit exceeded")
        pc += 1
        if op == "push":
            st.append(arg)
        elif op == "dup":
            st.append(st[-1])
        elif op == "copy":
            st.append(st[-1 - arg])
        elif op == "swap":
            st[-1], st[-2] = st[-2], st[-1]
        elif op == "discard":
            st.pop()
        elif op == "slide":
            top = st.pop()
            del st[-arg:]
            st.append(top)
        elif op in ("add", "sub", "mul", "div", "mod"):
            b_, a_ = st.pop(), st.pop()
            st.append({"add": a_ + b_, "sub": a_ - b_, "mul": a_ * b_,
                       "div": int(a_ / b_) if b_ else 0,
                       "mod": a_ % b_ if b_ else 0}[op])
        elif op == "store":
            v, k = st.pop(), st.pop()
            heap[k] = v
        elif op == "retr":
            st.append(heap.get(st.pop(), 0))
        elif op == "outc":
            out.append(chr(st.pop() & 0x10FFFF))
        elif op == "outn":
            out.append(str(st.pop()))
        elif op in ("inc", "inn"):
            key = st.pop()
            if op == "inc":
                ch = inp[0:1]
                inp = inp[1:]
                heap[key] = ch[0] if ch else 0
            else:
                tok = b""
                while inp and inp[:1] != b"\n":
                    tok += inp[0:1]
                    inp = inp[1:]
                inp = inp[1:]
                heap[key] = int(tok) if tok.strip() else 0
        elif op == "call":
            calls.append(pc)
            pc = labels[arg]
        elif op == "jmp":
            pc = labels[arg]
        elif op == "jz":
            if st.pop() == 0:
                pc = labels[arg]
        elif op == "jn":
            if st.pop() < 0:
                pc = labels[arg]
        elif op == "ret":
            pc = calls.pop()
        elif op == "end":
            break
        if len(out) > OUTCAP:
            raise RuntimeError("output cap exceeded")
    return "".join(out)


def run_jsfuck(src: str):
    node = shutil.which("node")
    if not node:
        return {"ok": False, "lang": "jsfuck",
                "note": "JSFuck detected but `node` is absent -- "
                        "cannot evaluate safely without a JS engine"}
    r = subprocess.run(
        [node, "-e", f"process.stdout.write(String(eval({src!r})))"],
        capture_output=True, text=True, timeout=10)
    return {"ok": r.returncode == 0, "lang": "jsfuck",
            "output": r.stdout.strip() or r.stderr.strip()[:200]}


def run(src: str, lang: str = "auto", inp: bytes = b""):
    lang = detect(src) if lang == "auto" else lang
    if lang == "brainfuck":
        return {"ok": True, "lang": lang,
                "output": run_bf("".join(c for c in src if c in BF), inp)}
    if lang == "ook":
        return {"ok": True, "lang": lang, "output": run_ook(src, inp)}
    if lang == "deadfish":
        return {"ok": True, "lang": lang, "output": run_deadfish(src)}
    if lang == "whitespace":
        return {"ok": True, "lang": lang,
                "output": run_ws(src, inp)}
    if lang == "jsfuck":
        return run_jsfuck(src)
    return {"ok": False, "lang": lang,
            "note": "no esolang signature matched -- this is a "
                    "carrier/encoding, not an esolang program"}


def _selftest():
    # brainfuck: print "Hi"  (8*9=72 'H', then +33 = 105 'i')
    bf = "++++++++[>+++++++++<-]>." + "+" * 33 + "."
    assert run_bf(bf) == "Hi"
    # ook equivalent of 'H' via wrapping hello-world fragment — build
    # by translating a known bf program
    bf2 = "+++."
    toks = {">": ("Ook.", "Ook?"), "<": ("Ook?", "Ook."),
            "+": ("Ook.", "Ook."), "-": ("Ook!", "Ook!"),
            ".": ("Ook!", "Ook."), ",": ("Ook.", "Ook!"),
            "[": ("Ook!", "Ook?"), "]": ("Ook?", "Ook!")}
    ooksrc = " ".join(t + " " for c in bf2 for t in toks[c])
    assert run_ook(ooksrc) == "\x03"
    # deadfish: i i i s o -> acc 3 -> 9 -> print 9
    assert run_deadfish("iiiso") == "9"
    # whitespace: push 65, output char, end
    S, T, L = " ", "\t", "\n"
    ws = (S + S +                        # IMP: stack manipulation
          S + T + S * 5 + T + L +        # push +65 (bits 1000001)
          T + L + S + S +                # IO: output char
          L + L)                         # flow: end program
    assert run_ws(ws) == "A", repr(run_ws(ws))
    # detect() classification
    assert detect("   \t \t\n\n") == "whitespace"
    assert detect(ooksrc) == "ook"
    assert detect("iiidsdso") == "deadfish"
    assert detect("!![]+[]") == "jsfuck"
    assert detect(bf) == "brainfuck"
    print("esolang_run selftest: ok (bf/ook/deadfish/ws/detect)")


def main():
    ap = argparse.ArgumentParser(description="esolang runner: bf, "
                                 "Ook!, Deadfish, Whitespace, JSFuck")
    ap.add_argument("file", nargs="?",
                    help="source file, or - for stdin")
    ap.add_argument("--lang", default="auto",
                    choices=["auto", "brainfuck", "ook", "deadfish",
                             "whitespace", "jsfuck"])
    ap.add_argument("--input", default="",
                    help="bytes fed to input ops (, / inc/inn)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required (or - for stdin)")
    src = sys.stdin.read() if a.file == "-" else open(
        a.file, encoding="utf-8", errors="replace").read()
    try:
        out = run(src, a.lang, a.input.encode())
    except (RuntimeError, ValueError) as exc:
        out = {"ok": False, "note": str(exc)}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if out.get("ok") and not a.lang == "auto":
        pass


if __name__ == "__main__":
    raise SystemExit(main())
