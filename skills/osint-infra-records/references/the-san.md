# Certificate SANs — the sibling leak

crt.sh shows every SAN ever issued for a domain — internal,
staging, and sibling hostnames included. The real next step is
usually a SAN-named host the challenge never handed you.

## Reading the SANs

- `internal.` / `dev.` / `staging.` / `admin.` names — the
  non-public hosts.
- `flag.` / `secret.` / `backup.` — the planted next step.
- Wildcard SANs — a `*.domain` doesn't name a specific host.
- The issuer + validity dates corroborate which certs are live.

Each distinct SAN is a candidate next host — query its records.

## The sources

Live cert SANs (openssl s_client) + crt.sh history — the union is the full sibling list; dedup them.

## Priority

Non-public prefixes (internal/dev/staging/admin/flag/secret/backup/mail) are the candidates; a wildcard SAN names nothing.
