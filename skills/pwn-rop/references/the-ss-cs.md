# cs/ss — the segment values


The frame's cs/ss: 0x33/0x2b typically (64-bit user segments) — wrong
values crash the frame load; copy them from a real frame (r2 -d at a
signal, or the standard values).
