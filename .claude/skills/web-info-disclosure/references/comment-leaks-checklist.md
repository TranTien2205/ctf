# HTML and code comments — operational checklist

Developers leave TODOs, credentials, internal hostnames, and dead routes in comments — free text the browser doesn't render but curl shows.

## Checklist

- [ ] curl every page and extract comments: grep -o '<!--.*-->' or a parser.
- [ ] Check JS files for // comments and /* blocks too.
- [ ] Collect: internal paths, hostnames, TODO hints, dead endpoints.
- [ ] Challenge breadcrumbs belong here — a 'hint' comment is usually intentional.

## Abort conditions

- Minified bundles strip comments — check the unminified/source-map version.
- Server-side comments (PHP/python) never reach the client — only template-visible ones leak.

## Falsifier

Falsifier — pages carry no comments beyond framework boilerplate: nothing disclosed.

## Cross-references

`secrets-in-js.md` · `exposed-artifacts.md`
