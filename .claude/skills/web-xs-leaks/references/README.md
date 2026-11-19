# web-xs-leaks — reference index

Cross-site leak / browser side channel — a bot reads under the
victim's session; the response is opaque but a side-channel leaks a
bit or a character-set.

## The sub-shape — name it first

- `detection.md` / `detection-deep.md` / `detection-checklist.md` — the
  signals; the bot, the CSP, the reflected secret, the server-state.
- `class-boundary.md` — vs web-cors (a read), web-csrf (a write),
  web-xss (JS on the target), web-cache-poisoning (a store), JSONP/
  postMessage (a real read).
- `summary.md` / `cheatsheet.md` — the one-page reference.

## The channels — the oracle catalog

- `oracles-index.md` — every channel indexed by type.
- `classic-oracles.md` / `classic-deep.md` — the client-side measures:
  frames.length, onload/onerror, timing, cache, :visited, window.open.
- `css-oracle.md` / `css-oracle-deep.md` — the attribute-selector and
  @font-face unicode-range channels.
- `sealed-deep.md` — the no-JS channels: CSS oracle, @font-face, LRU,
  counter, token, rate-limit, recency.
- `server-state-channels.md` / `server-state-deep.md` — the mutation
  oracles: LRU eviction, counter, one-shot token, rate-limit, last-seen.
- `timing-oracles.md` — the slow-vs-fast, cache-probe, resource-timing,
  DOM-timing channels.
- `history-oracles.md` — the :visited, window.open, history.length
  channels.
- `readback-oracles.md` — the exfil: a listener, a write-back, a
  DOM-writeback, a server-state read.

## The delivery — the page's path to the bot

- `bot-delivery.md` / `bot-delivery-deep.md` / `bot-triage.md` — the
  /report, the data: URL, the stored page, the managed-policy bot, the
  airgapped bot, the JSDOM bot.
- `delivery-shapes.md` / `delivery-troubleshoot.md` — the delivery
  variants and their failures.

## The CSP — the channel's gates

- `csp-matrix.md` — which directive blocks which channel.
- `same-site-and-cookie.md` — the cookie's reach per channel.
- `browser-behavior.md` — the per-browser oracle availability.

## The reconstruction — assembling the secret

- `reconstruction.md` / `reconstruction-deep.md` — a binary-search
  boolean, a sorted-secret char-set, an n-gram beam search.
- `channel-selection.md` — the decision tree for picking the oracle.

## The workflow — the attack sequence

- `workflow.md` / `workflow-deep.md` / `field-manual.md` — the
  end-to-end sequence with each step's failure.
- `audit-checklist.md` — a self-audit for the analysis.
- `evidence-rules.md` — the candidate-vs-confirm standard.
- `negative-results.md` — recording a dead channel.

## The payloads — the complete corpus

- `payload-dictionary.md` / `payload-variants.md` — every payload by
  oracle family.
- `extended-corpus.md` — the complete oracle + grep + payload index.

## The cases — the worked examples

- `case-studies.md` / `real-world-cases.md` / `ctf-shapes.md` — the
  named shapes end to end.
- `verified-chains.md` — the HTB Stylish unicode-range card.

## The theory — why it works

- `theory.md` / `theory-deep.md` — the SOP side-channel, the info-
  theoretic bound, the declarative match.
- `evasion-and-filter.md` — each defense and the surviving channel.

## The framework — the per-stack surface

- `framework-matrix.md` / `frameworks-deep.md` — the per-stack bot,
  store, CSP, CSS surface.
- `whitebox-hunt.md` — the greps that find each surface.

## The mistakes — the failure modes

- `common-mistakes.md` / `error-analysis.md` / `common-questions.md` /
  `extended-questions.md` — the confusions, the failures, the answers.
- `troubleshoot.md` — when the leak doesn't work.
- `glossary.md` / `extended-glossary.md` — the vocabulary.

## The deeper references — the exhaustive coverage

- `oracle-mechanics.md` — how each channel actually works.
- `oracle-calibration.md` — the control pair, per channel.
- `oracle-selection.md` / `channel-selection.md` — the decision tree.
- `oracle-deep-dive.md` — the remaining channel details.
- `advanced-oracles.md` — the subtler channels.
- `delivery-vectors.md` — every delivery path.
- `detection-workflow.md` — the detection sequence, step by step.
- `extended-workflow.md` — the attack, fully spelled out.
- `extended-deep.md` — the mechanics, exhaustively.
- `edge-cases-deep.md` — every variant that breaks the assumptions.
- `quick-reference.md` — the one-page field card.
