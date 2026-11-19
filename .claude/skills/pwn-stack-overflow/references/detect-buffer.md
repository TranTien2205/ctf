# Detecting the buffer — finding the sink

White-box: grep for the read functions and array bounds. Black-box: send patterns and watch for crashes at growing lengths.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| source shows gets/strcpy/read(unbounded) | the sink is named | direct to cyclic |
| black-box crash at length N | bound = N-ish | cyclic around N |

## Steps

1. Source: grep -nE 'gets|strcpy|strcat|scanf|read|memcpy|sprintf|vsprintf' — the dangerous set.
2. Each dangerous call's bound arg decides if it's this class.
3. Black-box: send increasing lengths; the length where a crash begins bounds the buffer.
4. Once the sink is named, cyclic measures the offset.

## Falsifier

Falsifier — every read is properly bounded: no stack-corruption exists; other classes own it.

## Traps

- sprintf/vsprintf into a stack buffer with user input is a hidden format-string too.
- memcpy of a computed length can be influenced via the computed n.
- strcpy of an env/argv value is the same class via a different transport.

## Commands

```bash
grep -nE 'gets|strcpy|strcat|scanf|read|memcpy|sprintf' source.c
```

## Cross-references

`detect-buffer.md` → `read-family.md`
