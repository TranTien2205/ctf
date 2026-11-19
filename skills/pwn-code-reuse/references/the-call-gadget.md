# call/jmp gadgets — landing on a function


After the argument pops, a call/jmp gadget transfers control to the
function — or you land directly on the function's address (ret into it
treats the next stack entry as its return address).

## Two shapes

- Land on `call func` / `jmp func` gadget — explicit transfer.
- Land on `func` itself — ret pops it as the "return address"; the
  function runs with your stack as its frame.

## The return-address slot

After landing on a function, the NEXT qword is ITS return address —
set it to another gadget (to continue the chain) or a safe exit.
