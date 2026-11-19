# Anti-patterns — the habits that read as noise

## The probe anti-patterns

- **Brute-forcing a CSPRNG** — `os.urandom`/`secrets`/keyed is not a PRNG
  recovery; the falsifier `predict != held-back` fires immediately.
- **`mt19937-clone` on a partial window** — the 624 bound is exact.
- **Lattice on a reused-`k` shape** — the closed form is cheaper and correct.
- **Running the attack before counting outputs** — the count IS the gate.

## The flag anti-patterns

- **Inventing `--flags`** — the gate's flag contract catches them; use
  `--help` output only.
- **`--outputs` with a file path** — it's comma-separated; `--outputs-file`
  is the file form.
- **`--low-bits`/`--taps`/`--width` guessed** — each has a real meaning;
  a wrong value silently returns a wrong state.

## The discipline anti-patterns

- **A match on ONE output called a recovery** — a coincidence isn't a clone;
  reproduce a sequence.
- **Statistical confidence as a confirm** — uniform-looking isn't the gate;
  bit-for-bit prediction is.
- **No falsifier recorded** — a dead attack goes in `attempts/`, not memory.
- **Staying past `predict != held-back`** — that's the class falsifier; the
  source isn't the generator you modeled.

## The claim anti-patterns

- **Catalogue-as-experience** — nothing in this tree has solved a PRNG
  challenge; don't claim otherwise.
- **A plausible `a`,`c`,`m` as "the key"** — it isn't until `predict` fires.
