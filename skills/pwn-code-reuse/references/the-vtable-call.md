# The vtable call — C++'s dispatch


A C++ virtual call `call [obj + offset]` is an indirect dispatch —
control the object's vtable pointer, and the call goes to your chosen
function.

## The forge

Plant a fake vtable; overwrite the object's vptr; the next virtual
call fires your function — the C++ analogue of GOT overwrite.
