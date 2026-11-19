# Evidence catalogue — the per-attack check

## The check, by what the attack returns

| Attack | Returns | The check |
|---|---|---|
| `batch-gcd` | `p` | `p*q==n`, `p|n`, `1<p<n` |
| `common-modulus` | `m` | `pow(m,e1,n)==c1` |
| `fermat` | `p`,`q` | `p*q==n` |
| `wiener` | `d` | `pow(c,d,n)==m`, `pow(m,e,n)==c` |
| `boneh-durfee` | `d` | `pow(c,d,n)==m`, `pow(m,e,n)==c` |
| `coppersmith-*` | `p`/`x` | `p|n`, `p*q==n` |
| `small-e-root`/`nth-root` | `m` | `pow(m,e)==c` |
| `hastad` | `m` | `pow(m,e)==x` (CRT value) |
| `pollard-pm1` | `p` | `1<gcd<n`, `p*q==n` |
| `franklin-reiter` | `m` | `pow(m,e,n)==c` |
| `crt` residues | `m` | `pow(m,e,n)==c` |
| `crt` Bellcore | `q` | `gcd==q`, `p*q==n` |
| `crt` dp | `p` | `p*q==n` |
| `factor-from-d` | `p`,`q` | `p*q==n` |
| `rsa-decrypt` | `m` | `pow(m,e,n)==c` |
| `eth-root` | `m` candidates | `pow(m,e,n)==c` + format |

## The evidence tuple (for `solved/`)

```python
{
  'challenge': <name>,
  'discriminator': <the row that fired>,
  'attack': <the crypto_attack.py id>,
  'bound': <the measured bound>,
  'input': <the leaked values>,
  'recovered': <p,q | d | m>,
  'verify': 'pow(m,e,n)==c' | 'p*q==n',
  'response': '<the pow/gcd output>',
}
```

## The quote rule

`hooks.py post-probe` asserts `--evidence` is a substring of `--response`. The
"response" is the `pow`/`gcd` output — put the `pow` result in `--response` and
the claim in `--evidence`.
