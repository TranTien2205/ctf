# The side write — a gadget's memory effect


A `mov [rX], rY` inside a gadget writes where rX points — ensure rX
isn't controlled-but-wrong at that point; the write's target is part
of the gadget's semantics.
