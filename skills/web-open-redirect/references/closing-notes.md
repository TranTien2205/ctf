# Closing notes — the class's operating summary

## The class's core lesson

```text
an open-redirect is a TRUST-LAUNDERING primitive — the server is a trusted
issuer of destinations; an unchecked param makes it issue the attacker's.
the confirm is a verbatim Location: carrying the canary; the falsifier is
a safe Location on every arm; the value is the laundered-trust chain.
```

## The operator's operating-loop

```text
1. map the param vocabulary      -> param-inventory.md
2. find the carrier               -> detection.md — Location/meta/JS/Referer/stored
3. send the canary                -> the verbatim Location
4. read the fingerprint           -> decision-table.md — names the filter
5. fire the matching arms         -> filter-bypass-deep.md + payload-*
6. the uniform-falsifier check    -> falsifiers-deep.md — Location: <safe> on all?
7. route the confirm to the chain -> chain-routes.md — the laundered-trust
8. record — the verbatim evidence -> evidence-rules-deep.md
```

## The discipline that keeps the operator honest

```text
- the verbatim Location: is the ONLY class-confirm — "it redirected" is not
- curl -si + grep -i location — never -L; the header is the evidence
- a Location: evil.com resolves RELATIVE — same-origin, not the gap;
  the cross-origin forms are //, https://, \\
- a uniform Location: <safe> closes THE SWEPT SURFACE — record the arms-
  tried + reopen on an unswept endpoint/carrier
- the meta/JS/Referer/stored are client-side twins — different carriers,
  same class — record the carrier
- a confirmed canary routes to the chain — the standalone Location: is
  the class-answer only if the challenge is the phishing shape
- the class is CATALOGUE — a verbatim Location:-canary on a live target
  is the local confirm that upgrades it
```

## The field-note loop — turning the catalogue into experience

```text
the corpus is published knowledge — a solve records the MEASURED filter
shape, the arm that fired, the verbatim Location, the chain it fed:
  field-note: the /login?next= filter was a startswith('/'); //evil.com
              fired; the OAuth launder reached the flag.
each solve upgrades the catalogue — `../field-notes.md` accumulates the
local experience; `LEARNING_LOOP.md` is the format; `classify_solve.py`
files the solve into the class
```

## The contract — the class's operating rule

```text
send one external destination; read the verbatim Location; a canary in
the Location confirms; a safe Location on every arm is the falsifier;
route the confirm to the laundered-trust chain for the flag-path.
```

## The corpus index — the file to start with

```text
the 60-second pass           -> quick-reference.md
the operating procedure      -> field-manual.md
the param vocabulary         -> param-inventory.md
the bypass corpus            -> filter-bypass-deep.md + payload-dictionary.md
the parser gaps              -> parser-differentials.md
the chain                    -> chain-routes.md
the evidence                 -> evidence-rules-deep.md
the verdict                  -> detection-verdicts.md
the falsifier                -> falsifiers-deep.md
the honest state             -> verified-chains.md — a catalogue class
```
