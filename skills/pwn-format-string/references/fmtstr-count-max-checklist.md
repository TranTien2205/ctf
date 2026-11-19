# The count maximum — practical write limits — checklist

Companion to `fmtstr-count-max.md`.

## Checklist

- [ ] A single %n write of value V needs V bytes printed — huge V impractical.
- [ ] %hhn writes only count&0xff — each byte needs count ≡ byte (mod 256),
- [ ] 8 %hhn writes, each ≤255 printed bytes → ~2KB for a full address.
