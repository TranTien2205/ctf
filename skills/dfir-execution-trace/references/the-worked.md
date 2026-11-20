# Worked — Sysmon 1 -> 3 by ProcessGuid

`--event-id 1 --field-contains CommandLine=-enc` -> 1 match,
ProcessGuid `{a1b2...}`; `--event-id 3 --field ProcessGuid=...`
-> answer.value `203.0.113.77` — the connection the encoded
command made.

## The chain

1 -> Guid -> 3 -> the destination.

## The answer

203.0.113.77 via the GUID join.
