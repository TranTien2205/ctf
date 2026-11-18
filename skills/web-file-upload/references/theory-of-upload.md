# The Theory — why file upload is unsafe, in one page

## The primitive — attacker writes a file into app-controlled storage

Everything else is consequences:

```
file lands where a server maps it to a handler  → exec by fetch
file lands where an interpreter includes it     → exec by include
file lands where a parser reads it              → parser attack (XXE/deser/gs/magick)
file lands over a config/template/source        → behavior change → exec
file lands where a person/bot opens it          → client-side exec (macro/xss/formula)
file's NAME reaches a sink                      → injection (sqli/cmd/ssti/log/crlf)
file's SIZE reaches an unbounded consumer       → DoS
file's EXISTENCE shifts state                   → race, second-order
```

## The four preconditions — each attack needs its subset

- **exec-by-serve**: exec-mapped dir + exec ext + fetchable URL
- **exec-by-include**: include primitive + file reachable by the include
  path (any ext — `<?php` inside an image executes under include)
- **parser attack**: a consumer exists + the payload survives to it
- **overwrite**: path control + a target that gets loaded
- **name-injection**: the name reflects/flows into an unsafe sink

## The defense taxonomy — every check answers one question

| Check | Answers | Residual attack when it's the only check |
|---|---|---|
| extension list | is the name's suffix safe? | polyglot/config/consumer/include |
| MIME header | does the client claim it's safe? | the claim is free |
| magic bytes | does it LOOK like the type? | polyglot — looks like one, is another |
| structural parse | does it PARSE as the type? | payload inside a real container |
| re-encode | does it survive processing? | pixel-level or consumer-side |
| AV/grep | does it CONTAIN bad bytes? | obfuscation, non-shell payloads |
| size cap | is it small? | none — DoS only |
| path sanitize | does the name stay inside? | traversal forms it misses |

A defense in depth needs the check AND the execution boundary — a strong
validator on a dir with `engine off` is robust; the same validator on an
exec-mapped dir is one polyglot away from RCE.

## The bug's real shape — disagreement, not absence

The validator and the consumer/storer are different parsers — the exploit
is almost never "no check" but "the check and the consumer parse the file
(or the request) differently":

- validator reads `filename`, store uses `filename*`
- validator checks ext, Apache maps `x.php.xyz` by walking right-to-left
- validator checks first ext, server uses last
- validator sniffs magic, consumer parses the same file as a different format
- validator checks the first part, store writes the last
- validator reads the CD name, extractor writes the local-header name

That's the whole bug class — find the two parsers, find where they disagree.

## The "impact is downstream" restatement

Upload bugs are never about the upload — they're about what a file of
your choosing does where it lands. The skill is tracing "bytes → disk →
consumer → effect" — every reference file maps one link of that chain.

## Where the class lives vs neighbors

- path control → `file-overwrite`/`path-traversal` (the write IS the bug)
- the file parses → `web-xxe`/`web-deserialization`/`web-ssti` (the bytes
  are a typed payload)
- the file is fetched-from → `web-ssrf` (upload-by-url)
- the file renders → `web-xss`/`svg-attacks` (client-side)
- the name injects → `filename-injection`/`web-sqli`/`web-command-injection`
- the endpoint smuggles → `web-request-smuggling`
- the process races → `web-race-condition`

The router's job ends here — the depth files pick the sink.

## Output to record

- the primitive identified + the link it hangs on
