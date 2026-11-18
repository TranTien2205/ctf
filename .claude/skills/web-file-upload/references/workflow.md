# Workflow — the file-upload working loop

## The loop, with what each step proves

```
1. surface map        → every endpoint that takes a file (detection.md)
2. marker upload      → where it lands + how it's served (retrieval.md)
3. rejected-ext probe → which validation layer answers (detection.md)
4. layer bypass       → the technique for THAT layer only
5. execution path     → serve+exec / include / phar / template / parser / argv
6. impact             → flag read, code exec, or a proven consumer attack
```

Never iterate step 4 while a step-5 question is unanswered — a bypassed
upload with no execution path is storage, not a chain.

## Time-boxing

```
0–10 min   surface + marker + rejected-ext probe
10–20 min  layer bypass attempts (one family at a time)
20–30 min  execution path construction OR consumer identification
30 min+    escalate — try a different endpoint or a different class
```

The controller's class budget is the outer bound; the inner rule is one
bypass family per probe round.

## The decision tree — which reference when

```
upload rejected?
 ├─ "extension"           → extension-bypass.md
 ├─ "media type"/415      → mime-bypass.md
 ├─ "invalid/corrupted"   → content-bypass.md → polyglot-files.md
 ├─ "malware"/AV          → filter-evasion.md
 └─ silent/none           → parser-differentials.md

upload accepted, file fetchable?
 ├─ executes              → webshell-templates.md
 ├─ served verbatim       → include/phar/template — execution-paths.md
 ├─ attachment/octet      → execution-paths.md
 └─ not fetchable         → second-order-processing.md

file lands in weird place?
 ├─ outside upload dir    → path-traversal.md → file-overwrite.md
 ├─ inside archive        → archive-attacks.md
 └─ on s3/gcs             → cloud-storage.md

upload is an archive       → archive-attacks.md
upload is an image         → image-attacks.md → svg-attacks.md
upload is a document       → document-attacks.md
upload is media            → video-audio-attacks.md

still stuck?
 ├─ check framework-specific sink → framework-sinks.md
 ├─ race/temp-file window         → race-and-temp-files.md
 ├─ re-check execution paths      → execution-paths.md
 └─ escalation rungs              → controller
```

## The discipline — the three rules

1. **A marker proves a path, not an exploit.** `marker.php` serving back
   `<?php echo "hi"` verbatim = served-raw — that IS a finding only if
   the flag is in the source; for RCE you need `executed` output.
2. **Bypass the layer that answered, not all layers.** If the rejection
   was a magic-byte check, don't burn probes on double-extensions.
3. **The consumer is often the sink.** Before iterating extensions, ask
   "what reads this file later" — the parser is usually softer than the
   uploader.

## Probe sequence — the minimum-viable run

```bash
# 1. marker probe
curl -s -F 'f=@m.txt' "$BASE/upload"          # returns path/url?

# 2. fetch-back
python3 tools/web/upload_probe.py verify \
  --url "$BASE/uploads/m.txt" --expect-source 'UNIQUE_MARKER'

# 3. rejected-ext probe
curl -s -F 'f=@m.php' "$BASE/upload"          # which layer rejects?

# 4. one bypass from the layer's family
# 5. verify exec/impact
python3 tools/web/upload_probe.py verify \
  --url "$BASE/uploads/x.php" --expect-source '<?php'
```

## Evidence discipline — what to write to the ledger

- the verbatim accept/reject response per probe — `tools/hooks.py
  post-probe` requires the quote to be a substring of `--response`
- the classify on fetch-back: `served-raw`/`executed-or-transformed`/
  `blocked`/`gone`
- the layer named by the rejection + the bypass that defeated it
- the execution path + the verbatim output

## Escalation order — when stuck at 25 probes / 45min

1. `chain_match` — has this shape been solved here?
2. `reclassify` — is it actually SSRF/XXE/template wearing upload clothes?
3. `writeup_search` — the challenge name + event → a published solve
4. `novel_plan` — layered white-box plan with falsifiers per layer
5. `fanout_sweep` — parallel bug-class probes
6. `solver_handoff`

A blocked upload challenge usually hides one of: a second upload endpoint,
a consumer-side attack (`second-order-processing.md`), or a traversal into
an overwrite (`file-overwrite.md`).

## Falsifier for the whole class

Re-stated: no upload becomes retrievable through any enumerable path AND
no parser/consumer ever touches the bytes. Both halves required — files
that are never served but ARE parsed remain exploitable.
