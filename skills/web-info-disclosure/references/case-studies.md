# Case studies — the canonical shapes

The recurring CTF shapes this class owns — each with the decision path.

## The .git handout
A challenge that literally ships `.git` in the handout or serves it: git_dumper, read the history, the flag is usually in a deleted commit or a config. Closest thing to a free solve.

## The backup that isn't supposed to be there
`/backup.zip` 200: extract, read the app source, find the sink — the disclosure converts a black-box challenge into white-box.

## The debug page that leaks env
Spring actuator/env or Django DEBUG page: secrets in env → session forge or DB creds. The disclosure is the whole chain.

## The source map that un-minifies
A shipped .map: recovered sources expose internal routes → probe them → one is an admin export. Disclosure as route discovery.

## The comment that names the path
`<!-- TODO: remove /admin-backup.swp before prod -->` — the comment IS the hint; probe exactly that one path.

## The catch-all that lies
SPA fallback returns the app shell for every path — the whole bounded sweep reads as 'all 200'. Baseline-diff or nothing counts.

## Falsifier

--

## Cross-references

`worked-examples.md`
