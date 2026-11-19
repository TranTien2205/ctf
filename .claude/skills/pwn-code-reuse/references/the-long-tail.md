# The long tail — multi-instruction gadgets


A gadget may be several instructions: `pop rdi; pop r14; pop r15; ret`
— three pops — consumes three qwords, sets three registers; the chain
must budget the extra qwords.
