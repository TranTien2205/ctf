# getattr — the name builder

`getattr(obj, "attr"[::-1])`, `getattr(obj,"at"+"tr")`,
`getattr(obj,chr(95)+chr(95))` — the attribute name is built at run
time, so a string blacklist never sees the source.

## The three forms

getattr(obj,'at'+'tr'), getattr(obj,'attra'[::-1]), getattr(obj,chr(...)).
