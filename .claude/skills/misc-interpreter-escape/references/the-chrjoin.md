# chr() joins — no banned byte

`chr(95)+chr(95)` builds `__` without an underscore literal;
`chr(105)+chr(109)+chr(112)...` builds `import`. pyjail_gen emits
this form for a banned attribute name.

## The build

chr() builds the byte; the source carries no banned literal.
