# The red zone — the 128 bytes below rsp


The x64 ABI's red zone: functions may use [rsp-128..rsp] without
adjusting — a chain entry in the red zone could be clobbered by a
called function; keep the chain above rsp.
