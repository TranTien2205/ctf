# Neonify (HackTheBox) — verified 2026-09-12

Chain: ERB template injection in the `neon` parameter; the charset filter is
bypassed with a newline.

## Evidence ancestry (live target this session)
- Recon: Server header WEBrick/1.6.1 (Ruby/2.7.5); form POST / with field `neon`.
- Router: ctf.py black-box observation routed to web (score 2). skill_select
  returned category unknown and only the playbook, as designed.
- chain_match: no candidate among 8 stored chains, so the router first probe
  was used.
- Benign reflection probe: neon=HACKTHEBOX reflected inside the glow span.
- Filter confirmed: `{{7*7}}` and `<%` trigger "Malicious Input Detected".
- Filter characterization: newline, space and alphanumerics pass; `_ - . tab
  $ ^ ( )` are blocked, so the accepted charset is a-zA-Z0-9 plus space.
- Discriminating probe: `abc\n<%= 7*7 %>` rendered as `abc\n49` — ERB SSTI.
- Payload: `<%= eval(Base64.decode64('...')) %>\nabc` with Ruby `File.read`
  and `Dir.pwd`; cwd was `/app`, `flag.txt` present in `/app`.
- Flag was read from the live response (redacted here per EVIDENCE_POLICY).
- Exploit script: challenges/neonify/exploit.py

## Traps
- Base64 wrapping is required because `(`, `'`, `.` are blocked by the filter.
- `puts` inside eval writes to server stdout; the template only renders the
  expression value, so return the value directly.
- The second benign line is what satisfies the line-anchored filter check.
