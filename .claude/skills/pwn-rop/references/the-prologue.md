# The prologue — the callee's own frame


The callee's prologue pushes rbp and sets up its frame — on YOUR
stack — its frame sits above the chain; its ret pops the next chain
entry.
