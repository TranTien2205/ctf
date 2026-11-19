# The dl alignment — the r_offset constraint


The fake rela's r_offset is the write target — the resolved address
goes there; it must be a writable slot the program later calls
through (or the chain continues from a controlled ret).
