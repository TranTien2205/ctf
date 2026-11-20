# MAM — compressed prefetch

8.1+ `.pf` bodies are XPRESS-Huffman compressed — `strings` returning
nothing is compression, not emptiness. `prefetch.py` decodes it;
`xpress.py --mam file.pf -o out.pf` unwraps the stream for manual
inspection.

## Compressed

MAM -> xpress.py, then SCCA.

## Not empty

Compression, not emptiness.
