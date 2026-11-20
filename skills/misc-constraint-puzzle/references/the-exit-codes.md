# Solver exit codes — the run's verdict

Exit nonzero on any failure (EOF before flag, parse stall, deadline)
so the transcript tail always carries the run's verdict — a silent
exit-0 without a flag hides a failure.
