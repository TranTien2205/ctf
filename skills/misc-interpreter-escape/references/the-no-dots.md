# No dots — getattr instead

No `.` — `getattr(obj,'attr')` reaches the attribute; `x['attr']`
on a dict does too.

## No .

getattr/dict[] — attribute access without the dot.
