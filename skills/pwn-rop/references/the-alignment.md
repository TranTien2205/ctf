# The alignment ret — the movaps fix


x64 libc calls need rsp ≡ 0 mod 16 at the function entry — a chain
that's one qword off crashes inside system on a `movaps`.

## The fix

Insert one bare `ret` gadget between the last pop and the call — it
advances rsp 8 bytes. rop_chain.py inserts it automatically when the
count leaves rsp misaligned.

## The tell

A crash INSIDE the called function (not at the call site) on a
movaps-family instruction is the alignment signature.
