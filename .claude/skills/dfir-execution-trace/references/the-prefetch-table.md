# Prefetch — the version table decides offsets

v17 XP (1 FILETIME @36, count @60), v23 Win7 (**1** @44, count @68),
v26 8.x (8 @44, count @124), v30 Win10 (8 @44, count @124/116 by
variant), v31 Win11 (8 @44, @116). "First run" = oldest non-zero of
the eight; Win7's single timestamp makes that answer not exist.

## The offsets

Read the version DWORD first.

## First run

Oldest non-zero of eight; Win7 lacks it.
