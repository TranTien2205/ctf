# Random-dependent — the seeded check


expected = f(rand()) — the seed decides; if the seed is fixed
(srand(0) or no srand), the sequence is deterministic — replicate
it; if seeded by time/pid, find the seed's leak.
