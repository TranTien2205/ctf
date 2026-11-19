---
name: rev-native-check
description: >
  Action-oriented depth skill for Native deciding check. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: rev-bytecode-vm, pwn-stack-overflow.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [rev, rev-native-check, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Native deciding check

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

locate the input read, follow the value to the comparison, and quote the disassembly that carries it: a described check is not a measured one. r2 -A then afl then pdf @ main; gdb is absent, so r2 -d is the debugger

**Falsifier** — the observation that closes this class: the comparison is against a value computed at run time from something you cannot observe or supply, so replicating the check in python cannot produce the input
## Recognise

A native binary reads input and prints a verdict. The work is locating **the
deciding check** — the one comparison the flag actually passes through — and
replicating it, not describing the whole binary.

## Confirm

Locate the input read, follow the value to the comparison, and quote the
disassembly that carries it. Then replicate the check in Python and verify: a
replicated check that produces the accepted input is the solve; a described
check is not a measured one.

| Pattern | Where it usually sits |
|---|---|
| literal `strcmp`/`memcmp` | the answer is one `strings` away or one xref from the read |
| per-character transform then compare | replicate the transform in Python |
| table-driven check | dump the table, invert the mapping |
| anti-debug or packer wrapper | `../rev-triage/references/packer-analysis.md` first — the check is underneath |

## Traps

- A comparison against a value computed at run time from something you cannot
  supply means replication cannot produce the input — that is the class
  falsifier, not a harder instance.
- `radare2` is the dynamic story here: `r2 -d` debugs, `r2 -A` analyses, `pdf @
  main` disassembles. There is no `gdb`.
- Read the xrefs **to** the success/failure strings — they walk you backwards
  to the check faster than `afl` walks you forwards.

## Operational probe

```bash
r2 -A ./chal
r2 -c "afl; iz" ./chal          # functions, then strings — find the verdict text
```

## Routing

Shares signals with: `../rev-bytecode-vm/`, `../pwn-stack-overflow/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-reverse/patterns-ctf.md`
- `skills/ctf-reverse/tools.md`
- `skills/rev-triage/references/packer-analysis.md`

| Any native binary check question | `references/static-and-dynamic.md` |

### Reference corpus (under `references/`)

Topic-based; each topic has a base file plus `-deep`, `-checklist`, and
`-map` companions.

**Finding the check**

- `references/the-check.md` — the deciding compare defined
- `references/the-xref-path.md` — backwards from the verdict string
- `references/the-input-follow.md` — forwards from the read
- `references/the-axt-xref.md`, `references/the-axt-list.md`, `references/the-verdict-func.md`
- `references/the-afl-map.md`, `references/the-iz-strings.md`, `references/the-iz-find.md`, `references/the-pdf-func.md`, `references/the-pd-window.md`, `references/the-main-entry.md`, `references/the-check-func.md`, `references/the-import-list.md`
- `references/the-cmp-find.md`, `references/the-vv-mode.md`, `references/the-agf-graph.md`, `references/the-block-map.md`, `references/the-agf-read.md`, `references/the-vv-walk.md`

**Compare shapes**

- `references/the-strcmp-shape.md`, `references/the-transform-shape.md`, `references/the-table-shape.md`, `references/the-hash-shape.md`
- `references/the-cmp-shapes.md`, `references/the-compare-insn.md`, `references/the-branch-read.md`, `references/the-test-forms.md`, `references/the-test-vs-cmp.md`, `references/the-zero-check.md`, `references/the-eax-check.md`, `references/the-neg-result.md`
- `references/the-multi-check.md`, `references/the-length-check.md`, `references/the-byte-walk.md`, `references/the-loop-check.md`, `references/the-loop-body.md`, `references/the-index-reg.md`, `references/the-expected-arr.md`, `references/the-sum-check.md`
- `references/the-memcmp-n.md`, `references/the-strncmp-note.md`, `references/the-bcmp-note.md`, `references/the-strcasecmp.md`, `references/the-mem-str.md`, `references/the-inline-cmp.md`, `references/the-rep-cmpsb.md`, `references/the-scasb.md`, `references/the-simd-cmp.md`, `references/the-align-cmp.md`
- `references/the-switch-check.md`, `references/the-jump-table.md`, `references/the-chained-checks.md`, `references/the-or-checks.md`, `references/the-depth-count.md`, `references/the-two-args.md`, `references/the-arg-order2.md`, `references/the-store-then.md`, `references/the-mem-cmp.md`, `references/the-cmp-width2.md`, `references/the-const-cmp.md`, `references/the-ptr-cmp.md`, `references/the-bool-cmp.md`, `references/the-count-cmp.md`, `references/the-eq-cmp.md`, `references/the-range-cmp.md`, `references/the-mod-cmp.md`, `references/the-parity.md`, `references/the-sign-cmp.md`

**Flags and branches**

- `references/the-flags-map.md`, `references/the-zero-flag.md`, `references/the-sign-flag.md`, `references/the-carry-note.md`, `references/the-over-flag.md`, `references/the-jl-vs-jb.md`, `references/the-jump-target.md`, `references/the-fall-thru.md`, `references/the-branch-dst.md`

**Constants and expected values**

- `references/the-const-loc.md`, `references/the-const-pool.md`, `references/the-data-val.md`, `references/the-bss-built.md`, `references/the-stack-built.md`, `references/the-reg-const.md`, `references/the-build-instr.md`, `references/the-xor-build.md`, `references/the-imm-move.md`, `references/the-dword-imm.md`, `references/the-str-decode.md`, `references/the-pc-rel.md`, `references/the-lea-read.md`, `references/the-lea-str.md`, `references/the-lea-forms.md`, `references/the-mov-arg.md`, `references/the-push-arg.md`, `references/the-mov-mem.md`, `references/the-movzx.md`

**Transforms**

- `references/the-xor-key.md`, `references/the-add-transform.md`, `references/the-rol-transform.md`, `references/the-rol-check.md`, `references/the-swap-transform.md`, `references/the-subst-table.md`, `references/the-multi-stage.md`, `references/the-seq-crypt.md`, `references/the-widths.md`, `references/the-key-sched.md`, `references/the-not-check.md`, `references/the-neg-check.md`, `references/the-bswap.md`, `references/the-xchg-check.md`, `references/the-shl-shr.md`, `references/the-sar-note.md`, `references/the-mul-div.md`, `references/the-imul.md`, `references/the-mod-inverse.md`
- `references/the-crc-note.md`, `references/the-crc-invert.md`, `references/the-adler.md`, `references/the-simple-sum.md`, `references/the-jenkins.md`, `references/the-md5-note.md`, `references/the-sha-detect.md`, `references/the-aes-note.md`, `references/the-rc4-note.md`, `references/the-tea-note.md`, `references/the-base64-tbl.md`, `references/the-custom-enc.md`
- `references/the-checksum-in.md`, `references/the-luhn.md`, `references/the-parity-bit.md`, `references/the-hamming.md`, `references/the-xor-sum.md`, `references/the-rol-sum.md`, `references/the-poly.md`, `references/the-gf-note.md`, `references/the-matmul.md`, `references/the-linear-sys.md`, `references/the-algebra.md`, `references/the-mod-eq.md`, `references/the-gcd-note.md`, `references/the-prime-check.md`, `references/the-factored.md`, `references/the-bignum.md`, `references/the-fp-check.md`, `references/the-fp-bits.md`, `references/the-epsilon.md`

**Input paths**

- `references/the-argv-check.md`, `references/the-stdin-check.md`, `references/the-file-check.md`, `references/the-env-check.md`, `references/the-arg-ptr.md`, `references/the-arg-regs.md`, `references/the-read-call.md`, `references/the-buf-addr.md`, `references/the-fgets-n.md`, `references/the-gets-risk.md`, `references/the-scanf-width.md`, `references/the-arg-idx.md`, `references/the-env-ptr2.md`, `references/the-getenv2.md`, `references/the-arg-count.md`, `references/the-argv-str.md`, `references/the-stdin-buf.md`, `references/the-scanf-fmt.md`, `references/the-atoi-conv.md`, `references/the-sscanf-split.md`, `references/the-strtok.md`, `references/the-getline.md`, `references/the-newline-in.md`, `references/the-nul-in.md`
- `references/the-two-buf.md`, `references/the-same-buf.md`, `references/the-split.md`, `references/the-prefix-suf.md`, `references/the-keyfile.md`, `references/the-ini-parse.md`, `references/the-env-fmt.md`, `references/the-regex-check.md`, `references/the-fn-match.md`, `references/the-glob-note.md`, `references/the-strpbrk.md`, `references/the-strspn.md`, `references/the-isdigit.md`, `references/the-char-class.md`, `references/the-suffix-chk.md`, `references/the-inner-str.md`, `references/the-memmem.md`, `references/the-prefix-zero.md`, `references/the-magic.md`, `references/the-version-cmp.md`, `references/the-usage-msg.md`, `references/the-charset.md`, `references/the-length-gate.md`

**Techniques**

- `references/the-replicate.md`, `references/the-patch.md`, `references/the-patch-where.md`, `references/the-patch-eax.md`, `references/the-patch-fail.md`
- `references/the-break-check.md`, `references/the-debug-flow.md`, `references/the-dbg-compare.md`, `references/the-loop-iter.md`, `references/the-step-the-loop.md`, `references/the-count-it.md`, `references/the-dump-expected.md`, `references/the-trace-file.md`
- `references/the-side-channel-rev.md`, `references/the-early-exit.md`, `references/the-verify-loop.md`, `references/the-brute-pos.md`, `references/the-byte-oracle.md`, `references/the-timing-diff.md`, `references/the-exit-code.md`, `references/the-err-msgs.md`, `references/the-fail-print.md`
- `references/the-packer-first.md`, `references/the-obfuscation.md`, `references/the-self-mod.md`, `references/the-anti-debug.md`, `references/the-emulation.md`, `references/the-runtime-val.md`, `references/the-static-first.md`, `references/the-dynamic-end.md`
- `references/the-solver-note.md`, `references/the-backtrack.md`, `references/the-sat-shape.md`, `references/the-nonlinear.md`, `references/the-small-space.md`, `references/the-meet.md`, `references/the-offline-brute.md`, `references/the-charset-brute.md`, `references/the-mask-brute.md`, `references/the-dict-brute.md`, `references/the-rainbow.md`, `references/the-john.md`, `references/the-hashcat.md`

**Environment and dependencies**

- `references/the-env-dep.md`, `references/the-time-dep.md`, `references/the-rand-dep.md`, `references/the-seed.md`, `references/the-pid-check.md`, `references/the-hostname.md`, `references/the-tty-check.md`, `references/the-file-content.md`, `references/the-net-dep.md`, `references/the-side-read.md`, `references/the-input-dep.md`, `references/the-per-char.md`, `references/the-stateful.md`, `references/the-dependent.md`, `references/the-fork-check.md`, `references/the-mmaped.md`, `references/the-dyn-gen.md`, `references/the-seccomp-rev.md`, `references/the-signal-check.md`, `references/the-constructor.md`, `references/the-atexit-check.md`, `references/the-tls-check.md`, `references/the-threaded.md`, `references/the-alarm-race.md`, `references/the-state-mach.md`, `references/the-nfa.md`, `references/the-parser.md`, `references/the-serial.md`, `references/the-hyphens.md`

**Verify and worked examples**

- `references/the-verify-flag.md`, `references/the-verify-by-run.md`, `references/the-no-verify.md`, `references/the-verify-fail.md`, `references/the-verify3.md`, `references/the-determinism.md`, `references/the-multi-ver.md`, `references/the-negative-ctrl.md`, `references/the-pos-ctrl.md`, `references/the-edge-case.md`, `references/the-length-edge.md`, `references/the-charset-edge.md`, `references/the-two-inputs.md`, `references/the-swap-bytes.md`, `references/the-flag-print.md`, `references/the-flag-fmt.md`, `references/the-flag-dec.md`, `references/the-input-key.md`, `references/the-derive-flag.md`, `references/the-success-path.md`, `references/the-fail-path.md`, `references/the-input-as-flag.md`, `references/the-flag-in-check.md`, `references/the-print-of-flag.md`, `references/the-flag-file.md`, `references/the-computed-flag.md`, `references/the-decrypt-path.md`, `references/the-guard-data.md`, `references/the-flag-format2.md`, `references/the-flag-verify.md`, `references/the-hook2.md`, `references/the-stage-flag.md`
- `references/the-worked-1.md` … `references/the-worked-5.md`, `references/the-e2e2.md` … `references/the-e2e8.md`, `references/the-easy-case.md`, `references/the-mid-case.md`, `references/the-hard-case.md`

**r2 commands**

- `references/the-r2-session.md`, `references/the-cmd-afl.md`, `references/the-cmd-axt.md`, `references/the-cmd-pdf.md`, `references/the-cmd-pdj.md`, `references/the-cmd-afi.md`, `references/the-cmd-afv.md`, `references/the-cmd-agC.md`, `references/the-cmd-axff.md`, `references/the-cmd-aaa2.md`, `references/the-cmd-dbg.md`, `references/the-cmd-db.md`, `references/the-cmd-dr.md`, `references/the-cmd-dm.md`, `references/the-cmd-px2.md`, `references/the-cmd-ps2.md`, `references/the-cmd-dcu.md`, `references/the-cmd-drr.md`, `references/the-cmd-esil.md`, `references/the-cmd-w.md`, `references/the-cmd-wa.md`, `references/the-cmd-oo.md`, `references/the-search.md`, `references/the-seek.md`, `references/the-ps-read.md`, `references/the-px-read.md`, `references/the-aaf-analyze.md`
- `references/the-r2pipe.md`, `references/the-objdump-alt.md`, `references/the-nm-strings.md`, `references/the-readelf-map.md`, `references/the-file-type.md`

**Discipline and index**

- `references/the-workflow.md`, `references/the-detection.md`, `references/the-checklist.md`, `references/the-evidence-std.md`, `references/the-falsifier-list.md`, `references/the-no-check.md`, `references/the-traps-list.md`, `references/the-walk-order.md`, `references/the-easy-case.md`, `references/the-mid-case.md`, `references/the-hard-case.md`, `references/the-vm-case.md`, `references/the-check-map.md`, `references/the-map-index.md`, `references/the-index2.md`, `references/the-map2.md`, `references/the-glossary.md`, `references/the-glossary2.md`, `references/the-close2.md` … `references/the-corpus-end.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
