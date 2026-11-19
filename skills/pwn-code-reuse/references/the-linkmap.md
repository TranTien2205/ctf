# The link_map — the resolver's context


The resolver's first arg is a link_map pointer — ret2dlresolve passes
a controlled one (or reuses the real one) — the structure the
resolution walk reads.
