# The link_map walk — enumerating libraries


link_map's chain lists every loaded object: l_addr (the base),
l_name, l_next — walking it enumerates the full library set.

## The find

r_debug → r_map → the l_next chain — every base without per-library
leaks.
