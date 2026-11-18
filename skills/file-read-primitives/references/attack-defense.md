# Attack-Defense — the file-read in a live-ad contest

## The ad-context — the flag rotates

In attack-defense the flag isn't static — it rotates each tick — the
file-read must find WHERE the flag lives, then the exploit-loop reads
it each tick — `tools/ad/` is the sibling loop.

## The flag-store — where the tick-flag lives

```
/var/flag /flag /app/flag /opt/flag /srv/flag
/run/flag /run/app/flag /run/secrets/flag
/var/run/secrets/* /run/secrets/* /etc/secrets/*
/tmp/flag /dev/shm/flag /dev/shm/app/flag
/proc/1/environ → FLAG=... — the env-injected tick-flag
/app/.env — FLAG=...
/app/config.php — FLAG
/etc/app/flag
/root/flag — root-perm — needs a write or a uid-0 read
```

`flag_farm` — `tools/ad/flag_farm` — the tick-loop — the flag-store is
the read-target.

## The "the flag is a service-response" — the service-read

The flag is served by the service itself — `GET /flag`/`/internal/flag`/
`/debug/flag`/`/api/flag` — `tools/ad/` — the flag is a RESPONSE not a
file — the service-read.

## The "the flag is a db-row" — the db-flag

`SELECT flag FROM flag_table` — the flag is a DB-row — read the DB-
creds → connect → select — the db-flag — `web-sqli` chain.

## The "the flag is a sibling-service" — the sibling-flag

`http://flag-svc/flag` — a flag-service container — the sibling-flag —
the SSRF-read — `web-ssrf` chain.

## The "the flag is a mounted-secret" — the secret-mount

`/run/secrets/flag`/`/var/run/secrets/kubernetes.io/serviceaccount/*` —
the secret-mount — `container-world.md` — the mounted-flag.

## The "the flag is env-injected" — the env-flag

`/proc/1/environ`/`/proc/self/environ` — `FLAG=flag{...}` — the env-
injected flag — the Docker-ENV flag — `container-world.md`.

## The "the flag is in the checker" — the checker-read

The checker hits the service → the service stores the flag → the
exploit-loop reads the flag — `tools/ad/` — the checker-driven flag —
a read that lands on the flag after the checker writes it.

## The "the flag is a checker-artifact" — the artifact-flag

`/var/lib/checker/flag`/`/tmp/checker/*` — the checker's own flag-artifact —
a checker-managed flag — `tools/ad/`.

## The "the flag is a heartbeat-token" — the heartbeat-flag

The checker emits a heartbeat-token the service must return — a
heartbeat-flag — a token-in-response not a file — `tools/ad/`.

## The "the flag is a scoreboard-submitted" — the submit-flag

The flag is submitted to a scoreboard — the read is the flag's VALUE
before submit — `tools/ad/flag_farm` — the submit-loop.

## The "the read is a farm-step" — the farm-chain

`tools/ad/flag_farm` — the exploit-loop — read→extract→submit each
tick — the farm-chain — the file-read is a step in the tick-loop.

## The "the read is a sla-step" — the sla-check

`tools/ad/sla_check` — the SLA-check — the flag-store's availability
matters — a read that breaks the SLA costs availability — the read's
blast-radius — `ad-patch-without-breaking-sla` skill.

## The "the read is a stealth-read" — the quiet-read

A read that doesn't log/alert — a `file_get_contents` is quieter than
an `include` — a `?file=/flag` is quieter than `?page=php://input` —
the stealth-read — the ad-contest quiet-read.

## The "the read is a patch-target" — the defender's view

The defender patches the read-sink — the attacker's read dies — the
defender's `open_basedir`/`realpath`-confine is the kill — the attack-
defense read-patch arms-race — `ad-patch-without-breaking-sla`.

## The "the read is a traffic-mine" — the traffic-chain

`tools/ad/traffic_mine` — the traffic-mine — a captured exploit's
read-pattern is replayable — the file-read is replayed each tick —
the traffic-chain.

## The "the read is a cap_split" — the cap-split

`tools/ad/cap_split` — the capture-split — a capture of the exploit's
read-request is the replay-template — the cap-split chain.

## The "the read is a tick-answer" — the tick.py answer

`tools/ad/tick` — the tick-answer — which of the runbook's three
steady-state questions is unanswered — the file-read is a step in
the tick-loop — the ad-contest file-read is a service-cadence.

## The "the read is a host-diff" — the host-diff

`tools/ad/host_diff` — the host-diff — a change on EVERY host is the
image, a change on ONE host of eight is a person — the file-read's
output is a diff-input — the host-diff chain.

## The "the read is a secret-inventory" — the secret-inventory

`tools/ad/secret_inventory` — the secret-inventory — credentials
grouped by fingerprint — the widely-shared one is rotated — the file-
read's output is a secret-inventory input — the secret-chain.

## The "the read is a preflight-check" — the preflight

`tools/ad/PREFLIGHT.md` — the preflight — what to install tonight —
the file-read reveals which tools are missing — the preflight-chain.

## The "the read is a runbook-step" — the runbook

`tools/ad/RUNBOOK.md` — the runbook — the first thirty minutes — the
file-read is a step in the runbook — the runbook-chain.
