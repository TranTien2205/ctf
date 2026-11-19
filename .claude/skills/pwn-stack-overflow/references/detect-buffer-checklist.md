# Detecting the buffer — finding the sink — checklist

White-box: grep for the read functions and array bounds. Black-box: send patterns and watch for crashes at growing lengths.

## Checklist

- [ ] Source: grep -nE 'gets|strcpy|strcat|scanf|read|memcpy|sprintf|vsprintf' — the dangerous set.
- [ ] Each dangerous call's bound arg decides if it's this class.
- [ ] Black-box: send increasing lengths; the length where a crash begins bounds the buffer.
- [ ] Once the sink is named, cyclic measures the offset.

## Abort conditions

- sprintf/vsprintf into a stack buffer with user input is a hidden format-string too.
- memcpy of a computed length can be influenced via the computed n.
- strcpy of an env/argv value is the same class via a different transport.

## Falsifier

Falsifier — every read is properly bounded: no stack-corruption exists; other classes own it.
