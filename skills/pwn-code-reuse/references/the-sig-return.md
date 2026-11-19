# Sigreturn — the frame loader


rt_sigreturn loads the frame from the stack — the SROP primitive; the
frame's 248 bytes set every register including rip.
