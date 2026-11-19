# Error-message taxonomy — what the reject actually tells you — map

| Layer | Typical answer | Distinguishes |
|---|---|---|
| Transport/framework | 400 bad request, 500 stack trace | malformed input vs processed input |
| Encoding layer | 'invalid hex', 'bad base64' | encoding vs crypto failure |
| Padding check | 'bad padding', silent reject | pad-valid vs pad-invalid |
| MAC/tag check | 'authentication failed' | MAC pass vs fail |
| Application | 'invalid user', 200-with-error | plaintext-level checks |

Expanded rows and abort conditions: `error-taxonomy.md` and `error-taxonomy-deep.md`.
