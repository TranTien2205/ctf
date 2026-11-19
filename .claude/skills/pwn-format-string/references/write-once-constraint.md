# One write per call — the shot budget


Each format call is one shot: plan all %n writes for the call — you can't
retry a write inside the same call once the specifier passed.

## Steps

1. In one call: all %n writes execute in order — compose multi-target
   writes carefully.
2. The cumulative count constraint applies within the call.
3. A re-triggerable service gives more shots.

## Falsifier

The needed writes can't fit one call's count sequence and the service is
one-shot.
