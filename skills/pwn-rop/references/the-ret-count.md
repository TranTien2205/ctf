# The ret count — alignment entries


How many rets: count the qwords to the call; if the call's entry rsp
is off, one ret fixes it — more than two rets signals a different bug
(the count is wrong, not the alignment).
