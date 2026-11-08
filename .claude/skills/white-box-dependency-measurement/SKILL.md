---
name: white-box-dependency-measurement
description: >
  Measure the installed dependency instead of reasoning about the published one.
  Use when a chain depends on what a library, proxy, engine or system tool
  actually does — a pinned version, a vendored module, an old base image — and
  when a negative result has to be recordable. Read the module source in the
  running container, build an oracle from what the app already leaks, and state
  every boundary as a number.
tags: [white-box, process, method, measurement, oracle, dependency, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "a behaviour is about to be asserted from documentation rather than from the installed source"
    - "a measurement has not been re-run on a clean instance before being recorded"
    - "no oracle with a distinguishable signal can be built for the deciding function"
evidence_level: verified
---
# White-box dependency measurement — Process Skill

**Verified here.** Chain cards that this method produced, in this repository:
`cscv2026-chromatic-mergecatalog-constructor-prototype-ejs-outputfunctionname-rce`,
`cscv2026-chromatic-xssi-json-svg-polyglot-cache-key-collision-bot-rce`,
`cscv-inoffice-authority-form-acl-bypass-restricted-pickle`.

Every one of those chains turns on a behaviour that **is not in any
documentation** and that was established by reading the installed code or by
observing the installed binary:

- `ejs` 3.1.6 compiles a prototype-inherited `outputFunctionName` option into
  `var <name> = __append;` verbatim — read out of the installed `ejs/lib/ejs.js`,
  not out of the changelog.
- Angular's `FetchBackend` strips `/^\)\]\}',?\n/` before `JSON.parse`, and the
  app's own `hasDocumentPreamble()` only rejects a first non-space `{` or `[`.
  The polyglot exists because both were read, in the shipped bundle and the
  shipped handler.
- Debian `file(1)` in that image answers `image/svg+xml` for a body whose first
  token is a `<!DOCTYPE svg>` — a property of the installed magic database, not
  of SVG.
- HAProxy `2.9.7-5742051`: `http_get_path()` yields *not-found* for an
  authority-form target, so the `path` ACL cannot match. Werkzeug's
  `parse_options_header` uses Python `str.strip()`, which strips `0x0b`, while
  HAProxy strips only SP and HTAB. Two parsers, two installed implementations,
  one differential.

None of that is derivable from a version number. It is derivable from `cat`.

## First probe

Name the **deciding function** — the single function whose behaviour the chain
depends on — then read its installed source:

```bash
docker compose ps                               # the container that runs it
docker compose exec <svc> sh -lc 'cat /app/package-lock.json | grep -A2 \"<lib>\"'
docker compose exec <svc> sh -lc 'sed -n "<line>,<line+40>p" /app/node_modules/<lib>/lib/<file>.js'
docker compose exec <svc> sh -lc 'python3 -c "import <mod>, inspect; print(inspect.getsource(<mod>.<fn>))"'
docker compose exec <svc> sh -lc '<binary> -v; <binary> --version'
```

**Falsifier** — the observation that closes this method: the installed source is
byte-identical to upstream at the published version **and** the published
behaviour is documented for the exact input shape in play. Then stop measuring
and go build the chain; there is no differential here.

## Rule 1 — never reason from the published version

A version number tells you which changelog to read. It does not tell you what
the deployed file contains. Images get patched, modules get vendored,
`package-lock.json` disagrees with `package.json`, a distribution backports, a
challenge author edits `node_modules` directly.

| Do not say | Say instead |
|---|---|
| "ejs 3.1.6 is vulnerable to CVE-2022-29078" | "`node_modules/ejs/lib/ejs.js:<line>` emits `var ' + opts.outputFunctionName + ' = __append;`, read in the running container" |
| "vm2 3.8.3 is ancient, so it escapes" | "`reporter.js:407` sets `allowedModules` to `'*'` only when `allowLocalFilesAccess === true`; it is false here, so `require` throws — observed" |
| "sanitize-html strips tags" | "`cleanString` runs `sanitizeHtml(..., {allowedTags: []})` then decodes exactly `&apos; &#39; &quot; &amp;`, so the decode step can emit only `' \" &` — read at `sanitize.js:32-35`" |

Three checks, in this order, every time:

1. **Is it the version claimed?** `package-lock.json`, `pip freeze`,
   `dpkg -l`, `--version`. Compare against what the handout *says*.
2. **Is the file upstream's?** `npm pack <lib>@<v>` / `pip download` and diff the
   one file you care about. A challenge author's edit inside `node_modules` is
   the whole challenge when it happens.
3. **Does the deciding function do what the docs claim?** Read it. Then prove it
   with a live probe.

## Rule 2 — build an oracle from what the app already leaks

You rarely get output. You almost always get a *difference*. Any of these is a
usable oracle, and each has carried a real measurement here:

| Channel | Example that worked |
|---|---|
| **Error text** | handlebars `Missing helper: <name>` separated the sandbox globals that are registered as helpers (`require`, `render`, `respond`, `setTimeout`, `childTemplateParseData`, `childTemplateSerializeData`) from those that are not (`eval`, `Function`, `global`, `globalThis`, `process`, `merge`, `escape`, `print`, …) — `CSCV2026/diemthi/WRITEUP.md` |
| **A 404 body that echoes a sanitized value** | the export route's 404 body interpolates the requested template name, and it does so *after* sanitisation, which made `removeBlockedWord()` directly observable and let 22 bypass shapes be tested at one request each |
| **Status-code split** | in-office: plain `multipart/form-data` → `403`, `\x0b`-prefixed → reaches Flask. One byte, two outcomes, and the whole ACL bypass proven before any pickle was built |
| **A different status for a different failure** | in-office: `503` (no backend selected) vs `404`/`200` (backend reached) separated the `use_backend` host rule from the path ACL |
| **Response-size / content delta** | chromatic: `GET /api/media/raw?id=…&workspace=<W>` then `GET /api/workspaces/manifest?workspace=<W>` and compare bodies — the cache-key collision was confirmed by the second body being the first one, before a single bot visit was spent |
| **Presence/absence in a list** | the import route returns unknown ids in `missing`, so the complement of a candidate list is every id that exists — an authorization-free existence oracle, unrate-limited, ~150k ids per request |

Pick the oracle **before** the payload. An oracle that answers yes/no in one
request is worth more than a payload that might do everything.

## Rule 3 — probe the real engine, never a local re-implementation

A local reimplementation measures your model of the library. It is the cheapest
way to be confidently wrong.

- Drive the fuzz through the app's own HTTP entry point, so the real middleware
  chain runs in the real order. The diemthi sanitizer has **two** paths —
  `req.body.template` is cleaned once, a string inside `req.body.data` is cleaned
  twice (the JSON text, then the parsed value). A re-implementation would have
  modelled one.
- When the engine is behind another service, `exec` into that service and call it
  there, with its installed modules and its environment.
- When the behaviour belongs to a binary (`file`, a proxy, a headless browser),
  run *that* binary in *that* image. `HeadlessChrome/79.0.3945.130` launched
  `--no-sandbox` against `file:///tmp/jsreport/autocleanup/<uuid>-chrome-pdf.html`
  was read out of jsreport's own log, not assumed from a Dockerfile.

## Rule 4 — state the boundary as a number

A negative result is only recordable if it has a denominator. "I could not find
a sink" is an impression; the following are measurements, and each one closed a
layer in `tools/decide.py` rather than leaving it open:

- **24228** grammar-fuzz cases across both sanitizer paths → **0** outputs
  containing `<`, **0** containing `secret`.
- **4605** NUL-free files scanned → **0** with a triple-stash expression in a
  non-text HTML context, **0** with a steerable `iframe/object/embed/frame/base`.
- **5098** files content-scanned → the password value appears at exactly **1**
  path.
- **350** symlinks enumerated in the app container → **0** leading into the
  secret directory.
- **0 of 8** store-template candidates polluted on a pristine `docker compose up`.

Write the number into the hypothesis ledger, not into prose:

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --verdict inconclusive --evidence '<verbatim tool output incl. the counts>'
```

A counted negative is what lets `tools/decide.py` return `switch_class` honestly
instead of the same class a sixth time.

## The trap that cost a session — a measurement that lied

Two failure modes, both real, both from `CSCV2026/diemthi/`:

1. **The scan that skipped symlinks.** A content scan that does not resolve
   symlinks cannot support the sentence "the value exists only at `<path>`".
   That container held **350** symlinks. The scan had to be redone with links
   followed (and with a loop guard) before the claim was worth anything. Any
   `find`/`os.walk` that defaults to not following links is a silently
   incomplete denominator — state whether links were followed, every time.
2. **The needle in the measurement's own environment.** A scan looking for a
   secret value, run from a process that had that value in its own environment,
   hits `/proc/self/environ` and reports a find that is the scanner itself. The
   same class of contamination is recorded a second time in
   `CSCV2026/diemthi/TICKET.md`: earlier local `LANDED`/`ASSETS` evidence for the
   `{#child}` chain came from a store that had been populated **by hand** in an
   earlier experiment; a pristine `docker compose up` re-measurement reported
   "pollution no" for all 8 candidates and the evidence had to be retracted.

**The rule: always re-run a measurement so the probe cannot contaminate its own
result.** Concretely — scrub the needle from the scanner's environment and
re-run; exclude `/proc/self`, `/proc/<own pid>` and your own artifacts; and
re-measure on a freshly rebuilt instance before any result is written to a chain
card. A measurement that has been run exactly once is a hypothesis.

## Blast radius

- Reading installed module source is read-only. `docker compose exec` into a
  **shared** instance may not be available at all; if the instance is not yours,
  rebuild the handout locally and measure there, then confirm the one deciding
  behaviour remotely with a single read-only oracle call.
- A fuzz driven through the app's HTTP entry point is load. Keep concurrency
  low, and never point a 24k-case grammar fuzz at a shared challenge host — run
  it locally and carry only the *conclusion* to the instance.
- Any probe that writes (an import, an upload, a planted record) goes through
  `tools/hooks.py pre-probe --write-ack` after the chain card's `blast_radius`
  has been read, and the rows are removed afterwards.
- Re-measuring on a pristine rebuild means destroying your local state, not the
  organiser's. Never "reset" a shared instance to clean a measurement.

## Route to depth

- The installed source differs from upstream in a way you did not expect → that
  edit is the challenge; `tools/classify.py --source <dir>` on the edited file
- The differential is between two parsers of the same request →
  `../web-parser-differential/`
- The measured behaviour is an option or property inherited through a prototype →
  `../web-prototype-pollution/`
- The measured behaviour is a template engine compiling an option into source →
  `../web-ssti/`
- The measurement is for a proxy or cache key → `../web-cache-poisoning/`,
  `../web-request-smuggling/`
- You measured a boundary and every layer is closed → `tools/decide.py <challenge>`;
  report the numbers as the evidence
- Nothing in the handout differs from stock and you do not yet know what the
  author added → `../white-box-intended-path/`

## Discipline

- Documentation is a hypothesis about the installed code. The installed code is
  the evidence. `../../EVIDENCE_POLICY.md`.
- A CVE identifier is not a measurement. Quote the line of installed source that
  makes the CVE apply here, or do not name it.
- One measurement, once, is not a result. Re-run it clean.
- A generated script is not an observation until it has run and produced captured
  output — see the reader/writer/hypothesizer split in `../../TRAINING.md`.
- A timeout or a connection reset is evidence about availability. It is never a
  confirm, and `tools/hooks.py post-probe` will refuse it.

## Field notes

`field-notes.md` in this directory grows every time a measurement decides a
session. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
