# Deep: TCP flag shapes worth reading

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

SYN-only rows (`tcp.flags.syn==1 and tcp.flags.ack==0`) to many ports = scan/dial-out attempt shape. A flow whose lifetime is `SYN, data, RST` is torn, not closed. Long-lived flows with steady PSH+ACK small segments are interactive; large MSS-sized segments back-to-back are bulk. `tcp.analysis.retransmission` marks retransmits — exclude for payload-accurate counts.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
