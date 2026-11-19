# Field manual — one page per move

## The five-minute identification

1. Replay: same input twice → deterministic?
2. Length: grow input → block or stream?
3. Repeat: 'A'*48 → ECB fingerprint?
4. Corrupt: pad-vs-MAC distinguishable?
5. Tag: checked before decrypt?

Each probe rules a branch in or out. The ordering is deliberate: cheap and
class-determining first, expensive and attack-specific last.

## The toolbox

| Job | Tool |
|---|---|
| Byte-at-a-time ECB over HTTP | `tools/ecb_oracle.py` |
| CBC padding oracle over HTTP | `tools/pad_oracle.py` |
| GCM forbidden attack | `tools/gcm_nonce.py` |
| RSA parity oracle (boundary) | `tools/parity_oracle.py` |
| Crib-drag two same-keystream cts | `tools/crypto_attack.py crib-drag` |
| Length-extension forge | `tools/crypto_attack.py length-extension` |
| Single-byte XOR | `tools/crypto_attack.py single-byte-xor` |

## The evidence discipline

- post-probe for every class/impact claim, with the verbatim response.
- pre-flag only on live-response bytes.
- Negatives recorded with the probe that produced them.

## The exits

- Class falsifier (authenticated before decrypt): record + route out.
- Budget spent with strategies untried: escalate, don't variant-loop.
- Flag verified: close, write the chain.
