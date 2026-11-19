# HTML and code comments

Developers leave TODOs, credentials, internal hostnames, and dead routes in comments — free text the browser doesn't render but curl shows.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| <!-- TODO/FIXME/admin in page source | comment leak | read all comments |
| Internal URLs in comments | route disclosure | probe them |
| Credentials or test values in comments | secret leak | test or note |
| <!-- flag{ or challenge hints | intended breadcrumb | follow |

## Steps

1. curl every page and extract comments: grep -o '<!--.*-->' or a parser.
2. Check JS files for // comments and /* blocks too.
3. Collect: internal paths, hostnames, TODO hints, dead endpoints.
4. Challenge breadcrumbs belong here — a 'hint' comment is usually intentional.

## Falsifier

Falsifier — pages carry no comments beyond framework boilerplate: nothing disclosed.

## Traps

- Minified bundles strip comments — check the unminified/source-map version.
- Server-side comments (PHP/python) never reach the client — only template-visible ones leak.

## Commands

```bash
curl -s '$BASE/' | grep -oE '<!--.*-->' ; curl -s '$BASE/app.js' | grep -nE '//|/\*'
```

## Cross-references

`secrets-in-js.md` · `exposed-artifacts.md`
