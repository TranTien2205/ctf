# The offset check — the page-alignment test


A real leak: low 12 bits = the symbol's offset's low 12 bits — a
mismatched low-12 means the wrong field was read.
