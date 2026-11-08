# Toolbox - first commands and generic utilities

The commands you run before you know what the challenge is. Nothing here is a
technique; it is the identification and unpacking layer.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Quick Start Commands

```bash
# File identification
file mystery_file
xxd mystery_file | head -5
python3 -c "import magic; print(magic.from_file('mystery_file'))"

# Encoding detection
python3 -c "import base64; print(base64.b64decode('<data>'))"
echo '<data>' | base64 -d
echo '<hex>' | xxd -r -p

# QR code
zbarimg qr.png
python3 -c "from pyzbar.pyzbar import decode; from PIL import Image; print(decode(Image.open('qr.png')))"

# Z3 constraint solving
python3 -c "from z3 import *; x=BitVec('x',32); s=Solver(); s.add(x^0xdead==0xbeef); s.check(); print(s.model())"

# Python jail test
python3 -c "__import__('os').system('id')"
```


## General Tips

- Read all provided files carefully
- Check file metadata, hidden content, encoding
- Power Automate scripts may hide API calls
- Use binary search when guessing multiple answers


## File Type Detection

```bash
file unknown_file
xxd unknown_file | head
binwalk unknown_file
```


## Archive Extraction

```bash
7z x archive.7z           # Universal
tar -xzf archive.tar.gz   # Gzip
tar -xjf archive.tar.bz2  # Bzip2
tar -xJf archive.tar.xz   # XZ
```

### Nested Archive Script
```bash
while f=$(ls *.tar* *.gz *.bz2 *.xz *.zip *.7z 2>/dev/null|head -1) && [ -n "$f" ]; do
    7z x -y "$f" && rm "$f"
done
```


## Hash Identification

MD5: `0x67452301` | SHA-256: `0x6a09e667` | MurmurHash64A: `0xC6A4A7935BD1E995`


## Useful One-Liners

```bash
grep -rn "flag{" .
strings file | grep -i flag
python3 -c "print(int('deadbeef', 16))"
```


## Technique Quick References

- **PyInstaller:** `pyinstxtractor.py packed.exe`. See [games-and-vms.md](games-and-vms.md) for opcode remapping.
- **Marshal:** `marshal.load(f)` then `dis.dis(code)`. See [games-and-vms.md](games-and-vms.md).
- **Python env RCE:** `PYTHONWARNINGS=ignore::antigravity.Foo::0` + `BROWSER="cmd"`. See [games-and-vms.md](games-and-vms.md).
- **WASM patching:** `wasm2wat` -> flip minimax -> `wat2wasm`. See [games-and-vms.md](games-and-vms.md).
- **Float precision:** Large multipliers amplify FP errors into exploitable fractions. See [games-and-vms.md](games-and-vms.md).
- **K8s RBAC bypass:** SA token -> impersonate -> hostPath mount -> read secrets. See [games-and-vms.md](games-and-vms.md).
- **Cookie checkpoint:** Save session cookies before guesses, restore on failure to brute-force without reset. See [games-and-vms-2.md](games-and-vms-2.md).
- **Flask cookie game state:** `flask-unsign -d -c '<cookie>'` decodes unsigned Flask sessions, leaking game answers. See [games-and-vms-2.md](games-and-vms-2.md).
- **WebSocket teleport:** Modify `player.x`/`player.y` in console, call verification function. See [games-and-vms-2.md](games-and-vms-2.md).
- **Time-only validation:** Start session, `time.sleep(required_seconds)`, submit win. See [games-and-vms-2.md](games-and-vms-2.md).
- **Quine context detection:** Dual-purpose quine that prints itself (passes validation) and runs payload only in server process via globals gate. See [pyjails.md](pyjails.md).
- **Repunit decomposition:** Decompose target integer into sum of repunits (1, 11, 111, ...) using only 2 characters (`1` and `+`) for restricted eval. See [pyjails.md](pyjails.md).
- **De Bruijn sequence:** B(k, n) contains all k^n possible n-length strings as substrings; linearize by appending first n-1 chars. See [games-and-vms-2.md](games-and-vms-2.md).
- **Brainfuck instrumentation:** Instrument BF interpreter to track tape cells, brute-force flag character-by-character via validation cell. See [games-and-vms-2.md](games-and-vms-2.md).
- **WASM memory manipulation:** Patch WASM linear memory at runtime to set game state variables directly, bypassing game logic. See [games-and-vms-2.md](games-and-vms-2.md).
- **Lua sandbox escape:** Bypass `load()`/`os.execute()` filters via `os["execute"]` table indexing or `loadstring` alias. See [games-and-vms.md](games-and-vms.md#lua-sandbox-escape-via-function-name-injection-csaw-ctf-2016).
- **C code jail via emoji + gadget embedding:** When only emoji and punctuation are allowed in C, use `(😃==😃)` as constant 1, build integers, embed gadgets in `add eax, imm32` constants, jump to offset+1 for shellcode primitives. See [games-and-vms-3.md](games-and-vms-3.md#c-code-jail-escape-via-emoji-identifiers-and-gadget-embedding-midnight-flag-2026).
- **Emulator ROM-switching:** `/load` replaces ROM but preserves CPU state (registers, RAM, PC). Switch ROMs at specific PCs to combine INIT from one ROM with display instructions from another → read protected memory. See [games-and-vms-3.md](games-and-vms-3.md#emulator-rom-switching-state-preservation-bsidessf-2026).
- **BuildKit daemon exploitation:** Exposed BuildKit gRPC allows nested `buildctl build` with `--mount=type=secret` to read build secrets. Two-stage Dockerfile: install buildctl → submit nested build mounting flag secret. See [games-and-vms-3.md](games-and-vms-3.md#buildkit-daemon-exploitation-for-build-secrets-bsidessf-2026).
- **Docker container escape:** Privileged breakout via host device mount, docker.sock socket escape, CAP_SYS_ADMIN cgroup release_agent, container info leakage via /proc and overlayfs. See [games-and-vms-3.md](games-and-vms-3.md#docker-container-escape-techniques).
- **Taint analysis bypass via type coercion:** In custom ML-like languages with secrecy/taint systems, if-expression secrecy depends on return type not condition — coerce side-effecting functions to private type to leak private data through public mutable refs. See [games-and-vms-3.md](games-and-vms-3.md#taint-analysis-bypass-in-custom-language-via-type-coercion-plaidctf-2018).
- **Shredded document pixel-edge reassembly:** Encode each strip's left/right edge as binary bitmask (dark=1), use XOR + popcount Hamming distance to greedily place strips by minimum edge distance for sub-second reassembly. See [games-and-vms-3.md](games-and-vms-3.md#shredded-document-pixel-edge-reassembly-under-time-pressure-nuit-du-hack-ctf-2018).
- **f-string config injection via stored eval:** Store payload as config value, create key named `eval(stored_key)` — f-string rendering evaluates the key name expression, triggering RCE. See [pyjails.md](pyjails.md#python-f-string-config-injection-via-stored-eval-inshack-2018).
- **Hexadecimal Sudoku + QR assembly:** 4 QR codes encode 16x16 hex Sudoku quadrants; solve grid, read diagonal as hex pairs → ASCII flag. See [encodings-advanced.md](encodings-advanced.md#hexadecimal-sudoku--qr-assembly-bsidessf-2026).
- **Z3 boolean gate network SAT solving:** Product key validation as 250 boolean gates (AND/OR/XOR/NOT) over 125 input bits. Model each gate as Z3 constraint, require all outputs True, solve in milliseconds. See [games-and-vms.md](games-and-vms.md#z3-sat-solving-for-boolean-logic-gate-networks-bsidessf-2026).


