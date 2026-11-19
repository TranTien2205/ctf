# Fencing the chain — the guard values


Between chain entries, benign qwords (0, a ret) fill gaps — they keep
the stack walk clean when a gadget consumes more slots than you
provided intentionally.
