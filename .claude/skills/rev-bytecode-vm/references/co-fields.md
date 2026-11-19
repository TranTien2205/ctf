# The code object — the fields that matter

marshal.loads gives a code object; its fields ARE the program's
data.

## co_code

The raw bytecode bytes — dis.dis decodes it.

## co_consts

Every constant: strings, numbers, tuples, nested code objects —
the check's expected value and flag-shaped strings live here.

    [c for c in code.co_consts if isinstance(c,str)]

## co_names

Names used: function calls, attributes, globals — the vocabulary
(check, verify, xor, key, flag).

## co_varnames

Local variable + argument names — readable names survive .pyc.

## co_consts nested code

Nested functions are code objects INSIDE co_consts — recurse:

    def walk(c, d=0):
        print(" "*d, c.co_name)
        dis.dis(c)
        for x in c.co_consts:
            if hasattr(x,'co_code'): walk(x, d+2)

## co_filename / co_firstlineno

Source hints — the original filename and line number.
