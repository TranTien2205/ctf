# State save — preserving what the chain needs


A register holding a needed value must survive: callee-saved regs
preserve across calls; a re-set after the call is the alternative.
