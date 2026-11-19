# Common mistakes — the host-header traps, exhaustively

The traps — a reflected host is a lead, not a finding.

---

## 1. The reflected host trap — a lead, not a finding

```text
a reflected host in the response is only a lead — the finding needs
the host reaching a decision — a link the victim clicks, a path the
middleware applies, a domain a cookie binds to.
```

## 2. The reset-link trap — the reset flow's reach

```text
password-reset poisoning requires a real reset flow — request a reset
for your OWN account and inspect the delivered link. Do not reset
other accounts.
```

## 3. The 400 trap — a negative result, not a retry signal

```text
some frameworks read `Host` only after validating it against a server
list; a 400 on a bad host is a negative result, not a retry signal.
```

## 4. The forwarded-header trap — the proxy's strip

```text
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
```

## 5. The forwarded-header trap — the proxy's verify

```text
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
```

## 6. The non-header check trap — the check's input

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → a different class.
```

## 7. The duplicated Host trap — the parsing differential

```text
a duplicated Host — the proxy and the app parse differently — the
proxy reads the first; the app reads the second → a differential.
```

## 8. The malformed Host trap — the parsing edge

```text
a malformed Host — a trailing dot, a double-dot, an @-separator, a
#-separator, a ?-separator, an empty host, a forged port → a parsing
edge → a differential.
```

## 9. The absolute-URI trap — the request-line differential

```text
an absolute-URI Host — a request-line differential — the proxy reads
the Host header; the app reads the absolute-URI → a differential.
```

## 10. The rewrite trap — the middleware's check

```text
the middleware's trust check reads a rewrite header's value — a
rewritten path reaches a gated route — an ACL bypass, a route-confusion,
an internal route reached.
```

## 11. The rewrite trap — the dummy outer path

```text
a dummy outer path — the middleware rewrites the inner path — the app's
route reads the rewritten path — a route-confusion.
```

## 12. The rewrite trap — the root outer path

```text
a root outer path — the middleware rewrites the inner path — the app's
route reads the rewritten path — a route-confusion.
```

## 13. The multi-header trap — the combined injection

```text
a multi-header bypass — a combined injection — a forged host + a forged
flag — a local + an internal check → a privileged route reached.
```

## 14. The multi-proxy trap — the chained normalization

```text
a multi-proxy chain — a header each strips differently — a chained
normalization boundary — a per-layer differential.
```

## 15. The budget trap — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
