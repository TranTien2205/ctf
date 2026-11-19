# The frame revisit — where the chain sits


The chain starts at the saved-rip slot: buf_end + the frame's
overhead (saved rbp's slot, then saved rip). The offsets differ by
function — measure, don't assume.
