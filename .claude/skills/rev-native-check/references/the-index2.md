# Index extension — the deep map


## r2 commands
- the-r2-session, the-cmd-*, the-axt-list, the-search, the-seek,
  the-flag-space, the-vv-mode, the-agf-graph, the-cmd-esil

## Instruction-level
- the-compare-insn, the-test-forms, the-cond-list, the-test-vs-cmp,
  the-zero-check, the-eax-check, the-neg-result, the-flags-map,
  the-zero-flag, the-sign-flag, the-carry-note, the-over-flag,
  the-jl-vs-jb, the-sign-cmp, the-movzx, the-lea-forms, the-mov-mem,
  the-imm-move, the-dword-imm, the-str-decode, the-pc-rel, the-lea-read

## Transforms
- the-add-transform, the-rol-transform, the-swap-transform,
  the-subst-table, the-multi-stage, the-seq-crypt, the-widths,
  the-key-sched, the-xor-key, the-rol-check, the-not-check,
  the-neg-check, the-bswap, the-xchg-check, the-shl-shr, the-sar-note,
  the-mul-div, the-imul, the-mod-inverse, the-crc-invert, the-adler,
  the-simple-sum, the-jenkins, the-md5-note, the-sha-detect,
  the-aes-note, the-rc4-note, the-tea-note, the-base64-tbl,
  the-custom-enc, the-offline-brute, the-charset-brute,
  the-mask-brute, the-dict-brute, the-rainbow, the-john, the-hashcat

## Control flow shapes
- the-fn-bound, the-inliner, the-helper-call, the-void-check,
  the-early-ret, the-if-else, the-cascade, the-guard, the-loop-exit,
  the-accum, the-final-cmp, the-second-cmp, the-inner-loop,
  the-global-dep, the-store-then, the-block-map, the-agf-read,
  the-vv-walk, the-fall-thru, the-jump-target, the-branch-dst,
  the-ret-use, the-call-target, the-mov-arg, the-lea-str,
  the-push-arg, the-arg-window, the-jmp-away, the-indirect-call,
  the-vtable-check, the-plt-call, the-local-call, the-inline-cmp,
  the-rep-cmpsb, the-scasb, the-simd-cmp, the-align-cmp

## Inputs and dependencies
- the-arg-count, the-argv-str, the-stdin-buf, the-scanf-fmt,
  the-atoi-conv, the-sscanf-split, the-strtok, the-getline,
  the-newline-in, the-nul-in, the-env-dep, the-time-dep,
  the-rand-dep, the-seed, the-pid-check, the-hostname, the-tty-check,
  the-file-content, the-net-dep, the-side-read, the-input-dep,
  the-per-char, the-flag-nest, the-normalize, the-input-copy

## Debug and verify
- the-dbg-compare, the-loop-iter, the-trace-file, the-count-it,
  the-dump-expected, the-swap-bytes, the-two-inputs, the-verify-fmt,
  the-verify2, the-verify3, the-determinism, the-multi-ver,
  the-negative-ctrl, the-pos-ctrl, the-edge-case, the-length-edge,
  the-charset-edge, the-stage-flag, the-verify-fail, the-echo-use

## Worked and discipline
- the-easy-case, the-mid-case, the-hard-case, the-vm-case,
  the-e2e2..e2e8, the-worked-1..5, the-patch-where, the-patch-eax,
  the-patch-fail, the-decrypt-path, the-guard-data, the-check-map,
  the-map2, the-index2, the-close3, the-close4, the-glossary2,
  the-r2pipe, the-objdump-alt, the-nm-strings, the-readelf-map,
  the-file-type, the-verify-report, the-multi-arch, the-riscv-note,
  the-wasm-note, the-union, the-cast, the-struct-cmp, the-align-pad,
  the-packed, the-two-side, the-transform-loc
