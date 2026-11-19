# The two addresses — stub vs resolved


Every import has two addresses: the PLT stub (binary, fixed) and the
resolved function (libc, needs leak) — call the stub; read the GOT
for the resolved.
