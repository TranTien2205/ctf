# Gadget quality — which gadgets are usable and which aren't — checklist

Not all gadgets are equal: a 'pop rdi; ret' is clean; 'pop rdi; pop rbp; ret' consumes an extra slot; a conditional gadget needs the right flags.

## Checklist

- [ ] pwn_triage --gadgets lists the matched gadgets.
- [ ] A 'pop r; ret' consumes the next qword into r — fill it, then the next address.
- [ ] A 'pop r; pop r2; ret' consumes TWO qwords — pad the second with junk or a value.
- [ ] A gadget with a side-effect (a call, an add) changes state — account for it.

## Abort conditions

- Each gadget's side-effects must be neutral or useful — a stray 'call' can crash.
- The essential set: pop rdi, pop rsi, pop rdx, syscall, ret.
- A missing pop rdx is the classic hole — ret2csu or mov rdx gadgets cover it.

## Falsifier

Falsifier — the only available gadget for a needed register has a side-effect that breaks the chain: find a different chain shape.
