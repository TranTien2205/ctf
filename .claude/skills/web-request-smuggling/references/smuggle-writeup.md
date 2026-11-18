# Smuggle writeup — documenting the chain

## The structure — the desync's narrative

```text
1. The setup — front-end X, back-end Y — the pair's names
2. The disagreement — which header they disagree on
3. The probe — the ambiguous request that proves it
4. The smuggle — the request that lands
5. The impact — what the smuggle reaches
6. The evidence — the verbatim response excerpt
```

## The card — `knowledge/chains/`

```json
{
  "id": "request-smuggling-<challenge>",
  "signals": ["the signals that named it"],
  "first_confirming_probe": "the probe that worked",
  "the_smuggle": "the working smuggle",
  "the_readback": "how the output reached you",
  "traps": ["the byte-count, the Host, the trailing fragment"],
  "blast_radius": "shared-instance notes"
}
```

## The verbatim excerpt — the flag's bytes

```text
the smuggle's response body — the flag text — verbatim
```

`evidence-rules.md` — the `--evidence` must be a substring of
`--response`.

## The pair-name — CL.TE / TE.CL / TE.TE / CL.CL / CL.0 / H2.*

The pair's name — `desync-taxonomy.md` — the writeup's title.

## The traps — what cost time

- the byte-count off-by-one
- the wrong `Host:` vhost
- the missing trailing fragment
- the non-shared connection
- the front re-parsing the tunnel

`common-mistakes.md`.

## The readback — how the output reached you

- the self-poison `GET /` — `response-poisoning.md`
- the stored-param — `session-hijack.md`
- the echo — `smuggle-readback.md`
- the OOB-listener — `blind-smuggle.md`

## The chain's falsifier — what closed it

```text
the control request — the same request without the ambiguity —
returned the normal response — the desync's signal was absent
```

The falsifier — `evidence-rules.md`.

## The `classify_solve` — file the solve

```bash
python3 tools/classify_solve.py --chain <chain-id>
```

After a flag — the solve lands in the right bug-class skill —
`LEARNING_LOOP.md`.
