# Web-service oracles vs local oracles — checklist

The same attacks exist in two transports; the differences are operational.

## Checklist

- [ ] Distinguishers: status, body, length, timing.
- [ ] Cost: network round-trip per query (~10-50ms LAN, more remote).
- [ ] Budget: a 40k-request padding loop is 20-60 min — measure the rate first.
- [ ] Tools: `pad_oracle.py`, `ecb_oracle.py` drive HTTP natively.

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
