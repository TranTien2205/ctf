# pop rsp — the direct pivot


`pop rsp; ret` sets rsp to the next qword — the cleanest pivot:
pop rsp = the buffer where your real chain lives.

## The recipe

    pop rsp ; the_buffer_addr

rsp now = buffer; the next ret pops its first entry.
