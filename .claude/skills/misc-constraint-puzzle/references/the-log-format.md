# Log format — raw plus derived

Log each round as `N raw-bytes | parsed | answer | verdict` — raw
first so a drift fix is replayable, derived second so a wrong answer
is traceable to parse or solve.
