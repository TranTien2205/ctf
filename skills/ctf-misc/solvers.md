# Solvers and automation

When the challenge is a search problem, an oracle or a protocol to drive, the
work is writing the solver, not finding a trick.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## pwntools Interaction

```python
from pwn import *

r = remote('host', port)
r.recvuntil(b'prompt: ')
r.sendline(b'answer')
r.interactive()
```


## Z3 / Constraint Solving

```python
from z3 import *
flag = [BitVec(f'f{i}', 8) for i in range(FLAG_LEN)]
s = Solver()
# Add constraints, check sat, extract model
```

See [games-and-vms.md](games-and-vms.md) for YARA rules, type systems as constraints, boolean logic gate network SAT solving.


## SHA-256 Length Extension Attack

MAC = `SHA-256(SECRET || msg)` with known msg/hash -> forge valid MAC via `hlextend`. Vulnerable: SHA-256, MD5, SHA-1. NOT: HMAC, SHA-3.

```python
import hlextend
sha = hlextend.new('sha256')
new_data = sha.extend(b'extension', b'original_message', len_secret, known_hash_hex)
```


## Levenshtein Distance Oracle Attack (SunshineCTF 2016)

Oracle returns edit distance between guess and secret. Determine length from empty string, identify present chars from single-char repeats, binary search for positions. O(n log n) queries. See [games-and-vms-3.md](games-and-vms-3.md#levenshtein-distance-oracle-attack-sunshinectf-2016).


## Backdoor Detection in Source Code

**Pattern (Rear Hatch):** Hidden command prefix triggers `system()` call.

**Common patterns:**
- `strncmp(input, "exec:", 5)` -> runs `system(input + 5)`
- Hex-encoded comparison strings: `\x65\x78\x65\x63\x3a` = "exec:"
- Hidden conditions in maintenance/admin functions


