# Falsifiers — what closes each disclosure channel

Every channel has one cheap observation that closes it. Check the falsifier before the sweep; it's cheaper.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| HEAD/.env all return catch-all body | channel closed | stop |
| debug paths all generic-error | debug off | stop |
| robots/sitemap only public paths | nothing hidden | stop |
| no comments beyond boilerplate | no comment leak | stop |

## Steps

1. Baseline the catch-all FIRST — without it every probe lies.
2. Run each channel's falsifier probe before its sweep.
3. A closed channel is a recorded negative, not a retry.
4. All channels closed → record and hand back to the router.

## Falsifier

--

## Traps

- A falsifier is channel-specific — .git closed doesn't close .env.
- The catch-all falsifier is the strongest: it nullifies the entire sweep at once.

## Cross-references

`catchall-falsifier.md` · `negative-results.md`
