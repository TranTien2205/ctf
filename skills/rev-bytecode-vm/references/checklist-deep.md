# The operational checklist — bytecode/custom-VM

## Identify
- [ ] Magic/header → format + version named
- [ ] .pyc → marshal version matched
- [ ] Custom VM → dispatch loop located

## Inventory
- [ ] pyc_dis --strings / wasm_info --names
- [ ] Check function located

## Decode
- [ ] Opcode table recovered (custom VM)
- [ ] Program stream decoded
- [ ] Transform ops read in order
- [ ] Expected value extracted

## Produce
- [ ] Input inverted/derived
- [ ] Flag-length = read-op count checked

## Verify
- [ ] Program run on the input → verdict
- [ ] Flag through the hook
