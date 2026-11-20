# apache vs nginx access logs

Same common/combined shape; nginx adds $request_time and upstream
fields in some configs. The column positions differ slightly —
verify by head before cutting.

## The trap

An nginx log with `log_format` including $request_time appends
fields after the standard ones — positional awk still works for
$1/$7/$9 but the tail shifts; check the format comment or head
first.
