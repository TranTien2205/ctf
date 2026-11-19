# Troubleshoot — the host-header failures, exhaustively

The failures — what went wrong, and the fix.

---

## 1. The reflected host trap — a lead, not a finding

```text
symptom:   a reflected host in the response — a canonical URL, a link,
           a script points to canary.example
cause:     a reflected host is only a lead — the finding needs the host
           reaching a decision — a link the victim clicks, a path the
           middleware applies, a domain a cookie binds to
fix:       read the downstream — a reset link, a cache key, a Location,
           a Set-Cookie, a middleware rewrite
```

## 2. The reset-link trap — the reset flow's reach

```text
symptom:   a reset link that doesn't reach the victim
cause:     password-reset poisoning requires a real reset flow — request
           a reset for your OWN account and inspect the delivered link
fix:       do not reset other accounts — request your own reset and
           inspect the link
```

## 3. The 400 trap — a negative result, not a retry signal

```text
symptom:   a 400 on a bad host
cause:     some frameworks read `Host` only after validating it against
           a server list — a 400 on a bad host is a negative result,
           not a retry signal
fix:       a different header, a different surface, or a different class
```

## 4. The forwarded-header trap — the proxy's strip

```text
symptom:   a client-supplied forwarded header that doesn't reach the app
cause:     a proxy that strips the client-supplied forwarded header →
           the header doesn't reach the app → the bypass fails
fix:       a different header, a different surface, or a different class
```

## 5. The forwarded-header trap — the proxy's verify

```text
symptom:   a client-supplied forwarded header that the proxy rejects
cause:     a proxy that verifies the forwarded header it added → a
           client-supplied header is rejected → the bypass fails
fix:       a different header, a different surface, or a different class
```

## 6. The non-header check trap — the check's input

```text
symptom:   a reflected forwarded header that doesn't reach a decision
cause:     a trust check that reads a different input (a session, a
           token, a signature) → the header isn't the check's input
fix:       a different class
```

## 7. The duplicated Host trap — the parsing differential

```text
symptom:   a duplicated Host that the proxy and the app parse the same
cause:     the proxy and the app parse the same way → no confusion
fix:       a different header, a different surface, or a different class
```

## 8. The malformed Host trap — the parsing edge

```text
symptom:   a malformed Host that the proxy and the app parse the same
cause:     the proxy and the app parse the same way → no confusion
fix:       a different header, a different surface, or a different class
```

## 9. The absolute-URI trap — the request-line differential

```text
symptom:   an absolute-URI Host that the proxy and the app parse the same
cause:     the proxy and the app parse the same way → no confusion
fix:       a different header, a different surface, or a different class
```

## 10. The rewrite trap — the middleware's check

```text
symptom:   a rewritten path that doesn't reach a gated route
cause:     the middleware's trust check reads a rewrite header's value —
           a rewritten path reaches a gated route — an ACL bypass
fix:       a different header, a different surface, or a different class
```

## 11. The rewrite trap — the dummy outer path

```text
symptom:   a dummy outer path that doesn't reach a gated route
cause:     a dummy outer path — the middleware rewrites the inner path —
           the app's route reads the rewritten path — a route-confusion
fix:       a different header, a different surface, or a different class
```

## 12. The rewrite trap — the root outer path

```text
symptom:   a root outer path that doesn't reach a gated route
cause:     a root outer path — the middleware rewrites the inner path —
           the app's route reads the rewritten path — a route-confusion
fix:       a different header, a different surface, or a different class
```

## 13. The multi-header trap — the combined injection

```text
symptom:   a combined injection that doesn't reach a privileged route
cause:     a multi-header bypass — a combined injection — a forged host +
           a forged flag — a local + an internal check → a privileged
           route reached
fix:       a different header, a different surface, or a different class
```

## 14. The multi-proxy trap — the chained normalization

```text
symptom:   a chained normalization that doesn't reach a per-layer
           differential
cause:     a multi-proxy chain — a header each strips differently — a
           chained normalization boundary — a per-layer differential
fix:       a different header, a different surface, or a different class
```

## 15. The budget trap — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
