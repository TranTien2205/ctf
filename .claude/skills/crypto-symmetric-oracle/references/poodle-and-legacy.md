# POODLE and the legacy TLS padding family

POODLE is the CBC padding oracle against SSL 3.0 / TLS CBC ciphersuites.
The same shape appears in CTF services that expose a TLS-like decrypt.

## The TLS difference

TLS pads with 'pad_len byte = last byte, pad content arbitrary' (pre-1.1) —
the oracle question is 'is the last byte equal to the pad length', a much
weaker signal than PKCS#7, but usable with record shifting.

| Variant | Pad semantics | Oracle answer |
|---|---|---|
| PKCS#7 (app-layer) | last N bytes = N | strict — full Vaudenay |
| SSL3 POODLE | last byte = pad len only | weaker — needs block shifting |
| TLS1.0 explicit IV | first block is IV | treat IV as C_{i-1} |
| Lucky13 timing | pad check timing differs | timing-channel variant |

## CTF translation

If the handout says 'SSL3' or shows arbitrary pad bytes in the last block,
the recipe changes: you can't force '\\x01' cleanly — instead shift the
target byte into the last position by constructing a record one byte longer.

## Detection

A handshake error or record-layer reject that differs between 'pad ok' and
'pad bad' is the same distinguisher, just transported inside TLS alerts.

## Falsifier

The service uses TLS ≥ 1.2 AEAD (GCM) or authenticates records before
decryption — the channel is closed identically to app-layer GCM.
