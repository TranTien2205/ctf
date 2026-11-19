# add rsp — the skip gadget


`add rsp, N; ret` skips N bytes of the frame — a way to jump over
chain entries you can't use (or to skip the saved regs block).

## The use

- Skip a fixed-size structure between the overwrite and your chain.
- A limited pivot when a full pivot isn't available.
