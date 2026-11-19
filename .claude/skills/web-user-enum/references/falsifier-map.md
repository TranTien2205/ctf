# Falsifier map — the kill condition per channel per form

## The class-level falsifier

Every account-touching endpoint, every channel, `KNOWN` vs `FAKE` vs
`FAKE2`: identical raw body (masked), identical status + `Location`,
identical `-sv` envelope, indistinguishable N>=8 timing medians, no
send-side, no lock — on EVERY form. The class is closed only when the
coverage matrix is all `uniform`.

## Per-channel falsifiers

| Channel | Kills the oracle when |
|---|---|
| body | the masked raw-byte diff is identical on all three arms |
| status+loc | the code and `Location` are identical on all three arms |
| timing | the N>=8 medians overlap within jitter on all three arms |
| side | the `-sv` envelope/cookie/send/lock identical on all arms |
| direct | no exists-endpoint; `?u=KNOWN`/`?u=FAKE` return the same |
| register | `KNOWN`-taken and `FAKE` arms return the same response |
| reset | the send/response/redirect identical on all three arms |
| graphql | `userByEmail`/`login` resolvers return uniform results |
| lock | no `423` on a real name at a bounded count |

## Per-form falsifiers

| Form | Kills it when |
|---|---|
| login | all 4 channels uniform on the three arms |
| register | the taken-check returns the same for `KNOWN`/`FAKE` |
| reset | the send-side + response uniform on all arms |
| check-* | `?u=KNOWN`/`?u=FAKE` return the same boolean |
| unlock | `KNOWN`/`FAKE` return the same response |
| mfa/otp | the send + response uniform on all arms |
| invite | the response/send uniform on all arms |
| api/graphql | the typed error/field/resolver uniform |
| users/{id} | `200`/`404` does not track existence |

## The timing falsifier — the specific one

The timing oracle dies when:
- `median(good)` − `median(bad)` ≤ 2× jitter, or
- the delta does not repeat on a re-run, or
- `FAKE` vs `FAKE2` also differ (it's noise, not the username-class), or
- the app hashes a dummy on the miss (a `stdev` read confirms the
  equalization — the defense, not an absence)

## The coverage falsifier

A `/login`-only uniform read does NOT close the class — register/
reset/check/api/graphql are separate cells. The falsifier is per-cell;
the class dies when every cell is uniform.

## The "uniform message" falsifier — inverted

A uniform text message is NOT a falsifier for the class — it is a
falsifier for the body/text channel only. The timing/side/send/lock
cells remain open. Treat a uniform message as one closed cell, not a
closed class.

## The falsifier grammar

`falsified: <form>:<channel>` — the measured-uniform cell. Never
`falsified: web-user-enum` until every (form × channel) cell is measured.
