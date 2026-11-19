# More side effects — the subtle ones


- A gadget that pops N registers consumes N qwords — the chain must
  supply them even if you only need one.
- A `push`-containing gadget writes to the stack below rsp — usually
  harmless but consumes slots.
- A conditional branch inside the gadget may skip the ret entirely.
