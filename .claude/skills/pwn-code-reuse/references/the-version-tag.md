# VERNEED — the version check trap


ret2dlresolve may trip a version check when the symbol has a version
requirement — the fake structures must satisfy or bypass the verneed
walk.

## The fix

Set the fake symbol's st_info/other to avoid the versioned path, or
align the fake structures so the version read lands benignly.
