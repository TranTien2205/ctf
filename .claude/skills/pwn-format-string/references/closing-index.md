# Closing index — the whole corpus

The modules, by job:

- Detect/measure: `detection` `arg-offset-finder` `the-leak-depth-table`
  `the-argument-window` `detection-by-crash`
- Primitives: `primitive-matrix` `fmtstr-as-rw-table` `leak-via-p`
  `arb-read-via-s` `arb-write-via-n` `partial-write` `blind-fmtstr`
  `count-field` `width-precision-fields` `percent-percent-escaping`
- Targets: `got-overwrite-fmt` `ret-addr-overwrite` `hooks-overwrite`
  `alternate-write-targets` `the-write-target-table`
- Composition: `format-string-leak` `canary-pie-composition`
  `fmtstr-inside-smash` `fmtstr-and-rop-composition` `multi-target-write`
  `two-stage-write` `second-stage`
- Internals: `the-stack-args` `x86-vs-x64-args` `the-first-six-args`
  `the-arg-consumption` `the-count-continuity` `starvation`
  `the-pointer-plant` `the-pointer-in-input`
  `the-write-through-pointer-chain` `the-write-value-constraint`
  `the-count-overflow` `partial-write-ordering` `the-precision-vs-width`
- Boundaries: `format-literal-boundary` `the-format-in-the-buffer`
  `printf-family-matrix` `the-printf-family-complete` `the-vfprintf-family`
  `format-wrapper-detection` `scanf-family` `the-sprintf-boundary`
  `fmtstr-write-vs-smash` `class-boundary`
- Edge/output: `output-restriction` `output-channels` `blind-write`
  `the-blind-leak-via-side` `the-multi-call-offset` `remote-vs-local`
- Misc: `tools-for-fmt` `the-call-site-args` `the-redirect-effect`
  `the-interpreted-input` `glibc-version-matrix` `write-granularity-table`
  `fmtstr-to-rip`
- Discipline: `workflow` `evidence` `falsifiers` `troubleshoot`
  `anti-patterns` `common-mistakes` `theory` `worked-examples`
  `case-studies` `negative-results` `multi-step-chains` `when-all-closed`
  `recon-order` `field-manual` `operator-notes` `preconditions` `glossary`
  `edge-cases` `the-read-vs-write-choice` `the-leak-shapes`
  `the-write-confirmation`
