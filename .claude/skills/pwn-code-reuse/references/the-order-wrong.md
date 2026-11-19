# The wrong order — common sequence bugs


- Pop before the offset: the gadget lands in the buffer, not at rip.
- Arg before the pop: the pop consumes the wrong qword.
- Call before the args: the call sees unset registers.
- Ending before the work: the chain exits before the payload.

The audit: walk the chain mentally, tracking rip and each register.
