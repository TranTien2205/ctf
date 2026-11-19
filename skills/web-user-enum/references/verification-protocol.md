# Verification protocol — the prove-it sequence

## The five-step verify

1. **noise baseline** — send the SAME bad username twice; byte-diff to
   find per-request noise (CSRF, timestamp, request-id). Mask it.
2. **good vs bad** — send known-good vs known-bad; measure all four
   channels (body, status+Location, timing, envelope/side).
3. **repeat the bad** — a SECOND different bad name gives the same
   response as the first bad → the signal tracks the username-class.
4. **re-run** — re-run the good/bad pair; the delta repeats.
5. **record** — verbatim excerpts + the channel + the delta + N.

## The verify checklist per channel

```
body:     bad1==bad2? (masked)  good!=bad?  second-bad==bad1?
status:   bad1==bad2?           good!=bad?  location identical?
timing:   N>=8?  interleaved?  median delta >3x jitter?  re-run?
side:     envelope identical bad1==bad2?  good!=bad?
```

All "yes" on any channel → the oracle is verified on that channel.

## The account-existence verify

To confirm a SPECIFIC candidate name is a real account:

```bash
curl -i -X POST -d 'user=CANDIDATE&pass=x' "$BASE/login" > cand
diff cand good    # cand should match the KNOWN-good response shape
diff cand bad1    # cand should DIFFER from the bad response shape
```

A candidate whose response matches the known-good arm (and differs from
the bad arm) is a confirmed account — verbatim excerpts attached.

## The throttle verify

- absence: `12-15 reqs → no 429/captcha/lock/delay` — the bounded count
  IS the measurement, not "didn't notice"
- presence: the N at which `429`/`423`/captcha/delay first appears
- bypass: a spoofed `X-Forwarded-For`/fresh-session request returns to
  pre-limit behavior after the limit fired

## The hook call

```bash
python3 tools/hooks.py post-probe <chal> --hypothesis-id <h> \
  --class web-user-enum --verdict confirms --evidence-kind class \
  --evidence '<the verbatim excerpt>' --response '<the full response>'
```

The excerpt must be a substring of the response — the gate checks.
