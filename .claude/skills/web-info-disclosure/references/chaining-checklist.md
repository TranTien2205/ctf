# Chaining disclosure to impact — operational checklist

A disclosed artifact is never the flag — it's the key that reaches one. Every find routes to the class that owns its sink.

## Checklist

- [ ] Classify each find: secret, source, endpoint, credential, path.
- [ ] Route to the owning class: source→sink search, key→session forge, cred→login, endpoint→its class.
- [ ] Record the disclosure as evidence, then work the chain — the disclosure alone is not impact.
- [ ] The flag arrives through the chain, not the artifact.

## Abort conditions

- A leaked secret that's already rotated is still evidence of the class, not impact.
- Don't stop at 'we found .env' — the chain is the point.

## Falsifier

Falsifier — disclosed material reaches no privileged path: a finding with no chain is a hardening note, not a solve.

## Cross-references

`evidence.md` · `env-config-leaks.md`
