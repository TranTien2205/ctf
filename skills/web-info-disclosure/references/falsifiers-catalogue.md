# Falsifiers — what closes each disclosure channel — case catalogue

Every channel has one cheap observation that closes it. Check the falsifier before the sweep; it's cheaper.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | HEAD/.env all return catch-all body | channel closed | stop |
| 2 | debug paths all generic-error | debug off | stop |
| 3 | robots/sitemap only public paths | nothing hidden | stop |
| 4 | no comments beyond boilerplate | no comment leak | stop |

## Falsifier

--

## Coverage notes

- A falsifier is channel-specific — .git closed doesn't close .env.
- The catch-all falsifier is the strongest: it nullifies the entire sweep at once.

## Cross-references

`catchall-falsifier.md` · `negative-results.md`
