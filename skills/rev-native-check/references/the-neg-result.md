# The negative result — nonzero comparisons


strcmp returns <0/0/>0 — a jg/jl branch on it is an ORDERING check,
rare for flags but seen in custom comparators.
