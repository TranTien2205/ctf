# Padding to the chain's end — the trailing bytes


After the chain's last entry, the buffer may continue — the trailing
bytes are the call's locals/args space or the ending's landing zone —
harmless, but bounded by the read's limit.
