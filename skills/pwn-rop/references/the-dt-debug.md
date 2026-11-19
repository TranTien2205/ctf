# DT_DEBUG — the debugger's link_map handle


The DT_DEBUG dynamic entry points at the r_debug structure — which
points at the link_map list — the loaded libraries' bases.

## The use

A read of r_debug.r_map walks the link_map list — every loaded
library's base is enumerable — the leak-free base find on some
setups.
