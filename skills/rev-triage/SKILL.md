---
name: rev-triage
description: >
  Reverse engineering triage. Use when given a binary/firmware/obfuscated code
  for a CTF RE challenge: identify, decompile, spot the check/crypto, replicate.
  Reference card — pull references/ for packer/crypto/VM/managed depth.
tags: [rev, reverse-engineering, decompiler, analysis]
environment: [ctf, lab]
---

# Reverse Engineering — Triage Card

## Triage (nhận diện nhanh)
`file ./bin` · `strings -n8 ./bin | grep -iE "flag|CTF\{|key|correct|wrong"` · `binwalk ./bin`
Packed? `strings|grep -iE "upx|themida|vmprotect|aspack"` + `binwalk -E` (entropy cao).
UPX: `upx -d ./bin`. Packer khác → `references/packer-analysis.md`.

## Static (decompile)
- r2: `r2 -A bin` → `afl` → `pdf @sym.<f>` (disasm) → `axt @sym.<f>` (xref) → `iz`/`izz` (strings).
- **Decompile ra C giả, ĐỪNG đọc hex/offset bằng mắt** (dễ đọc nhầm → kết luận sai,
  vd loop-stride vs counter-step). Local: r2 `pdc`/`pdcc @sym.<f>` (pseudo-C). Nếu cần
  chuẩn hơn: cài `r2pm -ci r2ghidra` rồi `pdg @sym.<f>`, hoặc Ghidra headless
  `analyzeHeadless <proj> tmp -import bin -postScript DecompileScript` (kiểm tra tồn tại trước).
- Hàm cần soi: `main win flag check verify encrypt decrypt transform`. UTF-16: `strings -e l`.
- **Reverse hàm QUYẾT ĐỊNH trước, đủ sâu** — đừng để lại đúng đoạn khả nghi nhất
  (state machine, vòng lặp so khớp, auth gate) "chưa đọc" rồi đi brute biến thể rẻ.

## Dynamic
`ltrace ./bin` (library call — hay lộ `strcmp` so sánh flag) · `strace` (syscall) · `gdb` (break tại hàm check).

## Pattern CTF hay gặp
- Input so với giá trị tính sẵn → tìm chỗ so sánh, trích expected HOẶC replicate phép tính với input đúng.
- XOR loop (key ngắn) / base64 / caesar / substitution → `references/crypto-recognition.md`.
- Anti-debug (`ptrace`,`IsDebuggerPresent`) → patch check hoặc `LD_PRELOAD`.

## Route to depth (references/)
packed → `packer-analysis.md` · crypto trong bin → `crypto-recognition.md` · VM obfuscation →
`vm-analysis.md` · .NET/Java (dnSpy/jadx) → `managed-code.md` · firmware/IoT → `firmware-analysis.md`.

## Discipline (../LOOP_DISCIPLINE.md)
- `ltrace`/`strace` TRƯỚC khi lao vào decompile — thường lộ ngay `strcmp`/flag.
- Hiểu thuật toán check rồi mới viết solver; có thể đảo ngược thì đừng brute mù.
- Nghi đọc nhầm asm (hex/offset/stride)? → verify bằng decompiler hoặc replica, đừng suy diễn.
- Binary + input? Dựng replica cục bộ để fuzz không giới hạn (xem LOOP_DISCIPLINE §6).
