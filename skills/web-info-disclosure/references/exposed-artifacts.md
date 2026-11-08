# Exposed artifacts: the bounded sweep

Info disclosure wins by *naming the right file*, not by volume. Order the
candidates by what a CTF author most plausibly leaves behind, and bound the
sweep — a hundred requests with a wordlist is recon, not a skill.

## The candidate ladder, cheapest first

| Guess | Reads | Signal |
|---|---|---|
| `/.git/HEAD` | leaked repo | `ref: refs/heads/` — then take `.git/` seriously (see below) |
| `/.env` | secrets, keys | `KEY=` lines, not a 404 |
| `/.DS_Store`, `/backup.*`, `/*.bak`, `/*.old`, `/*.zip` | source/config backups | binary or source bytes |
| `/robots.txt`, `/sitemap.xml` | unlinked routes | Disallow lines |
| `/server-status`, `/actuator`, `/_debug`, `/debug`, `/metrics` | framework internals | env vars, route maps, heap stats |
| `/swagger.json`, `/openapi.json`, `/api-docs` | the API's own map | every route the docs forgot to hide |
| `/composer.json`, `/package.json`, `/requirements.txt`, `/Gemfile` | dependency manifest | version → CVE pivot |
| `/.svn/entries`, `/.hg/`, `/.bzr/` | other VCS leaks | repo internals |
| `/.well-known/` | security.txt, OIDC config | endpoints + issuer names |

`tools/web_enum.py` exists for the bounded form; never point it at a wordlist
without `--max-paths` and `--rate` set.

## When `.git` answers

A leaked repo is a full source drop — the prize is the tree, not the HEAD:

```text
.git/HEAD           -> the branch
.git/config         -> the remote (names the origin, sometimes a token)
.git/index          -> the file list
.git/objects/...    -> the objects themselves
```

Reconstruct: read `.git/HEAD` and `.git/config`, walk `.git/refs/heads/*`,
then fetch objects by sha. Tools exist (`git-dumper`, `GitTools`); a manual
`git fsck` on a downloaded `.git/` recovers dangling objects — where deleted
secrets usually live. The flag in a leaked repo is as often in *history* as in
the working tree.

## Confirm wording

An artifact is a finding only if it changes what you can do next:

- credential or key → name what it unlocks
- source or config → name the route, version, or internal hostname it revealed
- route map → name the endpoint it exposed that recon missed

A 200 on an interesting path whose body is empty, generic, or a default page
is not a finding — record inconclusive.

## Falsifier

Every plausible candidate returns the same shaped 404/403, and the framework
endpoints are absent — the deployment exposes only intended routes.

## Traps

- A soft-404 (custom error page with status 200) will false-positive every
  guess — take a baseline from a path that cannot exist first.
- WAF/CDN error pages can mask real 403s; compare *body*, not status alone.
- Sensitive paths may be keyed to an internal host header — if `Host:` games
  exist, re-run the ladder through them.
