# Domain: OSINT identity tracking and fake accounts

Reference module for `contest-domain-map`. The event vocabulary sounds
like "follow the persona", "find the operator", "the account is fake",
"identify the insider". The owning router is
`skills/osint-triage/SKILL.md`; identity questions land in
`skills/osint-identity-pivot/SKILL.md`.

## Route

- A handle, email, or persona -> `osint-triage` -> `osint-identity-pivot`
- A photo to place -> `osint-geolocation`
- A domain, cert, or infrastructure record -> `osint-infra-records`
- Document metadata carrying the answer -> `osint-media-metadata`

## The pivot rule

Exactly one unique pivot before any searching. A handle like `xGhost_07`
is a pivot; "a guy in Hanoi who likes drones" is not. The wrong pivot
costs a budget on the wrong person — pick the token with the fewest
plausible owners.

## Corpus families inside identity-pivot

`handle-*`, `ssh-*`, `phone-*`, `pgp-*`, `org-*`, `name-*`, `location-*`
modules — one per pivot type: where that identifier leaks, which sources
resolve it, what corroboration the answer needs.

## Sockpuppet and fake-account tells — the event-specific gap

A "fake account" question is answered by tells, not vibes. Work the list:

1. **Account-age asymmetry.** Young account, deep expertise; or old
   account, activity that starts the week the campaign does. Creation
   date vs first-post date is the cheapest tell.
2. **Cross-platform reuse.** Same handle on three services with identical
   bio text — a persona built once and deployed wide. Real people drift;
   copy-paste is authored.
3. **Image provenance.** Profile photo that resolves to a stock library,
   a GAN face (asymmetric earrings, smeared background, too-perfect
   eyes), or a reverse-search hit under another name.
4. **Cadence.** Posts on machine intervals (exact 60/120-minute spacing),
   activity inside one timezone's working hours while claiming another,
   burst-then-silent patterns around ops.
5. **Graph shape.** Follows back everyone, no mutual community, replies
   only to seed accounts in the same cluster. A fake network amplifies
   itself.
6. **Language drift.** An insider persona writes fluently in the target's
   jargon but slips on locale details (holiday names, time formats,
   currency, spelling variants).

Two tells is a lead; three is the answer. One tell alone is a person who
just has a weird account — say so honestly.

## What not to do

- A handle match is not an identity. Same name, different human is the
  most common false positive; corroborate with a second pivot before the
  report names anyone.
- Public sources only. Anything requiring a login wall, scraping against
  ToS, or contacting the person is out.
