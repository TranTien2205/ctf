# Falsifiers — what closes each disclosure channel — operational checklist

Every channel has one cheap observation that closes it. Check the falsifier before the sweep; it's cheaper.

## Checklist

- [ ] Baseline the catch-all FIRST — without it every probe lies.
- [ ] Run each channel's falsifier probe before its sweep.
- [ ] A closed channel is a recorded negative, not a retry.
- [ ] All channels closed → record and hand back to the router.

## Abort conditions

- A falsifier is channel-specific — .git closed doesn't close .env.
- The catch-all falsifier is the strongest: it nullifies the entire sweep at once.

## Falsifier

--

## Cross-references

`catchall-falsifier.md` · `negative-results.md`
