# lea forms — the address arithmetic — checklist

Companion to `the-lea-forms.md`.

## Checklist

- [ ] lea rax, [rip+disp] — a static address.
- [ ] lea rax, [rbp-0x40] — a stack slot.
- [ ] lea rax, [rax+rbx*4] — an indexed slot — the array indexing.
