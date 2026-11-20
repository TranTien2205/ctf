# Binary protocols — struct, not text

Some puzzles speak binary — struct.unpack on recv_exact frames;
capture the first bytes to name the layout before assuming text.

## struct

recv_exact + unpack; capture names the layout.
