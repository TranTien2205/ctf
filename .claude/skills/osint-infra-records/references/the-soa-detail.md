# SOA — serial + responsible

The SOA serial is a date-ish number (zone age); the rname field is
the responsible-party email (encoded). Reveals the operator.

## The fields

- serial — often `YYYYMMDDNN`, the zone version/date.
- rname — `admin.domain.com` = `admin@domain.com`.
- refresh/retry/expire/minimum — the zone's timing.
The rname encodes the admin email — a useful contact.
