# The operational checklist — bytecode/custom-VM — checklist

Companion to `checklist-deep.md`.

## Checklist

- [ ] [ ] Magic/header → format + version named
- [ ] [ ] .pyc → marshal version matched
- [ ] [ ] Custom VM → dispatch loop located
- [ ] [ ] pyc_dis --strings / wasm_info --names
- [ ] [ ] Check function located
- [ ] [ ] Opcode table recovered (custom VM)
- [ ] [ ] Program stream decoded
- [ ] [ ] Transform ops read in order
- [ ] [ ] Expected value extracted
- [ ] [ ] Input inverted/derived
- [ ] [ ] Flag-length = read-op count checked
- [ ] [ ] Program run on the input → verdict
- [ ] [ ] Flag through the hook
