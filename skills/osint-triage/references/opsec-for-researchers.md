# OPSEC for OSINT Researchers

## Why OPSEC Matters During OSINT
Investigating a subject can inadvertently alert them if your research
activity is visible to them (e.g. viewing a private-but-visible LinkedIn
profile, following a social media account, visiting a personal website
that logs visitor analytics). For CTF this rarely matters, but for
authorized real-world OSINT (e.g. pre-engagement social engineering recon)
it can compromise the assessment or create real-world risk.

## Separate Research Identity
```
[ ] Use a dedicated research browser profile/VM, not your personal
    logged-in accounts
[ ] Avoid using personal social media accounts to view/follow/friend a
    research subject
[ ] Consider a separate, non-attributable email/account for platforms
    that require login to view content, if your engagement's rules permit
    creating research accounts
```

## Network-Level Precautions
```
[ ] Be aware that visiting a subject's personal website/blog may log your
    IP address in their analytics — use a VPN or the engagement's
    designated research infrastructure if avoiding attribution matters
[ ] Avoid downloading files directly from a subject-controlled server if
    that could alert them to research activity (their web server logs)
```

## Avoiding Direct Interaction
```
[ ] Do not message, comment, like, or otherwise interact with a research
    subject's content unless the engagement explicitly authorizes active
    elicitation as part of a social engineering assessment
[ ] Do not attempt to "friend" or "connect" with a subject to view
    restricted content — this alerts them directly and may itself be
    considered unauthorized/unethical depending on scope
```

## Data Handling
```
[ ] Store OSINT findings on subjects (especially for authorized
    engagements involving real people) securely, following the same data
    handling rules as any other sensitive engagement data
[ ] Redact/anonymize findings in any report intended for wider
    distribution beyond the immediate engagement stakeholders
[ ] Delete or securely dispose of research notes per the engagement's
    data retention policy once the report is delivered
```

## Legal and Ethical Boundaries
```
[ ] Only use information that is genuinely publicly accessible or
    obtained through legitimate, authorized means (e.g. an authorized
    breach-check service under your own engagement's terms)
[ ] Do not use social engineering, pretexting, or account creation to
    access non-public information unless that is explicitly the
    authorized scope of the engagement (e.g. a red team social engineering
    assessment with documented authorization)
[ ] Be aware that OSINT on private individuals can implicate privacy laws
    (GDPR and similar) depending on jurisdiction — this is especially
    relevant for engagements involving EU data subjects
```

## CTF-Specific OPSEC Notes
For OSINT CTF challenges, the "subject" is typically a fictional persona
or the challenge author's intentionally placed clues — OPSEC concerns
about real-world alerting don't apply, but verification discipline
(cross-checking sources, distinguishing confirmed vs speculative findings)
still matters for accuracy and avoiding wasted time on false leads.

## Verification Discipline Recap
Even with good OPSEC, findings are only as good as their verification.
Always apply the same standard from the main skill: cross-check facts
against independent sources, record confidence levels, and document the
exact source and access date for every claim used in a conclusion.
