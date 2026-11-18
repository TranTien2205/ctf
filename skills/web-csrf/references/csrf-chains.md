# CSRF chains — what the write unlocks

A CSRF write is rarely the end — it's the foothold. The write's
value is what it enables next: a credential swap, a config change,
a state that the next layer reads.

---

## 1. CSRF → XSS — the stored-write chain

```text
a CSRF writes a payload into a field that renders on a page the
victim visits — the CSRF stores an XSS:
- the CSRF sets the victim's 'bio' to '<script>...</script>'
- the victim's next profile-view runs it — stored XSS
- now you have JS in their origin — the full attack surface
```

The CSRF is the delivery that plants the XSS.

## 2. CSRF → account-takeover — the credential-write chain

```text
- CSRF changes the victim's email → password-reset to the new email
- CSRF sets a new password directly
- CSRF adds the attacker's email as a recovery contact
- login-CSRF swaps the session to the attacker's account (SSOS)
```

The write changes a credential/recovery field → full takeover.

## 3. CSRF → privilege-escalation — the role-write chain

```text
- CSRF grants the attacker 'admin' role
- CSRF adds the attacker to a privileged group
- CSRF enables a feature-flag on the victim's account
- CSRF approves a pending request
```

The write flips a permission bit → the next read is privileged.

## 4. CSRF → data-write — the exfil chain

```text
- CSRF transfers an asset to the attacker's account
- CSRF posts the flag/secret into a field the attacker reads
- CSRF changes a 'share' setting to public
- CSRF sends a message containing the secret
```

The write moves data into a reachable place → the readback is the
exfiltration.

## 5. CSRF → config-write — the foothold chain

```text
the TornadoService card: CSRF registered a machine → then class
pollution on the registered machine's object → signed-cookie secret
recovery → forge → /stats → flag. the CSRF write was the ENTRY that
made the next layer reachable.
```

The write sets up the next primitive — a config value the next
layer reads, a registered object, a state that unlocks a route.

## 6. CSRF → SSRF — the URL-write chain

```text
- CSRF sets a webhook/callback URL the server later fetches — the
  CSRF plants an SSRF target
- CSRF configures an import/fetch URL
- CSRF sets an avatar/image URL the server downloads
```

The write stores a URL → a later server-fetch is the SSRF.

## 7. CSRF → file-write — the upload-chain

```text
- a multipart CSRF uploads a file — the file lands and executes
- a CSRF writes content that gets saved to a template/config
```

The write delivers content → a later render/execute is the chain.

## 8. CSRF → race — the timing-write chain

```text
- a CSRF that triggers a state a race can exploit
- a CSRF that registers an account a race can hijack (SSOS's
  registration-race pairing)
```

## 9. CSRF → the flag directly — the rare case

```text
- a CSRF that writes the flag into a readable field
- a CSRF that triggers a flag-reveal
- a CSRF'd admin-action that returns the flag
```

Rare — usually the flag needs the next layer after the write.

## 10. The chain-evaluation — what the write buys

```text
after confirming the write lands, ask: what does it ENABLE?
- a credential swap → account-takeover → the flag on the victim's
  (or your) account
- a config write → the next layer's primitive → the chain
- a data move → the readback → the flag
- a foothold → the next bug class

the CSRF's value is the NEXT step it makes reachable. a write that
lands but enables nothing is inert — a different write or class.
```

## 11. The two-card chains — the grounded shapes

```text
TornadoService: CSRF → registered-machine → class-pollution →
  signed-cookie forge → /stats → flag
  (the CSRF write was the foothold for the pollution layer)

SSOS: CSRF(login) → cookie-swap in shared jar → bot writes flag
  to attacker's account → flag read from own account
  (the CSRF write was the credential-swap)
```

## 12. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "csrf-chain: write X -> enables <next-layer-primitive>"
```
