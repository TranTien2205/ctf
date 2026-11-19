# HTML and code comments — case catalogue

Developers leave TODOs, credentials, internal hostnames, and dead routes in comments — free text the browser doesn't render but curl shows.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | <!-- TODO/FIXME/admin in page source | comment leak | read all comments |
| 2 | Internal URLs in comments | route disclosure | probe them |
| 3 | Credentials or test values in comments | secret leak | test or note |
| 4 | <!-- flag{ or challenge hints | intended breadcrumb | follow |

## Falsifier

Falsifier — pages carry no comments beyond framework boilerplate: nothing disclosed.

## Coverage notes

- Minified bundles strip comments — check the unminified/source-map version.
- Server-side comments (PHP/python) never reach the client — only template-visible ones leak.

## Cross-references

`secrets-in-js.md` · `exposed-artifacts.md`
