# Heap anti-patterns — the ways runs go wrong


- Picking a technique before naming the version.
- Clicking through a menu interactively instead of scripting the
  alloc/free sequence.
- Corrupting fd without a heap leak on 2.32+ and wondering why the aim
  misses.
- Spraying blindly when the program exposes a fixed, knowable layout.
- Assuming unsorted-bin leak works on small chunks (tcache eats them).
- Writing a hook address on glibc 2.35+ and expecting a call.
- Releasing a "solved" exploit that only worked against a guessed libc.
- Treating an allocator abort as a crash to hide from — it names the
  exact check to bypass.
- Freeing guards in the wrong order and corrupting tcache state you
  needed clean.
- Claiming an overlap without a marker round-trip through both objects.
