# The return value — rax after a call


A call's return lands in rax — the chain rarely reads it directly
(no register-read gadgets matter); the value's USE is indirect (a
subsequent call's arg if you can move it).
