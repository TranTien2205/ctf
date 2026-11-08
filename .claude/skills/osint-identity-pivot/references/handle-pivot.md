# Handle pivot: one username, every platform

A handle is a seed, not an answer. The job is to pivot it across every
platform it exists on, then extract what one platform leaks that another
doesn't.

## The pivot sources, in order of yield

| Source | What it gives |
|---|---|
| `namechk`, `sherlock`, `whatsmyname` | platforms where the handle is taken |
| GitHub profile | real name, email in commit history, linked site |
| Twitter/X, Instagram, TikTok | photos, location hints, follower graph |
| LinkedIn | employer, school, the real name behind the handle |
| Reddit, Discord, Telegram | unguarded posting, voice messages |
| pastebin / forums under the handle | leaked email, password reuse |
| Wayback Machine on their site | the handle's earlier self |

## The pivot moves

- **Handle → real name**: LinkedIn, commit `Signed-off-by`/`Author:` fields,
  "About" pages.
- **Handle → email**: GitHub `git log` author field, forum profile "contact"
  pages, whois on a linked domain.
- **Email → more accounts**: `haveibeenpwned`, gravatar, the email's own
  domain — an email on a custom domain is a domain to pivot.
- **Photo → location**: reverse-image (Google Lens, Yandex, TinEye), EXIF
  GPS if present, distinctive landmarks.
- **Handle → phone number**: Telegram "add by phone", WhatsApp profile photo
  APIs, breaches that bind them.

## Recording a pivot

One row per hop: `handle -> platform -> what it leaked`. The chain is the
evidence — "found them on GitHub" is not the finding; "their commit history
leaked `name.surname@corp.com`" is.

## Falsifier

The handle exists on exactly one platform, every pivot terminates at a dead
end, and no email/name/domain surfaces — the seed is isolated.

## Traps

- Similar handles are not the same handle — `jdoe` vs `j.doe` vs `_jdoe` are
  often different people; verify a bio/photo link before pivoting.
- A platform where the handle is *available* is negative evidence — the
  person was never there.
- Scraped data ages — a location or employer from 2019 is stale; prefer
  the most recent post's signal.
