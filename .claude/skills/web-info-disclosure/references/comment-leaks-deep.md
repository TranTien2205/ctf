# HTML and code comments — deep

Developers leave TODOs, credentials, internal hostnames, and dead routes in comments — free text the browser doesn't render but curl shows.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — pages carry no comments beyond framework boilerplate: nothing disclosed.

## Highest-cost traps

- Minified bundles strip comments — check the unminified/source-map version.
- Server-side comments (PHP/python) never reach the client — only template-visible ones leak.

## Commands

```bash
curl -s '$BASE/' | grep -oE '<!--.*-->' ; curl -s '$BASE/app.js' | grep -nE '//|/\*'
```

## Cross-references

`secrets-in-js.md` · `exposed-artifacts.md`
