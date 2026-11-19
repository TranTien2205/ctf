# Web-service oracles vs local oracles

The same attacks exist in two transports; the differences are operational.

## Web-service oracle (HTTP)

- Distinguishers: status, body, length, timing.
- Cost: network round-trip per query (~10-50ms LAN, more remote).
- Budget: a 40k-request padding loop is 20-60 min — measure the rate first.
- Tools: `pad_oracle.py`, `ecb_oracle.py` drive HTTP natively.

## Local oracle (a binary/script you run)

- Distinguishers: exit code, stdout text, stderr.
- Cost: microseconds — the loop is free.
- Build the loop inline: subprocess per query, or import the check function.
- Faster to write the loop by hand than to adapt an HTTP tool.

## The hybrid

- A local helper binary that answers crypto questions for a remote service
  (e.g., `oracle --ct <hex>` prints 'ok'/'bad pad'): treat as local oracle,
  drive with subprocess.

## Choosing the transport

| Oracle is | Use |
|---|---|
| HTTP endpoint | pad_oracle/ecb_oracle tools |
| local binary | inline subprocess loop |
| function in handout source | import it — pure-Python loop |
| a mix | the cheapest channel per stage |

## Falsifier

None of the transports yields a distinguishing answer: the oracle doesn't
exist regardless of shape.
