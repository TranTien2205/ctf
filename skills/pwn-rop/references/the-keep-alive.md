# Keep-alive — the persistent socket


Some services keep the connection alive across stages — the same
socket serves stage 1 and 2; a close-then-reopen may lose state.
