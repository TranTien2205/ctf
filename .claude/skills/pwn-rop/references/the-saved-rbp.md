# The saved rbp slot — the pivot lever


Between the buffer's end and saved rip: the saved-rbp qword — its
value matters for leave;ret pivots (it becomes the new rsp).

## The use

Set saved-rbp = the pivot target; the leave;ret consumes it.
