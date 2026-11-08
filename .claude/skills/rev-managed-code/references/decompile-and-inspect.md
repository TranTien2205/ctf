# Managed code: decompile, don't disassemble

A managed binary (Java/.NET/Python-compiled/Go) keeps enough metadata to
rebuild near-source — the skill is choosing the right decompiler, not reading
raw bytecode.

## Identify the runtime

| `file`/`strings` says | Tool |
|---|---|
| Java `.class`/`.jar` | `jadx`, `jd-gui`, `cfr` — near-original source back |
| .NET `.exe`/`.dll` (`mscoree`, `System.`) | `dnSpy`, `ILSpy`, `monodis` — CIL is reversible to C# |
| Python `.pyc`/frozen | `uncompyle6`, `decompyle3`, `pycdc` — or `dis` module |
| Go binary | `gobuster`/`redress` — symbols survive, decompile to pseudo-Go |
| APK | `apktool` (smali) or `jadx` (dex→Java) |

## The three check shapes

| Shape | Read it as |
|---|---|
| string constant compare | the constant is the answer — `strings` already found it |
| computed digest (xor/sub/SHA) | the check is reversible or the digest is in `strings` |
| license/serial math | the valid key is a function of the input — invert the math |

## The fast answers

- `strings` on a `.jar`/`.dll` almost always shows the flag or the check
  constant — managed metadata is verbose.
- `javap -c`/`monodis` if the full decompiler isn't installed — readable
  enough for a compare.
- Android: `apktool d app.apk` for smali, `jadx-gui` for a Java view — the
  native `.so` inside an APK is a *different* class (see
  `../rev-native-check/`).

## Anti-decompile measures

| Measure | Response |
|---|---|
| obfuscated names (`a.a.a.b`) | still readable — follow the data, not the names |
| string encryption | decrypt at runtime or find the decryptor's constants |
| control-flow obfuscation | trace the actual calls — the check still ends in a compare |
| packed/protected .NET | dump at runtime — `MegaDumper`, or run under `dnSpy` |

## Falsifier

The binary is genuinely native (no managed metadata, no runtime strings) —
route to `../rev-native-check/` instead.

## Traps

- `jd-gui`/`jadx` may refuse a `module-info` or a corrupted jar — `cfr` is
  the fallback for one file at a time.
- A .NET assembly may be `AnyCPU`/mixed — `monodis` handles what `dnSpy`
  misdetects.
- Python `pyc` version matters: `uncompyle6` covers <3.9, `decompyle3`/
  `pycdc` cover newer — match the magic number first.
