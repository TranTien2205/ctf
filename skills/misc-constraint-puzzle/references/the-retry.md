# Retrying a failed send — idempotence

A dropped send mid-round — resend only if the protocol tolerates it;
a duplicate answer can desync round counters.

## Idempotence

Resend only if the protocol tolerates duplicates.

## Idempotent

Resend only if duplicates are safe.
